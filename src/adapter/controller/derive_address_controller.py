from typing import Union
from usecase.derive_address import (
    DeriveAddressUseCase,
    DeriveAddressInput,
    DeriveAddressOutput,
)


class DeriveAddressController:
    def __init__(self, uc: DeriveAddressUseCase):
        self.uc = uc

    def execute(
        self, input_data: DeriveAddressInput
    ) -> dict[str, Union[int, DeriveAddressOutput, dict[str, str]]]:
        try:
            output, err = self.uc.execute(input_data)
            if err:
                # エラーの種類に応じてHTTPステータスコードを決定
                error_msg = str(err)
                if "not found" in error_msg.lower():
                    # 郵便番号が見つからない場合
                    return {"status": 404, "data": {"error": error_msg}}
                elif "invalid" in error_msg.lower() or "bad" in error_msg.lower():
                    # リクエストの不正値
                    return {"status": 400, "data": {"error": error_msg}}
                else:
                    # その他のエラー（外部API接続エラーなど）
                    return {"status": 500, "data": {"error": error_msg}}
            
            # 成功
            return {"status": 200, "data": output}
        except Exception as e:
            # 予期せぬサーバーエラー
            return {"status": 500, "data": {"error": f"An unexpected error occurred: {e}"}}
