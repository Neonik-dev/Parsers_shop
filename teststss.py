event = {
  "meta": {
    "locale": "ru-RU",
    "timezone": "UTC",
    "client_id": "ru.yandex.searchplugin/7.16 (none none; android 4.4.2)",
    "interfaces": {
      "screen": {},
      "payments": {},
      "account_linking": {}
    }
  },
  "session": {
    "message_id": 1,
    "session_id": "591886b1-078e-4b86-93a1-a8da7d2ac3c0",
    "skill_id": "b319f818-0fdf-4a3e-88f7-369702bdb3cb",
    "user": {
      "user_id": "784654FB088186BB809FF54A16139806CA5039CDFE38F58B99FC501E38681B77"
    },
    "application": {
      "application_id": "7D572EAEEEC506D214F6BB49D071CD230FB41D1E8125FB95BDAFD07E91BCBB38"
    },
    "new": False,
    "user_id": "7D572EAEEEC506D214F6BB49D071CD230FB41D1E8125FB95BDAFD07E91BCBB38"
  },
  "request": {
    "command": "го факт",
    "original_utterance": "го факт",
    "nlu": {
      "tokens": [
        "го",
        "факт"
      ],
      "entities": [],
      "intents": {
        "talking": {
          "slots": {
            "what": {
              "type": "What",
              "tokens": {
                "start": 1,
                "end": 2
              },
              "value": "facts"
            }
          }
        }
      }
    },
    "markup": {
      "dangerous_context": False
    },
    "type": "SimpleUtterance"
  },
  "state": {
    "session": {},
    "user": {},
    "application": {}
  },
  "version": "1.0"
}

intent = event["request"]["nlu"]["intents"]["talking"]
print(type(intent))
print(intent["slots"]["what"]["value"])
