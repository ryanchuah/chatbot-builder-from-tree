import csv
from uuid import uuid4
import json
from collections import deque
import pyperclip


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

    def csv_data(self, path):
        with open(path, 'r') as csv_file:
            data = []
            csv_reader = csv.reader(csv_file, delimiter=',')

            next(csv_reader, None)  # skip header during iteration

            for row in csv_reader:
                row[YES] = self.format_possible_offset(row[YES])
                row[NO] = self.format_possible_offset(row[NO])
                data.append(row)

            return data


class CreateJsonData:
    result_data = []
    count = 0

    def __init__(self, data):
        self.csv_data = data
        self.queue = deque()
        self.queue.append({
            "index": 0,
            "output_context": None
        })

    def handle_yes_no(self, queue_head, answer_index, visited, input_context):

        curr_row = self.csv_data[queue_head["index"]]
        if curr_row[answer_index].isdigit() and queue_head["index"] + int(curr_row[answer_index]) not in visited:
            self.queue.append({
                "index": queue_head["index"] + int(curr_row[answer_index]),
                "output_context": curr_row[IDENTIFIER]
            })
            temp_intent_json = self.intent_json(queue_head, answer_index, input_context, False)
            self.result_data.append(temp_intent_json)
        else:
            temp_intent_json = self.intent_json(queue_head, answer_index, input_context, True)
            self.result_data.append(temp_intent_json)

    def bfs(self):
        while self.queue:
            visited = set()
            queue_head = self.queue.popleft()
            input_context = queue_head["output_context"]
            visited.add(queue_head["index"])

            self.handle_yes_no(queue_head, YES, visited, input_context)
            self.handle_yes_no(queue_head, NO, visited, input_context)

        return self.result_data

    def speech_value(self, queue_head, answer_index, is_terminal):
        curr_row = self.csv_data[queue_head["index"]]
        if is_terminal:
            return f"Your MD belongs to {curr_row[answer_index]}"
        else:
            return self.csv_data[queue_head["index"] + int(curr_row[answer_index])]

    def intent_json(self, queue_head, answer_index, input_context=None, is_terminal=False):
        speech_value = self.speech_value(queue_head, answer_index, is_terminal)
        curr_row = self.csv_data[queue_head["index"]]

        data = {
            "id": str(uuid4()),
            "name": curr_row[IDENTIFIER].title(),
            "auto": True,
            "contexts": input_context,
            "responses": [{
                "resetContexts": False,
                "affectedContexts": [
                    {
                        "name": curr_row[IDENTIFIER].replace(" ", ""),
                        "parameters": {},
                        "lifespan": 1
                    }
                ],
                "parameters": [
                    {
                        "id": str(uuid4()),
                        "required": True,
                        "dataType": "@confirmation",
                        "name": "confirmation",
                        "value": "$confirmation",
                        "promptMessages": [],
                        "noMatchPromptMessages": [],
                        "noInputPromptMessages": [],
                        "outputDialogContexts": [],
                        "isList": False
                    }
                ],
                "messages": [
                    {
                        "type": 0,
                        "lang": "en",
                        "condition": "",
                        "speech": speech_value
                    }
                ],
                "defaultResponsePlatforms": {},
                "speech": []
            }],
            "priority": 500000,
            "webhookUsed": False,
            "webhookForSlotFilling": False,
            "fallbackIntent": False,
            "events": [],
            "conditionalResponses": [],
            "condition": "",
            "conditionalFollowupEvents": []
        }
        
        return data


if __name__ == '__main__':
    data = CSVData()
    create_json_data = CreateJsonData(data.csv_data("./test.csv"))
    json_list = create_json_data.bfs()
    print(len(json_list))
    print(json.dumps(json_list))