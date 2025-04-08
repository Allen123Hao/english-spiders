from sqlalchemy import create_engine, text, select, and_, or_, desc, asc
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import expression
from typing import Dict, Any, List, Optional, Union
import json
import uuid
import logging
from .config import DBConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseUtils:
    def __init__(self):
        self.engine = create_engine(DBConfig.get_connection_url(), pool_recycle=3600)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.session = None

    def connect(self) -> bool:
        try:
            self.session = self.SessionLocal()
            logger.info("数据库连接成功")
            return True
        except Exception as e:
            logger.error(f"数据库连接错误: {e}")
            raise

    def disconnect(self):
        if self.session:
            self.session.close()
            logger.info("数据库连接已关闭")

    def execute_query(self, query: Union[str, expression.Select], params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        try:
            if isinstance(query, str):
                query = text(query)
            result = self.session.execute(query, params or {})
            return [dict(row._mapping) for row in result]
        except Exception as e:
            logger.error(f"查询执行错误: {e}, 查询: {query}, 参数: {params}")
            raise

    def execute_many(self, query: Union[str, expression.Select], data: List[Dict[str, Any]]):
        try:
            if not data:
                logger.warning("批量操作数据为空")
                return
                
            # 验证数据格式
            if not all(isinstance(item, dict) for item in data):
                raise ValueError("批量操作数据必须是字典列表")
            
            # 使用executemany处理批量操作
            self.session.execute(query, data)
            self.session.commit()
            logger.info(f"批量操作成功，处理数据量: {len(data)}")
        except Exception as e:
            logger.error(f"批量执行错误: {e}, 查询: {query}, 数据量: {len(data)}")
            self.session.rollback()
            raise

    @staticmethod
    def generate_uuid() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def create_meta(word_uuid: str, entry_uuid: str, sense_uuid: str) -> str:
        meta = {
            "wordUuid": word_uuid,
            "entryUuid": entry_uuid,
            "senseUuid": sense_uuid
        }
        return json.dumps(meta) 