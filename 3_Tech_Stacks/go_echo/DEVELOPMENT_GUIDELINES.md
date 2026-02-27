# プロジェクト構成と開発ガイドライン Go Echo Atlas

このドキュメントは、フォルダ構成 What/Where と新規API追加の標準的な開発手順 How を1つにまとめたものです。クリーンアーキテクチャの4層に基づき、配置場所と手順の両方をここで参照できます。

## 目次


* [プロジェクト構成 概要](#プロジェクト構成-概要)
* [1 フォルダ構成 ルート](#1-フォルダ構成-ルート)
* [2 フォルダ構成 src](#2-フォルダ構成-src)
* [3 各ディレクトリの責務 src](#3-各ディレクトリの責務-src)

* [新規APIの追加手順 ガイド](#新規apiの追加手順-ガイド)
* [実装前のチェック AI向け](#実装前のチェック-ai向け)
* [step-1-ドメイン層-src-domain](#step-1-ドメイン層-src-domain)
* [step-2-ユースケース層-src-usecase](#step-2-ユースケース層-src-usecase)
* [step-3-インフラ層-実装-src-infrastructure](#step-3-インフラ層-実装-src-infrastructure)
* [step-4-アダプタ層-翻訳-src-adapter](#step-4-アダプタ層-翻訳-src-adapter)
* [step-5-インフラ層-接続-src-infrastructure](#step-5-インフラ層-接続-src-infrastructure)
* [step-6-起動ファイル-src-main-go](#step-6-起動ファイル-src-main-go)

* [テスト設計と実装ガイドライン](#テスト設計と実装ガイドライン)
* [1-テストフォルダ構成](#1-テストフォルダ構成)
* [2-テスト環境とルール](#2-テスト環境とルール)
* [3-各層のテスト実装テンプレート](#3-各層のテスト実装テンプレート)
* [4-実行方法](#4-実行方法)



---

## プロジェクト構成 概要

この構成は、クリーンアーキテクチャで定義した4層の責務に基づいています。

注意 AI実装向けガイドライン

* このドキュメントのコード例は雛形かつ参照用です。要求にない機能や抽象化や汎用化は一切追加しないでください。
* 実装は最小限のスコープで行います。ルート、DTO、Presenter、Usecase、Repository、Serviceのうち、タスク達成に必要な部分だけを作成および編集します。
* 依存関係はレイヤ原則に厳密に従います。UsecaseはDomainのみに依存し、InfrastructureやAdapterの具体実装へ直接依存してはいけません。
* 例の名称や構造は参考であり、プロジェクトの既存命名や配置に優先度があります。既存と矛盾する場合、既存に合わせます。
* 追加でユーティリティ、共通化、設定項目、例外階層などを広げないでください。必要性が明確でユーザーが依頼した場合のみ追加します。

### 1 フォルダ構成 ルート

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

Goアプリケーションのコンテナ化に使用する backend/Dockerfile は次の内容を推奨します。マルチステージビルドを使用してコンテナを軽量化します。

```dockerfile
# ビルド環境
FROM golang:1.22-alpine AS builder

WORKDIR /app

# 環境変数を設定
ENV CGO_ENABLED=0 \
    GOOS=linux \
    GOARCH=amd64

# 依存ライブラリのリストをコピーしてダウンロード
COPY go.mod go.sum ./
RUN go mod download

# アプリケーションのコードをコピー
COPY . .

# バイナリのビルド
RUN go build -o main ./src/main.go

# 実行環境 軽量なdistrolessまたはalpineを使用
FROM alpine:latest

WORKDIR /app

# ビルドしたバイナリをコピー
COPY --from=builder /app/main .
COPY --from=builder /app/.env* ./

# コンテナ起動時にAPIサーバーを実行
EXPOSE 8000
CMD ["./main"]

```

補足

* go.mod は backend/ 直下に配置します。
* コンテナ起動時に実行されるバイナリは src/main.go をビルドしたものです。
* ローカル開発では air などのホットリロードツールを使用することがありますが、本番コンテナではコンパイル済みバイナリを直接実行します。
* データベースのマイグレーションはAtlasを使用し migrations/ ディレクトリで管理します。

### 2 フォルダ構成 src

ツリー表示です。Goのパッケージ構成に合わせています。

```text
src/
├─ domain/               # 1 ドメイン層 純粋なビジネスルール
│  ├─ entities/          # エンティティ 構造体 と リポジトリインターフェース
│  │  ├─ user.go
│  │  └─ agent.go
│  ├─ value_objects/     # 値オブジェクト
│  │  ├─ id.go
│  │  ├─ email.go
│  │  └─ file_data.go
│  └─ services/          # ドメインサービスインターフェース
│     ├─ auth_domain_service.go
│     └─ file_storage_domain_service.go
├─ usecase/              # 2 ユースケース層 操作フロー
│  ├─ auth_login.go
│  └─ create_agent.go    # ほか機能ごとに追加
├─ adapter/              # 3 アダプタ層 翻訳
│  ├─ controller/        # HTTPからUsecase入力へ
│  └─ presenter/         # Usecase出力からHTTPレスポンスへ
├─ infrastructure/       # 4 インフラ層 具体実装と外部技術
│  ├─ database/          # DB接続設定 各種DB技術
│  │  ├─ mysql/          # MySQLリポジトリ実装 各フォルダ直下に必ず config.go
│  │  │  ├─ config.go
│  │  │  ├─ agent_repository.go
│  │  │  └─ user_repository.go
│  │  └─ redis/          # Redisキャッシュ実装 例 config.go 必須
│  ├─ router/            # Echoルーティング簡易DIもここで
│  │  └─ echo.go
│  └─ storage/           # 外部ストレージクライアント 各フォルダに config.go 推奨
│     └─ s3/             # AWS S3クライアント実装
└─ main.go               # アプリケーション起動ファイル エントリーポイント

```

注意 エンティティと値オブジェクトの実装配置について
Goではインターフェースと実装を明確に分けることができます。ドメイン層には純粋な構造体とインターフェースのみを配置し、特定のフレームワーク echo.Context や multipart.FileHeader など に依存するコードは絶対に含めないでください。

### 3 各ディレクトリの責務 src

* src/domain/ ドメイン層
* 責務 純粋なビジネスルール
* 内容
* entities/ エンティティ構造体とリポジトリインターフェースを同じファイルまたはディレクトリに配置
* value_objects/ 値オブジェクト構造体とバリデーションロジック
* services/ ドメインサービスのインターフェース




* src/usecase/ ユースケース層
* 責務 アプリケーション固有のロジック
* 内容 具体的な操作フローを実装します。domain層のインターフェースや構造体にのみ依存します。


* src/adapter/ アダプタ層
* 責務 外部のHTTPリクエストと内部のUsecaseの翻訳
* 内容 controllerはEchoのコンテキストを受け取りUsecaseへ渡します。presenterはUsecaseの結果をHTTPレスポンス用の構造体に変換します。


* src/infrastructure/ インフラ層
* 責務 外部技術とdomainインターフェースの具体実装
* 内容 database配下には各DB技術のリポジトリ実装を配置します。routerにはEchoによるルーティング設定を配置します。


* src/main.go
* 責務 アプリケーションの起動と依存関係の注入
* 内容 DB接続の初期化、ルーターの設定、Echoサーバーの起動を行います。



---

## 新規APIの追加手順 ガイド

ここでは例として新しいエージェント Agent を作成するAPIを追加する手順をステップバイステップで示します。

### 実装前のチェック AI向け

* 要件を一文で明確化します 何を追加や変更するか。
* 既存のファイルや命名パターンを優先し、雛形を必要最小限で適用します。
* 依頼にない層や機能は追加しません 例 追加のサービス、共通ユーティリティ、設定拡張。
* 依存制約を確認します UsecaseからDomainのみ。AdapterはUsecaseに、InfraはDomainのインターフェースに。
* 既存テストや動作に影響する広範囲の変更は避けます。

### Step 1 ドメイン層 src domain

責務 ビジネスルール 何ができるか のインターフェースと構造体を定義します。

使用可能なライブラリ
ドメイン層では外部ライブラリへの依存を避け、Goの標準パッケージ errors context time など のみを使用します。

1 エンティティと値オブジェクトの定義
必要に応じて src/domain/entities/agent.go や src/domain/value_objects/ に、純粋なGoの構造体としてエンティティや値オブジェクトを定義または更新します。

コード例 値オブジェクト domain/value_objects/id.go

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

コード例 エンティティとリポジトリ domain/entities/agent.go

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

注意 Repositoryの実装範囲
CRUD以外のメソッド 検索条件の複雑化、集計、ページングユーティリティ等 は、明示的な要求がない限り追加しません。

2 ドメインサービス インターフェースの定義
エンティティや値オブジェクトに当てはまらないビジネスロジックは、 src/domain/services/ にドメインサービスとして定義します。

コード例 ドメインサービス domain/services/auth_domain_service.go

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

### Step 2 ユースケース層 src usecase

責務 アプリケーション固有のロジック どういう流れで実行するか を実装します。

依存関係の原則
ユースケース層はドメイン層のオブジェクトのみを使用してコードを書きます。infrastructureやadapter、外部ライブラリには依存しません。

1 ユースケースの作成
src/usecase/create_agent.go を作成します。入力DTO、出力DTO、Presenterインターフェース、Usecaseインターフェース、そして実装となるInteractor構造体を定義します。

コード例 create_agent.go

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

### Step 3 インフラ層 実装 src infrastructure

責務 domain層で定義されたインターフェースの具体的な実装を行います。

1 データベース設定 config.go
各データストアフォルダの直下に config.go を配置します。

コード例 MySQL設定 infrastructure/database/mysql/config.go

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

2 リポジトリの実装
エンティティパッケージ内で定義したリポジトリインターフェースを実装する構造体を定義します。

コード例 リポジトリ実装 infrastructure/database/mysql/agent_repository.go

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

### Step 4 アダプタ層 翻訳 src adapter

責務 HTTPリクエストとユースケース層の翻訳を行います。Echoの機能はここで使います。

1 コントローラーの作成
src/adapter/controller/create_agent_controller.go を作成します。

コード例 コントローラー adapter/controller/create_agent_controller.go

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

2 プレゼンターの作成
src/adapter/presenter/create_agent_presenter.go を作成します。

コード例 プレゼンター adapter/presenter/create_agent_presenter.go

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

### Step 5 インフラ層 接続 src infrastructure

責務 すべての部品を接続し、Echoエンドポイントとして公開します。手動DIを行います。

コード例 ルーター infrastructure/router/echo.go

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

### Step 6 起動ファイル src main go

責務 アプリケーション起動時にDB接続とEchoインスタンスを初期化し、全体を統合します。

コード例 起動ファイル src/main.go

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

Go言語における標準的なテスト手法に従い、クリーンアーキテクチャの階層構造に基づいてテストの責務を分離します。

### 1 テストフォルダ構成

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

### 2 テスト環境とルール

標準パッケージの testing を基本とし、必要に応じてモック生成ツールである gomock や testify などのアサーションライブラリを導入します。テストデータ生成やDBリセット処理は各統合テストのSetup関数内で定義します。

### 3 各層のテスト実装テンプレート

A ドメイン層の単体テスト
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

B ユースケース層の単体テスト
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

C インフラ層の統合テスト
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

### 4 実行方法

Goの標準テストコマンドを使用します。

```bash
# 単体テストのみ実行
go test ./src/...           

# 統合テストのみ実行
go test ./tests/...         

# 詳細出力ありですべて実行
go test -v ./...            

# 特定のテストを指定して実行
go test -run TestNewAgent   

```
