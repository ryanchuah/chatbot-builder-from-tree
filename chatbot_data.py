from uuid import uuid4
import os

QUESTION = 0
YES = 1
NO = 2
CLARIFICATION = 3
IDENTIFIER = 4


class Intents:

    def __init__(self, csv_data, webhook_used):
        self.csv_data = csv_data
        self.webhook_used = webhook_used
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
                            "lifespan": 3
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
            "webhookUsed": webhook_used,
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

        self.fallback_intent = {
            "id": "9332f025-2acd-4b98-9fd9-1c0a823a158a",
            "name": "Default Fallback Intent",
            "auto": True,
            "contexts": [],
            "responses": [
                {
                    "resetContexts": False,
                    "action": "input.unknown",
                    "affectedContexts": [],
                    "parameters": [],
                    "messages": [
                        {
                            "type": 0,
                            "lang": "en",
                            "condition": "",
                            "speech": [
                                "I didn\u0027t get that. Can you say it again?",
                                "I missed what you said. What was that?",
                                "Sorry, could you say that again?",
                                "Sorry, can you say that again?",
                                "Can you say that again?",
                                "Sorry, I didn\u0027t get that. Can you rephrase?",
                                "Sorry, what was that?",
                                "One more time?",
                                "What was that?",
                                "Say that one more time?",
                                "I didn\u0027t get that. Can you repeat?",
                                "I missed that, say that again?"
                            ]
                        }
                    ],
                    "defaultResponsePlatforms": {},
                    "speech": []
                }
            ],
            "priority": 500000,
            "webhookUsed": False,
            "webhookForSlotFilling": False,
            "fallbackIntent": True,
            "events": [],
            "conditionalResponses": [],
            "condition": "",
            "conditionalFollowupEvents": []
        }

        self.clarification_intent = {
            "id": "dc47ad0a-4596-4982-bf99-0a3503e24d5b",
            "name": "Clarification Intent",
            "auto": True,
            "contexts": [],
            "responses": [
                {
                    "resetContexts": False,
                    "affectedContexts": [],
                    "parameters": [],
                    "messages": [
                        {
                            "type": 0,
                            "lang": "en",
                            "condition": "",
                            "speech": []
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
            "events": [],
            "conditionalResponses": [],
            "condition": "",
            "conditionalFollowupEvents": []
        }

    def speech_value(self, queue_head):
        curr_row = self.csv_data[queue_head["index"]]

        if queue_head["curr_yes_or_no"] is None:
            return curr_row[QUESTION]
        answer = curr_row[queue_head["curr_yes_or_no"]]
        if answer.isdigit():
            return self.csv_data[queue_head["index"] + int(answer)][QUESTION]
        else:
            return answer

    def intent_json(self, queue_head, is_welcome_intent):

        curr_row = self.csv_data[queue_head["index"]]
        events = [{"name": "WELCOME"}] if is_welcome_intent else []
        output_context = []
        for context in queue_head["output_context"]:
            output_context.append({
                "name": context,
                "parameters": {},
                "lifespan": 3
            })
        if queue_head["prev_yes_or_no"] is None and queue_head["curr_yes_or_no"] is None:
            name = f"{curr_row[IDENTIFIER].replace('-', ' ').title()} - Initial"
            parameters = []
            speech = curr_row[QUESTION]
        elif queue_head["curr_yes_or_no"] is not None:
            name = curr_row[IDENTIFIER].replace('-', ' ').title() + " - " + (
                "Yes" if queue_head["curr_yes_or_no"] == YES else "No")
            parameters = [
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
            ]
            answer = curr_row[queue_head["curr_yes_or_no"]]
            if answer.isdigit():
                speech = self.csv_data[queue_head["index"] + int(answer)][QUESTION]
            else:
                speech = answer

        elif queue_head["prev_yes_or_no"] is not None:
            prev_yes_or_no = queue_head["prev_yes_or_no"]
            prev_row = queue_head["prev_row"]

            name = prev_row[IDENTIFIER].title() + " - " + ("Yes" if prev_yes_or_no == YES else "No")
            parameters = [
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
            ]
            speech = curr_row[QUESTION]

        data = {
            "id": str(uuid4()),
            "name": name,
            "auto": True,
            "contexts": [] if queue_head["input_context"] is None else [queue_head["input_context"]],
            "responses": [{
                "resetContexts": False,
                "affectedContexts": output_context,
                "parameters": parameters,
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
            "webhookUsed": self.webhook_used,
            "webhookForSlotFilling": False,
            "fallbackIntent": False,
            "events": events,
            "conditionalResponses": [],
            "condition": "",
            "conditionalFollowupEvents": []
        }

        return data


class Entities:
    confirmation_entity = {
        "id": "c2916dea-dec1-4a65-9163-96017d0dc31b",
        "name": "confirmation",
        "isOverridable": True,
        "isEnum": False,
        "isRegexp": False,
        "automatedExpansion": False,
        "allowFuzzyExtraction": False
    }

    confirmation_entries = [
        {
            "value": "yes",
            "synonyms": [
                "yes",
                "yeah",
                "that is correct",
                "correct",
                "yup"
            ]
        },
        {
            "value": "no",
            "synonyms": [
                "no",
                "nope",
                "incorrect",
                "that\u0027s not correct",
                "that\u0027s not right",
                "thats not right"
            ]
        }
    ]


class Usersays:
    yes_usersays_data = [
        {
            "id": str(uuid4()),
            "data": [
                {
                    "text": "yes that is correct",
                    "alias": "confirmation",
                    "meta": "@confirmation",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": str(uuid4()),
            "data": [
                {
                    "text": "that is correct",
                    "alias": "confirmation",
                    "meta": "@confirmation",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": str(uuid4()),
            "data": [
                {
                    "text": "they do",
                    "alias": "confirmation",
                    "meta": "@confirmation",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": str(uuid4()),
            "data": [
                {
                    "text": "does",
                    "alias": "confirmation",
                    "meta": "@confirmation",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": str(uuid4()),
            "data": [
                {
                    "text": "it does",
                    "alias": "confirmation",
                    "meta": "@confirmation",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": str(uuid4()),
            "data": [
                {
                    "text": "yup",
                    "alias": "confirmation",
                    "meta": "@confirmation",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": str(uuid4()),
            "data": [
                {
                    "text": "y",
                    "alias": "confirmation",
                    "meta": "@confirmation",
                    "userDefined": True
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": str(uuid4()),
            "data": [
                {
                    "text": "right",
                    "alias": "confirmation",
                    "meta": "@confirmation",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": str(uuid4()),
            "data": [
                {
                    "text": "yes it does",
                    "alias": "confirmation",
                    "meta": "@confirmation",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": str(uuid4()),
            "data": [
                {
                    "text": "yes",
                    "alias": "confirmation",
                    "meta": "@confirmation",
                    "userDefined": True
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        }
    ]

    no_usersays_data = [
        {
            "id": str(uuid4()),
            "data": [
                {
                    "text": "it does not",
                    "alias": "confirmation",
                    "meta": "@confirmation",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": str(uuid4()),
            "data": [
                {
                    "text": "nop",
                    "alias": "confirmation",
                    "meta": "@confirmation",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": str(uuid4()),
            "data": [
                {
                    "text": "not right",
                    "alias": "confirmation",
                    "meta": "@confirmation",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": str(uuid4()),
            "data": [
                {
                    "text": "not",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": str(uuid4()),
            "data": [
                {
                    "text": "no",
                    "alias": "confirmation",
                    "meta": "@confirmation",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        }
    ]

    welcome_usersays_data = [
        {
            "id": "469d1ade-b56c-42ab-b579-5eef4d6cb585",
            "data": [
                {
                    "text": "just going to say hi",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "03dd9704-fccd-47de-9584-bad1510d4dc1",
            "data": [
                {
                    "text": "heya",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "f13b2ca4-0b43-4694-8cde-6afe62a2dc31",
            "data": [
                {
                    "text": "hello hi",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "9c764687-e0bf-428b-96ca-7e2c82cb6035",
            "data": [
                {
                    "text": "howdy",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "d747716d-8a4b-4399-baf8-855fae4b72ff",
            "data": [
                {
                    "text": "hey there",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "e821b357-ab17-4b99-9bd8-12c03df2b6f9",
            "data": [
                {
                    "text": "hi there",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "28cebcf7-01a3-435d-9f70-1cd9f5c2a412",
            "data": [
                {
                    "text": "greetings",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "709ad98c-13ce-46f6-a3f5-56ec17666582",
            "data": [
                {
                    "text": "hey",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "c18959c2-8a84-4342-b3bc-72d41cc27237",
            "data": [
                {
                    "text": "long time no see",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "1404f78e-ecd0-486e-b436-2265b903a2be",
            "data": [
                {
                    "text": "hello",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "43ae41f3-e9e0-4876-87ed-8577e1d3d86c",
            "data": [
                {
                    "text": "lovely day isn\u0027t it",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "bc62063b-ee8f-4963-8dd0-49ecc83e3423",
            "data": [
                {
                    "text": "I greet you",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "d5fa15e8-76dd-4d56-bb39-76848229282e",
            "data": [
                {
                    "text": "hello again",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "23906f4f-fc68-4412-bccf-064162b47e11",
            "data": [
                {
                    "text": "hi",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "a902bbd4-c28b-475c-8304-ef4cb7e78a8e",
            "data": [
                {
                    "text": "hello there",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "4850b36e-f21e-4442-9630-f91a9950e84f",
            "data": [
                {
                    "text": "hi there",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "a5a9f58d-ef41-4bda-a26d-f581495a18d6",
            "data": [
                {
                    "text": "a good day",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        }
    ]

    clarification_usersays_data = [
        {
            "id": "7ae1603c-06c9-45b5-b5d4-0e690acee021",
            "data": [
                {
                    "text": "what is that?",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "6b51fd54-8ed2-48eb-a5bf-b8c18356d98d",
            "data": [
                {
                    "text": "elaborate please",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "950bfd6c-028a-4fb2-b511-3d5087f390d8",
            "data": [
                {
                    "text": "i\u0027m confused",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "b6ef812f-88e9-407b-9fd1-f88025424b47",
            "data": [
                {
                    "text": "huh?",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "11b7b74b-7af9-4d2e-8b88-a50b76680a7b",
            "data": [
                {
                    "text": "what do you mean?",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "7a61a660-1bd5-4c3b-9a58-1cebe0bbe198",
            "data": [
                {
                    "text": "can you clarify what you mean?",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "eb42e1e0-a4b2-428d-8765-a8c9a4705481",
            "data": [
                {
                    "text": "clarify please",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "e0767773-3d97-4f87-b86e-7714221f6886",
            "data": [
                {
                    "text": "please clarify",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "40bae683-153b-48ed-a811-41eea93f304d",
            "data": [
                {
                    "text": "please elaborate",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "2ae64f8b-985b-4b09-ae62-1616873f3909",
            "data": [
                {
                    "text": "can you elaborate?",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "a42371eb-5984-4450-8ea4-34a315280ac7",
            "data": [
                {
                    "text": "i don\u0027t understand?",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "924ddedc-6c50-4131-a825-25a69e5c546c",
            "data": [
                {
                    "text": "i don\u0027t understand",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "28aa965a-6d31-4314-8353-fe0532feabb0",
            "data": [
                {
                    "text": "what",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 0,
            "updated": 0
        },
        {
            "id": "95970d8d-5142-4d32-8cfa-126cf51fee5e",
            "data": [
                {
                    "text": "what?",
                    "userDefined": False
                }
            ],
            "isTemplate": False,
            "count": 1,
            "updated": 0
        }
    ]


class Agent:
    def __init__(self, webhook_used):
        self.webhook_used = webhook_used

        if self.webhook_used:
            self.webhook_data = {
                "url": "https://your-webhook-api.com",
                "username": "",
                "headers": {
                    "": ""
                },
                "available": True,
                "useForDomains": False,
                "cloudFunctionsEnabled": False,
                "cloudFunctionsInitialized": False
            }
        else:
            self.webhook_data = {
                "url": "",
                "username": "",
                "headers": {},
                "available": False,
                "useForDomains": False,
                "cloudFunctionsEnabled": False,
                "cloudFunctionsInitialized": False
            }

        self.agent_data = {
            "description": "Automatically Generated Agent",
            "language": "en",
            "shortDescription": "Automatically Generated Agent",
            "examples": "",
            "linkToDocs": "",
            "disableInteractionLogs": False,
            "disableStackdriverLogs": True,
            "googleAssistant": {
                "googleAssistantCompatible": False,
                "project": "testing-auto-create-neojhe",
                "welcomeIntentSignInRequired": False,
                "startIntents": [],
                "systemIntents": [],
                "endIntentIds": [],
                "oAuthLinking": {
                    "required": False,
                    "providerId": "",
                    "authorizationUrl": "",
                    "tokenUrl": "",
                    "scopes": "",
                    "privacyPolicyUrl": "",
                    "grantType": "AUTH_CODE_GRANT"
                },
                "voiceType": "MALE_1",
                "capabilities": [],
                "env": "",
                "protocolVersion": "V2",
                "autoPreviewEnabled": False,
                "isDeviceAgent": False
            },
            "defaultTimezone": "Africa/Casablanca",
            "webhook": self.webhook_data,
            "isPrivate": True,
            "customClassifierMode": "use.after",
            "mlMinConfidence": 0.3,
            "supportedLanguages": [],
            "onePlatformApiVersion": "v2",
            "analyzeQueryTextSentiment": False,
            "enabledKnowledgeBaseNames": [],
            "knowledgeServiceConfidenceAdjustment": -0.4,
            "dialogBuilderMode": False,
            "baseActionPackagesUrl": ""
        }


class PackageJson:
    package_json_data = {"version": "1.0.0"}


class AgentAPI:
    def __init__(self, clarification_list):
        self.clarification_list = clarification_list

    # agent.js code
    code = \
        """
        "use strict";
        const express = require("express");
        const router = express.Router();

        var mongoUtil = require("../mongoUtil");
        var db = mongoUtil.getDbData();
        const { WebhookClient } = require("dialogflow-fulfillment");
        const info = {};
        var currentUsername;
        process.env.DEBUG = "dialogflow:debug"; // enables lib debugging statements
        """

    def handler_function(self, curr_intent):
        agent_add_definition = ""
        speech = curr_intent['responses'][0]['messages'][0]['speech']
        if isinstance(speech, list):
            for s in speech:
                agent_add_definition += f'\tagent.add("{s}"){os.linesep}'
        else:
            agent_add_definition = f'\tagent.add("{speech}"){os.linesep}'
        return (
            f"function handle{curr_intent['name'].replace(' ', '').replace('-', '')}(agent) {{{os.linesep}"
            f"{agent_add_definition}"
            f"}}{os.linesep}"
        )

    def intent_map(self, intent):
        return f'intentMap.set("{intent["name"]}", handle{intent["name"].replace(" ", "").replace("-", "")});{os.linesep}'

    def clarification_map(self, output_context, clarification_text):
        return f'clarificationMap.set("{output_context["name"]}", "{clarification_text}");{os.linesep}'

    def agent_code(self, intents_list):

        code = \
            """
                "use strict";
                const express = require("express");
                const router = express.Router();
                
                var mongoUtil = require("../mongoUtil");
                var db = mongoUtil.getDbData();
                const { WebhookClient } = require("dialogflow-fulfillment");
                const info = {};
                var currentUsername;
                process.env.DEBUG = "dialogflow:debug"; // enables lib debugging statements
                router.post("/", async (request, response) => {
                  const agent = new WebhookClient({ request, response });
                  console.log("Dialogflow Request headers: " + JSON.stringify(request.headers));
                  console.log("Dialogflow Request body: " + JSON.stringify(request.body));
            """
        for i in range(len(intents_list) - 1):  # -1 to exclude Default Fallback Intent from agent code
            code += self.handler_function(intents_list[i])

        code += \
            """
                function handleClarification(agent){
                var clarificationMap = new Map()
            """
        visited_context = set()
        for i in range(len(self.clarification_list)):
            curr_intent = intents_list[i]
            output_contexts = curr_intent["responses"][0]["affectedContexts"]
            longest_context = max(output_contexts, key=lambda x: len(x['name']))

            code += self.clarification_map(longest_context, self.clarification_list[i])

        code += \
            """
                    const requestContexts = request.body.queryResult.outputContexts;
                    const mostRecentContext = requestContexts.reduce((max, ctx) => {
                    if (!("lifespanCount" in max)) return ctx;
        
                    if ("lifespanCount" in ctx) {
                        if (max.lifespanCount > ctx.lifespanCount) {
                            return max;
                        } else if (max.lifespanCount === ctx.lifespanCount) {
                            if (max.name.length > ctx.name.length) {
                                return max;
                            } else {
                                return ctx;
                            }
                        }
                    } else {
                        return max;
                    }
                });
        
                const words = mostRecentContext.name.split("/");
            
                    const context = words[words.length - 1];
            
                    if (clarificationMap.has(context)) {
                        var responseText = clarificationMap.get(context);
                    } else {
                        var responseText = "No clarification is available";
                    }
                    agent.add(responseText);
                }
            """

        code += \
            """
              // Run the proper function handler based on the matched Dialogflow intent name
              let intentMap = new Map();
            """

        for i in range(len(intents_list) - 1):  # -1 to exclude Default Fallback Intent from agent code
            code += self.intent_map(intents_list[i])

        code += 'intentMap.set("Clarification Intent", handleClarification);'
        code += \
            """
              agent.handleRequest(intentMap);
            });
            
            module.exports = router;
            """
        return code
