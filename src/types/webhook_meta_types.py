from typing import TypedDict, Literal

#PAYLOAD RAW

TypeMessage = Literal [
    "text",
    "image",
    "audio",
    "document",
    "video",
    "reaction",
    "button"
]

class TextMessageDict(TypedDict):
    body: str

class MessageDict(TypedDict, total=False):
    id: str
    timestamp: str
    type: TypeMessage
    text: TextMessageDict
    audio_id: str

class ProfileDict(TypedDict):
    name: str

class ContactDict(TypedDict):
    wa_id: str
    profile: ProfileDict

class ValueDict(TypedDict, total=False):
    contacts: list[ContactDict]
    messages: list[MessageDict]

class WebhookPayload(TypedDict):
    entry: list[dict]
