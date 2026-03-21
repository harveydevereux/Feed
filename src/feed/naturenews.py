from feed.utils import months
from feed.source import Entry, Source

from bs4 import BeautifulSoup
import datetime
from pathlib import Path

class NatureNews(Source):

    def __init__(self, data: Path):
        super().__init__(data)

    @property
    def url(self) -> str:
        return "https://www.nature.com/nature/articles?type=news"

    def _get_remote_entries(self, soup: BeautifulSoup):
        articles = soup.find_all('article')
        remote_entries = {}

        for article in articles:
            if article.find('time') is not None:
                sdate = article.find('time').text.strip().split(" ")

                day = int(sdate[0])
                month = months[sdate[1].lower()]
                year = int(sdate[2])
                date = datetime.date(year, month, day)

                link = article.find('a')
                picture = article.find('picture')
                picture_url = ""
                if link is not None:
                    title = link.text
                    link = f"https://www.nature.com/articles{link['href']}"
                    if picture is not None:
                        src = picture.find('img')
                        if src is not None:
                            picture_url = src["src"]

                remote_entries[date] = Entry(url=link, title=title, preview_image_url=picture_url)

        return remote_entries