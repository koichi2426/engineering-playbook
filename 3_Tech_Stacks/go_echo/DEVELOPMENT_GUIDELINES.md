# プロジェクト構成と開発ガイドライン Go Echo Atlas版

このドキュメントはフォルダ構成と新規API追加の標準的な開発手順を1つにまとめたものです。クリーンアーキテクチャの4層に基づき配置場所と手順の両方をここで参照できます。以前の内容をより詳細に、かつGoエコシステムに合わせた完全版として再構築しました。

## 目次

* [プロジェクト構成の概要](https://www.google.com/search?q=%23%E3%83%97%E3%83%AD%E3%82%B8%E3%82%A7%E3%82%AF%E3%83%88%E6%A7%8B%E6%88%90%E3%81%AE%E6%A6%82%E8%A6%81)
* [ルートのフォルダ構成](https://www.google.com/search?q=%23%E3%83%AB%E3%83%BC%E3%83%88%E3%81%AE%E3%83%95%E3%82%A9%E3%83%AB%E3%83%80%E6%A7%8B%E6%88%90)
* [src配下のフォルダ構成](https://www.google.com/search?q=%23src%E9%85%8D%E4%B8%8B%E3%81%AE%E3%83%95%E3%82%A9%E3%83%AB%E3%83%80%E6%A7%8B%E6%88%90)
* [各ディレクトリの責務](https://www.google.com/search?q=%23%E5%90%84%E3%83%87%E3%82%A3%E3%83%AC%E3%82%AF%E3%83%88%E3%83%AA%E3%81%AE%E8%B2%AC%E5%8B%99)


* [新規APIの追加手順](https://www.google.com/search?q=%23%E6%96%B0%E8%A6%8Fapi%E3%81%AE%E8%BF%BD%E5%8A%A0%E6%89%8B%E9%A0%86)
* [AI向けの実装前チェック](https://www.google.com/search?q=%23ai%E5%90%91%E3%81%91%E3%81%AE%E5%AE%9F%E8%A3%85%E5%89%8D%E3%83%81%E3%82%A7%E3%83%83%E3%82%AF)
* [Step 1: ドメイン層](https://www.google.com/search?q=%23step-1-%E3%83%89%E3%83%A1%E3%82%A4%E3%83%B3%E5%B1%A4)
* [Step 2: ユースケース層](https://www.google.com/search?q=%23step-2-%E3%83%A6%E3%83%BC%E3%82%B9%E3%82%B1%E3%83%BC%E3%82%B9%E5%B1%A4)
* [Step 3: インフラ層の実装](https://www.google.com/search?q=%23step-3-%E3%82%A4%E3%83%B3%E3%83%95%E3%83%A9%E5%B1%A4%E3%81%AE%E5%AE%9F%E8%A3%85)
* [Step 4: アダプタ層](https://www.google.com/search?q=%23step-4-%E3%82%A2%E3%83%80%E3%83%97%E3%82%BF%E5%B1%A4)
* [Step 5: インフラ層の接続](https://www.google.com/search?q=%23step-5-%E3%82%A4%E3%83%B3%E3%83%95%E3%83%A9%E5%B1%A4%E3%81%AE%E6%8E%A5%E7%B6%9A)
* [Step 6: 起動ファイル](https://www.google.com/search?q=%23step-6-%E8%B5%B7%E5%8B%95%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB)


* [テスト設計と実装ガイドライン](https://www.google.com/search?q=%23%E3%83%86%E3%82%B9%E3%83%88%E8%A8%AD%E8%A8%88%E3%81%A8%E5%AE%9F%E8%A3%85%E3%82%AC%E3%82%A4%E3%83%89%E3%83%A9%E3%82%A4%E3%83%B3)
* [テストフォルダ構成](https://www.google.com/search?q=%23%E3%83%86%E3%82%B9%E3%83%88%E3%83%95%E3%82%A9%E3%83%AB%E3%83%80%E6%A7%8B%E6%88%90)
* [テスト環境とルール](https://www.google.com/search?q=%23%E3%83%86%E3%82%B9%E3%83%88%E7%92%B0%E5%A2%83%E3%81%A8%E3%83%AB%E3%83%BC%E3%83%AB)
* [各層のテスト実装テンプレート](https://www.google.com/search?q=%23%E5%90%84%E5%B1%A4%E3%81%AE%E3%83%86%E3%82%B9%E3%83%88%E5%AE%9F%E8%A3%85%E3%83%86%E3%83%B3%E3%83%97%E3%83%AC%E3%83%BC%E3%83%88)
* [実行方法](https://www.google.com/search?q=%23%E5%AE%9F%E8%A1%8C%E6%96%B9%E6%B3%95)



---

## プロジェクト構成の概要

この構成はクリーンアーキテクチャで定義した4層の責務に基づいています。

AI実装向けガイドラインの注意

* このドキュメントのコード例は雛形かつ参照用です。要求にない機能や抽象化や汎用化は一切追加しないでください。
* 実装は最小限のスコープで行います。ルート、DTO、Presenter、Usecase、Repository、Serviceのうちタスク達成に必要な部分だけを作成および編集します。
* 依存関係はレイヤ原則に厳密に従います。UsecaseはDomainのみに依存し、InfrastructureやAdapterの具体実装へ直接依存してはいけません。
* 例の名称や構造は参考でありプロジェクトの既存命名や配置に優先度があります。既存と矛盾する場合は既存に合わせます。
* 追加でユーティリティ、共通化、設定項目、例外階層などを広げないでください。必要性が明確でユーザーが依頼した場合のみ追加します。

### ルートのフォルダ構成

階層が一目で分かるように整形したツリー表示です。

```text
backend/
├─ Dockerfile
├─ .env.example
├─ go.mod
├─ go.sum
├─ atlas.hcl              # Atlas設定ファイル
├─ migrations/            # AtlasによるDBマイグレーションディレクトリ
└─ src/                   # すべてのアプリケーションコード

```

推奨するDockerfileの内容を示します。マルチステージビルドを使用してコンテナを軽量化します。

```dockerfile
# ビルドステージ
FROM golang:1.22-alpine AS builder

WORKDIR /app

# 依存関係のダウンロード
COPY go.mod go.sum ./
RUN go mod download

# ソースコードのコピーとビルド
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o main ./src/main.go

# 実行ステージ
FROM gcr.io/distroless/static-debian12

WORKDIR /app

COPY --from=builder /app/main .
COPY --from=builder /app/.env* ./

# Echoのデフォルトポート
EXPOSE 8000

CMD ["/app/main"]

```

補足事項

* go.modはbackend直下に配置します。
* メインパッケージはsrc/main.goに配置し、ビルドしてコンテナ内で実行します。
* DBマイグレーションはアプリケーション起動時ではなく、Atlas CLIを用いてCIおよびCDパイプラインまたはローカル環境から独立して実行します。

### src配下のフォルダ構成

Goのパッケージ構成の慣例に合わせたツリー表示です。

```text
src/
├─ domain/
│  ├─ entities/
│  │  ├─ user.go
│  │  └─ agent.go
│  ├─ value_objects/
│  │  ├─ id.go
│  │  └─ file_data.go
│  └─ services/
│     └─ auth_domain_service.go
├─ usecase/
│  ├─ auth_login.go
│  └─ create_agent.go
├─ adapter/
│  ├─ controller/
│  │  └─ create_agent_controller.go
│  └─ presenter/
│     └─ create_agent_presenter.go
├─ infrastructure/
│  ├─ database/
│  │  ├─ mysql/
│  │  │  ├─ config.go
│  │  │  ├─ db.go
│  │  │  └─ agent_repository.go
│  ├─ router/
│  │  └─ echo.go
│  └─ storage/
│     └─ s3_client.go
└─ main.go

```

### 各ディレクトリの責務

src/domain/

* 責務: 純粋なビジネスルール
* 内容: entitiesディレクトリには構造体とリポジトリインターフェースを定義します。value_objectsディレクトリにはIDやファイルストリームなどの値オブジェクトを定義します。servicesディレクトリにはドメインサービスのインターフェースを配置します。

src/usecase/

* 責務: アプリケーション固有のロジック
* 内容: 具体的な操作フローを実装します。domain層のインターフェースや構造体にのみ依存します。

src/adapter/

* 責務: 外部のHTTPリクエストと内部のUsecaseの翻訳
* 内容: controllerはEchoのコンテキストを受け取りUsecaseへ渡します。presenterはUsecaseの結果をHTTPレスポンス用の構造体に変換します。

src/infrastructure/

* 責務: 外部技術とdomainインターフェースの具体実装
* 内容: database配下には各DB技術のリポジトリ実装を配置します。routerにはEchoによるルーティング設定を配置します。

src/main.go

* 責務: アプリケーションの起動と依存関係の注入
* 内容: DB接続の初期化、ルーターの設定、Echoサーバーの起動を行います。

---

## 新規APIの追加手順

新しいエージェントを作成するAPIを追加する手順をステップバイステップで示します。

### AI向けの実装前チェック

* 要件を一文で明確化します。
* 既存のファイルや命名パターンを優先し、雛形を必要最小限で適用します。
* 依頼にない層や機能は追加しません。
* 依存制約を確認します。
* 既存テストや動作に影響する広範囲の変更は避けます。

### Step 1: ドメイン層

責務はビジネスルールのインターフェース定義です。外部ライブラリへの依存を避け標準パッケージのみ使用します。

値オブジェクトの定義例である domain/value_objects/id.go を示します。

```go
package value_objects

import "errors"

type ID int

func NewID(value int) (ID, error) {
	if value < 0 {
		return 0, errors.New("ID must be non-negative")
	}
	return ID(value), nil
}

func (id ID) Value() int {
	return int(id)
}

```

エンティティとリポジトリインターフェースの定義例である domain/entities/agent.go を示します。インターフェースはそれを利用する構造体と同じパッケージに配置するのがGoの慣例です。

```go
package entities

import (
	"context"
	"src/domain/value_objects"
)

type Agent struct {
	ID          value_objects.ID
	UserID      value_objects.ID
	Owner       string
	Name        string
	Description string
}

func NewAgent(id, userID int, owner, name, description string) (*Agent, error) {
	agentID, err := value_objects.NewID(id)
	if err != nil {
		return nil, err
	}
	uID, err := value_objects.NewID(userID)
	if err != nil {
		return nil, err
	}

	return &Agent{
		ID:          agentID,
		UserID:      uID,
		Owner:       owner,
		Name:        name,
		Description: description,
	}, nil
}

type AgentRepository interface {
	Create(ctx context.Context, agent *Agent) (*Agent, error)
	FindByID(ctx context.Context, id value_objects.ID) (*Agent, error)
	ListByUserID(ctx context.Context, userID value_objects.ID) ([]*Agent, error)
	Update(ctx context.Context, agent *Agent) error
	Delete(ctx context.Context, id value_objects.ID) error
}

```

ドメインサービスのインターフェース例である domain/services/auth_domain_service.go を示します。

```go
package services

import (
	"context"
	"src/domain/entities"
)

type AuthDomainService interface {
	VerifyToken(ctx context.Context, token string) (*entities.User, error)
}

```

### Step 2: ユースケース層

責務はアプリケーション固有のロジック実装です。ドメイン層のオブジェクトのみを使用します。

ユースケースの定義例である usecase/create_agent.go を示します。入出力のDTOと、操作を実行するインターフェースおよび実装を含みます。

```go
package usecase

import (
	"context"
	"src/domain/entities"
	"src/domain/services"
)

type CreateAgentInput struct {
	Token       string
	Name        string
	Description string
}

type CreateAgentOutput struct {
	ID          int
	UserID      int
	Owner       string
	Name        string
	Description string
}

type CreateAgentPresenter interface {
	Output(agent *entities.Agent) *CreateAgentOutput
}

type CreateAgentUseCase interface {
	Execute(ctx context.Context, input CreateAgentInput) (*CreateAgentOutput, error)
}

type createAgentInteractor struct {
	presenter   CreateAgentPresenter
	agentRepo   entities.AgentRepository
	authService services.AuthDomainService
}

func NewCreateAgentInteractor(
	p CreateAgentPresenter,
	r entities.AgentRepository,
	a services.AuthDomainService,
) CreateAgentUseCase {
	return &createAgentInteractor{
		presenter:   p,
		agentRepo:   r,
		authService: a,
	}
}

func (i *createAgentInteractor) Execute(ctx context.Context, input CreateAgentInput) (*CreateAgentOutput, error) {
	user, err := i.authService.VerifyToken(ctx, input.Token)
	if err != nil {
		return nil, err
	}

	agentToCreate, err := entities.NewAgent(0, user.ID.Value(), user.Username, input.Name, input.Description)
	if err != nil {
		return nil, err
	}

	createdAgent, err := i.agentRepo.Create(ctx, agentToCreate)
	if err != nil {
		return nil, err
	}

	return i.presenter.Output(createdAgent), nil
}

```

### Step 3: インフラ層の実装

責務はドメイン層で定義されたインターフェースの具体的な実装です。

データベース設定の例である infrastructure/database/mysql/config.go を示します。

```go
package mysql

import (
	"fmt"
	"os"
)

type Config struct {
	Host     string
	Port     string
	User     string
	Password string
	Database string
}

func NewConfigFromEnv() *Config {
	return &Config{
		Host:     os.Getenv("DB_HOST"),
		Port:     os.Getenv("DB_PORT"),
		User:     os.Getenv("DB_USER"),
		Password: os.Getenv("DB_PASSWORD"),
		Database: os.Getenv("DB_NAME"),
	}
}

func (c *Config) DSN() string {
	return fmt.Sprintf("%s:%s@tcp(%s:%s)/%s?parseTime=true", c.User, c.Password, c.Host, c.Port, c.Database)
}

```

リポジトリ実装の例である infrastructure/database/mysql/agent_repository.go を示します。database/sql パッケージを使用します。

```go
package mysql

import (
	"context"
	"database/sql"
	"src/domain/entities"
	"src/domain/value_objects"
)

type agentRepository struct {
	db *sql.DB
}

func NewAgentRepository(db *sql.DB) entities.AgentRepository {
	return &agentRepository{db: db}
}

func (r *agentRepository) Create(ctx context.Context, agent *entities.Agent) (*entities.Agent, error) {
	query := `INSERT INTO agents (user_id, owner, name, description) VALUES (?, ?, ?, ?)`
	result, err := r.db.ExecContext(ctx, query, agent.UserID.Value(), agent.Owner, agent.Name, agent.Description)
	if err != nil {
		return nil, err
	}

	id, err := result.LastInsertId()
	if err != nil {
		return nil, err
	}

	return entities.NewAgent(int(id), agent.UserID.Value(), agent.Owner, agent.Name, agent.Description)
}

func (r *agentRepository) FindByID(ctx context.Context, id value_objects.ID) (*entities.Agent, error) {
	return nil, nil
}

func (r *agentRepository) ListByUserID(ctx context.Context, userID value_objects.ID) ([]*entities.Agent, error) {
	return nil, nil
}

func (r *agentRepository) Update(ctx context.Context, agent *entities.Agent) error {
	return nil
}

func (r *agentRepository) Delete(ctx context.Context, id value_objects.ID) error {
	return nil
}

```

### Step 4: アダプタ層

責務はHTTPリクエストとユースケース層の翻訳です。Echoフレームワークの機能を利用します。

コントローラーの例である adapter/controller/create_agent_controller.go を示します。

```go
package controller

import (
	"net/http"
	"src/usecase"
	"strings"

	"github.com/labstack/echo/v4"
)

type CreateAgentRequest struct {
	Name        string `json:"name"`
	Description string `json:"description"`
}

type CreateAgentController struct {
	usecase usecase.CreateAgentUseCase
}

func NewCreateAgentController(u usecase.CreateAgentUseCase) *CreateAgentController {
	return &CreateAgentController{usecase: u}
}

func (ctrl *CreateAgentController) Execute(c echo.Context) error {
	var req CreateAgentRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid request body"})
	}

	authHeader := c.Request().Header.Get("Authorization")
	token := strings.TrimPrefix(authHeader, "Bearer ")

	input := usecase.CreateAgentInput{
		Token:       token,
		Name:        req.Name,
		Description: req.Description,
	}

	output, err := ctrl.usecase.Execute(c.Request().Context(), input)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusCreated, output)
}

```

プレゼンターの例である adapter/presenter/create_agent_presenter.go を示します。

```go
package presenter

import (
	"src/domain/entities"
	"src/usecase"
)

type createAgentPresenter struct{}

func NewCreateAgentPresenter() usecase.CreateAgentPresenter {
	return &createAgentPresenter{}
}

func (p *createAgentPresenter) Output(agent *entities.Agent) *usecase.CreateAgentOutput {
	return &usecase.CreateAgentOutput{
		ID:          agent.ID.Value(),
		UserID:      agent.UserID.Value(),
		Owner:       agent.Owner,
		Name:        agent.Name,
		Description: agent.Description,
	}
}

```

### Step 5: インフラ層の接続

責務はすべての部品を接続しEchoエンドポイントとして公開することです。手動での依存性の注入を行います。

ルーターの例である infrastructure/router/echo.go を示します。

```go
package router

import (
	"database/sql"
	"src/adapter/controller"
	"src/adapter/presenter"
	"src/infrastructure/database/mysql"
	"src/infrastructure/services"
	"src/usecase"

	"github.com/labstack/echo/v4"
)

func InitRoutes(e *echo.Echo, db *sql.DB) {
	agentRepo := mysql.NewAgentRepository(db)
	authService := services.NewAuthServiceImpl()

	createAgentPresenter := presenter.NewCreateAgentPresenter()
	createAgentUsecase := usecase.NewCreateAgentInteractor(createAgentPresenter, agentRepo, authService)
	createAgentController := controller.NewCreateAgentController(createAgentUsecase)

	v1 := e.Group("/v1")
	v1.POST("/agents", createAgentController.Execute)
}

```

### Step 6: 起動ファイル

責務はアプリケーション起動時にDB接続とEchoインスタンスを初期化し全体を統合することです。

メインファイルの例である src/main.go を示します。

```go
package main

import (
	"database/sql"
	"log"
	"src/infrastructure/database/mysql"
	"src/infrastructure/router"

	_ "github.com/go-sql-driver/mysql"
	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

func main() {
	config := mysql.NewConfigFromEnv()
	db, err := sql.Open("mysql", config.DSN())
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	if err := db.Ping(); err != nil {
		log.Fatalf("Failed to ping database: %v", err)
	}

	e := echo.New()

	e.Use(middleware.Logger())
	e.Use(middleware.Recover())
	e.Use(middleware.CORSWithConfig(middleware.CORSConfig{
		AllowOrigins: []string{"*"},
		AllowMethods: []string{echo.GET, echo.POST, echo.PUT, echo.DELETE},
	}))

	router.InitRoutes(e, db)

	e.GET("/health", func(c echo.Context) error {
		return c.JSON(200, map[string]string{"status": "ok"})
	})

	e.Logger.Fatal(e.Start(":8000"))
}

```

---

## テスト設計と実装ガイドライン

Go言語における標準的なテスト手法に従いテストの責務を分離します。

### テストフォルダ構成

Goの規約に従い、単体テストはテスト対象のファイルと同じディレクトリに配置し、ファイル名の末尾を _test.go とします。統合テストは tests ディレクトリに分離します。

```text
src/
├─ domain/
│  └─ entities/
│     ├─ agent.go
│     └─ agent_test.go    # ドメインの単体テスト
├─ usecase/
│  ├─ create_agent.go
│  └─ create_agent_test.go # ユースケースの単体テスト
tests/
├─ integration/           # DB接続を伴う統合テストやE2Eテスト

```

### テスト環境とルール

標準パッケージの testing を基本とし、必要に応じてモック生成ツールである gomock や testify などのアサーションライブラリを導入します。テストデータ生成やDBリセット処理は各統合テストのSetup関数内で定義します。

### 各層のテスト実装テンプレート

ドメイン層の単体テスト
DB接続は行わず構造体や関数のロジックを検証します。

```go
package entities_test

import (
	"src/domain/entities"
	"testing"
)

func TestNewAgent_Valid(t *testing.T) {
	agent, err := entities.NewAgent(1, 100, "test_user", "MyAgent", "desc")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if agent.Name != "MyAgent" {
		t.Errorf("expected MyAgent, got %s", agent.Name)
	}
}

```

ユースケース層の単体テスト
すべての依存リポジトリやサービスをモック化してビジネスフローを検証します。

```go
package usecase_test

import (
	"context"
	"src/domain/entities"
	"src/usecase"
	"testing"
)

type mockAgentRepository struct {
	entities.AgentRepository
}

func (m *mockAgentRepository) Create(ctx context.Context, agent *entities.Agent) (*entities.Agent, error) {
	return entities.NewAgent(1, agent.UserID.Value(), agent.Owner, agent.Name, agent.Description)
}

func TestCreateAgentInteractor_Execute(t *testing.T) {
	repo := &mockAgentRepository{}
	// authServiceやpresenterのモックも定義して注入します
	// 依存関係を設定した上でExecuteを呼び出し戻り値を検証します
}

```

インフラ層の統合テスト
テスト用のDBを立ち上げAtlas等でスキーマを適用した状態に対してテストを実行します。

```go
package mysql_test

import (
	"context"
	"database/sql"
	"src/domain/entities"
	"src/infrastructure/database/mysql"
	"testing"
)

func TestAgentRepository_Create(t *testing.T) {
	// dbはテストセットアップで初期化された接続を使用します
	repo := mysql.NewAgentRepository(testDB)
	
	agent, _ := entities.NewAgent(0, 1, "owner", "RepoTest", "desc")
	created, err := repo.Create(context.Background(), agent)
	
	if err != nil {
		t.Fatalf("failed to create agent: %v", err)
	}
	if created.ID.Value() == 0 {
		t.Error("expected non-zero ID")
	}
}

```

### 実行方法

Goの標準テストコマンドを使用します。

```bash
go test ./src/...           # 単体テストのみ実行
go test ./tests/...         # 統合テストのみ実行
go test -v ./...            # 詳細出力ありですべて実行
go test -run TestNewAgent   # 特定のテストを指定して実行

```
