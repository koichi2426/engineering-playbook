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
│  ├─ database/          # DBセッション, Engine, SQLAlchemyモデル
│  │  └─ mysql/          # リポジトリの実装: user_repository.py 等
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

1.  **リポジトリの実装:**
      * `src/infrastructure/database/mysql/agent_repository.py`を作成します。
      * `IAgentRepository`を継承し、`AgentRepositoryImpl`クラスを定義します。
      * SQLAlchemyの`Session`など、具体的なDB技術を使って`create`メソッドを実装します。

**コード例 (`agent_repository.py`):**

```python
from src.domain.repositories.agent_repository import IAgentRepository
from src.domain.entities.agent import Agent
from sqlalchemy.orm import Session
# from src.infrastructure.database.models import AgentModel

class AgentRepositoryImpl(IAgentRepository):
    def __init__(self, db_session: Session):
        self.db = db_session

    def create(self, agent: Agent) -> Agent:
        # DBモデルへの変換とSQLAlchemyでの永続化処理
        # ...
        return agent
```

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
