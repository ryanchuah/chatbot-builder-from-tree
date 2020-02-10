# This script parses a CSV file containing questions followed by follow up questions
# This script then outputs the relevant JSON files that can then be imported into DialogFlow to allow the agent to prompt users with the questions
from collections import defaultdict
import sys
import json
import uuid


# stores each line of the csv file in an array element
def data_arr(file_path):
    temp_arr = []
    arr = []
    trimmed_arr = []
    try:
        with open(file_path, "r") as f:
            for line in f:
                if line.strip() != "":
                    # if line is not empty
                    temp_arr.append(line.strip())

        if not temp_arr:
            raise ValueError("The CSV file inputted is empty")

        for line in temp_arr:
            arr.append(line.split(","))

        return arr

    except IOError:
        print(f"ERROR: Could not read file in file path {file_path}")
        sys.exit(1)


if __name__ == '__main__':
    intent_json = '{'
    data = data_arr("./intents.csv")
    for i in range(2, len(data)):


        intent_json = '{'

        ID = 0
        NAME = 1
        DATA_TYPE = 2
        DATA_NAME = 3
        action_name = data[1][NAME]

        for j in range(1, i):
            action_name += "." + data[j][NAME] + "-custom"

        action_name = action_name.replace(" ","")

        if len(data[i][NAME]) > 25:
            data[i][NAME] = data[i][NAME][-25:]

            print(data[i][NAME])

        intent_json += f'"id": "{data[i][ID]}", "parentId": "{data[i - 1][ID]}", "rootParentId": "{data[1][ID]}"' \
                       f',"name": "{data[i][NAME]}","auto": true,"contexts": ["{data[i - 1][NAME].replace(" ","") + "-followup"}"],\
  "responses": [{{"resetContexts": false,"action": "{action_name}",' \
                       f'"affectedContexts": [\
        {{\
          "name": "{data[i][NAME].replace(" ", "")}-followup","parameters": {{}},\
          "lifespan": 2\
        }}\
      ],\
      "parameters": [\
        {{"id": "0{uuid.uuid4()}", "required": false,\
          "dataType": "{data[i][DATA_TYPE]}",\
          "name": "{data[i][DATA_NAME]}",\
          "value": "${data[i][DATA_NAME]}",\
          "promptMessages": [],\
          "noMatchPromptMessages": [],\
          "noInputPromptMessages": [],\
          "outputDialogContexts": [],\
          "isList": false}}\
      ],\
      "messages": [\
        {{\
          "type": 0,\
          "lang": "en",\
          "condition": "",\
          "speech": "Default"\
        }}\
      ],\
      "defaultResponsePlatforms": {{}},\
      "speech": []\
    }}\
  ],\
  "priority": 500000,\
  "webhookUsed": true,\
  "webhookForSlotFilling": false,\
  "fallbackIntent": false,\
  "events": [],\
  "conditionalResponses": [],\
  "condition": "",\
  "conditionalFollowupEvents": []\
}}'

        with open(f"./{data[i][NAME]}.json", "w") as outfile:
            outfile.write(intent_json)

        with open(f"./{data[i][NAME]}_usersays_en.json", "w") as outfile:
            outfile.write(f'[\
  {{\
    "id": "{uuid.uuid4()}",\
    "data": [\
      {{\
        "text": "i am ",\
        "userDefined": false\
      }},\
      {{\
        "text": "mulley",\
        "alias": "person",\
        "meta": "@sys.person",\
        "userDefined": true\
                }}\
    ],\
    "isTemplate": false,\
    "count": 0,\
    "updated": 0\
  }}]')
