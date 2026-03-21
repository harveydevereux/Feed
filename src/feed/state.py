import yaml
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass(kw_only=True)
class State:
    last_update: dict

def load_state(data: Path) -> State:
    path = data / "state.yml"
    if path.exists():
        with open(path, "r", encoding="utf-8") as io:
            return State(**yaml.safe_load(io))

    return State(last_update={})

def save_state(state: State, data: Path):
    path = data / "state.yml"
    with open(path, "w", encoding="utf-8") as io:
        yaml.dump(asdict(state), io)