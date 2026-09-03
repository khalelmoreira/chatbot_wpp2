import unicodedata


def normalize_word(texto: str) -> str:
    """Lowercase, drop accents, and strip surrounding whitespace / light punctuation.

    Shared by the deterministic reserved-word matchers (exit word, help word) so
    that "Ajuda!", " ajuda " and "ajuda" all compare equal.
    """
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sem_acento.casefold().strip(" \t\n.!?")
