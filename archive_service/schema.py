from jsonschema import validate

class ArchiveJsonSchema():

    def __init__(self, instance, maxItems=256):
        self.instance = instance
        self.schema = {
            "type" : "object",
            "properties" : {
                "urls" : {
                    "type" : "array",
                    "minItems":1,
                    "maxItems":maxItems,
                    "items" : {
                        "type" : "string"
                    }

                }
            }
        }

    def is_valid(self, strict=True):
        validate(instance=self.instance, schema=self.schema)
