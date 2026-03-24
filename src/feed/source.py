from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from pathlib import Path
from bs4 import BeautifulSoup
from urllib import request
import datetime
from pathlib import Path
import yaml
from warnings import warn
from typing import Tuple

@dataclass(kw_only=True)
class Entry():
    title: str
    url: str
    preview_image_url: str = ""

class Source(ABC):

    def __init__(self, data: Path):
        self._data = data / f"{self.id}.yml"
        self._entries = {}
        self._remote_entries = {}
        if self._data.exists():
            with open(self._data, "r", encoding="utf-8") as io:
                raw_entries = yaml.safe_load(io)

            if raw_entries is not None:
                for date in raw_entries:
                    self._entries[datetime.date.fromisoformat(date)] = [Entry(**entry) for entry in raw_entries[date]]

    @property
    def id(self) -> str:
        return type(self).__name__.lower()

    @property
    def entries(self) -> dict:
        return self._entries

    @property
    @abstractmethod
    def url(self) -> str:
        return NotImplemented

    def get(self):
        page = request.urlopen(self.url)
        data = page.read()
        soup = BeautifulSoup(data, 'html.parser')
        self._remote_entries = self._get_remote_entries(soup)

        if len(self._entries) > 0 and len(self._remote_entries) == 0:
            warn(f"Unable to get remote entries from {self.url}. But local entries exist.")

    def new_entries(self) -> list[Tuple[datetime.date, Entry]]:
        new = []
        seen_urls = set(entry.url for date in self.entries for entry in self.entries[date])
        for date, entries in self._remote_entries.items():
            for entry in entries:
                if entry.url not in seen_urls:
                    new.append((date, entry))
        return new

    def commit(self):
        seen_urls = set(entry.url for date in self.entries for entry in self.entries[date])
        for date, entries in self._remote_entries.items():
            for entry in entries:
                if entry.url not in seen_urls:
                    if date in self._entries:
                        self._entries[date].append(entry)
                    else:
                        self._entries[date] = [entry]

        with open(self._data, "w", encoding="utf-8") as io:
            data = {}
            for date, entries in self._entries.items():
                data[str(date)] = [asdict(entry) for entry in entries]
            yaml.dump(data, io)

    @abstractmethod
    def _get_remote_entries(self, soup: BeautifulSoup) -> dict:
        return NotImplemented