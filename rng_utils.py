import requests


class RNGApiClient:
    def __init__(self, url):
        self._url = url
        self._needles = []

    def add_needle(self, needle):
        self._needles.append(str(needle))

    def reset_needle(self):
        self._needles.clear()

    def send_request(self) -> dict:
        needle_string = ",".join(self._needles)
        params = {"needle": needle_string}

        response = requests.get(self._url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return response.raise_for_status()


class RNGResult:
    __slots__ = ("_g7tid", "_tid", "_sid", "_tsv", "_trv")

    def __init__(self, rand: int) -> None:
        uint_rand = rand & 0xFFFFFFFF
        self._g7tid = uint_rand % 1000000
        self._tid = uint_rand & 0xFFFF
        self._sid = (uint_rand >> 16) & 0xFFFF
        self._tsv = (self._tid ^ self._sid) >> 4
        self._trv = (self._tid ^ self._sid) & 0xF

    @property
    def G7TID(self) -> int:
        return self._g7tid

    @property
    def TID(self) -> int:
        return self._tid

    @property
    def SID(self) -> int:
        return self._sid

    @property
    def TSV(self) -> int:
        return self._tsv

    @property
    def TRV(self) -> int:
        return self._trv

    def __str__(self) -> str:
        return (
            f"G7TID: {self._g7tid:06}\nTID: {self._tid:05}\nSID: {self._sid:05}\n"
            f"TSV: {self._tsv:04}\nTRV: {self._trv:X}"
        )


if __name__ == "__main__":
    result = RNGResult(0x948C0FC80150279F)
    print(result)
