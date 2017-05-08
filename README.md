
# 简介

MyServer是一个Python实现的，简单的Unix服务器。支持Python WSGI应用部署，并提供以下特性：

⚠️ 该应用仍然处于开发阶段，目前只是一个原型

## 主要功能

* WSGI 应用支持
* Worker进程管理（因时间原因目前仅支持sync worker，今后会加入其他）
* 命令行和配置文件配置
* Server hooks支持
* 基于Python3.5.2开发(兼容性尚未测试）

## TODO

* 全面彻底的测试
* 其他类型worker支持（Async worker, greenlet worker, AsyncHTTP worker)
* HTTP/2 支持
* 针对Linux提供提高性能的特殊系统调用
* Proxy支持
* 监控中间件支持
* Unix socket support

see documents at: https://dispensable.github.io/myserver/
