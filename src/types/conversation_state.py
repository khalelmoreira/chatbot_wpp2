from enum import Enum

class ConversationStatus(str, Enum):
    COLLECTING  = "COLLECTING"
    CONFIRMING  = "CONFIRMING"
    QUEUED      = "QUEUED"
    DONE        = "DONE"
    ERROR       = "ERROR"
    CANCELLED   = "CANCELLED"