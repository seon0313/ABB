import json
import dataclasses

def dcToJson(data) -> dict:
    return dataclasses.asdict(data)