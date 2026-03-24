from feed.utils import months
from feed.source import Entry, Source

from urllib import request
from bs4 import BeautifulSoup
import datetime
from pathlib import Path

class BBCFuture(Source):

    def __init__(self, data: Path):
        super().__init__(data)

    @property
    def url(self) -> str:
        return "https://www.bbc.co.uk/future"

    @property
    def _remote_can_be_empty(self) -> bool:
        return True

    def _get_remote_entries(self, soup: BeautifulSoup):
        remote_entries = {}

        seen_urls = self.urls
        urls = set()

        for story in soup.find_all("div"):
            links = [a for a in story.find_all("a") if a["href"].startswith("/future/article/")]

            if len(links) == 0:
                continue

            if not links[0].has_attr("href"):
                continue

            url = f"https://www.bbc.co.uk{links[0]['href']}"
            if url not in seen_urls:
                urls.add(url)

        for url in urls:
            page = request.urlopen(url)
            data = page.read()
            soup = BeautifulSoup(data, 'html.parser')

            title = soup.find("h1").text

            picture = soup.find("div", class_="hero-image")
            picture_url = ""
            if picture is not None:
                img = picture.find("img")
                if img is not None and img.has_attr("src"):
                    picture_url = img["src"]

            div = [div for div in soup.find_all("div", class_="author-unit")]

            if len(div) == 0:
                continue

            span = div[0].find("span")
            if span is not None:
                d, m, y = span.text.split()
                d = int("".join(ch for ch in d if ch.isdigit()))
                m = months[m.lower()]
                y = int(y)
                date = datetime.date(y, m, d)

                entry = Entry(url=url, title=title, preview_image_url=picture_url)
                if date in remote_entries:
                    remote_entries[date].append(entry)
                else:
                    remote_entries[date] = [entry]

        return remote_entries