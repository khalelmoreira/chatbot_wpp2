from enum import Enum

class ConversationStatus(str, Enum):
    COLLECTING  = "COLLECTING"
    CONFIRMING  = "CONFIRMING"
    QUEUED      = "QUEUED"
    DONE        = "DONE"
    ERROR       = "ERROR"
    CANCELLED   = "CANCELLED"

class NfseStatus(str, Enum):
    QUEUED      = "QUEUED"
    PROCESSING  = "PROCESSING"
    ISSUED      = "ISSUED"
    ERROR       = "ERROR"
    CANCELLED   = "CANCELLED"