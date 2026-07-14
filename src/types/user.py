from enum import StrEnum
from dataclasses import dataclass

class UserStatus(StrEnum):
    COLLECTING  = "COLLECTING"
    ADDRESS     = "ADDRESS"
    CONFIRMING  = "CONFIRMING"
    PROJECT     = "PROJECT"
    CERTIFICATE = "CERTIFICATE"
    ACTIVE      = "ACTIVE"
    ERROR       = "ERROR"
    CANCELLED   = "CANCELLED"

class IntentUserType(StrEnum):
    ONBOARDING  = "ONBOARDING"
    ASK_PRICE   = "ASK_PRICE"
    ASK_WORKING = "ASK_WORKING"
    GENERAL_ASK = "GENERAL_ASK"
    NENHUM      = "NENHUM"

@dataclass
class User:
    id:     int
    phone:  str
    name:   str | None = None
    status: UserStatus | None = None