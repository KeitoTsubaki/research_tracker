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
  ├─ public/rss.xml を再生成してcommit (scripts/generate_rss.py)
  └─ 新着論文をSlack/メールに通知(任意, scripts/notify_new_papers.py)

[手動実行: 過去論文の一括バックフィル]
  └─ scripts/fetch_arxiv_historical.py が cooperative-transport キーワード群で
     arXivを2000年以降まで遡って検索(MARL手法を使っていない古典的な協調搬送
     研究も対象。crontabには乗せず、必要なときに手動実行する)

[GitHub Actions: Issue作成時]
  └─ サイトのメモ編集フォームから開いたIssueをパースし、data/papers.jsonの
     該当エントリのmemoを更新してcommit (.github/workflows/apply-memo.yml)

[静的サイト (Astro + Tailwind CSS, output: 'static')]
  ├─ data/papers.json をビルド時に読み込み、新着順(/, /2, /3, ...)と
  │  受賞順(/awards/, /awards/2, ...)の2系統×30件/ページで静的ページを生成
  │  (1ページに全件詰め込むと重くなるため; scripts/lib/papers.ts の PAGE_SIZE)
  ├─ /data.json として全論文データも静的出力し、検索・フィルタを使った瞬間だけ
  │  ブラウザがそれを1回だけ取得して全件横断で絞り込む(何も操作しなければ
  │  取得されないので、通常のページ閲覧は軽量なまま)
  ├─ カテゴリ・会議・キーワード・メモ有無・お気に入り・あとで読むで絞り込み、
  │  該当件数を "もっと見る" ボタンで追加読み込み
  ├─ お気に入り/あとで読むはブラウザのlocalStorageに保存(端末ごと、サーバー不要)
  ├─ メモ編集はGitHub Issue作成画面を開くリンクとして提供
  └─ GitHub Actionsでビルド& GitHub Pagesにデプロイ
```

## リポジトリ構成

```
/
├── .github/
│   ├── workflows/
│   │   ├── fetch-arxiv-daily.yml       # 毎日: arXiv収集 → commit → 通知
│   │   ├── fetch-conference-weekly.yml # 毎週: 会議受賞論文収集 → commit → 通知
│   │   ├── deploy-pages.yml            # push時: ビルド → GitHub Pagesデプロイ
│   │   └── apply-memo.yml              # Issue作成時: メモをpapers.jsonへ反映
│   └── ISSUE_TEMPLATE/
│       └── memo-update.yml             # メモ編集フォーム(サイトから自動入力)
├── scripts/
│   ├── fetch_arxiv.py               # 毎日: 新着論文を収集
│   ├── fetch_arxiv_historical.py    # 手動: 過去論文を一括バックフィル
│   ├── fetch_conference_awards.py
│   ├── generate_rss.py
│   ├── notify_new_papers.py         # 新着論文をSlack/メールに通知
│   ├── apply_memo_from_issue.py     # Issue本文をパースしてmemoを更新
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
├── src/                             # Astroプロジェクト本体
│   ├── pages/
│   │   ├── [...page].astro         # 新着順ページ(/, /2, /3, ...)
│   │   ├── awards/[...page].astro  # 受賞順ページ(/awards/, /awards/2, ...)
│   │   └── data.json.ts            # 全論文データのJSON出力(横断検索用、遅延取得)
│   ├── components/
│   │   ├── PaperListPage.astro     # 一覧ページの共通実装(フィルタ・ページング等)
│   │   └── PaperCard.astro         # カード1件分(お気に入り/あとで読む/メモ編集)
│   └── lib/papers.ts               # データ読込・ソート・PAGE_SIZE定義
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

### ページ分割・全件横断検索について

論文数が増えるにつれて1ページに全件表示すると重くなるため、`src/lib/papers.ts` の
`PAGE_SIZE`(デフォルト30件)ごとに静的ページを分割している。

- 新着順: `/`, `/2`, `/3`, ...(`src/pages/[...page].astro`)
- 受賞順: `/awards/`, `/awards/2`, ...(`src/pages/awards/[...page].astro`)
- 並び替えセレクタで「新着順⇔会議受賞順」を切り替えると、それぞれの1ページ目に
  遷移する(クライアント側での並べ替えではなくページ遷移)。
- 通常の閲覧(検索・フィルタ未使用)では、そのページの30件分のHTMLしか
  読み込まないので軽量。
- **検索・フィルタ(キーワード検索/カテゴリ/会議/タグ/メモ有無/お気に入り/
  あとで読む)のいずれかを使うと、全論文データ(`/data.json`, ビルド時に
  `src/pages/data.json.ts` から生成)を1回だけ取得し、全件を対象に絞り込む**。
  何も操作しなければ `/data.json` は取得されないので、通常の閲覧が重くなることはない。
  該当件数が多い場合は初回60件のみ描画し、「もっと見る」ボタンで追加描画する
  (`RESULTS_BATCH_SIZE`)。
