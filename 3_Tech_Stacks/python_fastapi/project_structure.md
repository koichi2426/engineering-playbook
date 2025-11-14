# プロジェクト構成 (FastAPI)

このドキュメントは、`python_fastapi`プロジェクトで採用するクリーンアーキテクチャの標準フォルダ構成を定義します。
この構成は、`2_Concepts/clean_architecture.md`で定義した4層の責務に基づいています。

## 1. フォルダ構成 (Root)

* **`backend/`**
    * `Dockerfile`
    * `docker-compose.yml`
    * `.env.example`
    * `requirements.txt`
    * `alembic.ini`
    * `alembic/` (DBマイグレーションスクリプト)
    * **`src/`** (★すべてのアプリケーションコードはここに配置)

---

## 2. フォルダ構成 (src/)

* **`src/`**
    * **`domain/`** (1. ドメイン層)
        * `entities/` (エンティティ: 例 `user.py`, `agent.py`)
        * `value_objects/` (値オブジェクト: 例 `email.py`, `id.py`)
        * `services/` (ドメインサービス: **インターフェース**)
        * `repositories/` (リポジトリ・**インターフェース**)
    * **`usecase/`** (2. ユースケース層)
        * `auth_login.py`
        * `create_agent.py`
        * `...` (機能・操作単位でファイルを作成)
    * **`adapter/`** (3. アダプタ層)
        * `controller/` (コントローラー: HTTPリクエストをUsecase入力に変換)
        * `presenter/` (プレゼンター: Usecase出力をHTTPレスポンスに変換)
    * **`infrastructure/`** (4. インフラ層)
        * `database/` (DBセッション, Engine, SQLAlchemyモデル)
            * `mysql/` (リポジトリの**実装**: 例 `user_repository.py`)
        * `service/` (ドメインサービスの**実装**: 例 `auth_domain_service_impl.py`)
        * `router/` (FastAPIのルーティング定義: `fastapi.py`)
        * `di/` (依存性注入コンテナ)
        * `storage/` (外部ストレージクライアントの実装)
    * **`main.py`** (アプリケーション起動ファイル / Entrypoint)

---

## 3. 各ディレクトリの責務 (src/)

### `src/domain/` (ドメイン層)
* **責務:** 純粋なビジネスルール。
* **内容:** `entities/`, `value_objects/`に加え、`services/` (ロジック)と`repositories/` (永続化)の**インターフェース**を定義。

### `src/usecase/` (ユースケース層)
* **責務:** アプリケーション固有のロジック。
* **内容:** `auth_login.py`のような具体的な操作フローを実装。`domain`層のインターフェースにのみ依存。

### `src/adapter/` (アダプタ層)
* **責務:** 外部（HTTP）と内部（Usecase）の「翻訳」。
* **内容:**
    * `controller/`: HTTPリクエストを受け取り、`usecase`層を呼び出す。
    * `presenter/`: `usecase`層の戻り値を、HTTPレスポンス（Pydanticモデルを使ったJSON）に変換する。

### `src/infrastructure/` (インフラ層)
* **責務:** すべての「外部」技術と、`domain`層インターフェースの「具体的な実装」。
* **内容:**
    * `database/mysql/`: `domain/repositories/`の**実装**を配置。
    * `service/`: `domain/services/`の**実装**を配置。
    * `router/`: `adapter/controller/`で定義されたコントローラーを FastAPI のルーターに登録する。
    * `di/`: 依存性の解決（インターフェースと実装の紐付け）を行う。

### `src/main.py`
* **責務:** アプリケーションの起動。
* **内容:** `infrastructure/router/fastapi.py` で定義されたFastAPIアプリを起動する。