from jsonschema import validate
from jsonschema.exceptions import ValidationError

# This JSON schema describes POST /download request body of the 
# downloader service

class DownloadPostSchema():

    def __init__(self, instance):
        self.instance = instance
        self.schema = {
            "type" : "object",
            "properties" : {
                "resourceURL" : {
                    "type" : "string"
                },
                "headers" : {
                    "type" : "object",
                    "properties" : {
                        "User-Agent" : {
                            "type" : "string"
                        },
                        "Accept-Language" : {
                            "type" : "string"
                        }
                    },
                    "additionalProperties" : False
                },
                "useTor" : {
                    "type" : "boolean"
                }
            },
            "additionalProperties" : False,
            "required" : ["resourceURL", "headers", "useTor"]
        }

    def is_valid(self):
        try:
            validate(instance=self.instance, schema=self.schema)
        except ValidationError:
            return False
        else:
            return True
