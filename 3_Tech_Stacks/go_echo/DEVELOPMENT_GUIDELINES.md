# 開発ガイドライン（テンプレート）

この文書は任意の API サービス実装で再利用できる汎用的な「開発ガイドライン（テンプレート）」です。
このリポジトリ内にある `reso`（Reso_backend）は本ドキュメントの例として使われている実装の一例にすぎません。
ガイドラインはプロジェクトごとに調整可能ですが、ここに示す慣習や責務分離は一貫性を保つための参考規約として機械的に守ることを推奨します。

- 本ドキュメント中の `MUST` は必須、`MUST NOT` は禁止を意味します。
- 明記のない最適化や抽象化は、チーム合意がない限り追加しないことを推奨します（原則として保守性優先）。

---

## 1. 目的と適用範囲

- 目的: 実装の一貫性を高め、レビュー・自動化・AI支援による変更の安全性を担保すること。
- 適用範囲: 言語やフレームワークに依存しないルールを優先しつつ、実例としてこのリポジトリの `reso` 実装（Go + Echo + PostgreSQL など）を参照しています。
- 注意: 実プロジェクトでは要件に応じて技術スタックやディレクトリ構成を柔軟に調整してください。

---

## 2. 最上位ルール（必須ガイドライン）

### 2.1 変更スコープ

- 依頼された機能達成に必要最小限の変更に留める（MUST）。
- 既存の公開 API（エンドポイント、JSON スキーマ、主要 DTO 名）を勝手に変更しない（MUST）。
- 新規レイヤ追加や大規模な共通化は、設計合意を得てから行う（MUST NOT：合意なし）。

### 2.2 依存方向（アーキテクチャ原則）

- ユースケース層はドメイン層に依存し、インフラやフレームワークには依存させない（例: Usecase -> Domain）（MUST）。
- ドメイン層は技術的依存（フレームワーク、DB ドライバ等）を持たない（MUST）。

（具体的なフォルダ名・パスはプロジェクトの慣習に合わせて調整可）

### 2.3 命名・配置（慣習）

- ファイル命名やコンストラクタの慣習をチームで定め、それを踏襲すること（MUST）。
- 例: Go プロジェクトでは `snake_case` ファイル名 + `NewXxx` コンストラクタを用いることが多い。

#### 2.3.1 ファイル命名と配置（具体例）

以下はこのリポジトリ（`reso`）で使われている具体的な慣習です。他プロジェクトでも参考になるため例として残します。

- ルート例（参考）:

```text
Reso_backend/
└─ app/
   └─ src/
      ├─ main.go
      ├─ adapter/
      │  ├─ controller/*_controller.go
      │  └─ presenter/*_presenter.go
      ├─ domain/
      │  ├─ entities/*.go
      │  ├─ services/*.go
      │  └─ value_objects/*.go
      ├─ infrastructure/
      │  ├─ database/postgres/*_repository.go
      │  ├─ domain_impl/services/*_impl.go
      │  └─ router/echo.go
      └─ usecase/*_usecase.go
```

- 命名例:
  - コントローラ: `register_spot_post_controller.go`
  - プレゼンター: `register_spot_post_presenter.go`
  - ユースケース: `register_spot_post.go` と `register_spot_post_test.go`
  - リポジトリ実装: `user_repository.go`, `spot_repository.go`

これらはあくまで「例」です。プロジェクト方針があればそちらを優先してください。

### 2.4 エラーハンドリング / コンテキスト

- エラーは適切にラップして伝搬する（例: `fmt.Errorf("...: %w", err)`）。
- `context.Context` は外部入力のライフサイクルに合わせて上位から下位へ受け渡す。

---

## 3. レイヤ責務（推奨パターン）

以下は Clean Architecture に沿った責務分離の例です。プロジェクトに合わせて緩やかに採用してください。

### 3.1 Domain 層

- 責務: Entity と VO の不変条件、ドメインルール、Repository / Domain Service のインターフェース定義。
- 禁止: フレームワークや DB ドライバへの依存注入をドメイン層に持ち込まない。

### 3.2 Usecase 層

- 責務: アプリケーションの操作フロー、Input/Output DTO、Presenter インターフェース、Interactor 実装。
- 必須構成例: `XxxInput`, `XxxOutput`, `XxxPresenter` interface, `XxxUseCase` interface, `xxxInteractor` struct, `Execute(ctx, input)` メソッド。

### 3.3 Adapter 層（インターフェース適合）

- 責務: HTTP/CLI/Batch など外部との入出力を Usecase の Input/Output に変換する。
- 例: Controller は HTTP リクエストを Bind/Validate し Usecase Input を生成、Presenter は Usecase Output を HTTP レスポンスへ整形。

### 3.4 Infrastructure 層

- 責務: Repository 実装、外部サービス統合、ルーティング初期化、依存注入の組み立て。

