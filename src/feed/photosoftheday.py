from feed.utils import months
from feed.source import Entry, Source

from bs4 import BeautifulSoup
import datetime
from pathlib import Path

class PhotosOfTheDay(Source):

    def __init__(self, data: Path):
        super().__init__(data)

    @property
    def url(self) -> str:
        return "https://www.theguardian.com/news/series/ten-best-photographs-of-the-day"

    def _get_remote_entries(self, soup: BeautifulSoup):
        sections = soup.find_all('section')
        remote_entries = {}

        for section in sections:
            if section.get('id') is not None:
                sdate = section.get('id').strip().split("-")
                if len(sdate) != 3:
                    continue

                day = int(sdate[0])
                month = months[sdate[1].lower()]
                year = int(sdate[2])
                date = datetime.date(year, month, day)

                links = section.find_all('a')
                picture = section.find('picture')
                picture_url = ""
                for link in links:
                    if link.has_attr('aria-label'):
                        title = link['aria-label']
                        link = f"https://www.theguardian.com{link['href']}"
                        if picture is not None:
                            src = picture.find('source')
                            if src is not None:
                                picture_url = src["srcset"]
                        break

                remote_entries[date] = Entry(url=link, title=title, preview_image_url=picture_url)

        return remote_entries