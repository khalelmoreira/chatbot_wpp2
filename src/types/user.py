from enum import StrEnum
from dataclasses import dataclass

class UserStatus(StrEnum):
    NEW         = "NEW"
    COLLECTING  = "COLLECTING"
    ADDRESS     = "ADDRESS"
    CONFIRMING  = "CONFIRMING"
    PROJECT     = "PROJECT"
    CERTIFICATE = "CERTIFICATE"
    ACTIVE      = "ACTIVE"
    ERROR       = "ERROR"
    CANCELLED   = "CANCELLED"

@dataclass
class User:
    id:     int
    phone:  str
    name:   str
    estado: UserStatus