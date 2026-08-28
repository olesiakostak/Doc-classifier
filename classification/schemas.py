DOC_TYPES = ["Invoice", "BOL", "POD", "Rate Confirmation", "Packing List", "Other"]

INVOICE_FIELDS = ["invoice_number", "invoice_date", "total_amount", "vendor_name"]
BOL_FIELDS = ["bol_number", "shipper", "consignee", "carrier", "pickup_date"]
POD_FIELDS = ["delivery_date", "receiver_signature_present", "delivery_address"]


document_classification_schema = {
    "type": "json_schema",
    "json_schema": {
        "name": "document_classification",
        "schema": {
            "type": "object",
            "properties": {
                "doc_type": {
                    "type": "string",
                    "enum": DOC_TYPES,
                },
                "confidence": {
                    "type": "number",
                },
            },
            "required": ["doc_type", "confidence"],
            "additionalProperties": False,
        },
    },
}

def field_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "value": {"type": ["string", "null"]},
            "confidence": {"type": "number"},
        },
        "required": ["value", "confidence"],
        "additionalProperties": False,
    }


def build_field_extraction_schema(name: str, field_names: list[str]) -> dict:
    properties = {field_name: field_schema() for field_name in field_names}

    return {
        "type": "json_schema",
        "json_schema": {
            "name": name,
            "schema": {
                "type": "object",
                "properties": properties,
                "required": field_names,
                "additionalProperties": False,
            },
        },
    }


FIELD_SCHEMAS = {
    "Invoice": build_field_extraction_schema("invoice_field_extraction", INVOICE_FIELDS),
    "BOL": build_field_extraction_schema("bol_field_extraction", BOL_FIELDS),
    "POD": build_field_extraction_schema("pod_field_extraction", POD_FIELDS),
}