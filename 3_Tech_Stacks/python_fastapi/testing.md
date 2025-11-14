はい、承知いたしました。
`python_fastapi`フォルダの3つ目のドキュメントとして、`testing.md`を作成します。

これは、`DEVELOPMENT_GUIDELINES.md`で定義したクリーンアーキテクチャ（特にDIとインターフェース）を**どのようにテストするか**を定義する、品質担保のための重要なファイルです。

-----

```markdown
# テストガイドライン (FastAPI)

このドキュメントは、`pytest`を使用したFastAPIプロジェクトのテスト方針と具体的な手法を定義します。
クリーンアーキテクチャの各層の責務に基づき、テストの種類を分離します。

## 1. 基本方針

1.  **`pytest`の使用:** すべてのテストは`pytest`フレームワークを使用して記述・実行します。
2.  **テストの分離:**
    * **ユニットテスト (Unit Tests):** `domain`層と`usecase`層のロジックをテストします。DBや外部APIには接続しません。
    * **E2E / 統合テスト (E2E Tests):** FastAPIのエンドポイント（HTTP）をテストします。必要に応じてテスト用DBに接続します。
3.  **配置場所:** テストコードはプロジェクトルートの`tests/`ディレクトリに配置します。

```

backend/
├── src/
│   └── ...
└── tests/
├── unit/
│   ├── domain/
│   │   └── test\_agent\_entity.py
│   └── usecase/
│       └── test\_create\_agent\_usecase.py
└── e2e/
└── test\_agent\_api.py

````

---

## 2. ユニットテスト (Unit Tests)

**目的:** ビジネスロジックが単体で正しく動作することを確認する。高速に実行される必要がある。

### A. ドメイン層 (src/domain/) のテスト
* **対象:** エンティティ（`entities/`）、値オブジェクト（`value_objects/`）
* **方法:**
    * `domain`層は純粋なPythonコードであり、外部依存がないため、インスタンスを作成して直接メソッドを呼び出します。
    * （例: `Agent`エンティティの`publish()`メソッドを呼び出し、ステータスが変わることを確認する）

### B. ユースケース層 (src/usecase/) のテスト
* **対象:** `create_agent.py`などのユースケースクラス。
* **方法:**
    * `usecase`層は**インターフェース**（`IAgentRepository`など）にのみ依存しています。この特性を活かし、**モック (Mock)** を使用します。
    * `pytest-mock`を使い、リポジトリ・インターフェースの「偽物（モック）」を作成し、ユースケースのコンストラクタに注入します。
    * これにより、DBに一切接続せず、「ユースケースのロジック（オーケストレーション）」が正しいかだけを高速に検証できます。

**コード例 (`test_create_agent_usecase.py`):**
```python
from src.usecase.create_agent import CreateAgentUseCase
from src.domain.repositories.agent_repository import IAgentRepository
from src.domain.entities.agent import Agent
from unittest.mock import MagicMock

def test_create_agent_usecase_success(mocker: MagicMock):
    # 1. 準備 (Arrange)
    # IAgentRepositoryインターフェースのモックを作成
    mock_agent_repo = mocker.MagicMock(spec=IAgentRepository)
    
    # モックが返すダミーのAgentエンティティを設定
    expected_agent = Agent(id="some-id", name="Test Agent", ...)
    mock_agent_repo.create.return_value = expected_agent

    # 2. 実行 (Act)
    # モックをユースケースに注入してインスタンス化
    usecase = CreateAgentUseCase(agent_repo=mock_agent_repo)
    result = usecase.execute(name="Test Agent", description="...")

    # 3. 検証 (Assert)
    # ユースケースが期待通りにリポジトリのcreateメソッドを呼び出したか検証
    mock_agent_repo.create.assert_called_once()
    
    # 結果がモックが返した値と一致するか検証
    assert result == expected_agent
````

-----

## 3\. E2E / 統合テスト (E2E Tests)

**目的:** HTTPリクエストからDB永続化まで、システム全体が結合して正しく動作することを確認する。

  * **対象:** `infrastructure/router/fastapi.py`で定義されたエンドポイント。
  * **方法:** FastAPIが提供する`TestClient`を使用します。

### A. `TestClient`のセットアップ

`conftest.py`（pytestの共通設定ファイル）で、`TestClient`とテスト用DBセッションを準備します。

### B. DI（依存性）のオーバーライド

  * E2Eテストの最大の鍵は、\*\*DI（依存性の注入）をテスト用に上書き（オーバーライド）\*\*することです。
  * `infrastructure/di/`で定義されたDI設定を、FastAPIの`app.dependency_overrides`機能を使って、テスト用の設定（例: テスト用DBセッション）に差し替えます。

**コード例 (`tests/conftest.py` - 抜粋):**

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- テスト用DBセッションの準備 (例: メモリ内SQLite) ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- DI（依存性）をオーバーライドする設定 ---
from src.infrastructure.di.container import get_db_session # 本物のDI関数
from src.main import app # 本物のFastAPIアプリ

# テスト用DBセッションを返す関数
def override_get_db_session():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# ★ 本物のDB取得関数を、テスト用の関数で上書きする
app.dependency_overrides[get_db_session] = override_get_db_session

@pytest.fixture(scope="function")
def client():
    # ここでテーブル作成などの初期化
    # Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    # ここでテーブル削除などの後片付け
    # Base.metadata.drop_all(bind=engine)
```

### C. テストの実行

`conftest.py`で準備した`client`フィクスチャを使って、HTTPリクエストをシミュレートします。

**コード例 (`tests/e2e/test_agent_api.py`):**

```python
from fastapi.testclient import TestClient

def test_create_agent_e2e(client: TestClient):
    # 1. 準備 (Arrange)
    request_payload = {
        "name": "E2E Test Agent",
        "description": "Test description"
    }

    # 2. 実行 (Act)
    # TestClientがDIオーバーライド済みのアプリにHTTP POSTリクエストを送信
    response = client.post("/api/v1/agents/", json=request_payload)

    # 3. 検証 (Assert)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "E2E Test Agent"
    assert "id" in data
```

```
```