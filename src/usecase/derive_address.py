import abc
from dataclasses import dataclass
from typing import Protocol

from domain.services.address_lookup_domain_service import AddressLookupDomainService
from domain.value_objects.address import Address


# ======================================
# Usecaseのインターフェース定義（Protocol）
# ======================================
class DeriveAddressUseCase(Protocol):
    def execute(
        self, input: "DeriveAddressInput"
    ) -> tuple["DeriveAddressOutput", Exception | None]:
        ...


# ======================================
# Input DTO
# ======================================
@dataclass
class DeriveAddressInput:
    zipcode: str


# ======================================
# Output DTO
# ======================================
@dataclass
class DeriveAddressOutput:
    zipcode: str
    prefecture: str
    city: str
    town: str


# ======================================
# Presenterのインターフェース定義
# ======================================
class DeriveAddressPresenter(abc.ABC):
    @abc.abstractmethod
    def output(self, address: Address) -> DeriveAddressOutput:
        pass


# ======================================
# Usecaseの具体的な実装（Interactor）
# ======================================
class DeriveAddressInteractor:
    def __init__(
        self,
        presenter: DeriveAddressPresenter,
        address_lookup_service: AddressLookupDomainService,
    ):
        self.presenter = presenter
        self.address_lookup_service = address_lookup_service

    def execute(
        self, input: DeriveAddressInput
    ) -> tuple[DeriveAddressOutput, Exception | None]:
        try:
            # ドメインサービスを使って郵便番号から住所を検索
            address = self.address_lookup_service.lookup(input.zipcode)
            
            # Presenterに渡してOutput DTOに変換
            output = self.presenter.output(address)
            return output, None
            
        except Exception as e:
            # エラー時は空のDTOと例外を返す
            empty_output = DeriveAddressOutput(
                zipcode="", prefecture="", city="", town=""
            )
            return empty_output, e


# ======================================
# Usecaseインスタンスを生成するファクトリ関数
# ======================================
def new_derive_address_interactor(
    presenter: DeriveAddressPresenter,
    address_lookup_service: AddressLookupDomainService,
) -> DeriveAddressUseCase:
    return DeriveAddressInteractor(
        presenter=presenter,
        address_lookup_service=address_lookup_service,
    )
