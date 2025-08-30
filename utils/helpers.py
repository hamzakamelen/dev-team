MAX_HISTORY_LENGTH = 20

def serialize_history(history: list[dict]) -> str:
    return "\n".join([f"{h['role'].capitalize()}: {h['content']}" for h in history])

def clean_output(text: str) -> str:
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if stripped:
            cleaned.append(stripped)
    return "\n".join(cleaned).strip()
