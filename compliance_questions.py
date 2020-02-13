import csv
import re
import json
from collections import deque
from usersays_data import welcome_usersays_data, yes_usersays_data, no_usersays_data
from intents_data import Intents

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
        result = string.replace(",", " ").replace("  ", " ").lower()
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


class CreateJsonData:

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


class CreateJsonFiles:
    data = CSVData()
    create_json_data = CreateJsonData(data.csv_data("./compliance-questions-formatted.csv"))
    # create_json_data = CreateJsonData(data.csv_data("./test.csv"))
    create_json_data.walk_tree()
    json_list = create_json_data.result_json_data
    yes_or_no_list = create_json_data.result_yes_or_no

    def __init__(self):
        print(self.yes_or_no_list)
        print(len(self.yes_or_no_list))

        print(self.json_list)
        print(len(self.json_list))
        with open("./target/_.json", "w") as file:
            json.dump(self.json_list, file, indent=2)

    def create_intent_files(self):
        for index in range(len(self.json_list)):
            curr_name = self.json_list[index]["name"]

            with open(f"./target/{curr_name}.json", "w", encoding="utf-8") as file:
                json.dump(self.json_list[index], file, indent=2)

            with open(f"./target/{curr_name}_usersays_en.json", "w", encoding="utf-8") as file:
                if self.yes_or_no_list[index] == True:
                    json.dump(yes_usersays_data, file, indent=2)
                elif self.yes_or_no_list[index] == False:
                    json.dump(no_usersays_data, file, indent=2)
                elif self.yes_or_no_list[index] is None:
                    json.dump(welcome_usersays_data, file, indent=2)
                elif self.yes_or_no_list[index] is not None:
                    raise SystemError("Error in code")


if __name__ == '__main__':
    # data = CSVData()
    # create_json_data = CreateJsonData(data.csv_data("./test.csv"))
    # json_list = create_json_data.walk_tree()
    # print(len(json_list))
    # print(json.dumps(json_list))
    create_json_files = CreateJsonFiles()
    create_json_files.create_intent_files()
