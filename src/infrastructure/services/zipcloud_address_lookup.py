import requests

from domain.services.address_lookup_domain_service import AddressLookupDomainService
from domain.value_objects.address import Address


class ZipCloudAddressLookup(AddressLookupDomainService):
    """
    ZipCloud API (https://zipcloud.ibsnet.co.jp/) を使った住所検索の実装。
    公開APIを使用して郵便番号から住所情報を取得する。
    """
    
    def __init__(self, timeout: int = 10):
        self.base_url = "https://zipcloud.ibsnet.co.jp/api/search"
        self.timeout = timeout
    
    def lookup(self, zipcode: str) -> Address:
        """
        ZipCloud APIを呼び出して郵便番号から住所を検索する。
        
        Args:
            zipcode: 郵便番号（7桁の数字文字列）
            
        Returns:
            Address: 住所情報を含む値オブジェクト
            
        Raises:
            ValueError: 郵便番号が見つからない、または検索に失敗した場合
        """
        try:
            response = requests.get(
                self.base_url,
                params={"zipcode": zipcode},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            # APIレスポンスのエラーチェック
            if data.get("status") != 200:
                raise ValueError(f"ZipCloud API error: {data.get('message', 'Unknown error')}")
            
            results = data.get("results")
            if not results or len(results) == 0:
                raise ValueError(f"Address not found for zipcode: {zipcode}")
            
            # 最初の結果を使用（通常は1件のみ）
            result = results[0]
            
            return Address(
                zipcode=result.get("zipcode", zipcode),
                prefecture=result.get("address1", ""),
                city=result.get("address2", ""),
                town=result.get("address3", "")
            )
            
        except requests.RequestException as e:
            raise ValueError(f"Failed to lookup address: {str(e)}")
