# 研究論文トラッカー

マルチエージェント強化学習(MARL)・協調ロボット搬送・自動運転関連の論文を自動収集し、
カード形式で閲覧できる静的サイトです。サーバーは使わず、GitHub Actions + リポジトリ内の
JSONファイルをDB代わりにした構成で動きます。

## アーキテクチャ

```
[GitHub Actions: 毎日 & 毎週 cron]
  ├─ arXiv APIから cs.RO, cs.AI, cs.LG, cs.MA の新着論文を取得 (scripts/fetch_arxiv.py)
  ├─ 国際会議のBest Paper系ページをスクレイピング (scripts/fetch_conference_awards.py)
  ├─ data/papers.json に追記・重複排除してcommit (memoフィールドは既存データを保持)
  └─ public/rss.xml を再生成してcommit (scripts/generate_rss.py)

[静的サイト (Astro + Tailwind CSS, output: 'static')]
  ├─ data/papers.json をビルド時に読み込みカード表示
  ├─ カテゴリ・会議・キーワード・メモ有無で絞り込み、新着順/受賞順でソート
  └─ GitHub Actionsでビルド& GitHub Pagesにデプロイ
```

## リポジトリ構成

```
/
├── .github/workflows/
│   ├── fetch-arxiv-daily.yml       # 毎日: arXiv収集 → commit
│   ├── fetch-conference-weekly.yml # 毎週: 会議受賞論文収集 → commit
│   └── deploy-pages.yml            # push時: ビルド → GitHub Pagesデプロイ
├── scripts/
│   ├── fetch_arxiv.py
│   ├── fetch_conference_awards.py
│   ├── generate_rss.py
│   ├── lib/store.py                # papers.json の読込・マージ・保存の共通処理
│   └── scrapers/                   # 会議ごとのスクレイパー(プラグイン方式)
│       ├── base.py                 # 共通パーサー(make_award_scraper)
│       ├── icra.py                 # ICRA
│       ├── cvpr.py                 # CVPR
│       ├── iros.py                 # IROS
│       ├── neurips.py              # NeurIPS
│       ├── icml.py                 # ICML
│       ├── aaai.py                 # AAAI
│       ├── rss.py                  # RSS (Robotics: Science and Systems)
│       ├── ieee_iv.py              # IEEE IV (Intelligent Vehicles Symposium)
│       └── itsc.py                 # IEEE ITSC
├── data/
│   └── papers.json                 # 論文データ(DB代わり)
├── src/                            # Astroプロジェクト本体
├── public/
│   └── rss.xml
├── requirements.txt
└── README.md
```

## セットアップ

```bash
npm install
npm run dev       # http://localhost:4321/research_tracker/ で確認

python -m venv .venv && source .venv/bin/activate   # Windowsは .venv\Scripts\activate
pip install -r requirements.txt
python scripts/fetch_arxiv.py
python scripts/fetch_conference_awards.py
python scripts/generate_rss.py
```

## GitHub Pagesの有効化

1. このリポジトリをGitHub上にPublicリポジトリとしてpushする。
2. リポジトリの Settings → Pages → Build and deployment の Source を
   **GitHub Actions** に設定する(`deploy-pages.yml` が自動でビルド&デプロイする)。
3. `main` ブランチにpushすると `deploy-pages.yml` が実行され、
   `https://<ユーザー名>.github.io/<リポジトリ名>/` で公開される。
4. `deploy-pages.yml` は `actions/configure-pages` の出力(`origin`/`base_path`)を
   `SITE_URL`/`SITE_BASE` として `astro.config.mjs` に渡しているため、
   リポジトリ名を変えても手動でbase pathを調整する必要はない。
   - ただし `<ユーザー名>.github.io` 形式のユーザー/組織ルートサイトとして公開する場合は
     base pathが `/` になるので、`astro.config.mjs` の `rawBase` のデフォルト値だけ
     確認すること(configure-pagesの出力が優先されるので通常は変更不要)。

## 運用方法

### cronの頻度を変える

- 毎日実行: `.github/workflows/fetch-arxiv-daily.yml` の `on.schedule.cron` を編集
  (例: `"0 3 * * *"` は毎日 UTC 3:00 = JST 12:00)。
- 毎週実行: `.github/workflows/fetch-conference-weekly.yml` の `on.schedule.cron` を編集
  (例: `"0 4 * * 1"` は毎週月曜 UTC 4:00 = JST 13:00)。
