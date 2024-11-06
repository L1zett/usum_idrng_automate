import ctypes
from ctypes import windll, pointer
from typing import Tuple


GetWindowTextLengthW = windll.user32.GetWindowTextLengthW
GetWindowTextW = windll.user32.GetWindowTextW
GetWindowRect = windll.user32.GetWindowRect
GetClientRect = windll.user32.GetClientRect
GetDpiForWindow = windll.user32.GetDpiForWindow
PrintWindow = windll.user32.PrintWindow
GetDC = windll.user32.GetDC
CreateCompatibleDC = windll.gdi32.CreateCompatibleDC
CreateCompatibleBitmap = windll.gdi32.CreateCompatibleBitmap
SelectObject = windll.gdi32.SelectObject
GetObjectA = windll.gdi32.GetObjectA
GetBitmapBits = windll.gdi32.GetBitmapBits
DeleteDC = windll.gdi32.DeleteDC
DeleteObject = windll.gdi32.DeleteObject
ReleaseDC = windll.user32.ReleaseDC
IsWindow = windll.user32.IsWindow
IsIconic = windll.user32.IsIconic
ShowWindow = windll.user32.ShowWindow
SetWindowPos = windll.user32.SetWindowPos
EnumWindows = windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)


SW_SHOWNORMAL = 1
SW_SHOWNOACTIVATE = 4
BITMAP_STRUCT_SIZE = 40
SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004


class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]


class WindowController:
    __slots__ = ["_hwnd"]

    def __init__(self, window_name=None):
        self._hwnd = None
        if window_name is not None:
            self.init(window_name)

    def init(self, window_name: str):
        """
        ウィンドウタイトルからハンドルを取得します。
        取得に成功した場合True, 失敗した場合Falseを返します。

        """

        def callback(hWnd, lParam):
            length = GetWindowTextLengthW(hWnd) + 1
            window_text = ctypes.create_unicode_buffer(length)
            GetWindowTextW(hWnd, window_text, length)
            if window_name in str(window_text.value):
                self._hwnd = hWnd
            return True

        EnumWindows(EnumWindowsProc(callback), 0)
        return self.is_window_vaild()

    def get_bitmap_data(self) -> Tuple[bytes, int, int]:
        """
        ウインドウのクライアント領域をキャプチャし、ビットマップデータとサイズ情報をタプルで返します

        戻り値:
            - bytes: キャプチャされたビットマップデータ
            - int: ウインドウの幅
            - int: ウインドウの高さ
        注意:
            - ビットマップデータはBGRX形式で格納されます。
            - 返されたビットマップデータは画像処理ライブラリを使ってBGRに変換するなどの処理が必要です
        """
        dpi = GetDpiForWindow(self._hwnd)
        
        width, height = self.get_client_size()

        width = int(width * dpi / 96)
        height = int(height * dpi / 96)

        hDC = GetDC(self._hwnd)
        compatibleDC = CreateCompatibleDC(hDC)
        bitmap = CreateCompatibleBitmap(hDC, width, height)
        SelectObject(compatibleDC, bitmap)

        PrintWindow(self._hwnd, compatibleDC, 1)

        # ビットマップの情報を格納するためのバッファを作成
        bitmap_info = ctypes.create_string_buffer(ctypes.sizeof(ctypes.c_ulong) * BITMAP_STRUCT_SIZE)
        GetObjectA(bitmap, ctypes.sizeof(bitmap_info), bitmap_info)

        # 幅×高さ×4バイト分のメモリを確保する
        bitmap_bits = ctypes.create_string_buffer(width * height * 4)
        GetBitmapBits(bitmap, len(bitmap_bits), bitmap_bits)

        # クリーンアップ
        DeleteDC(compatibleDC)
        DeleteObject(bitmap)
        ReleaseDC(self._hwnd, hDC)

        return bitmap_bits.raw, width, height

    def is_window_vaild(self) -> bool:
        return IsWindow(self._hwnd) != 0

    def is_minimized(self) -> bool:
        return IsIconic(self._hwnd) != 0

    def get_window_size(self):
        rect = RECT()
        GetWindowRect(self._hwnd, pointer(rect))
        width = rect.right - rect.left
        height = rect.bottom - rect.top
        return (width, height)

    def get_client_size(self):
        rect = RECT()
        GetClientRect(self._hwnd, pointer(rect))
        width = rect.right - rect.left
        height = rect.bottom - rect.top
        return (width, height)

    def restore_window_size(self) -> None:
        if self.is_minimized():
            ShowWindow(self._hwnd, SW_SHOWNOACTIVATE)

    def forced_change_size(self, width: int, height: int) -> None:
        rect = RECT()
        GetWindowRect(self._hwnd, pointer(rect))
        SetWindowPos(self._hwnd, 0, rect.left, rect.top, width, height, SWP_NOZORDER | SWP_NOMOVE)
