---
name: user-login
description: 用户名密码登录，校验SQLite用户表并返回token
trigger_keywords: ["登录", "login", "用户名密码登录", "用户认证"]
---
# 用户登录技能

## 功能
接收用户名和密码，验证 `SQLite users` 表中的用户，成功后返回 token。

## 输入
- username: 用户名（必填）
- password: 密码（必填）

## 输出
- success: 是否成功
- token: 认证令牌（成功时）
- uid: 用户ID（成功时）
- username: 用户名（成功时）
- error: 错误信息（失败时）

