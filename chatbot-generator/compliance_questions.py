import csv
import os
import re
import json
from collections import deque
from pathlib import Path
# from zipfile import ZipFile
import shutil
from chatbot_data import Intents, Entities, Usersays, Agent, PackageJson

QUESTION = 0
YES = 1
NO = 2
IDENTIFIER = 3


class CSVData:

    def format_possible_offset(self, string):
        # if string is "1 Line below", will return "1". If string is "Class 1", will return "Class 1"
        s = string.split(" ", 1)
        if s[0].isdigit():
            return s[0]
        else:
            return string

    def format_identifier(self, string, regex):
        # replace commas with spaces, then replace double spaces with single space
        result = string.replace(",", " ").replace("  ", " ").lower()

        # replace anything that is not in Dialogflow's allowed charset with a hyphen
        return regex.sub("-", result)

    def csv_data(self, path):
        regex = re.compile(r"[^a-zA-Z0-9_-]")  # (a-z A-Z), digits (0-9), underscore (_), and hyphen (-)

        with open(path, 'r') as csv_file:
            data = []
            csv_reader = csv.reader(csv_file, delimiter=',')

            next(csv_reader, None)  # skip header during iteration

            for row in csv_reader:
                row[YES] = self.format_possible_offset(row[YES])
                row[NO] = self.format_possible_offset(row[NO])
                row[IDENTIFIER] = self.format_identifier(row[IDENTIFIER], regex)
                data.append(row)

            return data


class CreateIntentsData:

    def __init__(self, data):
        self.csv_data = data
        self.intents = Intents(self.csv_data)
        self.result_json_data = [self.intents.welcome_intent]
        self.result_yes_or_no = [None]
        self.queue = deque()
        self.queue.append({
            "index": 0,
            "output_context": "DefaultWelcomeIntent-followup",
            "prev_was_yes_or_no": None
        })

    def walk_tree(self):
        visited = set()
        while self.queue:
            queue_head = self.queue.popleft()
            input_context = queue_head["output_context"]

            if queue_head["index"] not in visited:
                visited.add(queue_head["index"])

                self.handle_yes_no(queue_head, YES, visited, input_context)
                self.handle_yes_no(queue_head, NO, visited, input_context)

    def handle_yes_no(self, queue_head, answer_index, visited, input_context):
        curr_row = self.csv_data[queue_head["index"]]
        if curr_row[answer_index].isdigit() and queue_head["index"] + int(curr_row[answer_index]) not in visited:
            self.queue.append({
                "index": queue_head["index"] + int(curr_row[answer_index]),
                "output_context": curr_row[IDENTIFIER].replace(" ", "-"),
                "prev_was_yes_or_no": True if answer_index == YES else False
            })
            temp_intent_json = self.intents.intent_json(queue_head, answer_index, input_context, False)
        else:
            temp_intent_json = self.intents.intent_json(queue_head, answer_index, input_context, True)
        self.result_json_data.append(temp_intent_json)
        self.result_yes_or_no.append(True if answer_index == YES else False)


class CreateChatbotFiles:
    data = CSVData()
    create_intents = CreateIntentsData(data.csv_data("./compliance-questions-formatted.csv"))
    create_intents.walk_tree()
    intents_list = create_intents.result_json_data
    yes_or_no_list = create_intents.result_yes_or_no
    target_path = "./target/chatbot"

    def create_intent_files(self):
        usersays = Usersays()

        Path(f"{self.target_path}/intents").mkdir(parents=True, exist_ok=True)
        with open(f"{self.target_path}/intents/Default Fallback Intent.json", "w", encoding="utf-8") as file:
            json.dump(Intents.fallback_intent, file, indent=2)

        for index in range(len(self.intents_list)):
            curr_name = self.intents_list[index]["name"]

            with open(f"{self.target_path}/intents/{curr_name}.json", "w", encoding="utf-8") as file:
                json.dump(self.intents_list[index], file, indent=2)

            with open(f"{self.target_path}/intents/{curr_name}_usersays_en.json", "w", encoding="utf-8") as file:
                if self.yes_or_no_list[index] == True:
                    json.dump(usersays.yes_usersays_data, file, indent=2)
                elif self.yes_or_no_list[index] == False:
                    json.dump(usersays.no_usersays_data, file, indent=2)
                elif self.yes_or_no_list[index] is None:
                    json.dump(usersays.welcome_usersays_data, file, indent=2)
                elif self.yes_or_no_list[index] is not None:
                    raise SystemError("Error in code")

    def create_entity_files(self):
        entities = Entities()
        Path(f"{self.target_path}/entities").mkdir(parents=True, exist_ok=True)
        with open(f"{self.target_path}/entities/confirmation.json", "w", encoding="utf-8") as file:
            json.dump(entities.confirmation_entity, file, indent=2)

        with open(f"{self.target_path}/entities/confirmation_entries_en.json", "w", encoding="utf-8") as file:
            json.dump(entities.confirmation_entries, file, indent=2)

    def create_agent_file(self):
        agent = Agent()
        with open(f"{self.target_path}/agent.json", "w", encoding="utf-8") as file:
            json.dump(agent.agent_data, file, indent=2)

    def create_package_json_file(self):
        package_json = PackageJson
        with open(f"{self.target_path}/package.json", "w", encoding="utf-8") as file:
            json.dump(package_json.package_json_data, file, indent=2)


    def create_zip_file(self):
        # with ZipFile(f"{self.target_path}/chatbot.zip", 'w') as zipObj:
        #     # Iterate over all the files in directory
        #     # zipObj.write(self.target_path)
        #     for folderName, subfolders, filenames in os.walk(self.target_path):
        #         print(folderName)
        #         for filename in filenames:
        #             # create complete filepath of file in directory
        #             filePath = os.path.join(folderName, filename)
        #             # Add file to zip
        #             zipObj.write(filePath)
        shutil.make_archive(f"./target/chatbot", "zip", self.target_path)

    def create_chatbot_files(self):
        self.create_intent_files()
        self.create_entity_files()
        self.create_agent_file()
        self.create_package_json_file()
        self.create_zip_file()



if __name__ == '__main__':
    create_intent_files = CreateChatbotFiles()
    create_intent_files.create_chatbot_files()