---

## コード例（Go）

以下は他のAIやエンジニアが実装例を理解しやすくするための簡易コード例です。細部はプロジェクトに合わせて調整してください。

Usecase（Interactor）の簡易例:

```go
type RegisterSpotPostInput struct {
  SpotName  string
  Latitude  float64
  Longitude float64
  ImageURL  string
  Caption   string
  Overwrite bool
}

type RegisterSpotPostOutput struct {
  Message string
}

type RegisterSpotPostPresenter interface {
  Present(ctx context.Context, out RegisterSpotPostOutput) error
}

type RegisterSpotPostUseCase interface {
  Execute(ctx context.Context, in RegisterSpotPostInput) (RegisterSpotPostOutput, error)
}

type registerSpotPostInteractor struct {
  repo      SpotRepository
  presenter RegisterSpotPostPresenter
}

func NewRegisterSpotPostInteractor(r SpotRepository, p RegisterSpotPostPresenter) RegisterSpotPostUseCase {
  return &registerSpotPostInteractor{repo: r, presenter: p}
}

func (it *registerSpotPostInteractor) Execute(ctx context.Context, in RegisterSpotPostInput) (RegisterSpotPostOutput, error) {
  // ビジネスロジック（略）
  return RegisterSpotPostOutput{Message: "post created"}, nil
}
```

Presenter（HTTP 変換）の簡易例:

```go
type HTTPRegisterSpotPostPresenter struct{
  c echo.Context
}

func (p *HTTPRegisterSpotPostPresenter) Present(ctx context.Context, out RegisterSpotPostOutput) error {
  return p.c.JSON(http.StatusOK, out)
}
```

Controller（Echo ハンドラ）簡易例:

```go
func RegisterSpotPostController(u RegisterSpotPostUseCase) echo.HandlerFunc {
  return func(c echo.Context) error {
    var req RegisterSpotPostInput
    if err := c.Bind(&req); err != nil {
      return c.JSON(http.StatusBadRequest, map[string]string{"error":"Invalid request body"})
    }
    out, err := u.Execute(c.Request().Context(), req)
    if err != nil {
      return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
    }
    return c.JSON(http.StatusOK, out)
  }
}
```

Repository インターフェースの例:

```go
type SpotRepository interface {
  FindByMesh(ctx context.Context, meshID string) (*Spot, error)
  Create(ctx context.Context, s *Spot) error
}
```

---

---

## 4. API 契約と変更方針（重要）

- 既存 API の契約は破壊的変更を避ける（MUST）。
- 新しい API を追加する場合はスキーマ・ステータスコード・エラーフォーマットを仕様化してから実装する。
- `reso` の実装は具体例としていくつかのエンドポイント契約を示していますが、それらはプロジェクト固有の仕様として扱ってください。

（プロジェクトに合わせた例: login, signup, post 登録, 推薦 API 等 — 詳細は該当実装を参照）

---

## 5. ユースケース設計上の注意（例示）

- 特に分岐が多いユースケースは、まずドメインルールと期待出力を明確化する。
- 例として `RegisterSpotPost` のようなケースでは、既存情報の有無や overwrite フラグに基づく振る舞いをテストで明確化すること。

（実際の振る舞いは実装例 `reso` を参照の上、プロジェクト要件に合わせて調整）

---

## 6. DB・マイグレーション（運用上の注意）

- DB スキーマはマイグレーションファイルを単一の信頼できるソースとして管理する。
- 地理空間データを扱う場合は PostGIS 等の拡張を明示し、戻せるマイグレーションを用意する。

---

## 7. 新規 API 追加ワークフロー（推奨手順）

1. 影響範囲の確認（Domain 変更が必要かを判断）。
2. Usecase の作成（Input/Output/Presenter/Interactor）。
3. Presenter の作成（API スキーマへの整形）。
4. Controller の作成（HTTP 入力のバリデーションと Usecase 呼び出し）。
5. 必要であれば Infrastructure に Repository/Service 実装を追加。
6. ルーティングと DI の接続。
7. 単体テスト・結合テストの追加と CI での検証。

### 7.1 詳細手順（ファイル作成・配置の具体例）

以下は「新しい API（例: RegisterSpotPost）」を追加する際に作成/編集するファイルの具体例と最小テンプレートです。プロジェクトの命名規則に合わせて `<feature>` を置き換えてください。

1) Domain（必要な場合）
   - ファイル: `app/src/domain/entities/<feature>.go`
   - 内容: Entity 構造体とコンストラクタ（不変条件チェック）

```go
package entities

type Spot struct {
  ID       int64
  Name     string
  MeshID   string
}

func NewSpot(name, meshID string) (*Spot, error) {
  // バリデーション
  return &Spot{Name: name, MeshID: meshID}, nil
}
```

