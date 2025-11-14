# Engineering Playbook

## 🚀 このリポジトリの目的

このリポジトリは、私たちのチームにおける開発の「戦略書（Playbook）」です。

開発標準、設計思想、技術スタックごとの具体的な手順書を体系的にまとめることを目的としています。

最終的なゴールは、このPlaybookを**GitHub Copilotに「独自のルールブック」として読み込ませ**、開発作業を自動化することです。

---

## 🧭 このPlaybookの使い方 (AI利用パターン)

このPlaybookは、Copilotがあなたの開発手順を学習するための「教師データ」となります。

### 1. Copilot Chat での利用 (部分的な実装)

VS Codeのチャット機能で、特定の手順書（`.md`ファイル）を `#` で指定し、**部分的な実装**を依頼します。

**（例）**
> 「`#3_Tech_Stacks/python_fastapi/DEVELOPMENT_GUIDELINES.md` に従って、この関数のテストを書いて。」

### 2. Copilot Workspace での利用 (タスクの自動化)

Workspaceは、**GitHubのIssue（タスク）を起点**に動作します。

Workspaceを起動すると、AIは**このPlaybookリポジトリ全体を自動で読み込み**、ここに書かれた手順書（`DEVELOPMENT_GUIDELINES.md`など）を**最優先の指示**として扱います。

AIは、あなたのルールに従って「開発計画の立案」と「コードの自動実装」を**タスク単位で実行**してくれます。
