from typer import Option, Typer
from typing import Annotated
from pathlib import Path
from datetime import datetime

from feed.state import load_state, save_state
from feed.weekinwildlife import WeekInWildlife
from feed.photosoftheday import PhotosOfTheDay
from feed.naturenews import NatureNews
from feed.discord import send

app = Typer()

@app.command()
def update(
    data: Annotated[Path, Option(help="The directory for stored data")] = Path.cwd()/"data",
    webhook: Annotated[str | None, Option(help="Discord Webhook for sending messages")] = None):

    if not data.is_dir():
        print(f"Creating new data store at {data}")
        data.mkdir(parents=True)
    else:
        print(f"Using data store at {data}")

    state = load_state(data)

    for source in (WeekInWildlife, PhotosOfTheDay, NatureNews):
        src = source(data)
        src.update()

        if webhook != None and src.id in state.last_update:
            entries = src.entries
            last_update = datetime.fromisoformat(state.last_update[src.id])
            for entry in entries:
                if datetime(entry.year, entry.month, entry.day) > last_update:
                    send(webhook, entries[entry])

        state.last_update[src.id] = str(datetime.now())

    save_state(state, data)