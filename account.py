import plugins
from plugins import *
from common.log import logger
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from datetime import datetime, timedelta
import os
from plugins import Plugin, Event, EventAction
from plugins.event import EventContext
from .models import init_db, WxAccount

@plugins.register(
    name="Account",
    desc="微信账号管理插件,提供账号管理和过期控制功能",
    version="0.2",
    author="comtnt",
    desire_priority=0  # 设置为普通优先级
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
                    "database_path": "wx_accounts.db",
                    "default_expire_days": 30,
                    "expired_reply": "您的账号已过期或未开通，请联系管理员充值。",
                    "admin_wx_ids": []
                }
                self.save_config()
            
            # 初始化数据库
            db_path = os.path.join(os.path.dirname(__file__), self.config["database_path"])
            self.db = init_db(db_path)
            
            # 注册事件处理函数
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            logger.info("[Account] 插件已加载")
        except Exception as e:
            logger.error(f"[Account] 插件初始化异常: {e}")
            raise e

    def on_handle_context(self, e_context: EventContext):
        """处理消息事件"""
        context = e_context["context"]
        session = self.db.get_session()
        
        try:
            # 获取发送者wx_id
            if context.get("isgroup", False):
                # 群消息
                wx_id = context.get("msg").actual_user_id
                nickname = context.get("msg").actual_user_nickname
            else:
                # 私聊消息
                wx_id = context.get("msg").from_user_id
                nickname = context.get("msg").from_user_nickname
            
            # 处理管理员命令
            if context.type == ContextType.TEXT:
                content = context.content.strip()
                if content.startswith("$account") and wx_id in self.config["admin_wx_ids"]:
                    self._handle_admin_cmd(e_context, content, session)
                    return
                    
            # 检查账号状态
            account = session.query(WxAccount).filter_by(wx_id=wx_id).first()
            
            # 如果是管理员，跳过检查
            if wx_id in self.config["admin_wx_ids"]:
                return
            
            # 账号不存在，自动创建并设置为过期
            if not account:
                account = WxAccount(
                    wx_id=wx_id,
                    nickname=nickname,
                    expire_time=datetime.now(),
                    is_active=False,
                    remark="自动创建"
                )
                session.add(account)
                session.commit()
            
            # 检查账号是否可用
            if not account.is_active or account.is_expired():
                e_context["reply"] = Reply(ReplyType.TEXT, self.config["expired_reply"])
                e_context.action = EventAction.BREAK_PASS
                return
                
        finally:
            # 确保会话被关闭
            self.db.remove_session()

    def _handle_admin_cmd(self, e_context: EventContext, content: str, session):
        """处理管理员命令"""
        try:
            parts = content.split()
            if len(parts) == 1:
                self._show_help(e_context)
                return
                
            cmd = parts[1]
            if cmd == "add":
                # 添加账号 $account add wx_id days [nickname] [remark]
                if len(parts) < 4:
                    e_context["reply"] = Reply(ReplyType.ERROR, "格式错误,正确格式: $account add wx_id days [nickname] [remark]")
                    e_context.action = EventAction.BREAK_PASS
                    return
                    
                wx_id = parts[2]
                days = int(parts[3])
                nickname = parts[4] if len(parts) > 4 else ""
                remark = " ".join(parts[5:]) if len(parts) > 5 else ""
                
                account = session.query(WxAccount).filter_by(wx_id=wx_id).first()
                if not account:
                    account = WxAccount(wx_id=wx_id)
                    
                account.nickname = nickname
                account.expire_time = datetime.now() + timedelta(days=days)
                account.is_active = True
                account.remark = remark
                
                session.add(account)
                session.commit()
                
                e_context["reply"] = Reply(ReplyType.INFO, f"账号 {wx_id} 已添加/更新，过期时间: {account.expire_time}")
                
            elif cmd == "del":
                # 删除账号 $account del wx_id
                if len(parts) != 3:
                    e_context["reply"] = Reply(ReplyType.ERROR, "格式错误,正确格式: $account del wx_id")
                    e_context.action = EventAction.BREAK_PASS
                    return
                    
                wx_id = parts[2]
                account = session.query(WxAccount).filter_by(wx_id=wx_id).first()
                if account:
                    session.delete(account)
                    session.commit()
                    e_context["reply"] = Reply(ReplyType.INFO, f"账号 {wx_id} 已删除")
                else:
                    e_context["reply"] = Reply(ReplyType.ERROR, f"账号 {wx_id} 不存在")
                    
            elif cmd == "list":
                # 列出所有账号 $account list
                accounts = session.query(WxAccount).all()
                if not accounts:
                    e_context["reply"] = Reply(ReplyType.INFO, "暂无账号信息")
                    e_context.action = EventAction.BREAK_PASS
                    return
                    
                reply = "账号列表:\n"
                for acc in accounts:
                    status = "正常" if acc.is_active and not acc.is_expired() else "已过期"
                    reply += f"WX_ID: {acc.wx_id}\n"
                    reply += f"昵称: {acc.nickname}\n"
                    reply += f"状态: {status}\n"
                    reply += f"过期时间: {acc.expire_time}\n"
                    reply += f"备注: {acc.remark}\n"
                    reply += "----------\n"
                    
                e_context["reply"] = Reply(ReplyType.INFO, reply)
                
            elif cmd == "info":
                # 查看账号信息 $account info wx_id
                if len(parts) != 3:
                    e_context["reply"] = Reply(ReplyType.ERROR, "格式错误,正确格式: $account info wx_id")
                    e_context.action = EventAction.BREAK_PASS
                    return
                    
                wx_id = parts[2]
                account = session.query(WxAccount).filter_by(wx_id=wx_id).first()
                if not account:
                    e_context["reply"] = Reply(ReplyType.ERROR, f"账号 {wx_id} 不存在")
                    e_context.action = EventAction.BREAK_PASS
                    return
                    
                status = "正常" if account.is_active and not account.is_expired() else "已过期"
                reply = f"账号信息:\nWX_ID: {account.wx_id}\n"
                reply += f"昵称: {account.nickname}\n"
                reply += f"状态: {status}\n"
                reply += f"创建时间: {account.create_time}\n"
                reply += f"过期时间: {account.expire_time}\n"
                reply += f"备注: {account.remark}"
                
                e_context["reply"] = Reply(ReplyType.INFO, reply)
                
            else:
                e_context["reply"] = Reply(ReplyType.ERROR, f"未知命令: {cmd}\n请使用 $account 查看帮助")
                
        except Exception as e:
            logger.error(f"[Account] 处理管理员命令异常: {e}")
            e_context["reply"] = Reply(ReplyType.ERROR, f"处理命令出错: {e}")
            
        e_context.action = EventAction.BREAK_PASS

    def _show_help(self, e_context: EventContext):
        """显示帮助信息"""
        if e_context["context"]["msg"].from_user_id not in self.config["admin_wx_ids"]:
            e_context["reply"] = Reply(ReplyType.INFO, "您不是管理员，无法使用此功能")
            e_context.action = EventAction.BREAK_PASS
            return
            
        help_text = """账号管理插件使用帮助:
$account add wx_id days [nickname] [remark] - 添加/更新账号
$account del wx_id - 删除账号
$account list - 列出所有账号
$account info wx_id - 查看账号信息"""
        e_context["reply"] = Reply(ReplyType.INFO, help_text)
        e_context.action = EventAction.BREAK_PASS 
