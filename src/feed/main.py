from typer import Argument, Option, Typer
from typing import Annotated
from pathlib import Path
import datetime
import logging
from time import time

from feed.weekinwildlife import WeekInWildlife
from feed.photosoftheday import PhotosOfTheDay
from feed.naturenews import NatureNews
from feed.bbcinpcitures import BBCInPictures
from feed.bbcfuture import BBCFuture
from feed.subreddit import SubredditFactory
from feed.discord import send, send_summary

app = Typer()

@app.command()
def update(
    data: Annotated[Path, Option(help="The directory for stored data")] = Path.cwd()/"data",
    webhook: Annotated[str | None, Option(help="Discord Webhook for sending messages")] = None):

    start = time()
    log = logging.getLogger(__name__)
    logging.basicConfig(filename=data/"feed.log", level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    log.info(f"Feed: Update\n"+"-"*80)

    if not data.is_dir():
        print(f"Creating new data store at {data}")
        data.mkdir(parents=True)
    else:
        print(f"Using data store at {data}")

    for source in (WeekInWildlife, PhotosOfTheDay, NatureNews, BBCInPictures, BBCFuture,):
        src = source(data)
        src.get()

        if webhook != None:
            today = datetime.date.today()
            for (date, entry) in src.new_entries():
                if date == today:
                    send(webhook, entry, src.name)

        src.commit()

    log.info("-"*51+"\n"+" "*30+f"Took {round(time()-start, 2)} s")

@app.command()
def update_subreddit(
    subreddit: Annotated[str, Argument(help="The subreddit to extract from")],
    data: Annotated[Path, Option(help="The directory for stored data")] = Path.cwd()/"data",
    webhook: Annotated[str | None, Option(help="Discord Webhook for sending messages")] = None):

    start = time()
    log = logging.getLogger(__name__)
    logging.basicConfig(filename=data/"feed.log", level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    log.info(f"Feed: Update {subreddit}\n"+"-"*80)

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

    log.info("-"*51+"\n"+" "*30+f"Took {round(time()-start, 2)} s")
