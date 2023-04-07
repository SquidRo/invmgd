#
# util_schema.py
#
# json schema to validate json data for rest APIs
#

JSON_SCHEMA_FEED = {
    "type": "object",
    "properties": {
        "data" : {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "item": {
                        "type": "string"
                    },
                    "emp_id": {
                        "type": "string"
                    },
                    "count": {
                        "type": "integer",
                        "minimum": 0
                    },
                    "stack_id": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 30
                    }
                },
                "required": [
                    "item",
                    "count",
                    "emp_id",
                    "stack_id"
                ]
            }
        }
    },
    "required" : [
        "data"
    ]
}


JSON_SCHEMA_PICK = {
    "type": "object",
    "properties": {
        "data" : {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "item": {
                        "type": "string"
                    },
                    "reason": {
                        "type": "string"
                    }
                },
                "required": [
                    "item",
                    "reason"
                ]
            }
        }
    },
    "required" : [
        "data"
    ]
}


JSON_SCHEMA_UPD_PICK_REQ = {
    "type": "object",
    "properties" : {
        "data": {
            "type": "object",
            "properties": {
                "pkreq_id": {
                     "type": "integer"
                },
                "conv_id": {
                    "type": "integer"
                }
            },
            "required": [
                "pkreq_id",
                "conv_id"
            ]
        }
    },
    "required": [
        "data"
    ]
}


