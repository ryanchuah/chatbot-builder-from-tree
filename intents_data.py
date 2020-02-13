from uuid import uuid4

QUESTION = 0
YES = 1
NO = 2
IDENTIFIER = 3

class Intents:


    def __init__(self, csv_data):
        self.csv_data = csv_data
        self.welcome_intent = {
            "id": str(uuid4()),
            "name": "Default Welcome Intent",
            "auto": True,
            "contexts": [],
            "responses": [
                {
                    "resetContexts": False,
                    "affectedContexts": [
                        {
                            "name": "DefaultWelcomeIntent-followup",
                            "parameters": {},
                            "lifespan": 2
                        }
                    ],
                    "parameters": [],
                    "messages": [
                        {
                            "type": 0,
                            "lang": "en",
                            "condition": "",
                            "speech": f"Hi! {self.csv_data[0][QUESTION]}"
                        }
                    ],
                    "defaultResponsePlatforms": {},
                    "speech": []
                }
            ],
            "priority": 500000,
            "webhookUsed": True,
            "webhookForSlotFilling": False,
            "fallbackIntent": False,
            "events": [
                {
                    "name": "WELCOME"
                }
            ],
            "conditionalResponses": [],
            "condition": "",
            "conditionalFollowupEvents": []
        }

    def speech_value(self, queue_head, answer_index, is_terminal):
        curr_row = self.csv_data[queue_head["index"]]
        if is_terminal:
            return f"Your MD belongs to {curr_row[answer_index]}"
        else:
            return self.csv_data[queue_head["index"] + int(curr_row[answer_index])][QUESTION]


    def intent_json(self, queue_head, answer_index, input_context=None, is_terminal=False):
        speech = self.speech_value(queue_head, answer_index, is_terminal)
        curr_row = self.csv_data[queue_head["index"]]

        data = {
            "id": str(uuid4()),
            "name": curr_row[IDENTIFIER].title() + " - " + ("Yes" if answer_index == YES else "No"),
            "auto": True,
            "contexts": [] if input_context is None else [input_context],
            "responses": [{
                "resetContexts": False,
                "affectedContexts": [
                    {
                        "name": curr_row[IDENTIFIER].replace(" ", "-"),
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
                        "speech": speech
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

