# プロジェクト構成と開発ガイドライン (FastAPI)

このドキュメントは、フォルダ構成（What/Where）と新規API追加の標準的な開発手順（How）を1つにまとめたものです。クリーンアーキテクチャの4層に基づき、配置場所と手順の両方をここで参照できます。

## 目次

- [プロジェクト構成 (概要)](#プロジェクト構成-概要)
  - [フォルダ構成 (Root)](#1-フォルダ構成-root)
  - [フォルダ構成 (src/)](#2-フォルダ構成-src)
  - [各ディレクトリの責務](#3-各ディレクトリの責務-src)
- [新規APIの追加手順](#新規apiの追加手順-ガイド)
  - [実装前のチェック](#実装前のチェックai向け)
  - [Step 1: ドメイン層](#step-1-ドメイン層-srcdomain)
  - [Step 2: ユースケース層](#step-2-ユースケース層-srcusecase)
  - [Step 3: インフラ層 (実装)](#step-3-インフラ層-srcinfrastructure---実装)
  - [Step 4: アダプタ層](#step-4-アダプタ層-srcadapter---翻訳)
  - [Step 5: インフラ層 (接続)](#step-5-インフラ層-srcinfrastructure---接続)
  - [Step 6: 起動ファイル](#step-6-起動ファイル-srcmainpy)
- [テスト設計と実装ガイドライン](#テスト設計と実装ガイドライン)
  - [テストフォルダ構成](#1-テストフォルダ構成)
  - [テスト方針](#2-テスト方針)
  - [実装ルール](#3-実装ルール)
  - [実行方法](#4-実行方法)

---

## プロジェクト構成 (概要)

この構成は、`2_Concepts/clean_architecture.md`で定義した4層の責務に基づいています。

> 注意（AI実装向けガイドライン）
> - このドキュメントのコード例は「雛形」かつ「参照用」です。要求にない機能・抽象化・汎用化は一切追加しないでください。
> - 実装は「最小限のスコープ」で行います。ルート・DTO・Presenter・Usecase・Repository・Serviceのうち、タスク達成に必要な部分だけを作成・編集します。
> - 依存関係はレイヤ原則に厳密に従います（UsecaseはDomainのみ、InfrastructureやAdapterの具体実装へ直接依存しない）。
> - 例の名称・構造は参考であり、プロジェクトの既存命名・配置に優先度があります。既存と矛盾する場合、既存に合わせます。
> - 追加でユーティリティ、共通化、設定項目、例外階層などを広げないでください。必要性が明確でユーザーが依頼した場合のみ追加します。

### 1. フォルダ構成 (Root)

ツリー表示（階層が一目で分かるように整形）：

```
backend/
├─ Dockerfile
├─ .env.example
├─ requirements.txt
├─ alembic.ini
├─ alembic/              # DBマイグレーションスクリプト
└─ src/                  # ★ すべてのアプリケーションコード
```

#### Dockerfile（backend/Dockerfile 推奨内容）

FastAPIアプリのコンテナ化に使用する`backend/Dockerfile`は次の内容を推奨します。

```Dockerfile
# Pythonの公式軽量イメージを使用
FROM python:3.10-slim

# 作業ディレクトリを設定
WORKDIR /app

# 環境変数を設定（UTF-8対応）
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# 依存ライブラリのリストをコピー
COPY requirements.txt .

# 依存ライブラリをインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコードをコピー
COPY . .

# コンテナ起動時にAPIサーバーを実行（0.0.0.0を指定）
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

補足:
- `requirements.txt`は`backend/`直下に配置します。
- `main:app`は`backend/src/main.py`で定義されたFastAPIインスタンス`app`を参照します（`WORKDIR`が`/app`のため、`uvicorn`は`main`モジュールを解決します）。
- ローカル開発では`--reload`オプションを使用することがありますが、本番コンテナでは省略します。
 - YAMLの構成ファイル（例: docker-compose.yml）は本プロジェクトでは不要です。単一コンテナ起動を前提とします。

### 2. フォルダ構成 (src/)

ツリー表示：

```
src/
├─ domain/               # 1. ドメイン層（純粋なビジネスルール）
│  ├─ entities/          # エンティティ（クラスを実装）+ リポジトリIF: user.py, agent.py など
│  ├─ value_objects/     # 値オブジェクト（クラスを実装）: email.py, id.py など
│  └─ services/          # ドメインサービス（インターフェース）
├─ usecase/              # 2. ユースケース層（操作フロー）
│  ├─ auth_login.py
│  └─ create_agent.py    # ほか機能ごとに追加
├─ adapter/              # 3. アダプタ層（翻訳）
│  ├─ controller/        # HTTP → Usecase 入力
│  └─ presenter/         # Usecase 出力 → HTTP レスポンス
├─ infrastructure/       # 4. インフラ層（具体実装／外部技術）
│  ├─ database/          # DBセッション, Engine, 各種DB技術（SQL/NoSQL）
│  │  ├─ mysql/          # MySQLリポジトリ実装（各フォルダ直下に必ず config.py）
│  │  ├─ postgresql/     # PostgreSQLリポジトリ実装（例、config.py 必須）
│  │  ├─ sqlite/         # SQLiteリポジトリ実装（例、config.py 必須）
│  │  ├─ mongodb/        # MongoDBリポジトリ実装（例、config.py 必須）
│  │  ├─ dynamodb/       # DynamoDB実装（例、config.py 必須）
│  │  └─ redis/          # Redisキャッシュ実装（例、config.py 必須）
│  ├─ services/          # 外部連携・ドメインサービス等の具体実装
│  ├─ router/            # FastAPIルーティング: fastapi.py（簡易DIもここで）
│  ├─ storage/           # 外部ストレージクライアント（各フォルダに config.py 推奨）
│  │  ├─ s3/             # AWS S3クライアント実装（config.py 推奨）
│  │  ├─ gcs/            # Google Cloud Storageクライアント実装（例、config.py 推奨）
│  │  ├─ azure_blob/     # Azure Blob Storageクライアント実装（例、config.py 推奨）
│  │  └─ local/          # ローカルファイルシステム実装（開発用、config.py 推奨）
└─ main.py               # アプリケーション起動ファイル / Entrypoint
```

### 3. 各ディレクトリの責務 (src/)

* `src/domain/` (ドメイン層)
    - 責務: 純粋なビジネスルール
    - 内容: `entities/`(エンティティ+リポジトリIF), `value_objects/`, `services/`(ロジックIF)
* `src/usecase/` (ユースケース層)
    - 責務: アプリケーション固有のロジック
    - 内容: 具体的な操作フローを実装。`domain`層のインターフェースにのみ依存
* `src/adapter/` (アダプタ層)
    - 責務: 外部（HTTP）と内部（Usecase）の翻訳
    - 内容: `controller/`と`presenter/`
* `src/infrastructure/` (インフラ層)
    - 責務: 外部技術と`domain`インターフェースの具体実装
    - 内容: `database/*/`（各DB技術、各フォルダに`config.py`必須）, `services/`, `router/`
* `src/main.py`
    - 責務: アプリケーションの起動
    - 内容: `infrastructure/router/fastapi.py`で定義したFastAPIアプリを起動

---

## 新規APIの追加手順 (ガイド)

ここでは例として「新しいエージェント（Agent）を作成するAPI」を追加する手順をステップバイステップで示します。

### 実装前のチェック（AI向け）
- 要件を一文で明確化（何を追加・変更するか）。
- 既存のファイル/命名/パターンを優先し、雛形を必要最小限で適用。
- 依頼にない層・機能は追加しない（例: 追加のサービス、共通ユーティリティ、設定拡張）。
- 依存制約を確認（Usecase→Domainのみ。AdapterはUsecaseに、InfraはDomainのIFに）。
- 既存テストや動作に影響する広範囲の変更は避ける。

### Step 1: ドメイン層 (src/domain/)

**責務:** ビジネスルール（何ができるか）のインターフェースを定義します。

**使用可能なライブラリ:**  
ドメイン層では外部ライブラリへの依存を避け、以下の標準ライブラリのみ使用します。

```python
import abc
from dataclasses import dataclass, field
from typing import BinaryIO, Optional
```

**ドメイン層内での相互参照:**  
ドメイン層内のオブジェクト（エンティティ、値オブジェクト、リポジトリインターフェース、ドメインサービス）は互いに参照・利用できます。

例: エンティティで値オブジェクトをインポート
```python
# src/domain/entities/deployment_methods.py
from ..value_objects.id import ID
from ..value_objects.method import Method

@dataclass
class DeploymentMethods:
    id: ID
    deployment_id: ID
    methods: list[Method] = field(default_factory=list)
```

1.  **エンティティ / 値オブジェクトの定義:**
    * 必要に応じて`src/domain/entities/agent.py`や`src/domain/value_objects/`に、純粋なPythonクラスとしてエンティティや値オブジェクトを定義（または更新）します。

**コード例 (値オブジェクト: `domain/value_objects/id.py`):**
```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ID:
    """シンプルな ID 値オブジェクトラッパー（整数型）"""
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int):
            raise TypeError(f"ID.value must be int, got {type(self.value).__name__}")
        if self.value < 0:
            raise ValueError("ID.value must be non-negative")

    def __str__(self) -> str:
        return str(self.value)
```

**コード例 (値オブジェクト: `domain/value_objects/file_data.py`):**

> **注意:** この値オブジェクトは **APIでファイルデータ（アップロード/ダウンロード）を扱う場合のみ** 必要です。`file_storage_domain_service.py`と併せて定義します。

```python
import abc
from typing import BinaryIO, Optional


class FileStream(abc.ABC):
    """
    ファイルデータを抽象的に表現するドメイン層のインターフェース。
    アップロード、ダウンロード、内部生成など様々な形式のファイルに対応します。
    ユースケースはこの抽象型のみを参照し、FastAPIのUploadFileなどフレームワーク固有の型に依存しません。
    """
    @property
    @abc.abstractmethod
    def filename(self) -> str:
        """元のファイル名またはファイル識別子"""
        pass

    @property
    @abc.abstractmethod
    def content_type(self) -> Optional[str]:
        """ファイルのMIMEタイプ"""
        pass

    @property
    @abc.abstractmethod
    def file_stream(self) -> BinaryIO:
        """ファイルの内容にアクセスするための標準的なバイナリストリーム"""
        pass

    @abc.abstractmethod
    async def read(self) -> bytes:
        """
        ファイルの内容全体を非同期で読み込み、バイトデータとして返す。
        （FastAPIの UploadFile.read() に対応）
        """
        pass
```

**コード例 (エンティティとリポジトリ: `domain/entities/agent.py`):**
```python
import abc
from dataclasses import dataclass
from typing import Optional

from ..value_objects.id import ID


@dataclass
class Agent:
    id: ID
    user_id: ID
    owner: str
    name: str
    description: Optional[str]


class AgentRepository(abc.ABC):
    @abc.abstractmethod
    def create(self, agent: Agent) -> Agent:
        """エージェントを作成して返す"""
        pass

    @abc.abstractmethod
    def find_by_id(self, agent_id: ID) -> Optional[Agent]:
        """IDからエージェントを検索する"""
        pass

    @abc.abstractmethod
    def list_by_user_id(self, user_id: ID) -> list[Agent]:
        """指定ユーザーのエージェント一覧を取得する"""
        pass

    @abc.abstractmethod
    def find_all(self) -> list[Agent]:
        """すべてのエージェントを取得する"""
        pass

    @abc.abstractmethod
    def update(self, agent: Agent) -> None:
        """エージェント情報を更新する"""
        pass

    @abc.abstractmethod
    def delete(self, agent_id: ID) -> None:
        """IDでエージェントを削除する"""
        pass


def NewAgent(
    id: int, user_id: int, owner: str, name: str, description: Optional[str]
) -> Agent:
    """Agentエンティティを生成するファクトリ関数"""
    return Agent(
        id=ID(id),
        user_id=ID(user_id),
        owner=owner,
        name=name,
        description=description,
    )
```

注意（Repositoryの実装範囲）:
- CRUD以外のメソッド（検索条件の複雑化、集計、ページングユーティリティ等）は、明示的な要求がない限り追加しない。
- DB固有の最適化・トランザクション管理の高度化は必要最小限。例外は具体的な要件がある場合のみ。

2.  **ドメインサービス・インターフェースの定義:**
    * エンティティや値オブジェクトに当てはまらないビジネスロジックは、`src/domain/services/`にドメインサービスとして定義します。
    * 例: 複数のエンティティにまたがる処理、外部との連携ロジックなど。
    * 命名規則: `[ドメインサービスの名前]_service.py`（例: `auth_service.py`, `notification_service.py`）

**コード例 (ドメインサービス: `domain/services/deployment_test_service.py`):**
```python
import abc
from typing import Protocol

from domain.value_objects.file_data import FileStream
from domain.value_objects.deployment_test_result import DeploymentTestResult 

    
class DeploymentTestDomainService(Protocol):
    """
    デプロイされた推論エンジンに対するテスト実行ロジックを
    カプセル化するドメインサービスインターフェース。
    """
    
    @abc.abstractmethod
    async def run_batch_inference_test(
        self, 
        test_file: FileStream,
        endpoint_url: str,
    ) -> DeploymentTestResult: 
        """
        テストデータファイルの内容を解析し、外部エンドポイントに対し
        並列でリクエストを発行し、最終的な評価結果V.O.を返す。
        
        Args:
            test_file: テストデータファイル。
            endpoint_url: 推論を行うデプロイメントの完全なエンドポイントURL。
            
        Returns:
            DeploymentTestResult: テスト実行の最終結果を含むV.O.。
        """
        ...
```

**コード例 (ドメインサービス: `domain/services/file_storage_domain_service.py`):**

> **注意:** このドメインサービスは **APIでファイルデータ（アップロード/ダウンロード）を扱う場合のみ** 必要です。ファイル処理が不要なAPIでは定義しません。

```python
import abc
from typing import Protocol

from domain.value_objects.file_data import FileStream


class FileStorageDomainService(Protocol):
    """
    ファイルストレージへの永続化を抽象化したドメインサービスインターフェース。
    トレーニングファイルおよび訓練済みモデルを保存し、ワーカーがアクセス可能なパスを返す。
    具体的なストレージ実装（S3、GCS、ローカルFS等）はインフラ層に委譲される。
    """
    
    @abc.abstractmethod
    def save_training_file(self, uploaded_file: FileStream, unique_id: str) -> str:
        """
        訓練データとしてアップロードされたファイルストリームを保存し、ワーカーがアクセスできるパスを返す。

        Args:
            uploaded_file: 抽象ファイルストリームオブジェクト。
            unique_id: ファイル名の一意性を確保するためのID（例: Agent ID）。

        Returns:
            str: 永続化されたファイルの絶対パス。
        """
        ...
        
    @abc.abstractmethod
    def save_training_model(self, model_artifact: FileStream, unique_id: str) -> str:
        """
        訓練済みモデルの成果物（アーティファクト）を保存し、デプロイワーカーがアクセスできるパスを返す。

        Args:
            model_artifact: 訓練済みモデルのデータストリームを持つ抽象オブジェクト。
            unique_id: モデルを特定するための一意なID（例: Agent ID、または Agent ID + Version）。

        Returns:
            str: 永続化されたモデルファイルの絶対パス。
        """
        ...
```

3.  **リポジトリ・インターフェースの定義:**
    * リポジトリインターフェースは、**対応するエンティティと同じファイル内に定義**します（例: `domain/entities/agent.py`に`Agent`と`AgentRepository`の両方を定義）。
    * リポジトリで定義するメソッドは **CRUD操作のみ** です: **Create（作成）**、**Read（読み取り）**、**Update（更新）**、**Delete（削除）**
    * 例: `create`, `find_by_id`, `find_all`, `update`, `delete`
    * 上記の`Agent`と`AgentRepository`のコード例を参照してください。

### Step 2: ユースケース層 (src/usecase/)

**責務:** アプリケーション固有のロジック（どういう流れで実行するか）を実装します。

**依存関係の原則:**  
ユースケース層は **ドメイン層のオブジェクトのみ** を使用してコードを書きます。
- 使用可能: `domain/entities/`, `domain/value_objects/`, `domain/services/`（インターフェース）, `domain/repositories/`（インターフェース）
- 使用禁止: `infrastructure`, `adapter`, 外部ライブラリ（DB、API クライアントなど）

注意（Usecaseの実装範囲）:
- 入出力DTO、Presenter、Interactor、Factoryのみ作る。ログ、メトリクス、リトライ、キャッシュ等は要件がない限り追加しない。
- 例外やエラー整形はPresenterとControllerで行い、Interactor内で過剰なハンドリングをしない。

1.  **ユースケースの作成:**
      * `src/usecase/create_agent.py`を作成します。
      * 以下の要素を定義します:
        - **Usecaseインターフェース** (`CreateAgentUseCase` Protocol)
        - **Input DTO** (`CreateAgentInput`)
        - **Output DTO** (`CreateAgentOutput`)
        - **Presenterインターフェース** (`CreateAgentPresenter`)
        - **Interactor（実装クラス）** (`CreateAgentInteractor`)
        - **ファクトリ関数** (`new_create_agent_interactor`)
2.  **依存性の注入 (DI):**
      * Interactorのコンストラクタ（`__init__`）で、Step 1で定義した**インターフェース**（リポジトリ、ドメインサービスなど）とPresenterを受け取ります。
      * **注意:** `infrastructure`層の具体的な実装に依存してはいけません。

**コード例 (`create_agent.py`):**

```python
import abc
from dataclasses import dataclass
from typing import Protocol, Tuple, Optional

from domain.entities.agent import Agent, AgentRepository
from domain.services.auth_service import AuthDomainService
from domain.value_objects.id import ID


# ======================================
# Usecaseのインターフェース定義（Protocol）
# ======================================
class CreateAgentUseCase(Protocol):
    def execute(
        self, input: "CreateAgentInput"
    ) -> tuple["CreateAgentOutput", Exception | None]:
        ...


# ======================================
# Input DTO
# ======================================
@dataclass
class CreateAgentInput:
    token: str
    name: str
    description: Optional[str]


# ======================================
# Output DTO
# ======================================
@dataclass
class CreateAgentOutput:
    id: int
    user_id: int
    owner: str
    name: str
    description: Optional[str]


# ======================================
# Presenterのインターフェース定義
# ======================================
class CreateAgentPresenter(abc.ABC):
    @abc.abstractmethod
    def output(self, agent: Agent) -> CreateAgentOutput:
        pass


# ======================================
# Usecaseの具体的な実装（Interactor）
# ======================================
class CreateAgentInteractor:
    def __init__(
        self,
        presenter: CreateAgentPresenter,
        agent_repo: AgentRepository,
        auth_service: AuthDomainService,
        timeout_sec: int = 10,
    ):
        self.presenter = presenter
        self.agent_repo = agent_repo
        self.auth_service = auth_service
        self.timeout_sec = timeout_sec

    def execute(
        self, input: CreateAgentInput
    ) -> tuple[CreateAgentOutput, Exception | None]:
        try:
            # トークンを検証してユーザー情報を取得
            user = self.auth_service.verify_token(input.token)

            # Agentエンティティを生成（ファクトリ関数を使用）
            agent_to_create = NewAgent(
                id=0,  # IDはDBで自動採番される
                user_id=user.id.value,
                owner=user.username,
                name=input.name,
                description=input.description,
            )

            # リポジトリに永続化を委譲
            created_agent = self.agent_repo.create(agent_to_create)

            # Presenterに渡してOutput DTOに変換
            output = self.presenter.output(created_agent)
            return output, None
            
        except Exception as e:
            # エラー時は空のDTOと例外を返す
            empty_output = CreateAgentOutput(
                id=0, user_id=0, owner="", name="", description=""
            )
            return empty_output, e


# ======================================
# Usecaseインスタンスを生成するファクトリ関数
# ======================================
def new_create_agent_interactor(
    presenter: CreateAgentPresenter,
    agent_repo: AgentRepository,
    auth_service: AuthDomainService,
    timeout_sec: int = 10,
) -> CreateAgentUseCase:
    return CreateAgentInteractor(
        presenter=presenter,
        agent_repo=agent_repo,
        auth_service=auth_service,
        timeout_sec=timeout_sec,
    )
```

### Step 3: インフラ層 (src/infrastructure/) - 実装

**責務:** `domain`層で定義されたインターフェースの「具体的な実装」を行います。

1.  **データベース設定 (config.py):**
      * 各データストアフォルダの直下に`config.py`を配置します。
      * データベース接続情報を環境変数から読み込むファクトリ関数を定義します。

**コード例 (MySQL設定: `infrastructure/database/mysql/config.py`):**

```python
import os
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class MySQLConfig:
    """
    MySQLデータベースへの接続情報を保持するデータクラス。
    """
    host: str
    port: int
    user: str
    password: str
    database: str

def NewMySQLConfigFromEnv() -> MySQLConfig:
    """
    .envファイルから環境変数を読み込み、MySQLConfigインスタンスを生成するファクトリ関数。

    プロジェクトのルートに、以下のような内容で.envファイルを作成してください:
    DB_HOST=db
    DB_PORT=3306
    DB_USER=root
    DB_PASSWORD=your_local_password
    DB_NAME=method_selector_db
    """
    load_dotenv()

    host = os.getenv("DB_HOST")
    port_str = os.getenv("DB_PORT")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_NAME")

    if not all([host, port_str, user, password, database]):
        raise ValueError(".envファイルに必要なデータベース設定がすべて含まれていません。")

    try:
        port = int(port_str)
    except ValueError:
        raise ValueError("DB_PORTは有効な整数である必要があります。")

    return MySQLConfig(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
    )
```

2.  **リポジトリの実装:**
      * `src/infrastructure/database/`配下に、使用するデータベース技術ごとのディレクトリを作成します。
      * **SQL**: `mysql/`, `postgresql/`, `sqlite/` など
      * **NoSQL**: `mongodb/`（ドキュメント）, `redis/`（KVS/キャッシュ）, `dynamodb/`（KVS） など
      * 各フォルダ直下に必ず`config.py`を配置し、その後リポジトリ実装ファイルを作成します。
      * エンティティファイル内で定義したリポジトリインターフェースを継承し、実装クラスを定義します。
      * 各DB技術固有のライブラリ（SQLAlchemy、PyMongo、redis-py、boto3など）を使ってCRUDメソッドを実装します。

**コード例 (リポジトリ実装: `infrastructure/database/mysql/agent_repository.py`):**

```python
import mysql.connector
from mysql.connector import pooling
from typing import Optional
from contextlib import contextmanager

from domain.entities.agent import Agent, NewAgent, AgentRepository
from domain.value_objects.id import ID
from .config import MySQLConfig


class MySQLAgentRepository(AgentRepository):
    """
    AgentRepository の MySQL 実装
    """

    def __init__(self, config: MySQLConfig):
        try:
            self.pool = pooling.MySQLConnectionPool(
                pool_name="agent_repo_pool",
                pool_size=5,
                pool_reset_session=True,
                host=config.host,
                port=config.port,
                user=config.user,
                password=config.password,
                database=config.database
            )
        except mysql.connector.Error as err:
            print(f"Error initializing agent connection pool: {err}")
            raise

    @contextmanager
    def _get_cursor(self, commit: bool = False):
        """
        コネクションプールからカーソルを取得し、処理後にクローズするコンテキストマネージャ
        """
        conn = None
        cursor = None
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor()
            yield cursor
            if commit:
                conn.commit()
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            print(f"Database error in agent repository: {err}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def _map_row_to_agent(self, row: tuple) -> Optional[Agent]:
        """
        DBから取得した単一の行(タプル)をAgentドメインオブジェクトに変換する
        """
        if not row:
            return None
        
        # (id, user_id, owner, name, description) の順序を想定
        return NewAgent(
            id=row[0],
            user_id=row[1],
            owner=row[2],
            name=row[3],
            description=row[4]
        )

    def create(self, agent: Agent) -> Agent:
        sql = """
        INSERT INTO agents (user_id, owner, name, description)
        VALUES (%s, %s, %s, %s)
        """
        data = (
            agent.user_id.value,
            agent.owner,
            agent.name,
            agent.description
        )

        with self._get_cursor(commit=True) as cursor:
            cursor.execute(sql, data)
            new_id = cursor.lastrowid

        # 新しく採番されたIDでAgentオブジェクトを再構築して返す
        return NewAgent(
            id=new_id,
            user_id=agent.user_id.value,
            owner=agent.owner,
            name=agent.name,
            description=agent.description
        )

    def find_by_id(self, agent_id: ID) -> Optional[Agent]:
        sql = "SELECT id, user_id, owner, name, description FROM agents WHERE id = %s"
        with self._get_cursor() as cursor:
            cursor.execute(sql, (agent_id.value,))
            row = cursor.fetchone()
        
        return self._map_row_to_agent(row)

    def list_by_user_id(self, user_id: ID) -> list[Agent]:
        sql = "SELECT id, user_id, owner, name, description FROM agents WHERE user_id = %s ORDER BY id"
        with self._get_cursor() as cursor:
            cursor.execute(sql, (user_id.value,))
            rows = cursor.fetchall()
            
        return [self._map_row_to_agent(row) for row in rows if row]

    def find_all(self) -> list[Agent]:
        sql = "SELECT id, user_id, owner, name, description FROM agents ORDER BY id"
        with self._get_cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            
        return [self._map_row_to_agent(row) for row in rows if row]

    def update(self, agent: Agent) -> None:
        sql = """
        UPDATE agents
        SET name = %s, description = %s
        WHERE id = %s AND user_id = %s
        """
        data = (
            agent.name,
            agent.description,
            agent.id.value,
            agent.user_id.value
        )
        
        with self._get_cursor(commit=True) as cursor:
            cursor.execute(sql, data)

    def delete(self, agent_id: ID) -> None:
        sql = "DELETE FROM agents WHERE id = %s"
        with self._get_cursor(commit=True) as cursor:
            cursor.execute(sql, (agent_id.value,))
```

2.  **ドメインサービスの実装:**
      * `src/infrastructure/services/auth_service_impl.py`を作成します。
      * `domain/services/`で定義したドメインサービスインターフェースを実装します。
      * 外部API、認証ライブラリなど、具体的な技術を使用できます。

**コード例 (ドメインサービス実装: `infrastructure/services/auth_service_impl.py`):**

```python
from domain.services.auth_service import AuthDomainService
from domain.entities.user import User
from domain.value_objects.id import ID
import jwt  # 外部ライブラリの使用OK

class AuthServiceImpl(AuthDomainService):
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def verify_token(self, token: str) -> User:
        # JWTトークンを検証してユーザー情報を返す
        payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
        return User(
            id=ID(payload["user_id"]),
            username=payload["username"]
        )
```

3.  **ファイルストレージサービスの実装（APIでファイルデータを扱う場合）:**
      * APIでファイルアップロード/ダウンロードを扱う場合、`src/infrastructure/services/file_storage_domain_service_impl.py`を作成します。
      * `domain/services/file_storage_domain_service.py`で定義したインターフェースを実装します。
      * 実際のストレージクライアント（`infrastructure/storage/s3_client.py`など）を使用してファイルを保存します。

**コード例 (ファイルストレージサービス実装: `infrastructure/services/file_storage_domain_service_impl.py`):**
```python
from domain.services.file_storage_domain_service import FileStorageDomainService
from domain.value_objects.file_data import FileStream
from infrastructure.storage.s3_client import S3Client  # 具体的なストレージクライアント


class FileStorageDomainServiceImpl(FileStorageDomainService):
    def __init__(self, storage_client: S3Client, base_path: str = "training-data"):
        self.storage_client = storage_client
        self.base_path = base_path
    
    def save_training_file(self, uploaded_file: FileStream, unique_id: str) -> str:
        # S3やGCSなどにファイルを保存し、パスを返す
        object_key = f"{self.base_path}/{unique_id}/{uploaded_file.filename}"
        self.storage_client.upload(object_key, uploaded_file.file_stream)
        return f"s3://bucket-name/{object_key}"  # または絶対パス
    
    def save_training_model(self, model_artifact: FileStream, unique_id: str) -> str:
        object_key = f"models/{unique_id}/{model_artifact.filename}"
        self.storage_client.upload(object_key, model_artifact.file_stream)
        return f"s3://bucket-name/{object_key}"


def NewFileStorageDomainService() -> FileStorageDomainService:
    """ファクトリ関数でストレージクライアントを初期化"""
    s3_client = S3Client(bucket="your-bucket-name")  # 設定から読み込み
    return FileStorageDomainServiceImpl(s3_client)
```

4.  **その他の外部連携:**
      * `src/infrastructure/storage/`に外部ストレージクライアント（S3、GCSなど）の低レベル実装を配置します。
      * 必要に応じて、メール送信、通知サービスなどの実装もここに配置します。

### Step 4: アダプタ層 (src/adapter/) - 翻訳

**責務:** HTTPリクエストとユースケース層の「翻訳」を行います。

1.  **コントローラーの作成:**
      * `src/adapter/controller/create_agent_controller.py`を作成します。
      * `CreateAgentController`クラスを定義します。
      * コンストラクタで`CreateAgentUseCase`を受け取ります。
      * HTTPリクエスト（Input DTO）を受け取り、ユースケースを呼び出し、ステータスコードとレスポンスを返します。
2.  **プレゼンターの作成:**
      * `src/adapter/presenter/create_agent_presenter.py`を作成します。
      * `CreateAgentPresenter`インターフェースを実装し、エンティティを Output DTO に変換します。
      * ファクトリ関数を定義してPresenterインスタンスを生成します。

**コード例 (コントローラー: `adapter/controller/create_agent_controller.py`):**

```python
from typing import Union
from usecase.create_agent import (
    CreateAgentUseCase,
    CreateAgentInput,
    CreateAgentOutput,
)


class CreateAgentController:
    def __init__(self, uc: CreateAgentUseCase):
        self.uc = uc

    def execute(
        self, input_data: CreateAgentInput
    ) -> dict[str, Union[int, CreateAgentOutput, dict[str, str]]]:
        try:
            output, err = self.uc.execute(input_data)
            if err:
                # エラーの種類に応じてHTTPステータスコードを決定
                error_msg = str(err)
                if "Auth" in error_msg or "token" in error_msg.lower():
                    # 認証系エラー
                    return {"status": 401, "data": {"error": error_msg}}
                elif "Invalid" in error_msg or "not found" in error_msg.lower():
                    # リクエストの不正値
                    return {"status": 400, "data": {"error": error_msg}}
                else:
                    # その他のエラー
                    return {"status": 500, "data": {"error": error_msg}}
            
            # 成功
            return {"status": 201, "data": output}
        except Exception as e:
            # 予期せぬサーバーエラー
            return {"status": 500, "data": {"error": f"An unexpected error occurred: {e}"}}
```

**コード例 (プレゼンター: `adapter/presenter/create_agent_presenter.py`):**

```python
from usecase.create_agent import CreateAgentPresenter, CreateAgentOutput
from domain.entities.agent import Agent


class CreateAgentPresenterImpl(CreateAgentPresenter):
    def output(self, agent: Agent) -> CreateAgentOutput:
        """
        Agentドメインオブジェクトを CreateAgentOutput DTO に変換して返す。
        """
        return CreateAgentOutput(
            id=agent.id.value,
            user_id=agent.user_id.value,
            owner=agent.owner,
            name=agent.name,
            description=agent.description,
        )


def new_create_agent_presenter() -> CreateAgentPresenter:
    """
    CreateAgentPresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return CreateAgentPresenterImpl()
```

注意（Adapterの実装範囲）:
- ControllerはUsecase呼び出しとステータス整形に限定。追加のバリデーションやビジネスロジックは入れない。
- PresenterはDTO変換のみに限定。フォーマット変換の拡張（日時フォーマットの設定化など）は不要。

### Step 5: インフラ層 (src/infrastructure/) - 接続

**責務:** すべての部品を「接続」し、FastAPIエンドポイントとして公開します。

1.  **ルーター内での依存解決（簡易DI）:**
      * `src/infrastructure/router/fastapi.py`内で、設定読み込み（`NewMySQLConfigFromEnv`）→リポジトリ/サービスのインスタンス化→ユースケース/コントローラーの生成を行います。
      * これにより、専用DIコンテナなしでルーターファイルに依存関係を集約できます。

**雛形 (`infrastructure/router/fastapi.py`):**

```python
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse

# 設定と依存の初期化
from infrastructure.database.mysql.config import NewMySQLConfigFromEnv
from infrastructure.database.mysql.agent_repository import MySQLAgentRepository
from infrastructure.services.auth_service_impl import AuthServiceImpl

from adapter.controller.create_agent_controller import CreateAgentController
from adapter.presenter.create_agent_presenter import new_create_agent_presenter
from usecase.create_agent import CreateAgentInput, new_create_agent_interactor

router = APIRouter()
oauth2_scheme = HTTPBearer()
db_config = NewMySQLConfigFromEnv()
agent_repo = MySQLAgentRepository(db_config)
auth_service = AuthServiceImpl(secret_key="<replace-with-secret>")
ctx_timeout = 10.0

def build_create_agent_controller() -> CreateAgentController:
    presenter = new_create_agent_presenter()
    usecase = new_create_agent_interactor(presenter, agent_repo, auth_service, ctx_timeout)
    return CreateAgentController(usecase)

@router.post("/v1/agents")
def create_agent(request: CreateAgentInput, credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    controller = build_create_agent_controller()
    input_data = CreateAgentInput(
        token=credentials.credentials,
        name=request.name,
        description=request.description,
    )
    response = controller.execute(input_data)
    # 共通レスポンス整形は別関数に切り出してもOK
    return JSONResponse(content=response["data"], status_code=response["status"])
```

#### fastapi.py の進化ガイド（複数エンドポイント・共通ヘルパ・サービス集約）

単一のエンドポイントから、次のような構成へ段階的に進化させます。

- 共通レスポンス整形ヘルパ `handle_response()` を用意（`dataclass`の`datetime`をISO文字列へ変換、`StreamingResponse`は透過返却、成功/エラーのHTTPステータス統一）。
- PydanticのRequest DTOをルーター直下で定義し、Adapter層のOutput DTOを`response_model`で明示。
- 認証は `HTTPBearer` を使い、`NewAuthDomainService(user_repo)` を都度生成または共有。
- 主要リポジトリ・サービス類（ユーザー/エージェント/ジョブ/可視化/デプロイメント/メソッド）をファイル先頭で初期化し、各ルートでPresenter/Usecase/Controllerを生成。
- 非同期の外部呼び出し用に `httpx.AsyncClient` を初期化し、デプロイテストドメインサービスへ注入。
- ファイルアップロードはFastAPIの`UploadFile`を受け取り、ドメイン層の`UploadedFileStream`適合アダプタに変換してUsecaseへ渡す。

スケルトン例（抜粋・要点のみ）：

```python
from typing import Optional
from dataclasses import is_dataclass, asdict
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, Response, StreamingResponse
from pydantic import BaseModel
import httpx

# --- Repositories / Config ---
from infrastructure.database.mysql.config import NewMySQLConfigFromEnv
from infrastructure.database.mysql.user_repository import MySQLUserRepository
from infrastructure.database.mysql.agent_repository import MySQLAgentRepository
from infrastructure.database.mysql.finetuning_job_repository import MySQLFinetuningJobRepository
from infrastructure.database.mysql.weight_visualization_repository import MySQLWeightVisualizationRepository
from infrastructure.database.mysql.deployment_repository import MySQLDeploymentRepository
from infrastructure.database.mysql.methods_repository import MySQLMethodsRepository

# --- Domain Services Implementations ---
from infrastructure.services.auth_domain_service_impl import AuthServiceImpl
from infrastructure.services.file_storage_domain_service_impl import FileStorageDomainServiceImpl
from infrastructure.services.job_queue_domain_service_impl import JobQueueDomainServiceImpl
from infrastructure.services.system_time_domain_service_impl import SystemTimeDomainServiceImpl
from infrastructure.services.get_image_stream_domain_service_impl import FileStreamDomainServiceImpl
from infrastructure.services.job_method_finder_domain_service_impl import JobMethodFinderDomainServiceImpl
from infrastructure.services.deployment_test_domain_service_impl import DeploymentTestDomainServiceImpl

# --- Controllers / Presenters / Usecases ---
from adapter.controller.create_agent_controller import CreateAgentController
from adapter.presenter.create_agent_presenter import new_create_agent_presenter
from usecase.create_agent import CreateAgentInput, CreateAgentOutput, new_create_agent_interactor

# ...他のAuth/User/Jobs/Deploymentsのインポートも同様に追加...

router = APIRouter()
db_config = NewMySQLConfigFromEnv()
user_repo = MySQLUserRepository(db_config)
agent_repo = MySQLAgentRepository(db_config)
finetuning_job_repo = MySQLFinetuningJobRepository(db_config)
weight_visualization_repo = MySQLWeightVisualizationRepository(db_config)
deployment_repo = MySQLDeploymentRepository(db_config)
methods_repo = MySQLMethodsRepository(db_config)

file_storage_service = FileStorageDomainServiceImpl(storage_client=None)  # S3やGCSクライアントを注入
job_queue_service = JobQueueDomainServiceImpl()
system_time_service = SystemTimeDomainServiceImpl()
file_stream_service = FileStreamDomainServiceImpl()
job_method_finder_service = JobMethodFinderDomainServiceImpl(timeout=5)
auth_service = AuthServiceImpl(user_repo)

oauth2_scheme = HTTPBearer()
ctx_timeout = 10.0
async_http_client = httpx.AsyncClient(timeout=15.0)
test_inference_service = DeploymentTestDomainServiceImpl(client=async_http_client)

def handle_response(response_dict: dict, success_code: int = 200):
    status_code = response_dict.get("status", 500)
    data = response_dict.get("data")
    if isinstance(data, StreamingResponse):
        return data
    if is_dataclass(data):
        data = asdict(data)
        def convert_datetime_to_str(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, dict):
                return {k: convert_datetime_to_str(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [convert_datetime_to_str(v) for v in obj]
            return obj
        data = convert_datetime_to_str(data)
    if status_code >= 400:
        return JSONResponse(content=data, status_code=status_code)
    if success_code == 204:
        return Response(status_code=204)
    return JSONResponse(content=data, status_code=success_code)

class CreateAgentRequest(BaseModel):
    name: str
    description: Optional[str]

@router.post("/v1/agents", response_model=CreateAgentOutput)
def create_agent(request: CreateAgentRequest, credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    token = credentials.credentials
    presenter = new_create_agent_presenter()
    auth_service = NewAuthDomainService(user_repo)
    usecase = new_create_agent_interactor(presenter, agent_repo, auth_service, ctx_timeout)
    controller = CreateAgentController(usecase)
    input_data = CreateAgentInput(token=token, name=request.name, description=request.description)
    response_dict = controller.execute(input_data)
    return handle_response(response_dict, success_code=201)
```

上記パターンを踏襲して、Auth（signup/login/me）、Agent（一覧/作成/全件）、Finetuning Job（作成/一覧/可視化）、Deployment（作成/取得/メソッド取得・設定/テスト）、ファイルストリーム（画像可視化の配信）などのルートを同様に構築します。

補足:
- 依存の共有/生成方針は「リポジトリ/サービスは原則共有、Presenter/Usecase/Controllerは各リクエストで生成」。
- `httpx.AsyncClient` はアプリ終了時に`aclose()`が必要。Lifespan管理や`startup/shutdown`イベントでクリーンアップする設計を推奨。
- `response_model` には Adapter層の Output DTO を指定し、FastAPIによるスキーマ公開を活用。
- 大規模化したら、ルーターを複数モジュールに分割して`app.include_router()`で統合。

禁止事項（過剰実装の防止）:
- 依頼がないのに新規の共通ライブラリや設定モジュールを追加しない。
- 例示されていないルート/DTO/サービスを勝手に拡張しない。
- ドキュメントの雛形をすべて同時に導入しない。必要な部分のみ差し込む。
- レイヤー原則に反する依存を作らない（Usecase→Infra/Adapterへの直接参照など）。

最終チェックリスト:
- スコープ外のファイル変更をしていないか。
- 追加箇所が最小限（ルート、DTO、Presenter、Interactor、Repo/Serviceの必要分）か。
- エラーハンドリングはController/Presenterで十分か（Interactorで過剰に抱え込んでいないか）。
- 既存の命名・配置に整合しているか。
- Run/起動方法に影響がないか（`main.py`と`router`の構成は既存どおり）。

### Step 6: 起動ファイル (src/main.py)

**責務:** アプリケーション起動時に、FastAPIインスタンスを初期化し、全体を統合します。

- FastAPIインスタンスを作成します。
- CORSミドルウェアを設定し、フロントエンドからのアクセスを許可します。
- Step 5で定義したルーターを組み込みます。
- ヘルスチェックなどの基本エンドポイントを定義します。
- `src/infrastructure/router/fastapi.py`で定義された`app`をUvicornで起動します。

**コード例 (`main.py`):**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from infrastructure.router.fastapi import router

# FastAPIインスタンスを作成
app = FastAPI(
    title="Your API Title",
    description="A FastAPI application description.",
    version="0.1.0",
)

# フロントエンドからのアクセスを許可するためのCORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターを組み込む
app.include_router(router)


@app.get("/")
def read_root():
    """
    ルートエンドポイント
    """
    return {"message": "Hello from Backend!"}


@app.get("/health")
def health_check():
    """
    ヘルスチェック用エンドポイント
    """
    return {"status": "ok"}
```

**起動方法:**

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

- `--reload`: ファイル変更時に自動リロード（開発環境用）
- `--host 0.0.0.0`: すべてのインターフェースでリッスン
- `--port 8000`: ポート8000で起動

---

## テスト設計と実装ガイドライン

本プロジェクトでは、クリーンアーキテクチャの階層構造に基づき、テストの責務を明確に分離します。AIおよび開発者は、新規機能を実装する際、必ず以下の構造とテンプレートに従ってテストを作成してください。

### 1. テストフォルダ構成

`tests/`ディレクトリはプロジェクトルート（`src/`と同階層）に配置し、**テストの性質（外部接続の有無）**で大分類します。

```
backend/
├─ src/                  # アプリケーションコード
├─ tests/                # テストコード
│  ├─ conftest.py        # 共通フィクスチャ（DB接続、Mock設定など）
│  ├─ factories/         # テストデータ生成用（polyfactory推奨）
│  ├─ unit/              # ★ 単体テスト（DB/Networkなし、高速）
│  │  ├─ domain/         # 値オブジェクト・エンティティ
│  │  ├─ usecase/        # ビジネスロジック（最重要）
│  │  └─ adapter/        # Controller/Presenter
│  └─ integration/       # ★ 統合テスト（DB/Networkあり、低速）
│     ├─ infrastructure/ # Repository実装（実DB検証）
│     └─ api/            # E2Eエンドポイント検証
├─ pytest.ini            # pytest設定
└─ requirements.txt
```

### 2. 環境設定とルール

#### 必須ライブラリ

```
pytest
pytest-mock
pytest-asyncio
httpx
```

#### 設定ファイル (pytest.ini)

プロジェクトルートに配置し、srcモジュールを解決可能にします。

```ini
[pytest]
pythonpath = .
testpaths = tests
asyncio_mode = auto
```

#### 共通フィクスチャ (tests/conftest.py)

DB接続や共通のMock定義はここに集約します。

```python
import pytest
from infrastructure.database.mysql.config import MySQLConfig
from infrastructure.database.mysql.agent_repository import MySQLAgentRepository

@pytest.fixture
def db_config():
    return MySQLConfig(host="test_db", port=3306, user="root", password="pw", database="test")

@pytest.fixture
def agent_repo(db_config):
    return MySQLAgentRepository(db_config)
```

### 3. 各層のテスト実装テンプレート（AIリファレンス）

重要: 新規クラスを実装する際は、以下のテンプレートパターンを厳守してください。

#### A. Domain層 (Unit Test)

**配置**: `tests/unit/domain/`

**責務**: バリデーションやドメインロジックの検証。DB接続不可。

```python
# tests/unit/domain/entities/test_agent.py
import pytest
from domain.entities.agent import NewAgent
from domain.value_objects.id import ID

class TestAgent:
    def test_new_agent_valid(self):
        """正常系: 正しい値でエンティティが生成されること"""
        agent = NewAgent(id=1, user_id=100, owner="test_user", name="MyAgent", description="desc")
        assert agent.id == ID(1)
        assert agent.name == "MyAgent"

    def test_new_agent_invalid_name(self):
        """異常系: バリデーションエラー"""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            NewAgent(id=1, user_id=100, owner="test_user", name="", description="desc")
```

#### B. Usecase層 (Unit Test) ★最重要

**配置**: `tests/unit/usecase/`

**責務**: ビジネスフローの検証。全ての依存（Repo, Service）をMock化すること。

```python
# tests/unit/usecase/test_create_agent.py
import pytest
from unittest.mock import Mock
from usecase.create_agent import CreateAgentInteractor, CreateAgentInput, CreateAgentOutput
from domain.entities.agent import NewAgent

class TestCreateAgentInteractor:
    @pytest.fixture
    def mocks(self, mocker):
        return {
            "presenter": mocker.Mock(),
            "repo": mocker.Mock(),
            "auth_service": mocker.Mock(),
        }

    def test_execute_success(self, mocks):
        """正常系: 依存コンポーネントが正しく連携するか"""
        # Arrange
        input_data = CreateAgentInput(token="valid", name="Agent", description="desc")
        mocks["auth_service"].verify_token.return_value = Mock(id=Mock(value=99), username="tester")
        mocks["repo"].create.return_value = NewAgent(id=1, user_id=99, owner="tester", name="Agent", description="desc")
        mocks["presenter"].output.return_value = CreateAgentOutput(id=1, user_id=99, owner="tester", name="Agent", description="desc")

        interactor = CreateAgentInteractor(mocks["presenter"], mocks["repo"], mocks["auth_service"])

        # Act
        result, err = interactor.execute(input_data)

        # Assert
        assert err is None
        assert result.id == 1
        mocks["repo"].create.assert_called_once()  # 呼び出し確認
```

#### C. Adapter層 (Unit Test)

**配置**: `tests/unit/adapter/`

**責務**: Controllerのステータスコード振り分けやPresenterの変換ロジック検証。

```python
# tests/unit/adapter/controller/test_create_agent_controller.py
from adapter.controller.create_agent_controller import CreateAgentController
from usecase.create_agent import CreateAgentInput, CreateAgentOutput

def test_controller_success(mocker):
    # Arrange
    mock_usecase = mocker.Mock()
    mock_usecase.execute.return_value = (CreateAgentOutput(1, 1, "owner", "name", "desc"), None)
    controller = CreateAgentController(mock_usecase)

    # Act
    response = controller.execute(CreateAgentInput("token", "name", "desc"))

    # Assert
    assert response["status"] == 201
    assert response["data"].id == 1
```

#### D. Infrastructure層 (Integration Test)

**配置**: `tests/integration/infrastructure/`

**責務**: 実際にDBに接続し、SQLの正当性とCRUD動作を確認する。

```python
# tests/integration/infrastructure/mysql/test_agent_repository.py
import pytest
from infrastructure.database.mysql.agent_repository import MySQLAgentRepository
from domain.entities.agent import NewAgent

# conftest.py の db_config フィクスチャを利用
def test_repository_crud(db_config):
    # Setup
    repo = MySQLAgentRepository(db_config)
    agent = NewAgent(0, 1, "owner", "RepoTest", "desc")

    # Create & Read
    created = repo.create(agent)
    found = repo.find_by_id(created.id)
    assert found.name == "RepoTest"
    
    # Delete
    repo.delete(created.id)
    assert repo.find_by_id(created.id) is None
```

#### E. API End-to-End (Integration Test)

**配置**: `tests/integration/api/`

**責務**: ルーター設定、DIの結合、HTTPレスポンスの統合確認。

```python
# tests/integration/api/test_agents_api.py
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_post_agents_e2e():
    """DBまで貫通してAPIが成功するか検証"""
    response = client.post(
        "/v1/agents",
        json={"name": "E2E Agent", "description": "integration"},
        headers={"Authorization": "Bearer mock_valid_token"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "E2E Agent"
```

### 4. 実行コマンド

```bash
pytest                  # 全テスト実行
pytest tests/unit       # Unitテストのみ（開発中推奨）
pytest tests/integration # DB接続テストのみ
pytest -v               # 詳細出力
pytest -k "create_agent" # パターンマッチ実行
```
