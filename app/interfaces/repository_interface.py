from typing import Protocol, Optional, List, TypeVar, Generic
from datetime import datetime

T = TypeVar('T')

class IRepository(Protocol, Generic[T]):
    def get_by_id(self, id: int) -> Optional[T]:
        ...

    def get_all(self, skip: int = 0, limit: int = 10) -> List[T]:
        ...

    def create(self, entity: T) -> T:
        ...
        
    def update(self, id: int, entity: T) -> Optional[T]:
        ...
        
    def delete(self, id: int) -> None:
        ...
        
class ISoftDeleteRepository(IRepository[T], Protocol):
    def soft_delete(self, id: int) -> None:
        ...
        
    def restore(self, id: int) -> None:
        ...
        
    def get_active(self, skip: int = 0, limit: int = 100) -> List[T]:
        ...
    
    def get_deleted(self, skip: int = 0, limit: int = 100) -> List[T]:
        ...
        
class ILoanRepository(IRepository, ISoftDeleteRepository):
    def get_by_user(self, user_id: int, include_deleted: bool = False) -> List:
        ...
        
    def get_active_by_user(self, user_id: int) -> List:
        ...
        