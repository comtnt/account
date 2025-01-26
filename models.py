"""
数据库模型和管理类
"""
from __future__ import annotations  # 用于类型注解中的字符串引用
from datetime import datetime
from typing import Optional

from sqlalchemy import create_engine, Column, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.ext.declarative import declarative_base
import os

# 创建数据库基类
Base = declarative_base()

class WxAccount(Base):
    """微信账号模型"""
    __tablename__ = 'wx_accounts'

    wx_id: str = Column(String(100), primary_key=True)  # 微信ID
    nickname: Optional[str] = Column(String(100))       # 微信昵称
    create_time: datetime = Column(DateTime, default=datetime.now)  # 创建时间
    expire_time: Optional[datetime] = Column(DateTime)  # 过期时间
    is_active: bool = Column(Boolean, default=True)     # 是否激活
    remark: Optional[str] = Column(String(500))        # 备注

    def is_expired(self) -> bool:
        """检查账号是否过期"""
        return datetime.now() > self.expire_time if self.expire_time else True

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
