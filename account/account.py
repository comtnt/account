import plugins
from plugins import *
from common.log import logger
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from datetime import datetime
import json
import os

@plugins.register(
    name="Account",
    desc="账户管理插件,提供用户账户管理相关功能",
    version="0.1",
    author="comtnt",
    desire_priority=0
)
class Account(Plugin):
    def __init__(self):
        super().__init__()
        try:
            # 加载配置文件
            self.config = super().load_config()
            if not self.config:
                # 初始化默认配置
                self.config = {
                    "accounts": {}  # 用于存储账户信息
                }
                self.save_config()
            
            # 注册事件处理函数
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            logger.info("[Account] 插件已加载")
        except Exception as e:
            logger.error(f"[Account] 插件初始化异常: {e}")
            raise e

    def on_handle_context(self, e_context: EventContext):
        """处理消息事件"""
        if e_context["context"].type != ContextType.TEXT:
            return
        
        content = e_context["context"].content.strip()
        if not content.startswith("#account"):
            return
            
        try:
            # 解析命令
            parts = content.split()
            if len(parts) == 1:
                # 显示帮助信息
                self._show_help(e_context)
                return
                
            cmd = parts[1]
            if cmd == "register":
                # 注册账户
                if len(parts) != 4:
                    e_context["reply"] = Reply(ReplyType.ERROR, "格式错误,正确格式: #account register <username> <password>")
                    e_context.action = EventAction.BREAK_PASS
                    return
                self._register_account(e_context, parts[2], parts[3])
            
            elif cmd == "login":
                # 登录账户
                if len(parts) != 4:
                    e_context["reply"] = Reply(ReplyType.ERROR, "格式错误,正确格式: #account login <username> <password>")
                    e_context.action = EventAction.BREAK_PASS
                    return
                self._login_account(e_context, parts[2], parts[3])
            
            elif cmd == "logout":
                # 登出账户
                self._logout_account(e_context)
            
            elif cmd == "info":
                # 查看账户信息
                self._show_account_info(e_context)
            
            else:
                e_context["reply"] = Reply(ReplyType.ERROR, f"未知命令: {cmd}\n请使用 #account 查看帮助")
                e_context.action = EventAction.BREAK_PASS
                
        except Exception as e:
            logger.error(f"[Account] 处理消息异常: {e}")
            e_context["reply"] = Reply(ReplyType.ERROR, f"处理命令出错: {e}")
            e_context.action = EventAction.BREAK_PASS

    def _show_help(self, e_context: EventContext):
        """显示帮助信息"""
        help_text = """账户管理插件使用帮助:
#account register <username> <password> - 注册新账户
#account login <username> <password> - 登录账户
#account logout - 登出当前账户
#account info - 查看当前账户信息"""
        e_context["reply"] = Reply(ReplyType.INFO, help_text)
        e_context.action = EventAction.BREAK_PASS

    def _register_account(self, e_context: EventContext, username: str, password: str):
        """注册新账户"""
        if username in self.config["accounts"]:
            e_context["reply"] = Reply(ReplyType.ERROR, "该用户名已存在")
            e_context.action = EventAction.BREAK_PASS
            return
            
        # 存储账户信息(实际应用中应该加密存储密码)
        self.config["accounts"][username] = {
            "password": password,
            "create_time": str(datetime.now())
        }
        self.save_config()
        
        e_context["reply"] = Reply(ReplyType.INFO, f"账户 {username} 注册成功")
        e_context.action = EventAction.BREAK_PASS

    def _login_account(self, e_context: EventContext, username: str, password: str):
        """登录账户"""
        if username not in self.config["accounts"]:
            e_context["reply"] = Reply(ReplyType.ERROR, "用户不存在")
            e_context.action = EventAction.BREAK_PASS
            return
            
        account = self.config["accounts"][username]
        if account["password"] != password:
            e_context["reply"] = Reply(ReplyType.ERROR, "密码错误")
            e_context.action = EventAction.BREAK_PASS
            return
            
        # 记录登录状态
        user_id = e_context["context"]["session_id"]
        self.config["accounts"][username]["last_login"] = str(datetime.now())
        self.config["accounts"][username]["session_id"] = user_id
        self.save_config()
        
        e_context["reply"] = Reply(ReplyType.INFO, f"账户 {username} 登录成功")
        e_context.action = EventAction.BREAK_PASS

    def _logout_account(self, e_context: EventContext):
        """登出账户"""
        user_id = e_context["context"]["session_id"]
        logged_in = False
        
        # 清除登录状态
        for username, account in self.config["accounts"].items():
            if account.get("session_id") == user_id:
                del account["session_id"]
                logged_in = True
                self.save_config()
                e_context["reply"] = Reply(ReplyType.INFO, f"账户 {username} 已登出")
                break
                
        if not logged_in:
            e_context["reply"] = Reply(ReplyType.ERROR, "当前未登录任何账户")
        e_context.action = EventAction.BREAK_PASS

    def _show_account_info(self, e_context: EventContext):
        """显示账户信息"""
        user_id = e_context["context"]["session_id"]
        
        # 查找当前登录的账户
        for username, account in self.config["accounts"].items():
            if account.get("session_id") == user_id:
                info = f"""当前登录账户信息:
用户名: {username}
创建时间: {account['create_time']}
最后登录: {account.get('last_login', '从未登录')}"""
                e_context["reply"] = Reply(ReplyType.INFO, info)
                e_context.action = EventAction.BREAK_PASS
                return
                
        e_context["reply"] = Reply(ReplyType.ERROR, "当前未登录任何账户")
        e_context.action = EventAction.BREAK_PASS 
