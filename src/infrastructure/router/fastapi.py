from dataclasses import asdict, is_dataclass
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse

from infrastructure.services.zipcloud_address_lookup import ZipCloudAddressLookup
from adapter.controller.derive_address_controller import DeriveAddressController
from adapter.presenter.derive_address_presenter import new_derive_address_presenter
from usecase.derive_address import DeriveAddressInput, new_derive_address_interactor


router = APIRouter()


def build_derive_address_controller() -> DeriveAddressController:
    """
    DeriveAddressController のインスタンスを生成する。
    簡易DIとして、必要な依存をここで組み立てる。
    """
    # インフラ層: ZipCloud API クライアント
    address_lookup_service = ZipCloudAddressLookup(timeout=10)
    
    # アダプタ層: Presenter
    presenter = new_derive_address_presenter()
    
    # ユースケース層: Interactor
    usecase = new_derive_address_interactor(presenter, address_lookup_service)
    
    # アダプタ層: Controller
    return DeriveAddressController(usecase)


@router.get("/v1/address")
def get_address(zipcode: str = Query(..., description="郵便番号（7桁の数字）")):
    """
    郵便番号から住所を検索するエンドポイント。
    
    Args:
        zipcode: 郵便番号（例: 1000001）
        
    Returns:
        JSONResponse: 住所情報を含むレスポンス
    """
    controller = build_derive_address_controller()
    input_data = DeriveAddressInput(zipcode=zipcode)
    response = controller.execute(input_data)
    
    status_code = response.get("status", 500)
    data = response.get("data")
    
    # dataclassをdictに変換
    if is_dataclass(data):
        data = asdict(data)
    
    return JSONResponse(content=data, status_code=status_code)
