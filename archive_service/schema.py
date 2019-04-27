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
                        "type" : "string",
                    }
                },
            },
            "required": ["urls"]
        }
        self.schema_strict = {
            "type" : "object",
            "properties" : {
                "urls" : {
                    "type" : "array",
                    "minItems":1,
                    "maxItems":maxItems,
                    "items" : {
                        "type" : "string",
                        "maxLength": 2048
                    }
                },
            },
            "additionalProperties" : False,
            "required": ["urls"]
        }

    def is_valid(self, strict=False):
        if strict:
            validate(instance=self.instance, schema=self.schema_strict)
        else:
            validate(instance=self.instance, schema=self.schema)
