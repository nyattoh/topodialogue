import json
from pathlib import Path
from typing import Iterable
from .models import DialogueTurn

COLLECTION_KEYS = ("messages", "turns", "dialogue", "conversation", "items", "entries", "events", "data")


def _text_of(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(part for item in value if (part := _text_of(item)))
    if not isinstance(value, dict):
        return ""
    for key in ("text", "content", "message", "output", "input"):
        if key in value and (text := _text_of(value[key])):
            return text
    return ""


def _speaker_of(value: dict, fallback: str = "user") -> str:
    raw = str(value.get("speaker", value.get("role", value.get("who", fallback)))).casefold()
    if raw in {"assistant", "ai", "bot", "claude", "chatgpt", "gemini", "grok"}:
        return "assistant"
    if raw in {"system", "developer"}:
        return "system"
    return "user"


def _expand_record(value: object, output: list[dict]) -> None:
    if not isinstance(value, dict):
        return
    event_type = str(value.get("type", "")).casefold()
    if event_type == "turn" or ("input" in value and "output" in value):
        round_number = value.get("round", value.get("turn", len(output) + 1))
        input_text = _text_of(value.get("input"))
        output_text = _text_of(value.get("output"))
        if input_text:
            output.append({"turn": round_number, "speaker": "user", "text": input_text})
        if output_text:
            output.append({"turn": round_number, "speaker": _speaker_of(value, "assistant"), "text": output_text})
        return
    text = _text_of(value)
    if text:
        output.append({**value, "speaker": _speaker_of(value), "text": text})


def load_dialogue(path: str | Path) -> list[DialogueTurn]:
    """Load JSON, JSONL, llm-copy exports, or llm-rally event logs."""
    source_path = Path(path)
    raw_text = source_path.read_text(encoding="utf-8-sig")
    try:
        parsed: object = json.loads(raw_text)
    except json.JSONDecodeError:
        parsed = [json.loads(line) for line in raw_text.splitlines() if line.strip()]

    if isinstance(parsed, dict):
        source: object = next(
            (parsed[key] for key in COLLECTION_KEYS if isinstance(parsed.get(key), list)),
            parsed,
        )
        session_id = str(parsed.get("case_id", parsed.get("session_id", source_path.stem)))
    else:
        source = parsed
        session_id = source_path.stem

    records: list[dict] = []
    if isinstance(source, list):
        for value in source:
            _expand_record(value, records)
    else:
        _expand_record(source, records)

    turns: list[DialogueTurn] = []
    for index, record in enumerate(records, 1):
        excluded = {"case_id", "turn", "speaker", "role", "who", "text", "content", "message", "timestamp", "session_id"}
        metadata = {key: value for key, value in record.items() if key not in excluded}
        turns.append(DialogueTurn(
            turn_id=f"t{index}",
            session_id=str(record.get("case_id", record.get("session_id", session_id))),
            speaker=_speaker_of(record),
            text=str(record["text"]),
            timestamp=record.get("timestamp"),
            metadata=metadata,
        ))
    return turns

def load_jsonl(path: str | Path) -> list[DialogueTurn]:
    """Backward-compatible alias; now accepts every supported dialogue format."""
    return load_dialogue(path)

def normalize_turns(turns: Iterable[DialogueTurn]) -> list[DialogueTurn]:
    return [t.model_copy(update={"text": " ".join(t.text.split())}) for t in turns]
