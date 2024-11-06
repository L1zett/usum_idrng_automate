import clr
import os

def unblock_dll(dll_path):
    zone_identifier = f"{dll_path}:Zone.Identifier"
    if os.path.exists(zone_identifier):
        os.remove(zone_identifier)

class SFMTWrapper:
    def __init__(self):
        current_dir = os.path.dirname(__file__)
        dll = os.path.join(current_dir, "PokemonPRNG.SFMT.dll")
        unblock_dll(dll)
        try:
            clr.AddReference(dll)
            from PokemonPRNG.SFMT import SFMT

            self._sfmt = SFMT
        except Exception as e:
            raise ImportError(f"DLLの読み込みに失敗しました: {e}")
        self._rng = None

    def init(self, seed):
        self._rng = self._sfmt(seed)

    def _check_initialized(self):
        if self._rng is None:
            raise RuntimeError("初期化されていません")

    def advance(self, n: int):
        self._check_initialized()
        self._rng.Advance(n)

    def get_rand_64(self, m=None) -> int:
        self._check_initialized()
        if m is None:
            return self._rng.GetRand64()
        else:
            return self._rng.GetRand64(m)

    def get_rand_32(self) -> int:
        self._check_initialized()
        return self._rng.GetRand32()
