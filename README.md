# Account Plugin for ChatGPT-on-WeChat

这是一个为 [ChatGPT-on-WeChat](https://github.com/zhayujie/chatgpt-on-wechat) 开发的账户管理插件。

## 功能特性

- 账户注册
- 账户登录
- 账户登出
- 查看账户信息

## 安装方法

### 方法一：使用插件管理器（推荐）

在与机器人对话中执行：
```bash
#installp https://github.com/comtnt/plugin_account.git
```

### 方法二：手动安装

1. 进入 ChatGPT-on-WeChat 的插件目录：
```bash
cd chatgpt-on-wechat/plugins
```

2. 克隆插件仓库：
```bash
git clone https://github.com/comtnt/plugin_account.git account
```

3. 安装依赖：
```bash
cd account
pip install -r requirements.txt
```

4. 重启程序使插件生效

## 配置说明

1. 复制配置模板：
```bash
cp config.json.template config.json
```

2. 编辑 `config.json` 添加管理员：
```json
{
    "database_path": "wx_accounts.db",
    "default_expire_days": 30,
    "expired_reply": "您的账号已过期或未开通，请联系管理员充值。",
    "admin_wx_ids": ["your_wx_id"]  # 替换为管理员的微信ID
}
```

## 使用方法

插件提供以下管理命令（仅管理员可用）：

- `#account add wx_id days [nickname] [remark]` - 添加/更新账号
- `#account del wx_id` - 删除账号
- `#account list` - 列出所有账号
- `#account info wx_id` - 查看账号信息

## 注意事项

1. 必须先在配置文件中设置管理员wx_id
2. 账号过期后将无法使用机器人功能
3. 管理员不受账号过期限制
4. 数据库文件默认保存在插件目录下

## 开发计划

- [ ] 添加密码加密存储
- [ ] 添加用户权限管理
- [ ] 添加账户有效期设置
- [ ] 添加登录失败次数限制

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进这个插件。

## 许可证

MIT License 
