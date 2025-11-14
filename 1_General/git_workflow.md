# 1. Gitワークフロー (Git Workflow)

このドキュメントは、私たちのリポジトリにおけるGitのブランチ戦略とコミット規約を定義します。

## 1. 基本戦略 (Base Strategy)

私たちは「GitHub Flow」を基本戦略として採用します。

1.  `main` ブランチは常にデプロイ可能な状態（Production Ready）を維持します。
2.  `main` ブランチへの直接の `push` は禁止します。
3.  すべての作業は `feature` ブランチ（トピックブランチ）で行います。
4.  作業が完了したら、`main` ブランチに対して `Pull Request (PR)` を作成します。
5.  コードレビューで1名以上の `Approve` (承認) を得た後、`main` に `merge` します。

## 2. ブランチ命名規則 (Branch Naming Convention)

ブランチ名は、作業内容が明確にわかるように命名します。

* **フォーマット:** `[type]/[issue-number]-[short-description]`
* `[type]` の種類:
    * `feature`: 新機能の実装 (例: `feature/101-add-user-api`)
    * `fix`: バグ修正 (例: `fix/102-fix-login-bug`)
    * `refactor`: リファクタリング (例: `refactor/103-optimize-db-query`)
    * `docs`: ドキュメントの修正 (例: `docs/104-update-readme`)

## 3. コミットメッセージ規約 (Commit Message Convention)

コミットメッセージは「Conventional Commits」の規約に従います。
これにより、変更履歴の可読性が向上し、将来的なリリースノートの自動生成も可能になります。

* **フォーマット:** `[type]([scope]): [subject]`
* `[type]` の種類:
    * `feat`: 新機能（`feature`）
    * `fix`: バグ修正
    * `refactor`: 仕様変更のないコード修正
    * `docs`: ドキュメント
    * `style`: コードフォーマット（インデント、typo修正など）
    * `test`: テストコードの追加・修正
    * `chore`: ビルドプロセスや補助ツールの変更（雑務）

* **良い例:**
    * `feat(api): add user registration endpoint`
    * `fix(db): correct typo in user model`
    * `docs(readme): update setup instructions`

## 4. Pull Request (PR) のルール

1.  **Small PR:** PRは可能な限り小さく、単一の関心事に集中させてください。
2.  **明確な説明:** PRの説明欄には、Issue番号と「何を」「なぜ」変更したかを明確に記述します。
3.  **セルフレビュー:** PRを作成したら、まず自分自身でコードレビューを行い、不要なファイルやデバッグコードが残っていないか確認してください。