# 2. 認証と認可 (Authentication & Authorization)

このドキュメントは、APIの認証（「あなたは誰か」）と認可（「あなたは何ができるか」）に関する共通の方式を定義します。

## 1. 認証方式 (Authentication Strategy)

**JSON Web Token (JWT)** を標準の認証方式として採用します。

* **ステートレス (Stateless):** JWTを利用することで、サーバー側でセッション情報を持つ必要がなくなり（ステートレス）、APIのスケールが容易になります。
* **署名 (Signature):** トークンはサーバーの秘密鍵によって署名されており、改ざんを検知できます。

## 2. トークンの流れ (Token Flow)

### A. トークンの発行 (Login)

1.  ユーザーは、ID（メールアドレスなど）とパスワードを **`/api/v1/auth/login`** のような専用エンドポイントに `POST` します。
2.  サーバーは資格情報（ID・パスワード）を検証します。
3.  検証が成功した場合、サーバーは署名付きの **`accessToken`**（アクセストークン）と、オプションで **`refreshToken`**（リフレッシュトークン）を生成し、JSONレスポンスで返します。

**レスポンス例:**
```json
{
  "accessToken": "ey...",
  "tokenType": "Bearer",
  "expiresIn": 3600,
  "refreshToken": "df..."
}