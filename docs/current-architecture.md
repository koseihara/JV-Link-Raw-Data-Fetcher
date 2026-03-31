# 現状アーキテクチャ整理

## このアプリケーションが行うこと

このアプリケーションは、JRA-VAN JV-Link から raw ファイルを取得し、そのまま `.jvdat` として保存する downloader です。
責務は次の 4 つに限定します。

- `download`: JV-Link から dataspec ごとに raw ファイルを取得する
- `resume`: 中断した run を再開する
- `verify`: 公開済み snapshot と object の整合性を検証する
- `publish view`: 人が見やすい `view/current/...` を公開する

このリポジトリは parser ではありません。PostgreSQL への保存も責務に含めません。
別の parser アプリケーションが、この downloader が残した raw ファイルを読み取る前提です。

## 現在のデータフロー

1. CLI が `setup` または `update` を受け付ける
2. `job_runner.py` が dataspec 単位で run を開始する
3. `jvlink_session.py` が `JVInit -> JVSetSavePath -> JVOpen -> JVStatus -> JVRead` を扱う
4. `raw_writer.py` が取得中データを `runs/<run_id>/staging` に書き出す
5. `job_state.py` が `last_completed_filename` などの再開用状態を保持する
6. `archive_store.py` が staging を object 化し、`commits/<commit_id>` を確定する
7. `refs/current.json` を更新して公開中 snapshot を切り替える
8. `view/current/<format_code>/...` を再生成する
9. `verify` が `refs / commits / objects / runs` の整合性を検証する

## 現在の公開面

後段の parser に対する公開契約は、次の 3 つです。

- `view/current/<format_code>/<logical_filename>.jvdat`
- `refs/current.json`
- `commits/<commit_id>/manifest.jsonl`

`objects/` は内部実装です。後段アプリは依存しない前提です。

## モジュール責務

- `main.py`
  - package CLI への互換 shim
- `jv_link_raw_data_fetcher/cli.py`
  - CLI、引数解析、ログ設定、コマンド振り分け
- `jv_link_raw_data_fetcher/app_config.py`
  - user config の保存と既定値解決
- `jv_link_raw_data_fetcher/platform.py`
  - Windows / 32bit / pywin32 / COM / 書込権限の診断
- `job_runner.py`
  - dataspec 実行オーケストレーション
- `jvlink_session.py`
  - JV-Link COM 境界
- `raw_writer.py`
  - staging への raw ファイル書き込み
- `job_state.py`
  - run 再開用の状態管理
- `archive_store.py`
  - snapshot / objects / view / verify の中核
- `config.py`
  - dataspec、JVOpen option、encoding の定数

## 技術的負債

### 1. core / storage / platform の一部がまだ root module に残っている

package CLI は導入済みですが、`job_runner.py` と `archive_store.py` はまだ root module です。
将来的には package 内へ寄せて、依存方向をより明確にする余地があります。

### 2. 公開契約は事実上存在するが、schema version をまだ持っていない

`current.json` と `manifest.jsonl` はすでに実質的な handoff 契約ですが、明示的な version field はまだありません。

### 3. 実 COM を使う自動テストは未整備

fake session を使った Python テストはありますが、JV-Link 実機環境の acceptance は手動確認が必要です。

## 位置づけ

この repo の目標は、Windows / x86 / JV-Link 環境で raw ファイルを取得できる OSS downloader を提供することです。
v1 の責務は次に限定します。

- raw 取得
- 整合性検証
- 再開
- 人間向け view 公開

次はこの repo の責務に含めません。

- parser
- schema 解釈
- PostgreSQL への保存
