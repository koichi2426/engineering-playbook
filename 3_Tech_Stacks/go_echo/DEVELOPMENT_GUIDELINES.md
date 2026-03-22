# Reso Backend 実装固定仕様書（AI開発テンプレート）

この文書は、Reso_backend のバックエンド開発を AI に実行させるための固定仕様です。
目的は「実装の揺れをなくすこと」です。

- この仕様書のキーワード `MUST` は必須です。
- この仕様書のキーワード `MUST NOT` は禁止です。
- 明記されていない最適化・抽象化・拡張は `MUST NOT` です。

---

## 1. プロジェクト前提（固定）

- 言語: Go
- モジュール: `app`
- HTTP フレームワーク: Echo v4
- DB: PostgreSQL + PostGIS
- マイグレーション: Atlas
- アーキテクチャ: Clean Architecture（Domain / Usecase / Adapter / Infrastructure）

ルート構成（固定）:

```text
Reso_backend/
├─ atlas.hcl
├─ docker-compose.yml
├─ README.md
├─ gid.md
└─ app/
   ├─ Dockerfile
   ├─ go.mod
   ├─ migrations/
   │  └─ 001_init.sql
   └─ src/
      ├─ main.go
      ├─ adapter/
      │  ├─ controller/
      │  └─ presenter/
      ├─ domain/
      │  ├─ entities/
      │  ├─ services/
      │  └─ value_objects/
      ├─ infrastructure/
      │  ├─ database/postgres/
      │  ├─ domain_impl/services/
      │  ├─ router/
      │  └─ storage/
      └─ usecase/
```

---

## 2. 最上位ルール（必ず守る）

### 2.1 変更スコープ

- 依頼された機能達成に必要な最小ファイルのみ変更すること（MUST）。
- 既存の公開 API（エンドポイント、JSON キー名、主要 DTO 名）を勝手に変更しないこと（MUST）。
- 依頼されていない新規レイヤ・新規共通化・新規抽象化を追加しないこと（MUST NOT）。

### 2.2 依存方向

- `usecase` は `domain` のみ参照すること（MUST）。
- `usecase` から `adapter` / `infrastructure` を import しないこと（MUST NOT）。
- `domain` はフレームワーク依存しないこと（MUST）。

### 2.3 命名・配置

- 既存命名規則 `snake_case` ファイル名 + `NewXxx...` コンストラクタを踏襲すること（MUST）。
- コントローラーは `app/src/adapter/controller/*_controller.go` に配置すること（MUST）。
- プレゼンターは `app/src/adapter/presenter/*_presenter.go` に配置すること（MUST）。
- ユースケースは `app/src/usecase/*.go` に配置し、同名 `_test.go` を作ること（MUST）。

### 2.4 既存スタイル維持

- VO から値を取り出すときは `String()`, `Value()`, `Int()`, `Float64()` を使用すること（MUST）。
- エラーは `fmt.Errorf("context: %w", err)` でラップする既存流儀を優先すること（MUST）。
- `context.Context` は controller -> usecase -> repository へ受け渡すこと（MUST）。

---

## 3. レイヤ責務（固定）

### 3.1 Domain 層

配置:
- `app/src/domain/entities/`
- `app/src/domain/value_objects/`
- `app/src/domain/services/`

責務:
- Entity と VO の不変条件管理
- Repository / Domain Service interface 定義

禁止:
- Echo, SQL ドライバ, JWT ライブラリなどの技術依存を入れること

### 3.2 Usecase 層

配置:
- `app/src/usecase/`

責務:
- アプリケーションの操作フローを定義
- Input / Output DTO 定義
- Presenter interface 定義
- Interactor 実装

必須構造:
- `XxxInput`
- `XxxOutput`（必要なら中間 Payload 構造体）
- `XxxPresenter` interface
- `XxxUseCase` interface
- `xxxInteractor` struct
- `NewXxxInteractor(...)`
- `Execute(ctx context.Context, input XxxInput) (..., error)`

### 3.3 Adapter 層

配置:
- `app/src/adapter/controller/`
- `app/src/adapter/presenter/`

責務:
- Controller: HTTP -> Usecase Input 変換
- Presenter: Domain/Usecase data -> JSON DTO 整形

