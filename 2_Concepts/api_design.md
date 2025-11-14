# 1. API設計原則 (API Design Principles)

このドキュメントは、私たちが開発するすべてのバックエンドAPIに共通する設計原則と規約を定義します。

## 1. 基本方針 (Base Principle)

**RESTful API** を基本方針として採用します。
リソース（Resource）ベースで設計し、HTTPメソッド（Verb）によって操作（Operation）を表現します。

## 2. エンドポイント (Endpoint / URI)

1.  **リソースは「名詞」の複数形:**
    * 良い例: `/users`, `/articles`, `/users/{user_id}/posts`
    * 悪い例: `/getUser`, `/createArticle`, `/user-post`
2.  **小文字とケバブケース (kebab-case):**
    * URIには小文字のみを使用します。単語の区切りが必要な場合は、アンダースコア (`_`) ではなくハイフン (`-`) を使用します。
    * 良い例: `/article-tags`
    * 悪い例: `/ArticleTags`, `/article_tags`
3.  **操作をURIに含めない:**
    * URIはリソースの場所を示すべきです。操作はHTTPメソッドで表現します。
    * 悪い例: `/users/create`, `/get-user-by-id`

## 3. HTTPメソッドの使い分け (HTTP Methods)

CRUD（Create, Read, Update, Delete）操作に以下のメソッドを正しく割り当てます。

* **`GET` (Read):** リソースの取得。
    * `/users` (一覧取得)
    * `/users/{id}` (個別取得)
* **`POST` (Create):** リソースの新規作成。
    * `/users` (新しいユーザーを作成)
* **`PUT` / `PATCH` (Update):** リソースの更新。
    * `PUT`: リソース全体の置換（例：ユーザーの全情報を更新）
    * `PATCH`: リソースの一部修正（例：ユーザーのニックネームだけ変更）
    * `/users/{id}`
* **`DELETE` (Delete):** リソースの削除。
    * `/users/{id}`

## 4. リクエスト (Requests)

1.  **ボディ (Body):** `POST`, `PUT`, `PATCH` で送信するデータは **JSON** 形式を基本とします。
2.  **クエリパラメータ (Query Params):**
    * `GET` での一覧取得時に、絞り込み（Filter）、並び順（Sort）、ページネーション（Pagination）のために使用します。
    * 例: `GET /articles?status=published&sort=-created_at&page=2`
3.  **認証 (Authentication):**
    * 認証が必要なAPIは、`Authorization` HTTPヘッダー（例: `Bearer [TOKEN]`）で認証情報を要求します。
    * （詳細は `authentication.md` を参照）

## 5. レスポンス (Responses)

1.  **ボディ (Body):**
    * レスポンスも **JSON** 形式を基本とします。
    * データは `data` キーに格納し、ページネーション情報などは `meta` キーに含めるなど、構造を統一します。（JSend規約など）
2.  **HTTPステータスコード (Status Codes):**
    * 操作の結果をステータスコードで正確に返します。
    * **`200 OK`**: `GET` の成功、`PUT`/`PATCH` の成功（更新完了）。
    * **`201 Created`**: `POST` の成功（新規作成完了）。
    * **`204 No Content`**: `DELETE` の成功（レスポンスボディなし）。
    * **`400 Bad Request`**: リクエストのバリデーションエラー（例：必須項目が欠けている）。
    * **`401 Unauthorized`**: 認証エラー（トークンがない、または無効）。
    * **`403 Forbidden`**: 認可エラー（権限がない）。
    * **`404 Not Found`**: リソースが見つからない。
    * **`500 Internal Server Error`**: サーバー側の予期せぬエラー。
3.  **エラーレスポンス (Error Response):**
    * `4xx` や `5xx` のエラー時は、エラーの理由がわかるJSONを返します。
    * （詳細は `error_handling.md` を参照）

## 6. バージョニング (Versioning)

将来の破壊的変更に備え、APIのバージョンをURIに含めます。

* 例: `/api/v1/users`