# XTB Chem3D 連携用ツール xtbc3d

- [XTB Chem3D 連携用ツール xtbc3d](#xtb-chem3d-連携用ツール-xtbc3d)
	- [1. 概要](#1-概要)
	- [2. 更新履歴](#2-更新履歴)
			- [2021/6/10](#2021610)
	- [3. 動作要件](#3-動作要件)
	- [4. セットアップ](#4-セットアップ)
	- [5. 使用方法](#5-使用方法)
	- [6. 注意点](#6-注意点)
	- [7. おまけ](#7-おまけ)

## 1. 概要

GrimmeのXTB [https://github.com/grimme-lab/xtb] は半経験的な量子化学計算手法で、遷移金属を含むほとんどの元素について利用可能で、低い計算コストで錯体などの妥当な構造を計算することができます。元々はLinux用のプログラムですが、一応Windowsでもコンパイルして利用できます[https://github.com/npe1011/xtb_windows_build]。xtbc3d はこれを利用して、Chem3D上の分子の構造最適化をするツールです。

## 2. 更新履歴

#### 2021/8/20
- XTBのWindowsバイナリの公開が消えてるので対応。

#### 2021/6/10
- とりあえず完成

## 3. 動作要件

- Windows10
- Python3 + wxpython + comtypes + pyperclip
- XTB のWindowsバイナリ (MSYS2/MinGW-w64で作成するのを想定しています)
- Chem3D

動作確認は下記の通りの環境でやっています。

- Windows10 64bit
- Python 3.7.5
- wxPython==4.1.1
- comtypes==1.1.10
- pyperclip==1.8.1
- XTB 6.4.1
- Chem3D 19.0

## 4. セットアップ

Pythonのライブラリは pip install してください。XTBのバイナリは適当なところにおいてください。パスなどは内部的に処理するので通す必要はありません。
config.py を編集して必要な設定をします。

以下の2つは、Windowsに登録されているChem3DのCOM名です。多分メジャーバージョンだけ修正すれば大丈夫？

```config.py
CHEM3D_COM_NAME = 'Chem3D.Application.19'
CHEM3D_DOC_COM_NAME = 'Chem3D.Document'
```

WOR_DIR はXTB計算するときのファイルの置き場所です。書き込みできるところに設定してください。
なお**一時ファイルは勝手に消えない**ので適宜消して下さい。INIT_DIR は、xyzファイルを保存しようとしたときに開く初期ディレクトリです。

```config.py
WORK_DIR =  os.path.join(CONFIG_DIR, './temp')
INIT_SAVE_DIR = CONFIG_DIR
```

下記はXTB計算のための設定です。PATHLIBはMSYS2/MinGW-w64のDLLのあるディレクトリ（static linkのものを使えるなら None にしておく）、PATH はxtbバイナリのあるディレクトリ、XTBPATH はパラメータファイルのあるディレクトリを指定します。OMP_NUM_THREADS は並列数、OMP_STACKSIZE は各スレッドのメモリ使用量です。

```config.py
PATHLIB  = 'C:/msys64/mingw64/bin'  # None if not necessary
PATH = 'D:/programs/xtb-6.4.1/bin'
XTBPATH = 'D:/programs/xtb-6.4.1/bin/share/xtb'
OMP_NUM_THREADS = 4
OMP_STACKSIZE = '1G'
```

## 5. 使用方法

xtbc3d.pyw を実行してください。設定があっていれば、同時にChem3Dが立ち上がります。立ち上がったChem3D上に構造を書くなりChemdrawからコピペするなりした後、別途開いているウィンドウから、構造最適化をおこないます。

optimizeボタンを押すと計算中は止まって見えますが大丈夫です。エラーが出たときはウィンドウが開いてエラーメッセージが表示されます。計算が終わって構造の更新が終わるとメッセージボックスがでます。何らかの理由でダメだった場合は、とりあえずできたところまでで構造を更新するかどうかを聞かれます。Noを選択すると、代わりにXTBのログを表示します。

contrain atoms には、原子の番号（1スタート）をカンマ区切りで入力すると、その番号の原子を固定して構造最適化をします。3-15 のような範囲指定も可能です。

## 6. 注意点

色々やっているのですが、どうもChem3Dとの連携がおかしいことがあり、うまく認識しなかったり、終了したあともChem3Dのプロセスがバックグランドで残ってしまうときがあります。おかしかったら一旦プログラムを落として、タスクマネージャーからバックグランドのChem3Dのプロセスを全部落としてやり直して下さい。メモリリークもありそうなので、ずっと使ってるとメモリを浪費して再起動が必要になるかもしれません。

## 7. おまけ

opt.py は用意したxyz形式のファイルからXTBによる構造最適化をするコマンドライン用のスクリプトです。上記のセットアップをした上で利用できます。WindowsのGUI環境で.pyファイルが適切なPython環境に関連付けられていれば、xyzファイルをopt.pyかそのショートカットにドラッグアンドドロップすれば実行できます。パラメータはコマンドラインから対話的に入力できます。

コマンドラインから実行する場合の引数は、-h オプションで実行すると参照できます。