固定動作:
- Controller は `c.Bind` または `c.QueryParam` で入力を取得
- 認証が必要な API は `Authorization: Bearer <token>` を明示処理
- HTTP ステータスは既存 API 契約を維持

### 3.4 Infrastructure 層

配置:
- `app/src/infrastructure/database/postgres/`
- `app/src/infrastructure/domain_impl/services/`
- `app/src/infrastructure/router/`

責務:
- Repository 実装
- Domain Service 実装（JWT 発行/検証、推薦アルゴリズムの具体化）
- ルーティングと手動 DI

固定動作:
- ルーティング初期化は `router.InitRoutes(e, db)`
- 依存注入順序は「Repository -> DomainImplService -> Presenter -> Usecase -> Controller」

---

## 4. API 契約（現行固定）

この章は現行実装と一致させること。AI は勝手に変更してはいけない。

### 4.1 POST /v1/auth/login

Request JSON:

```json
{
  "username": "string",
  "password": "string"
}
```

Response 200:

```json
{
  "token": "jwt"
}
```

Error:
- 400: `{"error":"Invalid request body"}`
- 401: `{"error":"..."}`

### 4.2 POST /v1/users/signup

Request JSON:

```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

Response 201:

```json
{
  "id": 1,
  "token": "jwt"
}
```

Error:
- 400: `{"error":"Invalid request body"}`
- 500: `{"error":"..."}`

### 4.3 PUT /v1/mesh/spots

Header:
- `Authorization: Bearer <token>`

Request JSON:

```json
{
  "spot_name": "string",
  "latitude": 35.0,
  "longitude": 139.0,
  "image_url": "string",
  "caption": "string",
  "overwrite": false
}
```

Response 200（概形）:

```json
{
  "message": "post created",
  "has_existing_info": false,
  "spot": {
    "id": 1,
    "name": "string",
    "mesh_id": "string",
    "location": {
      "latitude": 35.0,
      "longitude": 139.0
    }
  },
  "post": {
    "id": 1,
    "user_name": "string",
    "image_url": "string",
    "caption": "string",
    "posted_at": "RFC3339"
  }
}
```

Error:
- 401: `{"error":"Missing or invalid authorization header"}`
- 400: `{"error":"Invalid request body"}`
- 409: `{"error":"..."}`

### 4.4 GET /v1/recommendation/distill

Header:
- `Authorization: Bearer <token>`

Query:
- `latitude` (required)
- `longitude` (required)

Response 200（概形）:

```json
{
  "recommendation": {
    "spot": {
      "id": 1,
      "name": "string",
      "mesh_id": "string",
      "location": {
        "latitude": 35.0,
        "longitude": 139.0
      }
    },
    "distillation_analysis": {
      "resonance_score": 0,
      "density_score": 0,
      "total_score": 0.0,
      "reason": "string"
    },
    "posts": [
      {
        "id": 1,
        "user_name": "string",
        "caption": "string",
        "image_url": "string",
        "posted_at": "RFC3339"
      }
    ]
  }
}
```

Error:
- 401: 認証不備/認証失敗
- 400: 緯度経度パラメータ不備/形式不正
- 404: `{"message":"No recommendation found in your resonance circle"}`

### 4.5 GET /v1/users/me/spots

Header:
- `Authorization: Bearer <token>`

Response 200（概形）:

```json
{
  "user_spots": [
    {
      "spot": {
        "id": 1,
        "name": "string",
        "mesh_id": "string",
        "location": {
          "latitude": 35.0,
          "longitude": 139.0
        }
      },
      "post": {
        "id": 10,
        "user_name": "string",
        "image_url": "string or null",
        "caption": "string",
        "posted_at": "RFC3339"
      }
    }
  ]
}
```

Error:
- 401: `{"error":"Missing or invalid authorization header"}` または認証エラー

---

## 5. RegisterSpotPost の業務ルール（固定）

このユースケースは分岐が複雑なため、以下を固定仕様とする。

1. `mesh_id` を座標から計算する。
2. ユーザー自身の同一メッシュ投稿を検索する。
3. `overwrite=false` かつ同一メッシュ投稿あり:
- 新規投稿を作らず、既存 Spot 情報とユーザー最新 Post を返す。
4. `overwrite=true`:
- 入力座標の Spot を再解決（なければ作成）。
- その Spot 上の「自分の既存投稿」を削除。
- 新規投稿を 1 件だけ作成。
5. ユーザー自身の同一メッシュ投稿なし:
- 同一座標 Spot があれば合流。
- なければ Spot 新規作成後に投稿。

注意:
- `has_existing_info` は既存情報の有無を正しく反映する。
- `posted_at` は RFC3339 文字列として返す。

---

## 6. DB 仕様（固定）

`app/migrations/001_init.sql` を正とする。

主要テーブル:
- `users`
- `spots`
- `posts`

固定ポイント:
- PostGIS 拡張を利用する。
- `spots.location` は `GEOGRAPHY(POINT,4326)`。
- 同一座標一意制約（`ST_X`, `ST_Y`）を維持する。
- `posts.image_url` は NULL 許容。

---

## 7. 新規 API 追加手順（必須ワークフロー）

AI は以下の順序で実装すること。

1. Domain 変更の要否確認
- 新しい Entity/VO/Repository method が必要かだけ判断
- 不要なら Domain は触らない

2. Usecase 作成
- `app/src/usecase/<feature>.go`
- Input/Output/Presenter interface/UseCase interface/Interactor/Execute を作成

3. Presenter 作成
- `app/src/adapter/presenter/<feature>_presenter.go`
- Usecase Output へ正規化

4. Controller 作成
- `app/src/adapter/controller/<feature>_controller.go`
- HTTP 入力を Usecase Input へ変換

5. Infrastructure 実装
- 必要時のみ `postgres/*_repository.go` と `domain_impl/services/*` を実装/拡張

6. Router 接続
- `app/src/infrastructure/router/echo.go` に DI と route を追加

7. テスト作成
- `app/src/usecase/<feature>_test.go` を作成/更新
- 正常系/異常系を最低 1 件ずつ追加

---

## 8. テスト規約（固定）

### 8.1 単体テスト対象

- 最優先: Usecase
- 必要に応じて Presenter / Domain VO

### 8.2 テスト方針

- `testify/assert` + `testify/mock` を使用。
- 依存はモック化し、Usecase の分岐を検証する。
- 異常系は「どこで失敗したか」が分かる assertion を記述する。

### 8.3 既知の注意点（再発防止）

- `entities.NewUser` などのコンストラクタ error を無視しない。
- フィクスチャの hashed password は妥当値を使う（例: `"hashed_password"`）。
- `RegisterSpotPost` の overwrite 分岐は競合しやすいので、
  `overwrite=true/false` を別ケースで明示テストする。

### 8.4 テスト実行コマンド

```bash
cd app
go test -v ./src/usecase/...
```

必要に応じて:

```bash
go test -v ./src/usecase/ -run TestRegisterSpotPost
```

---

## 9. 実装時の禁止事項

- 要求外のパッケージ追加（MUST NOT）
- 要求外の DB スキーマ変更（MUST NOT）
- 既存 API の JSON キー名変更（MUST NOT）
- 認証方式（Bearer JWT）の変更（MUST NOT）
- 一括リファクタなど広範囲変更（MUST NOT）

---

## 10. AI 作業完了条件（Definition of Done）

以下をすべて満たした場合のみ完了とする。

1. 実装した機能が本仕様のレイヤ責務に違反していない。
2. 追加/変更 API が既存契約を壊していない。
3. 追加/変更した Usecase に対応する `_test.go` が存在する。
4. `go test -v ./src/usecase/...` が通る（少なくとも変更箇所関連）。
5. 変更理由を「何を」「なぜ」「どこで」説明できる。

---

## 11. 他AIへ渡す実行プロンプト（コピペ用）

以下を他 AI への冒頭指示に使うこと。

```text
あなたは Reso_backend のバックエンド実装者です。
最優先で gid.md を順守してください。

ルール:
- gid.md の MUST/MUST NOT に従うこと
- 依頼スコープ外の変更をしないこと
- Clean Architecture の依存方向を守ること
- 既存 API 契約（path, method, JSON keys, status）を壊さないこと
- 実装後に usecase テストを追加/更新すること

出力形式:
1. 変更したファイル一覧
2. 実装内容（要点）
3. テスト内容
4. 残課題（なければ「なし」）
```

この仕様書と既存コードが矛盾する場合は、既存コードを正としてこの仕様書を更新してから実装すること。
