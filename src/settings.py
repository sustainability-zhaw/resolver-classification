import json
import os


class Settings(dict):
    def __init__(self, value: dict):
        self.update({ 
            key.upper(): Settings(value) if isinstance(value, dict) else value 
            for key, value in value.items() 
        })

    def __getattr__(self, name):
        return self[name.upper()]

    def __setattr__(self, name, value):
        self[name.upper()] = Settings(value) if isinstance(value, dict) else value 


settings = Settings({
    "DB_HOST": os.getenv("DB_HOST", "localhost:8080"),
    "LOG_LEVEL": os.getenv("LOG_LEVEL", "ERROR"),
    "MQ_HOST": os.getenv("MQ_HOST", "mq"),
    "MQ_EXCHANGE": os.getenv("MQ_EXCHANGE", "zhaw-km"),
    "MQ_QUEUE": os.getenv("MQ_QUEUE", "classificationqueue"),
    "MQ_BINDKEYS": list([routing_key.strip() for routing_key in os.getenv("MQ_BINDKEYS", "importer.object").split(",")]),
    "MQ_HEARTBEAT": int(os.getenv("MQ_HEARTBEAT", 6000)),
    "MQ_TIMEOUT": int(os.getenv("MQ_TIMEOUT", 3600)),
    "MQ_USER": os.getenv("MQ_USER", "resolver-classification"),
    "MQ_PASS": os.getenv("MQ_PASS", "guest")
})

for path in ["/etc/app/config.json", "/etc/app/secrets.json"]:
    if os.path.exists(path):
        with open(path) as file:
            values = json.load(file)
            settings.update(values)
