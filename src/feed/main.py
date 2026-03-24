from typer import Argument, Option, Typer
from typing import Annotated
from pathlib import Path
import datetime

from feed.weekinwildlife import WeekInWildlife
from feed.photosoftheday import PhotosOfTheDay
from feed.naturenews import NatureNews
from feed.bbcinpcitures import BBCInPictures
from feed.subreddit import SubredditFactory
from feed.discord import send, send_summary

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

    for source in (WeekInWildlife, PhotosOfTheDay, NatureNews, BBCInPictures,):
        src = source(data)
        src.get()

        if webhook != None:
            today = datetime.date.today()
            for (date, entry) in src.new_entries():
                if date == today:
                    send(webhook, entry, src.name)

        src.commit()

@app.command()
def update_subreddit(
    subreddit: Annotated[str, Argument(help="The subreddit to extract from")],
    data: Annotated[Path, Option(help="The directory for stored data")] = Path.cwd()/"data",
    webhook: Annotated[str | None, Option(help="Discord Webhook for sending messages")] = None):

    if not data.is_dir():
        print(f"Creating new data store at {data}")
        data.mkdir(parents=True)
    else:
        print(f"Using data store at {data}")

    for source in (SubredditFactory(subreddit), ):
        src = source(data)
        src.get()

        if webhook != None:
            entries = [entry for (_, entry) in src.new_entries()]
            if len(entries) > 0:
                send_summary(webhook, entries, f"r/{src.name}")

        src.commit()
