import uuid
import time

def generate_message_id() -> str:
    return f"wamid.{uuid.uuid4().hex}"

def generate_timestamp() -> str:
    return str(int(time.time()))