from feed.utils import months
from feed.source import Source

from dataclasses import asdict
from bs4 import BeautifulSoup
from urllib import request
import datetime
from pathlib import Path
import yaml
from warnings import warn

class WeekInWildlife:

    def __init__(self, data: Path):
        self._data = data / f"{self.id}.yml"
        self._entries = {}
        self._url = "https://www.theguardian.com/environment/series/weekinwildlife"

    @property
    def id(self) -> str:
        return "weekinwildlife"

    @property
    def entries(self) -> dict:
        return self._entries

    def update(self):
        page = request.urlopen(self._url)
        data = page.read()
        soup = BeautifulSoup(data, 'html.parser')
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

                remote_entries[date] = Source(url=link, title=title, preview_image_url=picture_url)

        if self._data.exists():
            with open(self._data, "r", encoding="utf-8") as io:
                raw_entries = yaml.safe_load(io)

            if raw_entries is not None:
                self._entries = {}
                for date in raw_entries:
                    self._entries[datetime.date.fromisoformat(date)] = Source(**raw_entries[date])
            else:
                self._entries = {}
        else:
            self._entries = {}

        if len(self._entries) > 0 and len(remote_entries) == 0:
            warn(f"Unable to get remote entries from {self._url}. But local entries exist.")
        else:
            for e in remote_entries:
                if e not in self._entries:
                    self._entries[e] = remote_entries[e]

        with open(self._data, "w", encoding="utf-8") as io:
            data = {str(date): asdict(entry) for date, entry in self._entries.items()}
            yaml.dump(data, io)
