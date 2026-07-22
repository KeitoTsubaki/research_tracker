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

[手動実行: 過去論文の一括バックフィル]
  └─ scripts/fetch_arxiv_historical.py が cooperative-transport キーワード群で
     arXivを2000年以降まで遡って検索(MARL手法を使っていない古典的な協調搬送
     研究も対象。crontabには乗せず、必要なときに手動実行する)

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
│   ├── fetch_arxiv.py               # 毎日: 新着論文を収集
│   ├── fetch_arxiv_historical.py    # 手動: 過去論文を一括バックフィル
│   ├── fetch_conference_awards.py
│   ├── generate_rss.py
│   ├── lib/
│   │   ├── store.py                # papers.json の読込・マージ・保存の共通処理
│   │   └── keywords.py             # キーワードグループ(marl/cooperative-transport/
│   │                                # autonomous-driving)の単一の定義元
│   └── scrapers/                   # 会議ごとのスクレイパー(プラグイン方式)
│       ├── base.py                 # 共通パーサー(make_award_scraper)
│       ├── icra.py                 # ICRA(専用パーサー)
│       ├── cvpr.py                 # CVPR(専用パーサー)
│       ├── iros.py                 # IROS(汎用パーサー、結果ページ未特定)
│       ├── neurips.py              # NeurIPS(専用パーサー)
│       ├── icml.py                 # ICML(専用パーサー)
│       ├── aaai.py                 # AAAI(専用パーサー)
│       ├── rss.py                  # RSS: Robotics: Science and Systems(専用パーサー)
│       ├── ieee_iv.py              # IEEE IV(汎用パーサー、結果ページ未特定)
│       └── itsc.py                 # IEEE ITSC(専用パーサー)
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

# 過去論文の一括バックフィル(2000年以降、必要なときに手動実行)
python scripts/fetch_arxiv_historical.py
python scripts/fetch_arxiv_historical.py --start-year 1995   # 開始年を変えたい場合
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

- `scripts/lib/keywords.py` の `KEYWORD_GROUPS` 辞書がキーワード定義の唯一の場所。
  `fetch_arxiv.py`(日次)・`fetch_arxiv_historical.py`(過去バックフィル)・
  `fetch_conference_awards.py`(会議受賞論文へのタグ付け)の全てがここを参照する。
- `marl`(MARL手法) / `cooperative-transport`(協調ロボット搬送。MARLでなくても
  該当すればタグ付けする) / `autonomous-driving` のいずれかにキーワードを追記するか、
  新しいグループを追加する場合は `src/lib/papers.ts` の `KEYWORD_GROUPS` にも
  同じslugを追加してフィルタUIに反映させる。
- キーワードは小文字で判定しているので、追加時も小文字で書けばOK
  (マッチングはタイトル+要旨を小文字化してから部分一致で行う)。
- 新しいキーワードを追加したら、`python scripts/fetch_arxiv_historical.py` を
  再実行すると過去分も遡って拾い直せる(既存論文はmemoを保持したままタグだけ
  更新される)。

### 会議スクレイパーを追加する

1. `scripts/scrapers/新しい会議名.py` を作成し、`scrape() -> list[AwardPaper]` を実装する。
   実装方法は2通り:
   - **汎用パーサー**: `scripts/scrapers/base.py` の `make_award_scraper()` に
     会議名・URL・賞ラベルのキーワード辞書を渡すだけ(`iros.py` / `ieee_iv.py`参照)。
     見出しやリスト項目の中に賞のキーワードとリンクが同居しているシンプルな
     ページ向け。
   - **専用パーサー**: ページ構造が複雑な場合(テーブル、`Winner:`マーカー、
     `<h2>`区切りの複数段落など)は `AwardPaper` / `fetch_html` だけを使って
     独自にBeautifulSoupでパースする(`icra.py` / `cvpr.py` / `neurips.py` /
     `icml.py` / `aaai.py` / `rss.py` / `itsc.py` が実例)。
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
  `REQUEST_INTERVAL_SECONDS`)。arXiv APIのURLは必ず `https://` を使うこと
  (`http://` だと `https://` へのリダイレクトでハングすることがある)。
- 会議の受賞論文ページはURL・HTML構造が年ごとに変わるため、`scripts/scrapers/` 配下の
  各モジュールのURL・パーサーは毎年見直しが必要になる。現時点(2026年7月)では
  2026年の各カンファレンスがまだ開催されておらず受賞ページも存在しないため、
  全スクレイパーは **2025年開催回** を対象にしている。新しい年が開催され次第、
  各モジュールの `CONFERENCE_NAME` / `*_AWARDS_URL` を更新すること
  (年が変わってもページ構造自体はほぼ変わらないことが多いので、まずURLだけ
  差し替えて動作確認するとよい)。
  - 実データが取得できているのは ICRA / CVPR / NeurIPS / ICML / AAAI / RSS / ITSC の7会議。
  - IROS と IEEE IV は調査時点で安定した受賞結果ページを見つけられなかった
    (IROS はCall for Nominationsページのみで、かつサイト証明書が期限切れだった。
    IEEE IVはトップページ止まり)。見つかったらそれぞれ `iros.py` / `ieee_iv.py` の
    `*_AWARDS_URL` を差し替えること。
  - その場合でもスクレイパーは例外を出さず「0件」を返して処理を続行するだけなので、
    パイプライン自体は壊れない(`scripts/scrapers/base.py` の `make_award_scraper` が
    持つ最低文字数チェックにより、ナビゲーションリンクなどの誤検出も除外される)。
- `scripts/lib/store.py` の `merge_papers()` は、既存IDの論文でも `memo` /
  `memo_updated_at` 以外のフィールド(タグなど)は毎回最新の取得結果で上書きする。
  キーワードやパーサーを直しても再実行するだけで反映されるが、`memo` を手動編集した
  論文がスクリプトの再実行で消えることはない。
- 本構成は無料の範囲で完結するように設計されている(有料API・シークレットは不要)。
