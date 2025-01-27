"""
数据库模型和管理类
"""
from __future__ import annotations  # 用于类型注解中的字符串引用
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Integer
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.ext.declarative import declarative_base
import os

# 创建数据库基类
Base = declarative_base()

class WxAccount(Base):
    """微信账号模型"""
    __tablename__ = 'wx_accounts'

    id = Column(Integer, primary_key=True)
    wx_id = Column(String(50), unique=True, nullable=False)
    nickname = Column(String(50))
    create_time = Column(DateTime, default=datetime.now)
    expire_time = Column(DateTime)
    is_active = Column(Boolean, default=False)
    remark = Column(String(200))
    free_quota = Column(Integer, default=0)  # 剩余免费额度
    quota_reset_time = Column(DateTime)  # 下次额度重置时间

    def is_expired(self):
        """检查账号是否过期"""
        return self.expire_time < datetime.now()

    def should_reset_quota(self):
        """检查是否需要重置免费额度"""
        return not self.quota_reset_time or self.quota_reset_time < datetime.now()

    def reset_quota(self, quota_limit):
        """重置免费额度"""
        self.free_quota = quota_limit
        # 设置下次重置时间为明天0点
        tomorrow = datetime.now() + timedelta(days=1)
        self.quota_reset_time = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0)

class Database:
    """数据库管理类"""
    _instance: Optional[Database] = None
    engine = None
    Session = None
    
    def __new__(cls, db_path: Optional[str] = None) -> Database:
        if cls._instance is None and db_path:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._init_db(db_path)
        return cls._instance
        
    def _init_db(self, db_path: str) -> None:
        """初始化数据库"""
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(session_factory)
        
    def get_session(self) -> Session:
        """获取新的会话"""
        if not self.Session:
            raise RuntimeError("Database not initialized")
        return self.Session()
        
    def remove_session(self) -> None:
        """移除当前线程的会话"""
        if self.Session:
            self.Session.remove()

def init_db(db_path: str) -> Database:
    """初始化数据库并返回数据库管理实例
    
    Args:
        db_path: 数据库文件路径
        
    Returns:
        Database: 数据库管理实例
        
    Raises:
        RuntimeError: 数据库初始化失败
    """
    return Database(db_path) 
