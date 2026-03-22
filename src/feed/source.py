from dataclasses import dataclass
from abc import ABC, abstractmethod
from pathlib import Path
from dataclasses import asdict
from bs4 import BeautifulSoup
from urllib import request
import datetime
from pathlib import Path
import yaml
from warnings import warn

@dataclass(kw_only=True)
class Entry():
    title: str
    url: str
    preview_image_url: str = ""

class Source(ABC):

    def __init__(self, data: Path):
        self._data = data / f"{self.id}.yml"
        self._entries = {}

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

    def update(self):
        page = request.urlopen(self.url)
        data = page.read()
        soup = BeautifulSoup(data, 'html.parser')
        remote_entries = self._get_remote_entries(soup)

        if self._data.exists():
            with open(self._data, "r", encoding="utf-8") as io:
                raw_entries = yaml.safe_load(io)

            if raw_entries is not None:
                self._entries = {}
                for date in raw_entries:
                    self._entries[datetime.date.fromisoformat(date)] = [Entry(**entry) for entry in raw_entries[date]]
            else:
                self._entries = {}
        else:
            self._entries = {}

        if len(self._entries) > 0 and len(remote_entries) == 0:
            warn(f"Unable to get remote entries from {self.url}. But local entries exist.")
        else:
            for e in remote_entries:
                if e not in self._entries:
                    self._entries[e] = remote_entries[e]

        with open(self._data, "w", encoding="utf-8") as io:
            data = {}
            for date, entries in self._entries.items():
                data[str(date)] = [asdict(entry) for entry in entries]
            yaml.dump(data, io)

    @abstractmethod
    def _get_remote_entries(self, soup: BeautifulSoup) -> dict:
        return NotImplemented