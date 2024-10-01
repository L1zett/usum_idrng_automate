## 概要
Poke-Controllerを使用して『ポケットモンスター ウルトラサン・ウルトラムーン』の ID 調整を自動化するマクロです。  
[**Qingpi**](https://github.com/U-1F992/qingpi) および偽トロキャプチャ基板を使用しているユーザー向けに設計されています。

## 事前準備
### 1. 偽トロ側の設定
- **バックバッファ**: 自動リサイズ  
- **転送モード**: Light Weight Mode  
- **3Dモード**: 3D OFF  
- **等倍調整**: dot by dot x1  
- **上下表示**: 上下画面表示、上下比率 [50％:50％]  
- **回転**: 正面 0°  

### 2. ゲーム側の設定
- ID 調整を行いたい ROM のセーブデータを **十字キー↑ + Bボタン + Xボタン** で完全に消去してください。
- ゲームを起動し、ソフトリセットできる状態にしてください。

## 使い方
1. リポジトリをクローンし、フォルダを`Commands\PythonCommands` に配置してください。
    - Gitコマンドがよくわからないという方は、右上の「Code」ボタンをクリックし、「Download ZIP」でファイルをダウンロードして解凍してください。

2. ディレクトリ内にある `G7TID.txt` もしくは `ID.txt` に、**1行ずつ**目標の ID を記述します。 　
    - ファイル内に無効なデータ（数値以外の文字列や空行）が含まれている場合、その行は実行時に無視されます。  

### 記述例(G7TID):
000000    
001122    

### 記述例(TID/SID):
00000, 00000     
20043, 00000 


3. マクロを実行するとダイアログが表示されます。適切な項目を選択し、OK ボタンを押してください。  
4. 目標 ID が見つかった場合、結果が `result.txt` に保存され、そのまま消費作業へ移行します。  
5. 消費作業が完了したら、任意の名前を入力してゲームを開始してください。  


## 動作環境
- Windows 11
- Poke-Controller Modified
- Poke-Controller Modified Extension

## Requirements
- [NumPy](https://github.com/numpy/numpy)
- [pythonnet](https://github.com/pythonnet/pythonnet)
- [OpenCV-Python](https://github.com/opencv/opencv-python)
- [Requests](https://github.com/psf/requests)

## 参照
- [ポケモン ID 調整についての解説 - milk4724's blog](https://milk4724.hatenadiary.org/entry/2021/08/21/00000000)
- [サン・ムーンの ID 調整方法 - blastoise-x's blog](https://blastoise-x.hatenablog.com/entry/SM-ID-RNG)

## Credits
- [rng-api](https://github.com/odanado/rng-api) - 開発者: **odanado**様
- [PokemonPRNG](https://github.com/yatsuna827/PokemonPRNG) - 開発者: **yatsuna827**様
