# 🎮 Sota Command Game System

日本語での自然な指示文を解析し、**Sota ロボットの動作と発話**を模倣して出力する  
テキストベースのインタラクションゲームです。  

ユーザーが「りんごを投げてください」と入力すると、  
形態素解析を使って「りんご（名詞）」と「投げる（動詞）」を認識し、  
対応する動作（例：右手を上げる）と発話（例：「リンゴを投げるよ」）を出力します。  

> ⚠️ 現在は Sota 実機 SDK が不明なため、**すべての動作・発話はコンソール出力でエミュレーション**しています。

---

## 📁 ディレクトリ構成

```
project/
├─ nouns.json          # 名詞データ
├─ verbs.json          # 動詞データ
├─ actions.json        # 動作・発話テンプレート
│
├─ sota_actions.py     # Sota制御クラス（モーション／スピーチ管理）
├─ game_system.py      # 入力解析・ランダム対応生成・Sota連携
└─ game_run.py         # 実行エントリーポイント
```

---

## ⚙️ 環境構築

### 1. 必要ライブラリのインストール

```bash
pip install "fugashi[unidic-lite]"
pip install jaconv
```

> **fugashi[unidic-lite]**  
> → 日本語形態素解析エンジン（MeCab + UniDicベース）  
>
> **jaconv**  
> → カタカナ・ひらがな・全角半角変換のために使用  

---

## 🧠 システム概要

### 1. 入力解析
- `fugashi` で入力文を形態素解析  
- 「名詞」「動詞」を JSON 辞書に基づいて照合  

### 2. ランダム対応生成
- 起動時に `(名詞 × 動詞)` ごとの組み合わせに対して  
  `actions.json` の動作を **ランダムに割り当て**  
- 同一セッション中は同じ動作が返る  

### 3. 動作実行
- `SotaAction` に「動き」と「発話」を設定  
- `SotaController` が `move()`（動き）→ `speak()`（発話）を順に実行  
- 現状は `print()` によるコンソール出力  

---

## 🧩 各ファイルの役割

| ファイル名 | 役割 |
|-------------|------|
| **nouns.json** | 名詞リスト。ID・表示名・同義語（エイリアス）を定義。 |
| **verbs.json** | 動詞リスト。辞書形（例：「投げる」「押す」）を定義。 |
| **actions.json** | 動作リスト。動作内容・発話テンプレートを定義。 |
| **sota_actions.py** | `SotaController` クラスを定義。<br> `move()`・`speak()`・`perform_action()`を管理。 |
| **game_system.py** | 入力解析と Sota の動作制御をまとめたメインロジック。 |
| **game_run.py** | 実行エントリーポイント。ゲームループを起動し、ユーザー入力を処理。 |

---

## 🏃‍♂️ 実行方法

1. 同ディレクトリ内に JSON ファイルを配置  
2. 以下を実行：

```bash
python game_run.py
```

---

## 💬 実行例

```
=== ランダム対応（サンプル）===
「りんごを投げる」 → 右手を上げる
「ボールを開ける」 → 両手を広げる
「本を押す」 → うなずく
================================

Sotaコマンドゲーム開始！
例：「りんごを投げて」「ボールを押して」など
終了するには「終了」と入力。

あなた > りんごを投げてください
---- Sota 動作 ----
[動き] 右手を上げる
-------------------

---- Sota 発話 ----
[発話] リンゴを投げるよ
-------------------
```

---

## 🧩 JSON データ仕様

### nouns.json
```json
[
  { "id": "apple", "display": "りんご", "aliases": ["りんご", "リンゴ", "林檎"] },
  { "id": "ball",  "display": "ボール", "aliases": ["ボール", "ぼーる"] }
]
```

### verbs.json
```json
[
  { "id": "throw", "dict": "投げる" },
  { "id": "open",  "dict": "開ける" }
]
```

### actions.json
```json
[
  { "id": "right_hand_up", "motion": "右手を上げる", "speech_template": "{noun_disp}を{verb}よ" },
  { "id": "spread_arms",   "motion": "両手を広げる", "speech_template": "{noun_disp}を{verb}よ" }
]
```

---

## 🧱 クラス構成概要

```
GameSystem
├── CommandInterpreter
│   ├── _load_nouns()
│   ├── _load_verbs()
│   ├── _load_actions()
│   ├── parse_command()
│   ├── build_action_from_text()
│   └── show_mapping_sample()
│
└── SotaController
    ├── move()
    ├── speak()
    ├── perform_action()
    └── perform()
```

---

## 🔄 今後の拡張案

| 分類 | 内容 |
|------|------|
| 💾 学習モード | ランダム対応を保存し、次回起動時も同じマッピングを利用可能に。 |
| 🧩 GUI対応 | Tkinter や PyQt による視覚的なコマンド入力UI。 |
| 🎤 音声入力 | `speech_recognition` でマイクからの音声コマンドに対応。 |
| 🗣️ 音声出力 | `pyttsx3` や OpenJTalk による音声合成。 |
| 🤖 実機対応 | Sota SDK 公開後、`SotaController.move()` と `speak()` に直接制御を実装。 |

---

## 📜 ライセンス

本プロジェクトは学術・教育用途を想定しています。  
ライセンスは **MIT License** を推奨します。

```
MIT License
Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## ✨ 開発メモ

- **Python 3.10 以上推奨**
- クラス設計済みのため、Sota SDK 実装時は `SotaController` のみ差し替えで対応可能。
- `seed` パラメータを指定すれば、ランダム対応の再現性を確保できます。

---

📘 **開発・動作確認環境**
- OS: Windows 10 / macOS Sonoma  
- Python: 3.11  
- 主要ライブラリ: fugashi, jaconv  

---

**作者:** 百々 大貴 (Daiki Dodo)  
**作成日:** 2025年  
**プロジェクト名:** Sota Command Game System