2) Repository インターフェース
   - ファイル: `app/src/domain/services/<feature>_repository.go` または `app/src/domain/repository/<feature>_repository.go`

```go
package services

import "context"

type SpotRepository interface {
  FindByMesh(ctx context.Context, meshID string) (*Spot, error)
  Create(ctx context.Context, s *Spot) error
}
```

3) Usecase（ビジネスロジック）
   - ファイル: `app/src/usecase/<feature>.go`
   - 必要要素: `Input`, `Output`, `Presenter` interface, `UseCase` interface, `interactor`, `New...`、`Execute`

```go
package usecase

import "context"

type RegisterSpotPostInput struct { /* ... */ }
type RegisterSpotPostOutput struct { Message string }

type RegisterSpotPostPresenter interface { Present(ctx context.Context, out RegisterSpotPostOutput) error }
type RegisterSpotPostUseCase interface { Execute(ctx context.Context, in RegisterSpotPostInput) (RegisterSpotPostOutput, error) }

type registerSpotPostInteractor struct {
  repo SpotRepository
  p    RegisterSpotPostPresenter
}

func NewRegisterSpotPostInteractor(r SpotRepository, p RegisterSpotPostPresenter) RegisterSpotPostUseCase {
  return &registerSpotPostInteractor{repo: r, p: p}
}

func (it *registerSpotPostInteractor) Execute(ctx context.Context, in RegisterSpotPostInput) (RegisterSpotPostOutput, error) {
  // ロジック
  return RegisterSpotPostOutput{Message: "ok"}, nil
}
```

4) Presenter（Adapter）
   - ファイル: `app/src/adapter/presenter/<feature>_presenter.go`

```go
package presenter

import ("net/http" "github.com/labstack/echo/v4")

type HTTPRegisterSpotPostPresenter struct { c echo.Context }

func (p *HTTPRegisterSpotPostPresenter) Present(ctx context.Context, out usecase.RegisterSpotPostOutput) error {
  return p.c.JSON(http.StatusOK, out)
}
```

5) Controller（Adapter）
   - ファイル: `app/src/adapter/controller/<feature>_controller.go`

```go
package controller

import ("net/http" "github.com/labstack/echo/v4")

func RegisterSpotPostController(u usecase.RegisterSpotPostUseCase) echo.HandlerFunc {
  return func(c echo.Context) error {
    var req usecase.RegisterSpotPostInput
    if err := c.Bind(&req); err != nil {
      return c.JSON(http.StatusBadRequest, map[string]string{"error":"Invalid request body"})
    }
    out, err := u.Execute(c.Request().Context(), req)
    if err != nil {
      return c.JSON(http.StatusInternalServerError, map[string]string{"error":err.Error()})
    }
    return c.JSON(http.StatusOK, out)
  }
}
```

6) Infrastructure - Repository 実装
   - ファイル: `app/src/infrastructure/database/postgres/<feature>_repository.go`

```go
package postgres

import ("context" "database/sql")

type spotRepository struct { db *sql.DB }

func NewSpotRepository(db *sql.DB) SpotRepository { return &spotRepository{db: db} }

func (r *spotRepository) FindByMesh(ctx context.Context, meshID string) (*entities.Spot, error) {
  // SQL 実装
  return nil, nil
}
```

7) Router 接続
   - ファイル: `app/src/infrastructure/router/echo.go` にルート登録を追加

```go
e.POST("/v1/mesh/spots", controller.RegisterSpotPostController(interactor))
```

8) テスト（Usecase）
   - ファイル: `app/src/usecase/<feature>_test.go`
   - テンプレート: `testify` を使ったモックと正常/異常ケース

```go
package usecase_test

import ("testing" "github.com/stretchr/testify/assert")

func TestRegisterSpotPost_Success(t *testing.T) {
  // モックを用意して Execute を呼ぶ
  assert.True(t, true)
}
```

9) テスト実行コマンド

```bash
cd app
go test -v ./src/usecase/...
```

---

この節は「テンプレート」かつ最小実装例です。実装の際はエラーハンドリング、ログ、トランザクション、入力バリデーション、権限チェック、タイムアウト制御（context）を必ず追加してください。

---

## 8. 補足 — `reso` 実装について

- このリポジトリに含まれる `reso`（Reso_backend）は本ガイドの「具体例」として参照できます。実装パターンやテストの書き方、ディレクトリ構成の例として活用して構いません。
- ただし、`reso` 固有の命名や API 契約は他プロジェクトにそのまま適用するべきではなく、プロジェクト要件に合わせて方針を決めてください。

---

必要ならこのテンプレートを基に、あなたのプロジェクト用にカスタマイズした `DEVELOPMENT_GUIDELINES.md` を作成します。どの部分を固定にして、どの部分を可変にしたいか指示してください。
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
