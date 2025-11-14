# 4. エラーハンドリング (Error Handling)

このドキュメントは、APIがエラー（4xxおよび5xxステータスコード）を返す際の、共通のJSONレスポンス形式を定義します。

## 1. 基本方針 (Base Principle)

1.  **HTTPステータスコードを正しく使う:**
    * `api_design.md` で定義されたHTTPステータスコード（`400`, `401`, `404`, `500`など）を、エラーの種別に応じて正確に返します。
2.  **詳細な情報はJSONボディで返す:**
    * クライアント（フロントエンド）がエラーの理由をプログラム的に処理したり、ユーザーに分かりやすく表示したりできるように、エラーの詳細をJSON形式で返します。

## 2. 共通エラーレスポンス形式 (Common Error JSON Structure)

クライアントエラー（`4xx`）およびサーバーエラー（`5xx`）は、以下のJSON構造をレスポンスボディとして返します。

```json
{
  "code": "unique_error_code",
  "message": "A human-readable explanation of what went wrong.",
  "details": [
    {
      "field": "field_name",
      "reason": "Specific reason why this field failed validation."
    }
  ]
}