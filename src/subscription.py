import dataclasses
import requests
import typing
import base64
import json
import pathlib
import pickle
import datetime


@dataclasses.dataclass(
    order=True
)
class Subscription:
    last_updated: float = dataclasses.field(compare=False)
    name: str = dataclasses.field(compare=True)
    url: str = dataclasses.field(compare=False)
    headers: dict[str, str] = dataclasses.field(compare=False)
    config: list[dict[str, typing.Any]] = dataclasses.field(compare=False)
    geoip: bytes | None = dataclasses.field(compare=False)
    geosite: bytes | None = dataclasses.field(compare=False)

    url_etag: str | None = dataclasses.field(compare=False)
    geoip_etag: str | None = dataclasses.field(compare=False)
    geosite_etag: str | None = dataclasses.field(compare=False)

    def __hash__(self) -> int:
        return hash(self.url)

    @staticmethod
    def get(
        url: str,
        etag: str | None,
        headers: dict[str, str] | None = None
    ):
        if etag:
            if headers:
                headers["If-None-Match"] = etag
            else:
                headers = {
                    "If-None-Match": etag
                }
        return requests.get(
            url,
            headers=headers
        )

    def update(
        self
    ):
        if self.url.startswith("file://"):
            filepath = pathlib.Path(self.url.removeprefix("file://"))
            if not filepath.exists():
                raise ValueError(f"{self.url} don't exist.")
            elif not filepath.is_file():
                raise ValueError(f"{self.url} is not file")
            filedata: str | list[dict[str, typing.Any]] | dict[str,
                                                               typing.Any] = json.loads(filepath.read_bytes())

            if isinstance(filedata, dict):
                filedata = [filedata]
            if not isinstance(filedata, list):
                raise ValueError(f"Incorrect data format: {filedata}")

            self.name = f"🛠️ {filepath.name.removesuffix(".json")}"
            self.config = filedata

        else:
            response = self.get(
                url=self.url,
                etag=self.url_etag,
                headers=self.headers
            )
            response.raise_for_status()
            self.config = response.json()
            self.url_etag = response.headers.get("Etag")
            routing = response.headers.get("routing")
            if routing and routing.startswith(
                "happ://"
            ):
                routing_base64_encoded = routing.removeprefix(
                    "happ://routing/add/").removeprefix("happ://routing/onadd/")
                routing_json: dict[str, str] = json.loads(
                    base64.b64decode(routing_base64_encoded))
                geoip_url = routing_json.get("Geoipurl")
                geosite_url = routing_json.get("Geositeurl")
                if geoip_url:
                    geoip_response = self.get(
                        url=geoip_url,
                        etag=self.geoip_etag
                    )
                    self.geoip = geoip_response.content
                    self.geoip_etag = geoip_response.headers.get("ETag")
                if geosite_url:
                    geosite_response = self.get(
                        url=geosite_url,
                        etag=self.geosite_etag
                    )
                    self.geosite = geosite_response.content
                    self.geosite_etag = geosite_response.headers.get("ETag")

            self.name = response.headers.get("profile-title", self.url)
            try:
                self.name = base64.b64decode(
                    self.name.removeprefix("base64:")).decode()
            except:
                pass

        self.last_updated = datetime.datetime.now(datetime.UTC).timestamp()

    @classmethod
    def from_url(
        cls,
        url: str,
        headers: dict[str, str]
    ):
        sub = cls(
            last_updated=0,
            name="N/A",
            url=url,
            headers=headers,
            config=[],
            geoip=None,
            geosite=None,
            url_etag=None,
            geoip_etag=None,
            geosite_etag=None
        )

        sub.update()

        return sub

    def show(self):
        print(f"Название: {self.name}")
        print(f"URL: {self.url} | {self.url_etag}")
        if self.geoip:
            print(f"geoip: {len(self.geoip)} B | {self.geoip_etag}")
        if self.geosite:
            print(f"geosite: {len(self.geosite)} B | {self.geosite_etag}")


class SubscriptionManager:
    def __init__(
        self,
        data_dir: pathlib.Path,
        headers: dict[str, str]
    ) -> None:
        self._data_file = data_dir / "subs.pkl"
        self._backup_file = data_dir / "urls.json"
        self.__subs: set[Subscription] = set()
        self.__headers = headers

    def add_sub(
        self,
        url: str
    ):

        sub = Subscription.from_url(
            url,
            headers=self.__headers
        )
        self.__subs.add(
            sub
        )
        return sub

    def del_sub(
        self,
        sub: Subscription
    ):
        self.__subs.discard(sub)

    @property
    def subs(
        self
    ):
        return self.__subs

    @property
    def urls(self):
        return [i.url for i in self.subs]

    def __enter__(self):
        if self._data_file.exists():
            self.__subs = pickle.loads(self._data_file.read_bytes())
        elif self._backup_file.exists():
            for url in json.loads(self._backup_file.read_bytes()):
                print(f"⬇️ Download data for {url}")
                self.add_sub(url=url)
        return self

    def __exit__(self, *_) -> None:
        self._data_file.write_bytes(pickle.dumps(self.__subs))
        self._backup_file.write_bytes(json.dumps(self.urls).encode())
