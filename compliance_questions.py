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
    def bfs(self, data, start=0):
        queue = deque()
        queue.append({
            "index": start,
            "output_context": None
        })

        while queue:
            visited = set()
            queue_head = queue.popleft()
            curr_index = queue_head["index"]
            print(curr_index)
            curr_row = data[curr_index]
            input_context = queue_head["output_context"]
            visited.add(curr_index)

            if curr_row[YES].isdigit() and curr_index+int(curr_row[YES]) not in visited:
                queue.append({
                    "index": curr_index + int(curr_row[YES]),
                    "output_context": curr_row[IDENTIFIER]
                })
            else:
                self.result_data.append(self.intent_json(curr_row, YES, input_context))

            if curr_row[NO].isdigit() and curr_index+int(curr_row[NO]) not in visited:
                queue.append({
                    "index": curr_index + int(curr_row[NO]),
                    "output_context": curr_row[IDENTIFIER]
                })
            else:
                self.result_data.append(self.intent_json(curr_row, NO, input_context))
        return self.result_data


    def intent_json(self, row, answer_index, input_context=None):
        data = {
            "id": str(uuid4()),
            "name": row[IDENTIFIER].title(),
            "auto": True,
            "contexts": input_context,
            "responses": [{
                "resetContexts": False,
                "affectedContexts": [
                    {
                        "name": row[IDENTIFIER].replace(" ", ""),
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
                        "speech": f"Your MD belongs to {row[answer_index]}"
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
    create_json_data = CreateJsonData()
    json_list = create_json_data.bfs(data.csv_data("./test.csv"))
    print(len(json_list))
    print(json.dumps(json_list))