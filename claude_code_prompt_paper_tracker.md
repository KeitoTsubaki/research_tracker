# 研究論文トラッカーサイト 実装プロンプト

以下の要件で、GitHub Pages上で動く静的Webサイトを実装してください。
サーバーは一切立てず、GitHub Actions + GitHubリポジトリをDB代わりに使う構成にしてください。

## 目的

研究テーマ(マルチエージェント強化学習・協調ロボット搬送・MAPPO/BenchMARL関連)に関する論文を
自動収集し、カード形式で閲覧・メモ管理できるサイトを作る。

## 全体アーキテクチャ

```
[GitHub Actions: 毎日 & 毎週 cron]
  ├─ arXiv APIから cs.RO, cs.AI, cs.LG 等の新着論文を取得
  ├─ 指定キーワード(下記)でフィルタリング
  ├─ 国際会議(CVPR, ICRA, NeurIPS, ICML, AAAI, IROS等)のBest Paper公式ページをスクレイピング
  ├─ data/*.json に追記・重複排除してcommit
  └─ RSS用XML(public/rss.xml)を生成してcommit

[静的サイト (Astro推奨、静的出力)]
  ├─ data/*.json をビルド時に読み込み
  ├─ カード形式で論文一覧を表示(タグ、会議名/カテゴリ、日付、メモ有無で絞り込み)
  ├─ 各カードにメモ欄(下記「メモの保存方式」参照)
  └─ GitHub Pagesにデプロイ(GitHub Actionsで自動ビルド&デプロイ)
```

## 技術スタック

- フロントエンド: Astro(静的サイト生成、`output: 'static'`)
- スタイリング: Tailwind CSS
- データ収集スクリプト: Python(`requests`, `feedparser`または`arxiv`パッケージ, `BeautifulSoup4`)
- CI/CD: GitHub Actions(cronスケジュール + push時ビルド)
- ホスティング: GitHub Pages
- DB: リポジトリ内のJSONファイル(サーバーDBは使わない)

## データモデル

`data/papers.json` に以下の形式で論文を蓄積:

```json
{
  "id": "arxiv:2506.xxxxx または conf:icra2026:award:1",
  "title": "...",
  "authors": ["..."],
  "source": "arxiv" または "conference_award",
  "category": "cs.RO / cs.AI / ...",
  "conference": "ICRA 2026 (該当する場合のみ)",
  "award": "Best Paper Award (該当する場合のみ)",
  "url": "...",
  "abstract": "...",
  "published_date": "YYYY-MM-DD",
  "fetched_at": "YYYY-MM-DDTHH:MM:SSZ",
  "tags": ["MARL", "cooperative-transport", ...],
  "memo": "",
  "memo_updated_at": null
}
```

同じIDの論文は重複追加せず、`memo`フィールドだけは既存データを保持したままマージすること。

## 機能要件

### 1. arXiv自動収集(毎日実行)
- 対象カテゴリ: `cs.RO`, `cs.AI`, `cs.LG`, `cs.MA`(マルチエージェント関連があれば)
- 以下のキーワードを含む論文を優先的にタグ付け・強調表示(タグは複数付与可):
  - MARL関連: multi-agent reinforcement learning, MARL, cooperative transport, MAPPO,
    Dec-POMDP, CTDE, decentralized control, multi-robot
  - 自動運転関連: autonomous driving, self-driving, end-to-end driving,
    motion planning, trajectory prediction, motion forecasting, sensor fusion,
    BEV perception, occupancy prediction, V2X, software-defined vehicle, SDV
- 上記2グループを別タグ(`marl`, `autonomous-driving`)として分け、
  フィルタUIでどちらか一方または両方を選べるようにする
- arXiv APIの利用規約(3秒間隔のリクエスト制限)を守ること

