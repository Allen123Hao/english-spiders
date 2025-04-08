import os
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path

# 获取当前文件所在目录
current_dir = Path(__file__).parent.absolute()
# 加载.env文件
load_dotenv(current_dir / '.env')

class DBConfig:
    HOST: str = os.getenv('DB_HOST', 'localhost')
    PORT: int = int(os.getenv('DB_PORT', '3306'))
    DATABASE: str = os.getenv('DB_NAME', 'hedgie_base_dev')
    USER: str = os.getenv('DB_USER', 'root')
    PASSWORD: str = os.getenv('DB_PASSWORD', '')
    CHARSET: str = os.getenv('DB_CHARSET', 'utf8mb4')
    TIMEZONE: str = os.getenv('DB_TIMEZONE', 'Asia/Shanghai')

    @classmethod
    def get_connection_url(cls) -> str:
        return f"mysql+pymysql://{cls.USER}:{cls.PASSWORD}@{cls.HOST}:{cls.PORT}/{cls.DATABASE}?charset={cls.CHARSET}"
