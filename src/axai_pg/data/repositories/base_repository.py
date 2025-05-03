from typing import TypeVar, Generic, Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..config.database import DatabaseManager
from .metrics_utils import track_metrics
import threading

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Thread-safe base repository implementation with metrics tracking."""
    
    def __init__(self, model_class: type):
        self.model_class = model_class
        self.db = DatabaseManager.get_instance()
        self._session_lock = threading.Lock()
        # Initialize metrics
        from .repository_metrics import RepositoryMetrics
        from .metrics_config import RepositoryMetricsConfig
        self._metrics = RepositoryMetrics(RepositoryMetricsConfig.create_minimal())
    
    def _get_session(self) -> Session:
        """Get a database session in a thread-safe manner."""
        with self._session_lock:
            return self.db.get_session()
    
    @track_metrics(model_class=T)
    async def find_by_id(self, id: int) -> Optional[T]:
        try:
            with self._get_session() as session:
                return session.query(self.model_class).filter_by(id=id).first()
        except SQLAlchemyError as e:
            # Log error
            raise RuntimeError(f"Database error in find_by_id: {str(e)}") from e
    
    @track_metrics(model_class=T)
    async def find_many(self, criteria: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> List[T]:
        try:
            with self._get_session() as session:
                query = session.query(self.model_class)
                
                # Apply criteria filters
                for key, value in criteria.items():
                    query = query.filter(getattr(self.model_class, key) == value)
                
                # Apply options if provided
                if options:
                    if 'offset' in options:
                        query = query.offset(options['offset'])
                    if 'limit' in options:
                        query = query.limit(options['limit'])
                    if 'order_by' in options:
                        for field, direction in options['order_by'].items():
                            column = getattr(self.model_class, field)
                            if direction == 'DESC':
                                column = column.desc()
                            query = query.order_by(column)
                
                return query.all()
        except SQLAlchemyError as e:
            # Log error
            raise RuntimeError(f"Database error in find_many: {str(e)}") from e
    
    @track_metrics(model_class=T)
    async def create(self, entity: Dict[str, Any]) -> T:
        try:
            with self._get_session() as session:
                db_entity = self.model_class(**entity)
                session.add(db_entity)
                session.commit()
                session.refresh(db_entity)
                return db_entity
        except SQLAlchemyError as e:
            # Log error
            raise RuntimeError(f"Database error in create: {str(e)}") from e
    
    @track_metrics(model_class=T)
    async def update(self, id: int, entity: Dict[str, Any]) -> Optional[T]:
        try:
            with self._get_session() as session:
                db_entity = session.query(self.model_class).filter_by(id=id).first()
                if not db_entity:
                    return None
                
                for key, value in entity.items():
                    setattr(db_entity, key, value)
                
                session.commit()
                session.refresh(db_entity)
                return db_entity
        except SQLAlchemyError as e:
            # Log error
            raise RuntimeError(f"Database error in update: {str(e)}") from e
    
    @track_metrics(model_class=T)
    async def delete(self, id: int) -> bool:
        try:
            with self._get_session() as session:
                entity = session.query(self.model_class).filter_by(id=id).first()
                if not entity:
                    return False
                session.delete(entity)
                session.commit()
                return True
        except SQLAlchemyError as e:
            # Log error
            raise RuntimeError(f"Database error in delete: {str(e)}") from e
    
    @track_metrics(model_class=T)
    async def transaction(self, operation):
        """Execute operations within a transaction context."""
        try:
            with self._get_session() as session:
                result = await operation(session)
                session.commit()
                return result
        except Exception as e:
            # Log error
            session.rollback()
            raise RuntimeError(f"Transaction error: {str(e)}") from e
