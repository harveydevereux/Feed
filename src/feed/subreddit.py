from feed.utils import months
from feed.source import Entry, Source

from bs4 import BeautifulSoup
import datetime
from pathlib import Path

def SubredditFactory(subreddit: str):
    return lambda data: Subreddit(data, subreddit)

class Subreddit(Source):

    def __init__(self, data: Path, subreddit: str):
        self._subreddit = subreddit
        super().__init__(data)

    @property
    def id(self) -> str:
        return self._subreddit.lower()

    @property
    def name(self) -> str:
        return self._subreddit

    @property
    def url(self) -> str:
        return f"https://www.reddit.com/r/{self._subreddit}/top/?t=day&feedViewType=compactView"

    def _get_remote_entries(self, soup: BeautifulSoup):
        articles = soup.find_all('article')
        remote_entries = {}

        for article in articles:
            if article.has_attr('aria-label'):
                link = article.find('a')
                if link is not None:
                    title = article['aria-label']
                    picture = article.find('img')
                    if picture is not None and picture.has_attr("alt"):
                        if "avatar" in picture["alt"].lower():
                            picture = None

                    picture_url = ""
                    if picture is not None and picture.has_attr("src"):
                        picture_url = picture["src"]

                    shreddit = article.find('shreddit-post')
                    if shreddit.has_attr("created-timestamp"):
                        sdate = shreddit["created-timestamp"].split("T")[0].split("-")
                        date = datetime.date(year=int(sdate[0]), month=int(sdate[1]), day=int(sdate[2]))
                    else:
                        date = datetime.date.today()
                    link = f"https://www.reddit.com{link['href']}"
                    entry = Entry(url=link, title=title, preview_image_url=picture_url)
                    if date in remote_entries:
                        remote_entries[date].append(entry)
                    else:
                        remote_entries[date] = [entry]


        return remote_entries