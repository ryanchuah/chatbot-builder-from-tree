import csv
import os
import re
import json
from collections import deque
from pathlib import Path

import shutil
from chatbot_data import Intents, Entities, Usersays, Agent, PackageJson, AgentAPI

WEBHOOK_USED = True  # change this value depending on whether webhooks/fulfillment will be used
QUESTION = 0
YES = 1
NO = 2
CLARIFICATION = 3
IDENTIFIER = 4


class CSVData:

    def format_possible_offset(self, string):
        # if string is "1 Line below", will return "1".
        # if string is "You are unhealthy", will return "You are unhealthy"
        s = string.split(" ", 1)
        if s[0].isdigit():
            return s[0]
        else:
            return string

    def format_identifier(self, string, regex):
        return regex.sub("-", string).lower()

    def csv_data(self, path):
        regex = re.compile(r"[^a-zA-Z0-9_-]")  # (a-z A-Z), digits (0-9), underscore (_), and hyphen (-)

        with open(path, 'r') as csv_file:
            data = []
            csv_reader = csv.reader(csv_file, delimiter=',')

            next(csv_reader, None)  # skip header during iteration
            identifiers = set()
            for row in csv_reader:
                row[YES] = self.format_possible_offset(row[YES])
                row[NO] = self.format_possible_offset(row[NO])
                row[IDENTIFIER] = self.format_identifier(row[IDENTIFIER], regex)  # replace invalid chars with a hyphen
                if not row[IDENTIFIER]:
                    raise ValueError("Identifier field in CSV file cannot be left blank")
                elif row[IDENTIFIER] in identifiers:
                    raise ValueError("Two or more identifiers in CSV file are equal. Identifiers must be unique.")

                identifiers.add(row[IDENTIFIER])
                data.append(row)
            return data


class CreateIntentsData:

    def __init__(self, data):
        self.csv_data = data
        self.intents = Intents(self.csv_data, WEBHOOK_USED)
        self.result_json_data = []
        self.result_yes_no = []
        self.result_clarification = []
        self.queue = deque()
        self.queue.append({
            "index": 0,
            "prev_row": None,
            "input_context": None,
            "curr_yes_or_no": None,
            "prev_yes_or_no": None,
            "output_context": [f"{self.csv_data[0][IDENTIFIER]}-initial"]
        })

    def walk_tree(self):
        visited = set()
        is_welcome_intent = True
        while self.queue:
            queue_head = self.queue.popleft()
            if self.queue_head_hash(queue_head) not in visited:
                visited.add(self.queue_head_hash(queue_head))

                curr_row = self.csv_data[queue_head["index"]]
                curr_clarification = curr_row[CLARIFICATION]

                if self.yes_no_is_empty(queue_head):
                    self.queue.append({
                        "index": queue_head["index"] + 1,
                        "prev_row": curr_row,
                        "input_context": queue_head["output_context"][0],
                        "curr_yes_or_no": None,
                        "prev_yes_or_no": None,
                        "output_context": [
                            f"{self.csv_data[queue_head['index'] + 1][IDENTIFIER].replace(' ', '-')}-initial"],
                        # "name": f"{self.csv_data[queue_head['index'] + 1][IDENTIFIER].replace('-', ' ').title()} - Initial"
                    })
                else:
                    self.handle_yes_no_fields(queue_head, YES)
                    self.handle_yes_no_fields(queue_head, NO)

                curr_intent = self.intents.intent_json(queue_head, is_welcome_intent)
                if is_welcome_intent:
                    self.result_yes_no.append("Welcome")
                elif queue_head["curr_yes_or_no"] is None and queue_head["prev_yes_or_no"] is None:
                    self.result_yes_no.append(None)
                elif queue_head["curr_yes_or_no"] is not None:
                    self.result_yes_no.append(YES if queue_head["curr_yes_or_no"] == YES else NO)
                elif queue_head["prev_yes_or_no"] is not None:
                    self.result_yes_no.append(YES if queue_head["prev_yes_or_no"] == YES else NO)

                self.result_json_data.append(curr_intent)
                self.result_clarification.append(curr_clarification)
                is_welcome_intent = False

        # append fallback_intent and clarification_intent to back of lists
        self.result_json_data.append(self.intents.fallback_intent)
        self.result_yes_no.append(None)
        self.result_json_data.append(self.intents.clarification_intent)
        self.result_yes_no.append("Clarification")

    def handle_yes_no_fields(self, queue_head, answer):
        curr_row = self.csv_data[queue_head["index"]]

        if curr_row[answer].isdigit():
            self.queue.append({
                "index": queue_head["index"] + int(curr_row[answer]),
                "prev_row": curr_row,
                "input_context": queue_head["output_context"][0],
                "curr_yes_or_no": None,
                "prev_yes_or_no": answer,
                "output_context": [curr_row[IDENTIFIER].replace(" ", "-"),
                                   curr_row[IDENTIFIER].replace(" ", "-") + ("-yes" if answer == YES else "-no")],
            })
        else:
            self.queue.append({
                "index": queue_head["index"],
                "prev_row": curr_row,
                "input_context": queue_head["output_context"][0],
                "curr_yes_or_no": answer,
                "prev_yes_or_no": None,
                "output_context": [curr_row[IDENTIFIER].replace(" ", "-"),
                                   curr_row[IDENTIFIER].replace(" ", "-") + ("-yes" if answer == YES else "-no")],
            })

    def queue_head_hash(self, queue_head):
        return queue_head["index"], queue_head["curr_yes_or_no"]

    def yes_no_is_empty(self, queue_head):
        curr_row = self.csv_data[queue_head["index"]]
        if curr_row[YES] == '' and curr_row[NO] == '':
            return True
        return False


