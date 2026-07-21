# Changelog

## [Unreleased] - 2026-07-21

### 加载入口收口

- 克隆目录入口改为转发到维护中的 `src.plugins.welcome` 实现。
- 移除旧入口中的重复 notice handler，避免同一进退群事件发送两次。
- 移除过时的 Windows `D:\HongXingBot` 图片路径和旧 Base64 发送逻辑。
- 保留 `handle_member_notice` 与 `member_handler` 导出，兼容现有加载方。

### 范围

本轮只整理欢迎插件的加载入口，不修改 avatar、maimai sync 或 amia-core。