- cron式は [crontab.guru](https://crontab.guru/) 等で確認するとよい。
- どちらも `workflow_dispatch` を設定してあるので、Actionsタブから手動実行もできる。

### キーワードを追加する

- `scripts/fetch_arxiv.py` の `KEYWORD_GROUPS` 辞書にキーワードを追記する
  (`marl` グループと `autonomous-driving` グループのどちらかに追加、
  または新しいグループを追加する場合は `src/lib/papers.ts` の
  `KEYWORD_GROUPS` にも同じslugを追加してフィルタUIに反映させる)。
- キーワードは小文字で判定しているので、追加時も小文字で書けばOK
  (マッチングはタイトル+要旨を小文字化してから部分一致で行う)。

### 会議スクレイパーを追加する

1. `scripts/scrapers/新しい会議名.py` を作成し、`scrape() -> list[AwardPaper]` を実装する
   (`scripts/scrapers/base.py` の `AwardPaper` / `fetch_html` / `classify_award` を利用可能)。
2. `scripts/scrapers/__init__.py` の `SCRAPERS` 辞書に登録する。
3. 1つのスクレイパーが例外を投げても他のスクレイパーの処理は止まらない設計になっている
   (`scripts/fetch_conference_awards.py` が各スクレイパーを try/except で個別に実行するため)。
4. 会議サイトの利用規約・robots.txtを必ず確認すること。

### メモ機能について

現在の実装は方式 **(b)**: メモは各カードに表示されるが、サイト上からの編集はできない。
メモを追加・更新したい場合は、ローカルで `data/papers.json` の該当エントリの
`memo` / `memo_updated_at` フィールドを直接編集し、コミット&pushする。
自動収集スクリプト(`fetch_arxiv.py` / `fetch_conference_awards.py`)は既存IDの
`memo` フィールドを一切上書きしないので、手動で書いたメモが自動収集で消えることはない。

#### 拡張案 (a): GitHub Issue経由でのメモ書き込み

サイト上でメモを直接編集できるようにする場合は、以下のような拡張が考えられる。

1. カードのメモ欄に入力フォームを追加し、送信すると
   `https://github.com/<owner>/<repo>/issues/new?title=...&body=...&labels=memo-update`
   のようなprefilled URLを組み立てて新しいタブで開く
   (Issue本文に論文ID・メモ本文をテンプレート化して埋め込む)。
2. ユーザーが実際にGitHub上でIssueをsubmitする。
3. `issues` イベント(`opened`)をトリガーとする新しいワークフロー
   (例: `.github/workflows/apply-memo.yml`)を追加し、
   - Issue本文をパースして対象の論文ID・メモ本文を取り出す
   - `data/papers.json` の該当エントリの `memo` / `memo_updated_at` を更新してcommit
   - 処理が終わったIssueはコメントを付けてcloseする
4. GitHub Appやトークンの追加設定は不要(`GITHUB_TOKEN` + `contents: write` で完結)。
   Issueの作成自体はユーザーのGitHubアカウントで行われるため、
   誰でも自由に書き込めてしまわないようにする場合は
   Issueテンプレートやリポジトリのコラボレーター権限で制御する。

## 注意事項

- 外部サイトへのスクレイピングは各サイトの利用規約・robots.txtを尊重すること。
- arXiv APIはリクエスト間隔を3秒以上空けるようにしている(`scripts/fetch_arxiv.py` の
  `REQUEST_INTERVAL_SECONDS`)。
- 会議の受賞論文ページはURL・HTML構造が年ごとに変わるため、`scripts/scrapers/` 配下の
  各モジュール(ICRA / CVPR / IROS / NeurIPS / ICML / AAAI / RSS / IEEE IV / ITSC)の
  URL・パーサーは年に一度程度の見直しが必要になる。特に多くの会議は開催直前まで
  正式な受賞ページを公開しないため、`*_AWARDS_URL` が現状カンファレンスのトップページ
  (または推測パスで404)になっているものがある。その場合スクレイパーは例外を出さず
  「0件」を返して処理を続行するだけなので、パイプライン自体は壊れない
  (`scripts/scrapers/base.py` の `make_award_scraper` が持つ最低文字数チェックにより、
  ナビゲーションリンクなどの誤検出も除外される)。受賞ページが公開され次第、
  該当モジュールの `*_AWARDS_URL` を実際のURLに差し替えること。
- 本構成は無料の範囲で完結するように設計されている(有料API・シークレットは不要)。