class CreateChatbotFiles:
    data = CSVData()
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "questions-formatted.csv")
    create_intents = CreateIntentsData(data.csv_data(filename))
    create_intents.walk_tree()
    intents_list = create_intents.result_json_data
    yes_or_no_list = create_intents.result_yes_no
    clarification_list = create_intents.result_clarification
    chatbot_target_path = os.path.join(dirname, "target", "chatbot")

    def __init__(self):
        if os.path.exists(os.path.join(self.dirname, "target")):
            shutil.rmtree(os.path.join(self.dirname, "target"))

    def create_intent_files(self):
        usersays = Usersays()
        Path(os.path.join(self.chatbot_target_path, "intents")).mkdir(parents=True, exist_ok=True)

        with open(os.path.join(self.chatbot_target_path, "intents", "Clarification Intent.json"), "w",
                  encoding="utf-8") as file:
            clarification_intent_index = len(self.intents_list) - 1
            json.dump(self.intents_list[clarification_intent_index], file, indent=2)

        with open(os.path.join(self.chatbot_target_path, "intents", "Default Fallback Intent.json"), "w",
                  encoding="utf-8") as file:
            fallback_intent_index = len(self.intents_list) - 2
            json.dump(self.intents_list[fallback_intent_index], file, indent=2)

        for index in range(len(self.intents_list)):
            curr_name = self.intents_list[index]["name"]
            with open(os.path.join(self.chatbot_target_path, "intents", f"{curr_name}.json"), "w",
                      encoding="utf-8") as file:
                json.dump(self.intents_list[index], file, indent=2)

            with open(os.path.join(self.chatbot_target_path, "intents", f"{curr_name}_usersays_en.json"), "w",
                      encoding="utf-8") as file:
                if self.yes_or_no_list[index] == "Welcome":
                    json.dump(usersays.welcome_usersays_data, file, indent=2)
                elif self.yes_or_no_list[index] == "Clarification":
                    json.dump(usersays.clarification_usersays_data, file, indent=2)
                elif self.yes_or_no_list[index] == YES:
                    json.dump(usersays.yes_usersays_data, file, indent=2)
                elif self.yes_or_no_list[index] == NO:
                    json.dump(usersays.no_usersays_data, file, indent=2)
                elif self.yes_or_no_list[index] is None:
                    json.dump([], file, indent=2)
                elif self.yes_or_no_list[index] is not None:
                    raise RuntimeError("Error in internal code")

    def create_entity_files(self):
        entities = Entities()

        Path(os.path.join(self.chatbot_target_path, "entities")).mkdir(parents=True, exist_ok=True)

        with open(os.path.join(self.chatbot_target_path, "entities", "confirmation.json"), "w",
                  encoding="utf-8") as file:
            json.dump(entities.confirmation_entity, file, indent=2)

        with open(os.path.join(self.chatbot_target_path, "entities", "confirmation_entries_en.json"), "w",
                  encoding="utf-8") as file:
            json.dump(entities.confirmation_entries, file, indent=2)

    def create_agent_file(self):
        agent = Agent(WEBHOOK_USED)
        with open(os.path.join(self.chatbot_target_path, "agent.json"), "w", encoding="utf-8") as file:
            json.dump(agent.agent_data, file, indent=2)

    def create_package_json_file(self):
        package_json = PackageJson()
        with open(os.path.join(self.chatbot_target_path, "package.json"), "w", encoding="utf-8") as file:
            json.dump(package_json.package_json_data, file, indent=2)

    def create_zip_file(self):
        shutil.make_archive(self.chatbot_target_path, "zip", self.chatbot_target_path)

    def create_agent_api_file(self):
        agent_api = AgentAPI(self.clarification_list)
        with open(os.path.join(self.dirname, "target", "agent.js"), "w", encoding="utf-8") as file:
            file.write(agent_api.agent_code(self.intents_list))

    def create_chatbot_files(self):
        self.create_intent_files()
        self.create_entity_files()
        self.create_agent_file()
        self.create_package_json_file()
        self.create_zip_file()
        if WEBHOOK_USED:
            self.create_agent_api_file()


if __name__ == '__main__':
    create_chatbot_files = CreateChatbotFiles()
    create_chatbot_files.create_chatbot_files()
