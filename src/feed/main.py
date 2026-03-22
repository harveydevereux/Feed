from typer import Option, Typer
from typing import Annotated
from pathlib import Path
import datetime

from feed.state import load_state, save_state
from feed.weekinwildlife import WeekInWildlife
from feed.photosoftheday import PhotosOfTheDay
from feed.naturenews import NatureNews
from feed.bbcinpcitures import BBCInPictures
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

    for source in (WeekInWildlife, PhotosOfTheDay, NatureNews, BBCInPictures):
        src = source(data)
        src.update()

        if webhook != None:
            entries = src.entries
            today = datetime.date.today()
            for date in entries:
                if date == today:
                    for entry in entries[date]:
                        if entry.url not in state.sent_today:
                            state.sent_today.add(entry.url)
                            send(webhook, entry)

    save_state(state, data)