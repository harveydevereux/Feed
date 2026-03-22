import yaml
from dataclasses import dataclass, asdict
from pathlib import Path
import datetime

@dataclass(kw_only=True)
class State:
    sent_today: set
    today: str

def load_state(data: Path) -> State:
    path = data / "state.yml"
    if path.exists():
        with open(path, "r", encoding="utf-8") as io:
            state = State(**yaml.safe_load(io))
            if datetime.date.fromisoformat(state.today) == datetime.date.today():
                return State(sent_today=set(url for url in state.sent_today), today=state.today)

    return State(sent_today=set(), today=str(datetime.date.today()))

def save_state(state: State, data: Path):
    path = data / "state.yml"
    with open(path, "w", encoding="utf-8") as io:
        yaml.dump({"today": state.today, "sent_today": list(state.sent_today)}, io)