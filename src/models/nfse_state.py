from enum import Enum

class ConversationStatus(str, Enum):
    COLLECTING = "COLLECTING"
    CONFIRMING = "CONFIRMING"
    EMITTING = "EMITTING"
    DONE = "DONE"
    ERROR = "ERROR"
    CANCELLED = "CANCELLED"