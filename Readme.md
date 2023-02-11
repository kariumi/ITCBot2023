# ITC bot 2023 取扱説明書
- コマンドは随時追加予定。

⚠️コマンドは`BOT使用`のロールが付与されていないと使用できません。

⚠️ コマンドを入力する時はbot-consoleチャンネルを使用してください。

![ITC](readme/bot_banner.png "ITC Bot 2023")

---
# 目次
- [BOTを使用するための準備](#botを使用するための準備)
- [コマンド一覧](#コマンド一覧)
  - [!shuffle](#-shuffle) - `BOT使用`メンバーをボイスチャンネルに均等に振り分ける
  - [!vote](#-vote)
    - [create](#-vote-create) - `BOT使用`投票を作成する
- [あとがき](#あとがき)
- [更新履歴](#更新履歴)

---
# BOTを使用するための準備
以下の手順で、開発者モードをONにしてください。

①Discordのユーザー設定を開く


②「アプリの設定」にある「詳細設定」を押す


③開発者モードをONにする。


コマンドを使用する際は、テキストチャンネル「bot-consol」をご使用ください。

---
# コマンド一覧

## ✅ !shuffle
必要ロール：`BOT使用`

自分が入っているボイスチャンネルの人を指定したボイスチャンネルにランダムに振り分け、自動的に移動させるコマンドです。
```
!shuffle [ボイスチャンネルID 1] [ボイスチャンネルID 2] ...

例：
!shuffle 123456789012345678 123456789012345679
```
- ↑ボイスチャンネルのみ指定すると、指定したボイスチャンネルにランダムに振り分けることができます。
![shuffle](readme/shuffle.gif "シャッフル")
```
!shuffle [(任意)ロール 1] [(任意)ロール 2] [(任意)ロール 3] [ボイスチャンネルID 1] [ボイスチャンネルID 2] ...

例：
!shuffle @DTM部 @CG部 123456789012345678 123456789012345679
```
- ↑ロールを指定すると、指定したロールのメンバーは均等に振り分けられます。
- ロールは0~3個の間で指定することができます。


## ✅ !vote

投票を作成して様々なことができる予定の機能です。
### ✅ !vote create
必要ロール：`BOT使用`

```
!vote create [テキストチャンネルID] [投票タイトル] [投票先1] [投票先2] [投票先3] ...

例:
!vote create 123456789012345678 学部は？ 工学部 先進工学部 薬学部 その他
!vote create 123456789012345678 @prog部昼ごはん食べた？__⚠️期限：~2/20__ はい 食べない 今から
```
⚠️ 投票タイトルに空白や改行は使用できません。
![vote](readme/vote.gif "投票")
- 選択肢に投票したメンバーの名前がリアルタイムで表示されます。

⚠️ 投票結果がバグったときはリサイクルマークを押してください。

![リフレッシュマーク](readme/Vote-Reflesh.gif "バグった時")


---
# あとがき

## 参考リンク
- discord.py APIリファレンス - (https://discordpy.readthedocs.io/ja/latest/api.html)
- heroku - (https://dashboard.heroku.com/)
  
---
# 更新履歴
### 2022/12/**
- ITC bot ver1.1.0から移植。

### 2023/2/3
- voteコマンドを削除。

### 2023/2/4
- shuffleコマンドの軽微な修正。
- Readmeを執筆。

### 2023/2/5
- voteコマンドの追加。
