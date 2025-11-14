# 開発ガイドライン (FastAPI)

このドキュメントは、`project_structure.md`で定義されたフォルダ構成に基づき、新規API（ユースケース）を追加する際の標準的な開発手順を定義します。

---

## 新規APIの追加手順

ここでは例として「新しいエージェント（Agent）を作成するAPI」を追加する手順をステップバイステップで示します。

### Step 1: ドメイン層 (src/domain/)

**責務:** ビジネスルール（何ができるか）のインターフェースを定義します。

1.  **エンティティ / 値オブジェクトの定義:**
    * 必要に応じて`src/domain/entities/agent.py`や`src/domain/value_objects/`に、純粋なPythonクラスとしてエンティティや値オブジェクトを定義（または更新）します。
2.  **リポジトリ・インターフェースの定義:**
    * `src/domain/repositories/agent_repository.py`に、`IAgentRepository`というインターフェース（ABC: 抽象基底クラス）を定義します。
    * 「操作」のみ（例: `create`, `find_by_id`）を定義します。

**コード例 (`IAgentRepository`):**
```python
from abc import ABC, abstractmethod
from src.domain.entities.agent import Agent

class IAgentRepository(ABC):

    @abstractmethod
    def create(self, agent: Agent) -> Agent:
        pass
````

### Step 2: ユースケース層 (src/usecase/)

**責務:** アプリケーション固有のロジック（どういう流れで実行するか）を実装します。

1.  **ユースケースの作成:**
      * `src/usecase/create_agent.py`を作成します。
      * `CreateAgentUseCase`クラスを定義します。
2.  **依存性の注入 (DI):**
      * コンストラクタ（`__init__`）で、Step 1で定義した**インターフェース**（`IAgentRepository`など）を受け取ります。
      * **注意:** `infrastructure`層の具体的な実装（`AgentRepositoryImpl`など）に依存してはいけません。

**コード例 (`create_agent.py`):**

```python
from src.domain.repositories.agent_repository import IAgentRepository
from src.domain.entities.agent import Agent

class CreateAgentUseCase:
    def __init__(self, agent_repo: IAgentRepository):
        self.agent_repo = agent_repo

    def execute(self, name: str, description: str) -> Agent:
        # ドメインのロジックを呼び出し
        new_agent = Agent(name=name, description=description)
        
        # インターフェースを介して永続化
        created_agent = self.agent_repo.create(new_agent)
        return created_agent
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
