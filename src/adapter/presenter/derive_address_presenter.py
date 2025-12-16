from usecase.derive_address import DeriveAddressPresenter, DeriveAddressOutput
from domain.value_objects.address import Address


class DeriveAddressPresenterImpl(DeriveAddressPresenter):
    def output(self, address: Address) -> DeriveAddressOutput:
        """
        Addressドメインオブジェクトを DeriveAddressOutput DTO に変換して返す。
        """
        return DeriveAddressOutput(
            zipcode=address.zipcode,
            prefecture=address.prefecture,
            city=address.city,
            town=address.town,
        )


def new_derive_address_presenter() -> DeriveAddressPresenter:
    """
    DeriveAddressPresenterImpl のインスタンスを生成するファクトリ関数。
    """
    return DeriveAddressPresenterImpl()
