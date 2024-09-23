from Commands.Keys import Button, Hat
from Commands.PythonCommandBase import ImageProcPythonCommand
from threading import Event
from time import perf_counter
from enum import Enum
from logging import getLogger, DEBUG, NullHandler
import numpy as np
import os

from .rng_utils import RNGApiClient, RNGResult
from .sfmt import SFMTWrapper
from .mylib import image_process, WindowController


class SearchMethod(Enum):
    G7TID = "G7TID"
    TIDSID = "TID/SID"
    
class UsumIdrngAutomate(ImageProcPythonCommand):
    NAME = "USUM_ID調整自動化"

    def __init__(self, cam):
        super().__init__(cam)
        self._read_count = 10
        self._fps = 59.8261
        self._wait_time = (230 / self._fps)
        self._cur_dir = os.path.dirname(__file__)
        self._template = os.path.join(self._cur_dir, "templates")
        self._search_method_list = [i.value for i in SearchMethod]
        self._gender_list = [
            "男主人公1", "男主人公2", "男主人公3", "男主人公4", 
            "女主人公1", "女主人公2", "女主人公3", "女主人公4"
        ]
        self._lang_list = [
            "日本語", "英語", "スペイン語", "フランス語", "ドイツ語", 
            "イタリア語", "韓国語", "中国語(簡体字)", "中国語(繁体字)"
        ]

        self._logger = getLogger(__name__)
        self._logger.addHandler(NullHandler())
        self._logger.setLevel(DEBUG)
        self._logger.propagate = True
        
    def do(self):
        self.command_init()
        found = False
        while not found:
            self.skip_intro()
            seed = self.find_initial_seed()
            if seed is None:
                continue
            found, adv = self.id_search(seed)
            
        print(f"目標IDが見つかりました。消費作業を開始します。\n消費数: {adv}")
        self.shohi(adv)
        print("消費が終了しました")
        
    def command_init(self):
        try:
            self._window_controller = WindowController("nonstd 3pairs Diff Signal Viewer")
            if not self._window_controller.is_window_vaild():
                raise Exception("偽トロビューワーを検出できませんでした")
            
            self._api_client = RNGApiClient("https://rng-api.odanado.com/usm/sfmt/seed/id")
            self._sfmt = SFMTWrapper()
            png_files = [os.path.join(self._cur_dir, "needles", f"{i}.png") for i in range(17)]
            self._compare_binaries = [image_process.load_and_binarize(path, 156) for path in png_files]
            self._target_id = self.read_id_text()
            self._target_g7tid = self.read_g7tid_text()
            self._setting = self.dialogue6widget("設定",
                                    [["Radio", "検索方法", self._search_method_list, self._search_method_list[0]],
                                    ["Entry", "検索範囲", "50000"],
                                    ["Combo", "言語", self._lang_list, self._lang_list[0]],
                                    ["Combo", "主人公の見た目", self._gender_list, self._gender_list[0]]])
            self.valid_setting()
        except Exception as e:
            print(f"{e}")
            self.finish()
    
    def valid_setting(self):        
        if not self._setting:
            raise Exception("")
        
        is_valid = True
        if self._setting[0] == SearchMethod.G7TID.value:
            if not self._target_g7tid:
                is_valid = False
        elif self._setting[0] == SearchMethod.TIDSID.value:
            if not self._target_id:
                is_valid = False
        if not is_valid:
            raise Exception("テキストファイルに目標IDが書き込まれていません")
        
        self._setting[1] = int(self._setting[1])
        if self._setting[2] not in self._lang_list or self._setting[3] not in self._gender_list:
            raise Exception("パラメータが正しく設定されていません")

    def read_id_text(self):
        target_id = []
        with open(os.path.join(self._cur_dir, "ID.txt"), 'r') as file:
            for line in file:
                parts = line.strip().split(",")
                if len(parts) != 2:
                    continue
                try:
                    pair = tuple(int(item.strip()) for item in parts)
                    target_id.append(pair)
                except ValueError:
                    continue
        return target_id
        
    def read_g7tid_text(self):
        target_g7tid = []
        with open(os.path.join(self._cur_dir, "G7TID.txt"), 'r') as file:
            for line in file:
                try:
                    number = int(line.strip())
                    target_g7tid.append(number)
                except ValueError:
                    continue
        return target_g7tid
    
    def skip_intro(self):
        """
        言語選択～名前選択画面まで自動化します
        """
        
        self.soft_reset()
        yellow = np.array([0, 255, 255])
        while True:
            upper, _ = image_process.split_img_vertical(self.get_capture())
            if image_process.is_color_detected(upper, yellow):
                break
            self.wait(0.2)
            
        # 言語選択
        for _ in range(self._lang_list.index(self._setting[2])):
            self.press(Hat.BTM)
        self.press(Button.A, wait=0.5)
        self.press(Button.A, wait=3)
        
        # 博士と会話
        while True:
            _, lower = image_process.split_img_vertical(self.get_capture())
            if not np.all(lower == 0):
                self.wait(0.2)
                break
            self.press(Button.A, wait=0.3)
        
        # 写真を選択
        if "男" in self._setting[3]:
            for _ in range(self._gender_list.index(self._setting[3])):
                self.press(Hat.RIGHT)
        else:
            self.press(Hat.BTM)
            for _ in range(self._gender_list.index(self._setting[3]) - 4):
                self.press(Hat.RIGHT)
                
        # 名前入力画面まで連打
        yellow_green = np.array([0, 255, 128])
        while True:
            _, lower = image_process.split_img_vertical(self.get_capture())
            if image_process.is_color_detected(lower, yellow_green):
                break
            self.press(Button.A, wait=0.2)
        
        # 適当に名前を入力する
        self.press(Button.A)
        self.press(Button.PLUS)
        self.press(Button.A)
        
        while not np.all(image_process.split_img_vertical(self.get_capture())[1] == 0):
            self.wait(0.2)
        
    def find_initial_seed(self): 
        for i in range(self._read_count):
            index = self.read_needle()
            self._api_client.add_needle(index)
            
            if i != self._read_count - 1:
                print(index, end=",")
            else:
                print(index)
        
        results = self._api_client.send_request().get("results", [])
        self._logger.debug(f"results: {results}")
        self._api_client.reset_needle()
        
        if results:
            seed = results[0]["seed"]
            print(f"seed: {seed.upper()}")
            return seed
        else:
            return None
    
    def id_search(self, seed):
        self._sfmt.init(int(seed, 16))
        self._sfmt.advance((1132 + self._read_count + 1) * 2) # 初期消費 + 針を見た回数 + 名前入力分
        if self._setting[0] == SearchMethod.G7TID.value:
            return self.g7tid_search()
        elif self._setting[0] == SearchMethod.TIDSID.value:
            return self.tidsid_search()
    
    def shohi(self, adv):
        # カーソルが表示されるまで待つ
        red = np.array([0, 0, 255])
        while not image_process.is_color_detected(self.get_capture(), red):
            self.wait(0.2)
            
        for i in range(adv):
            self.press(Button.B, wait=2.1)
            if i != adv - 1:
                self.press(Button.A)
                self.press(Button.PLUS)
                self.press(Button.A, wait=3.8)
    
    def g7tid_search(self):
        for i in range(self._setting[1]):
            rng_result = RNGResult(self._sfmt.get_rand_64())
            if rng_result.G7TID in self._target_g7tid:
                print(f"{rng_result}")
                self.save_result(rng_result)
                return (True, i + 1)
        return (False, None)
    
    def tidsid_search(self):
        for i in range(self._setting[1]):
            rng_result = RNGResult(self._sfmt.get_rand_64())
            if (rng_result.TID, rng_result.SID) in self._target_id:
                print(f"{rng_result}")
                self.save_result(rng_result)
                return (True, i + 1)
        return (False, None)
    
    def read_needle(self):
        self.check_client_size()
        
        # カーソルが表示されるまで待つ
        red = np.array([0, 0, 255])
        while not image_process.is_color_detected(self.get_capture(), red):
            self.wait(0.2)
        
        # いいえを選択　→　暗転
        start = perf_counter()
        self.press(Button.B)
        
        # 名前入力画面
        self.wait(2.5)
        self.press(Button.A)
        self.press(Button.PLUS)
        
        # 230F待機する
        while (perf_counter() - start) < self._wait_time:
            self.checkIfAlive()
            
        # 入力画面を抜ける
        start = perf_counter()
        self.press(Button.A, wait=1)
        
        # 針が表示される部分を切り取る
        while True:
            img = image_process.crop_image(self.get_capture(), 381, 221, 14, 14)
            binary_img = image_process.to_binarize(img, 156)
            if image_process.is_significant_white_area(binary_img, 0.3):
                break
            self.checkIfAlive()
        
        index, match_rate = image_process.calc_highest_match(binary_img, self._compare_binaries)
        self._logger.debug(f"needle: {index} Match Rate: {match_rate}")
        return index

    def get_capture(self) -> np.ndarray:
        if self._window_controller.is_minimized():
            print("ウインドウが最小化されたため一時停止しました")
            while self._window_controller.is_minimized():
                self.wait(1)
                self.checkIfAlive()
        bitmap_bits, width, height = self._window_controller.get_bitmap_data()
        return np.frombuffer(bitmap_bits, dtype=np.uint8).reshape((height, width, 4))[:, :, :3]

    def soft_reset(self):
        self.press([Button.L, Button.R, Button.START], wait=1)
        
    def save_result(self, rng_result):
        with open(os.path.join(self._cur_dir, "result.txt"), "w", encoding="utf-8") as file:
            file.write(str(rng_result))
    
    def check_client_size(self):
        if not (self._window_controller.get_client_size() == (400, 480)):
            self._window_controller.forced_change_size(416, 558)