- 全件データを毎回転送するので、論文数が数千〜数万件規模まで増えた場合は
  `/data.json` 自体が重くなる。その規模になったら、検索専用の軽量インデックス
  (要旨を除いたタイトル・著者・タグのみ等)に分けることを検討するとよい。
- 1ページあたりの件数を変えたい場合は `PAGE_SIZE` を編集するだけでよい
  (ページ数は自動的に再計算される)。

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

### メモ機能(GitHub Issue経由)

サイトは静的なのでブラウザから直接 `data/papers.json` を書き換えることはできないため、
GitHub Issueを仲介させる方式で実装している。

1. カードの「メモを編集」を開いてテキストを入力し、「GitHub Issueで保存」を押すと、
   `.github/ISSUE_TEMPLATE/memo-update.yml` フォームに論文ID・タイトル・メモ本文が
   事前入力された状態でGitHubのIssue作成画面が新しいタブで開く。
2. 内容を確認して「Submit new issue」を押す(GitHubへのログインが必要)。
3. `.github/workflows/apply-memo.yml` が `memo-update` ラベル付きIssueの作成を検知し、
   `scripts/apply_memo_from_issue.py` がIssue本文から論文ID・メモを抽出して
   `data/papers.json` の該当エントリを更新・commit・pushする。
4. 成功すればIssueに完了コメントが付いて自動クローズされる。失敗した場合
   (論文IDが一致しない等)はエラーコメントが付き、Issueは開いたままになる
   ので、内容を直して新しくIssueを作り直す。
5. サイトへの反映は次回の `deploy-pages.yml` 実行後(pushで自動トリガーされる)。

追加のシークレットやトークン設定は不要(`GITHUB_TOKEN` + `contents: write` /
`issues: write` で完結)。Issueの作成自体はGitHubにログインした任意のユーザーが
行えるので、荒らし対策をしたい場合はリポジトリを非公開にするか、
`apply-memo.yml` の条件に「Issue作成者がリポジトリのコラボレーターであること」
のチェックを追加するとよい。

### お気に入り / あとで読む機能

サーバーを持たない構成のため、ブラウザの `localStorage` に論文IDを保存する方式。
カード右上の ☆(お気に入り)/ 🔖(あとで読む)ボタンで切り替えられ、
フィルタバーの「お気に入りのみ」「あとで読むのみ」で絞り込める。

- 保存先はブラウザ単位(同じ端末・同じブラウザでのみ有効。別端末や別ブラウザ、
  シークレットモードでは共有されない。ブラウザの履歴削除で消える)。
- 複数端末で同期したい場合は、メモ機能と同様にGitHub Issue経由でJSONに
  書き戻す方式へ拡張できる(実装コストとのトレードオフでlocalStorageを初期実装とした)。

### 新着論文の通知(Slack / メール、任意)

`scripts/notify_new_papers.py` が `data/latest_new.json`(直近の収集で新規追加された
論文のID一覧)を読み、受賞論文とそれ以外に分けて通知メッセージを組み立てる。
毎日・毎週のワークフローで収集直後に自動実行されるが、**通知先を1つも設定しなければ
何もせず正常終了する**ので、有効化は任意。

有効化するには、リポジトリの Settings → Secrets and variables → Actions で
以下のいずれか(両方でも可)を設定する。

- **Slack**: [Incoming Webhook](https://api.slack.com/messaging/webhooks)(無料)を
  作成し、`SLACK_WEBHOOK_URL` シークレットにWebhook URLを設定する。
- **メール**: SMTPサーバーの情報を以下のシークレットに設定する
  (例: Gmailなら [アプリパスワード](https://support.google.com/accounts/answer/185833)
  を発行して使う。SMTPサーバーが使える無料メールサービスであれば他でもよい)。
  - `SMTP_HOST`(例: `smtp.gmail.com`)
  - `SMTP_PORT`(例: `587`)
  - `SMTP_USER`(送信元アドレス)
  - `SMTP_PASSWORD`(パスワード/アプリパスワード)
  - `NOTIFY_EMAIL_TO`(通知を受け取るメールアドレス)
- 任意で Settings → Secrets and variables → Actions → **Variables** タブに
  `SITE_URL` を設定すると、通知メッセージにサイトのURLが添えられる。

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
- 本構成は無料の範囲で完結するように設計されている。通知機能(Slack Webhook /
  メールSMTP)は追加のシークレット設定が必要だが、いずれも無料で使えるサービスの
  範囲で完結し、設定しなくてもパイプライン自体は問題なく動く。
