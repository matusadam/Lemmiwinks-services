from jsonschema import validate
from jsonschema.exceptions import ValidationError

class Schema():
    """Base class for JSON schema validation

    JSON schema is used to validate JSON data in API body requests.
    """

    def __init__(self, instance):
        self.instance = instance
        self.schema = {}

    def is_valid(self):
        try:
            validate(instance=self.instance, schema=self.schema)
        except ValidationError:
            return False
        else:
            return True

class ArchiveDetailSchema(Schema):

    def __init__(self, instance):
        super().__init__(instance)
        self.schema = {
            "type" : "object",
            "properties" : {
                "file" : {
                    "type" : "string"
                },
                "name" : {
                    "type" : "string"
                },
                "id" : {
                    "type" : "string"
                },
                "ctime" : {
                    "type" : "integer"
                },
                "size" : {
                    "type" : "integer"
                },
                "href_download" : {
                    "type" : "string"
                },
                "href_detail" : {
                    "type" : "string"
                },
            },
            "required": ["file", "name", "id", "ctime", "size", "href_download", "href_detail"]
        }

class ArchivePostSchema(Schema):

    def __init__(self, instance):
        super().__init__(instance)
        self.schema = {
            "type" : "object",
            "properties" : {
                "urls" : {
                    "type" : "array",
                    "items" : {
                        "type" : "string",
                    }
                },
                "name" : {
                    "type" : "string"
                },
                "forceTor" : {
                    "type" : "boolean"
                },
                "headers" : {
                    "type" : "object",
                    "properties" : {
                        "User-Agent" : {
                            "type" : "string",
                        },
                        "Accept-Language" : {
                            "type" : "string",
                        }
                    }
                },
            },
            "required": ["urls", "name", "forceTor"]
        }

class ArchiveCreatedSchema(Schema):

    def __init__(self, instance):
        super().__init__(instance)
        self.schema = {
            "type" : "object",
            "properties" : {
                "message" : {
                    "type" : "string"
                },
                "status" : {
                    "type" : "integer"
                },
                "href" : {
                    "type" : "string"
                },
            },
            "required": ["message", "status", "href"]
        }