### 2. 国際会議受賞論文の収集(週次実行)
- 対象: CVPR, ICRA, IROS, NeurIPS, ICML, AAAI, RSS(Robotics: Science and Systems),
  IEEE IV(Intelligent Vehicles Symposium), ITSC(Intelligent Transportation Systems)
  のBest Paper / Best Student Paper系ページ
- 各会議ごとにHTML構造が異なるため、会議ごとにパーサーを分離した設計にする
  (例: `scrapers/icra.py`, `scrapers/cvpr.py` のようにプラグイン的な構成)
- 会議サイトの構造が変わった場合にエラーで全体が落ちないよう、
  1つの会議のスクレイピングが失敗しても他の会議の処理は続行する

### 3. RSS配信
- `public/rss.xml` を毎回の収集後に再生成
- 新着論文のみをRSSに含める(全件ではなく直近の差分)

### 4. カード表示UI
- カードには: タイトル、著者、会議/カテゴリバッジ、受賞バッジ(該当時)、日付、要旨(折りたたみ)、タグ
- フィルタ: カテゴリ、会議、キーワード検索、「メモあり/なし」
- ソート: 新着順、会議受賞順

### 5. メモ機能
- サイト自体はGitHub Pagesの静的サイトなので、ブラウザから直接JSONを書き換えることはできない
- メモは以下のいずれかの方式で実装(実装しやすい方でよい):
  a) サイト上でメモを入力すると、GitHub Issue作成用のリンク(prefilled URL)が生成され、
     手動でIssueを開いてsubmitすると、別のGitHub Actionsがそれを検知して
     `papers.json` の該当エントリに書き戻す
  b) もしくは、開発時はローカルでJSONを直接編集する運用にして、
     サイト側は表示のみに割り切る(実装コストを下げたい場合はこちらを初期実装にしてよい)
- まずは (b) のシンプルな方式で実装し、README に (a) の拡張案を書き残しておくこと

## リポジトリ構成(例)

```
/
├── .github/workflows/
│   ├── fetch-arxiv-daily.yml
│   ├── fetch-conference-weekly.yml
│   └── deploy-pages.yml
├── scripts/
│   ├── fetch_arxiv.py
│   ├── scrapers/
│   │   ├── icra.py
│   │   ├── cvpr.py
│   │   └── ...
│   └── generate_rss.py
├── data/
│   └── papers.json
├── src/  (Astroプロジェクト)
├── public/
│   └── rss.xml
└── README.md
```

## 実装ステップ

1. Astroプロジェクトを初期化し、`data/papers.json` を読み込んでカード表示する
   トップページを実装(まずはダミーデータでUI確認)
2. `scripts/fetch_arxiv.py` を実装し、ローカルで動作確認
3. `scripts/scrapers/` 配下に会議ごとのスクレイパーを1〜2個実装(まずICRAとCVPRなど)
4. `scripts/generate_rss.py` を実装
5. GitHub Actionsワークフローを作成:
   - 毎日実行: arXiv収集 → commit & push
   - 毎週実行: 会議受賞論文収集 → commit & push
   - push時: Astroビルド → GitHub Pagesデプロイ
   - commit & pushには、ワークフローに `permissions: contents: write` を設定した上で
     `GITHUB_TOKEN` を使ったgit操作(もしくは `stefanzweifel/git-auto-commit-action`)を使うこと。
     追加のシークレットやSSH鍵の設定は不要。
6. GitHub Pagesを有効化(`gh-pages`ブランチ or Actions経由のデプロイ)し、公開確認
7. README に運用方法(cronの頻度変更方法、キーワード追加方法、メモの拡張案)を記載

## 注意事項

- 外部サイトへのスクレイピングは各サイトの利用規約・robots.txtを尊重すること
- arXiv APIは公式に無料・認証不要だが、リクエスト間隔を空けること
- リポジトリはPublicにする前提(論文メタデータは公開情報のため問題なし)
- コストが一切かからない構成であることを常に優先し、有料サービス・APIキーが
  必要な実装は提案しないこと
