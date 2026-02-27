# GoとEchoとAtlasによるプロジェクト構成と開発ガイドライン

このドキュメントはフォルダ構成や新規API追加の標準的な開発手順を1つにまとめたものです。クリーンアーキテクチャの4層に基づき配置場所と手順の両方をここで参照できます。

## 目次

* [プロジェクト構成の概要](https://www.google.com/search?q=%23%E3%83%97%E3%83%AD%E3%82%B8%E3%82%A7%E3%82%AF%E3%83%88%E6%A7%8B%E6%88%90%E3%81%AE%E6%A6%82%E8%A6%81)
* [ルートディレクトリのフォルダ構成](https://www.google.com/search?q=%23%E3%83%AB%E3%83%BC%E3%83%88%E3%83%87%E3%82%A3%E3%83%AC%E3%82%AF%E3%83%88%E3%83%AA%E3%81%AE%E3%83%95%E3%82%A9%E3%83%AB%E3%83%80%E6%A7%8B%E6%88%90)
* [srcディレクトリのフォルダ構成](https://www.google.com/search?q=%23src%E3%83%87%E3%82%A3%E3%83%AC%E3%82%AF%E3%83%88%E3%83%AA%E3%81%AE%E3%83%95%E3%82%A9%E3%83%AB%E3%83%80%E6%A7%8B%E6%88%90)
* [srcディレクトリの各責務](https://www.google.com/search?q=%23src%E3%83%87%E3%82%A3%E3%83%AC%E3%82%AF%E3%83%88%E3%83%AA%E3%81%AE%E5%90%84%E8%B2%AC%E5%8B%99)


* [新規APIの追加手順ガイド](https://www.google.com/search?q=%23%E6%96%B0%E8%A6%8Fapi%E3%81%AE%E8%BF%BD%E5%8A%A0%E6%89%8B%E9%A0%86%E3%82%AC%E3%82%A4%E3%83%89)
* [AI向けの実装前チェック](https://www.google.com/search?q=%23ai%E5%90%91%E3%81%91%E3%81%AE%E5%AE%9F%E8%A3%85%E5%89%8D%E3%83%81%E3%82%A7%E3%83%83%E3%82%AF)
* [Step 1: ドメイン層](https://www.google.com/search?q=%23step-1-%E3%83%89%E3%83%A1%E3%82%A4%E3%83%B3%E5%B1%A4)
* [Step 2: ユースケース層](https://www.google.com/search?q=%23step-2-%E3%83%A6%E3%83%BC%E3%82%B9%E3%82%B1%E3%83%BC%E3%82%B9%E5%B1%A4)
* [Step 3: インフラ層の実装](https://www.google.com/search?q=%23step-3-%E3%82%A4%E3%83%B3%E3%83%95%E3%83%A9%E5%B1%A4%E3%81%AE%E5%AE%9F%E8%A3%85)
* [Step 4: アダプタ層の翻訳](https://www.google.com/search?q=%23step-4-%E3%82%A2%E3%83%80%E3%83%97%E3%82%BF%E5%B1%A4%E3%81%AE%E7%BF%BB%E8%A8%B3)
* [Step 5: インフラ層の接続](https://www.google.com/search?q=%23step-5-%E3%82%A4%E3%83%B3%E3%83%95%E3%83%A9%E5%B1%A4%E3%81%AE%E6%8E%A5%E7%B6%9A)
* [Step 6: 起動ファイル](https://www.google.com/search?q=%23step-6-%E8%B5%B7%E5%8B%95%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB)


* [テスト設計と実装ガイドライン](https://www.google.com/search?q=%23%E3%83%86%E3%82%B9%E3%83%88%E8%A8%AD%E8%A8%88%E3%81%A8%E5%AE%9F%E8%A3%85%E3%82%AC%E3%82%A4%E3%83%89%E3%83%A9%E3%82%A4%E3%83%B3)

---

## プロジェクト構成の概要

この構成はクリーンアーキテクチャの4層の責務に基づいています。

注意書きとしてAI実装向けのガイドラインを示します。

* このドキュメントのコード例は雛形かつ参照用です。要求にない機能や抽象化や汎用化は一切追加しないでください。
* 実装は最小限のスコープで行います。ルート、DTO、Presenter、Usecase、Repository、Serviceのうちタスク達成に必要な部分だけを作成および編集します。
* 依存関係はレイヤ原則に厳密に従います。UsecaseはDomainのみに依存しInfrastructureやAdapterの具体実装へ直接依存してはいけません。
* 例の名称や構造は参考でありプロジェクトの既存命名や配置に優先度があります。既存と矛盾する場合既存に合わせます。
* 追加でユーティリティ、共通化、設定項目、例外階層などを広げないでください。必要性が明確でユーザーが依頼した場合のみ追加します。

### ルートディレクトリのフォルダ構成

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

推奨するDockerfileの内容を示します。Goアプリケーションのコンテナ化に使用します。

```dockerfile
# ビルド環境
FROM golang:1.22-alpine AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
# バイナリのビルド
RUN go build -o main ./src/main.go

# 実行環境
FROM alpine:latest

WORKDIR /app

COPY --from=builder /app/main .
COPY --from=builder /app/.env* ./

EXPOSE 8000

CMD ["./main"]

```

補足事項です。

* go.modはbackend直下に配置します。
* コンテナ起動時に実行されるバイナリはsrc/main.goをビルドしたものです。
* YAMLの構成ファイルは本プロジェクトでは不要です。単一コンテナ起動を前提とします。
* データベースのマイグレーションはAtlasを使用しmigrationsディレクトリで管理します。

### srcディレクトリのフォルダ構成

ツリー表示です。Goのパッケージ構成に合わせています。

```text
src/
├─ domain/
│  ├─ entities/
│  │  ├─ user.go
│  │  └─ agent.go
│  ├─ value_objects/
│  │  ├─ id.go
│  │  ├─ email.go
│  │  └─ file_data.go
│  └─ services/
│     ├─ auth_domain_service.go
│     └─ file_storage_domain_service.go
├─ usecase/
│  ├─ auth_login.go
│  └─ create_agent.go
├─ adapter/
│  ├─ controller/
│  └─ presenter/
├─ infrastructure/
│  ├─ database/
│  │  ├─ mysql/
│  │  │  ├─ config.go
│  │  │  ├─ agent_repository.go
│  │  │  └─ user_repository.go
│  ├─ router/
│  │  └─ echo.go
│  └─ storage/
│     └─ s3/
└─ main.go

```

### srcディレクトリの各責務

src/domain/ はドメイン層です。

* 責務: 純粋なビジネスルール
* 内容: entitiesディレクトリには構造体とリポジトリインターフェースを配置します。value_objectsディレクトリには値オブジェクトを配置します。servicesディレクトリにはドメインサービスのインターフェースを配置します。

src/usecase/ はユースケース層です。

* 責務: アプリケーション固有のロジック
* 内容: 具体的な操作フローを実装します。domain層の定義にのみ依存します。

src/adapter/ はアダプタ層です。

* 責務: 外部のHTTPリクエストと内部のUsecaseの翻訳
* 内容: controllerとpresenterを配置します。

src/infrastructure/ はインフラ層です。

* 責務: 外部技術とdomainインターフェースの具体実装
* 内容: databaseディレクトリには各DB技術のリポジトリ実装を配置します。routerディレクトリにはEchoによるルーティングを配置します。storageディレクトリにはファイルストレージクライアントなどを配置します。

src/main.go は起動ファイルです。

* 責務: アプリケーションの起動
* 内容: infrastructure/router/echo.goで定義したEchoインスタンスを起動します。

---

## 新規APIの追加手順ガイド

新しいエージェントを作成するAPIを追加する手順をステップバイステップで示します。

### AI向けの実装前チェック

* 要件を一文で明確化します。
* 既存のファイルや命名パターンを優先し雛形を必要最小限で適用します。
* 依頼にない層や機能は追加しません。
* 依存制約を確認します。UsecaseはDomainのみに依存します。AdapterはUsecaseに依存します。InfraはDomainのインターフェースに依存します。
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

エンティティとリポジトリインターフェースの定義例である domain/entities/agent.go を示します。

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

### Step 2: ユースケース層

責務はアプリケーション固有のロジック実装です。ドメイン層のオブジェクトのみを使用します。

ユースケースの定義例である usecase/create_agent.go を示します。

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

リポジトリ実装の例である infrastructure/database/mysql/agent_repository.go を示します。

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
	// 実装は省略しますが標準的な database/sql の処理を記述します
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

### Step 4: アダプタ層の翻訳

責務はHTTPリクエストとユースケース層の翻訳です。

コントローラーの例である adapter/controller/create_agent_controller.go を示します。Echoのコンテキストを使用します。

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
	"src/infrastructure/services_impl"
	"src/usecase"

	"github.com/labstack/echo/v4"
)

func InitRoutes(e *echo.Echo, db *sql.DB) {
	agentRepo := mysql.NewAgentRepository(db)
	authService := services_impl.NewAuthServiceImpl()

	createAgentPresenter := presenter.NewCreateAgentPresenter()
	createAgentUsecase := usecase.NewCreateAgentInteractor(createAgentPresenter, agentRepo, authService)
	createAgentController := controller.NewCreateAgentController(createAgentUsecase)

	v1 := e.Group("/v1")
	v1.POST("/agents", createAgentController.Execute)
}

```

### Step 6: 起動ファイル

責務はアプリケーション起動時にEchoインスタンスを初期化し全体を統合することです。

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

### テスト配置のルール

Goでは単体テストはテスト対象のファイルと同じディレクトリに配置します。ファイル名の末尾を _test.go とします。統合テストはルートディレクトリ直下に tests ディレクトリを作成しそこに配置します。

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

### 単体テストの実装例

ユースケースのテストではモックを使用します。Goではインターフェースを利用して手動でモック構造体を作成するかgomockなどのツールを利用します。

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
	// presenterとauthServiceのモックも同様に作成し注入します
	// 実行結果を検証するアサーションを記述します
}

```

### 統合テストの実行

統合テストは実際のデータベースが必要です。Atlasを使用してテスト用データベースのスキーマを同期したうえでテストを実行します。

すべてのテストを実行するコマンドです。

```bash
go test ./...

```