import abc
from typing import Protocol

from ..value_objects.address import Address


class AddressLookupDomainService(Protocol):
    """
    郵便番号から住所を検索するドメインサービスインターフェース。
    具体的な実装（外部API連携など）はインフラ層で提供される。
    """
    
    @abc.abstractmethod
    def lookup(self, zipcode: str) -> Address:
        """
        郵便番号から住所情報を検索する。
        
        Args:
            zipcode: 郵便番号（7桁の数字文字列）
            
        Returns:
            Address: 住所情報を含む値オブジェクト
            
        Raises:
            ValueError: 郵便番号が見つからない、または検索に失敗した場合
        """
        ...
