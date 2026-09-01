"""Recent conversation turns, shaped for the AI layer.

`classify` and `respond` calls need to see what was said just before the current
message — a bare "sim" only means "start the cadastro" in light of the bot's
previous question. Extraction does NOT use this: it may only see what the user
actually sent in this message (cross-message data flows through `MergeableMixin`).

Roles here use the domain's own vocabulary (`user` / `ai`, from `Role`); the
provider SDK name (`assistant`) is applied only inside `ai_client.py`.
"""

from src.types import Role

AIMessage = dict[str, str]

_ROLE_MAP = {
    Role.USER: "user",
    Role.AI: "ai",
}

def to_ai_history(rows: list[dict[str, str]]) -> list[AIMessage]:
    """Map stored `messages` rows (role/content) to the history wire shape.

    Drops empty-content rows and any leading `ai` turns — the provider SDKs
    require the first turn to be `user`.
    """
    mapped: list[AIMessage] = []
    for row in rows:
        content = (row.get("content") or "").strip()
        if not content:
            continue
        role = _ROLE_MAP.get(Role(row["role"]))
        if role is None:
            continue
        mapped.append({"role": role, "content": content})

    while mapped and mapped[0]["role"] == "ai":
        mapped.pop(0)

    return mapped
