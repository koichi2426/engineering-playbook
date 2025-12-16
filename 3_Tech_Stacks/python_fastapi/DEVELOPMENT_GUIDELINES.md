# プロジェクト構成と開発ガイドライン (FastAPI)

このドキュメントは、フォルダ構成（What/Where）と新規API追加の標準的な開発手順（How）を1つにまとめたものです。クリーンアーキテクチャの4層に基づき、配置場所と手順の両方をここで参照できます。

---

## プロジェクト構成 (概要)

この構成は、`2_Concepts/clean_architecture.md`で定義した4層の責務に基づいています。

### 1. フォルダ構成 (Root)

ツリー表示（階層が一目で分かるように整形）：

```
backend/
├─ Dockerfile
├─ docker-compose.yml
├─ .env.example
├─ requirements.txt
├─ alembic.ini
├─ alembic/              # DBマイグレーションスクリプト
└─ src/                  # ★ すべてのアプリケーションコード
```

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
│  │  ├─ mysql/          # MySQLリポジトリ実装
│  │  ├─ postgresql/     # PostgreSQLリポジトリ実装（例）
│  │  ├─ mongodb/        # MongoDBリポジトリ実装（例）
│  │  └─ redis/          # Redisキャッシュ実装（例）
│  ├─ services/          # 外部連携・ドメインサービス等の具体実装
│  ├─ router/            # FastAPIルーティング: fastapi.py
│  ├─ di/                # 依存性注入コンテナ
│  └─ storage/           # 外部ストレージクライアント
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
    - 内容: `database/mysql/`, `services/`, `router/`, `di/`
* `src/main.py`
    - 責務: アプリケーションの起動
    - 内容: `infrastructure/router/fastapi.py`で定義したFastAPIアプリを起動

---

## 新規APIの追加手順 (ガイド)

ここでは例として「新しいエージェント（Agent）を作成するAPI」を追加する手順をステップバイステップで示します。

### Step 1: ドメイン層 (src/domain/)

**責務:** ビジネスルール（何ができるか）のインターフェースを定義します。

**使用可能なライブラリ:**  
ドメイン層では外部ライブラリへの依存を避け、以下の標準ライブラリのみ使用します。

```python
import abc
from dataclasses import dataclass, field
from typing import List, Optional
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
    methods: List[Method] = field(default_factory=list)
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

2.  **ドメインサービス・インターフェースの定義:**
    * エンティティや値オブジェクトに当てはまらないビジネスロジックは、`src/domain/services/`にドメインサービスとして定義します。
    * 例: 複数のエンティティにまたがる処理、外部との連携ロジックなど。
    * 命名規則: `[ドメインサービスの名前]_service.py`（例: `auth_service.py`, `notification_service.py`）

**コード例 (ドメインサービス: `domain/services/deployment_test_service.py`):**
```python
import abc
from typing import Protocol

from domain.value_objects.file_data import UploadedFileStream 
from domain.value_objects.deployment_test_result import DeploymentTestResult 

    
class DeploymentTestDomainService(Protocol):
    """
    デプロイされた推論エンジンに対するテスト実行ロジックを
    カプセル化するドメインサービスインターフェース。
    """
    
    @abc.abstractmethod
    async def run_batch_inference_test(
        self, 
        test_file: UploadedFileStream,
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
    ) -> Tuple["CreateAgentOutput", Exception | None]:
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
    ) -> Tuple[CreateAgentOutput, Exception | None]:
        try:
            # トークンを検証してユーザー情報を取得
            user = self.auth_service.verify_token(input.token)

            # Agentエンティティを生成
            agent_to_create = Agent(
                id=ID(0),  # IDはDBで自動採番される
                user_id=user.id,
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
from typing import Optional, List
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

    def list_by_user_id(self, user_id: ID) -> List[Agent]:
        sql = "SELECT id, user_id, owner, name, description FROM agents WHERE user_id = %s ORDER BY id"
        with self._get_cursor() as cursor:
            cursor.execute(sql, (user_id.value,))
            rows = cursor.fetchall()
            
        return [self._map_row_to_agent(row) for row in rows if row]

    def find_all(self) -> List[Agent]:
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

3.  **その他の外部連携:**
      * `src/infrastructure/storage/`に外部ストレージクライアント（S3、GCSなど）を実装します。
      * 必要に応じて、メール送信、通知サービスなどの実装もここに配置します。

### Step 4: アダプタ層 (src/adapter/) - 翻訳

**責務:** HTTPリクエストとユースケース層の「翻訳」を行います。

1.  **コントローラーの作成:**
      * `src/adapter/controller/create_agent_controller.py`を作成します。
      * `CreateAgentController`クラスを定義します。
      * コンストラクタで`CreateAgentUseCase`と`CreateAgentPresenter`を受け取ります。
      * HTTPリクエスト（Pydanticモデル）を受け取り、ユースケースを呼び出します。
2.  **プレゼンターの作成:**
      * `src/adapter/presenter/create_agent_presenter.py`を作成します。
      * Pydanticモデルを使い、レスポンスのJSON形式を定義（`AgentResponse`など）し、ユースケースの戻り値（エンティティ）をJSONに変換するロジック（`output`メソッドなど）を提供します。

### Step 5: インフラ層 (src/infrastructure/) - 接続

**責務:** すべての部品を「接続」し、FastAPIエンドポイントとして公開します。

1.  **DIコンテナの設定:**
      * `src/infrastructure/di/`内のDI設定ファイル（例: `container.py`）を編集します。
      * `IAgentRepository`が要求されたら`AgentRepositoryImpl`を返すように、インターフェースと実装を紐付けます。
      * `CreateAgentUseCase`や`CreateAgentController`の依存関係も定義します。
2.  **ルーターの定義:**
      * `src/infrastructure/router/fastapi.py`を編集します。
      * DIコンテナから`CreateAgentController`を取得し、FastAPIのエンドポイント（`@router.post("/agents")`）を定義します。
      * リクエストをコントローラーに渡し、コントローラーからの戻り値（プレゼンターが生成したレスポンス）を返します。

### Step 6: 起動ファイル (src/main.py)

  * `src/main.py`が`src/infrastructure/router/fastapi.py`で定義された`app`をUvicornで起動することを確認します（通常、変更は不要）。
