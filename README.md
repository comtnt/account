# Account Plugin for ChatGPT-on-WeChat

这是一个为 [ChatGPT-on-WeChat](https://github.com/zhayujie/chatgpt-on-wechat) 开发的账户管理插件。

## 功能特性

- 账户注册
- 账户登录
- 账户登出
- 查看账户信息

## 安装方法

### 方法一：直接安装

1. 将插件文件夹复制到 ChatGPT-on-WeChat 的 plugins 目录下：
```bash
cd chatgpt-on-wechat/plugins
git clone https://github.com/comtnt/plugin_account.git account
```

2. 重启程序，插件会自动加载

### 方法二：使用插件管理器

使用 `#installp` 命令安装：
```bash
#installp https://github.com/comtnt/plugin_account.git
```

## 使用方法

插件提供以下命令：

- `#account register <username> <password>` - 注册新账户
- `#account login <username> <password>` - 登录账户
- `#account logout` - 登出当前账户
- `#account info` - 查看当前账户信息

## 配置说明

插件的配置文件为 `config.json`，初次使用时将自动从 `config.json.template` 创建。

配置文件结构：
```json
{
    "accounts": {
        "username": {
            "password": "用户密码",
            "create_time": "创建时间",
            "last_login": "最后登录时间",
            "session_id": "当前会话ID"
        }
    }
}
```

## 注意事项

1. 密码目前以明文形式存储，建议在实际使用时增加加密功能
2. 用户登录状态基于会话ID，重启程序后需要重新登录

## 开发计划

- [ ] 添加密码加密存储
- [ ] 添加用户权限管理
- [ ] 添加账户有效期设置
- [ ] 添加登录失败次数限制

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进这个插件。

## 许可证

MIT License 
