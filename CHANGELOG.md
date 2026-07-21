# Changelog

## [Unreleased] - 2026-07-22

### Gensokyo 成员事件消息

- 保留原始 `[CQ:member]` 段，并按 `member + at + markdown` 顺序发送入群消息。
- 通过 `get_group_member_info` 获取显示名，通过 `get_avatar` 获取头像直链，失败时使用 QQ 头像 CDN 降级。
- 使用 Markdown 图片尺寸语法 `#35px #35px`，避免头像占满消息。
- 保留随机入群、离群文案；机器人自身事件不会发送。
- notice matcher 使用 `block=False`，不阻断其他插件处理成员事件。
- 移除旧的 `D:\HongXingBot` 本地图片依赖和旧的本地图片发送路径。

### 远端同步

- 合并 GitHub `main` 上先于本地提交到达的 8 个欢迎插件提交，保留远端的配置、测试、文案和 CQ 成员段处理。

### 范围

本轮只整理欢迎插件入口和成员事件消息，不修改 maimai sync 或 amia-core；头像获取仍由欢迎插件自己的 `get_avatar` 调用负责。
