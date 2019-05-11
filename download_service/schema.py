from jsonschema import validate

# This JSON schema describes POST /download request body of the 
# downloader service

class DownloaderJsonSchema():

    def __init__(self, instance):
        self.instance = instance
        self.schema = {
            "type" : "object",
            "properties" : {
                "resourceURL" : {"type" : "string"},
                "useTor" : {"type":"boolean"}
            },
            "additionalProperties" : False,
            "required": ["resourceURL"]
        }

    def is_valid(self, strict=True):
        validate(instance=self.instance, schema=self.schema)
