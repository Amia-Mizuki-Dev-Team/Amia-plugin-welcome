# Amia-plugin-welcome

`Amia-plugin-welcome` 是 Mizuki Bot 的群成员加入/离开提示插件。

当前仓库代码仍是旧版普通 OneBot V11 实现；项目下一阶段目标是兼容 `Te-River/Gensokyo-NewQQ Release006` 的 `CQ:member + CQ:markdown` 回复机制。README 将当前实现与目标实现分开说明，避免误认为 Release006 方案已经上线。

## 当前已实现

监听事件：

```text
GroupIncreaseNoticeEvent
GroupDecreaseNoticeEvent
```

入群：

- 忽略机器人自身加入事件。
- 随机选择欢迎文案。
- 使用 `MessageSegment.at(event.user_id)`。
- 按概率读取本地图片，转换为 Base64 后发送。

离群：

- 忽略机器人自身离群事件。
- 随机选择离群文案。
- 统一显示“成员离开”，不区分主动退群、被踢或其他原因。

## 当前配置位置

旧版配置直接写在 `__init__.py`：

```python
WELCOME_IMAGES = [
    r"D:\HongXingBot\1.jpg",
]

IMAGE_PROBABILITY = 1.0
WELCOME_TEXTS = [...]
LEAVE_TEXTS = [...]
```

这套方式存在环境耦合：

- 写死 Windows 绝对路径。
- 文案修改必须改代码。
- 无法按群设置开关和模板。
- 图片读取会把整张文件转为 Base64，占用内存和消息体积。

后续应迁移到 NoneBot 配置和可选模板文件。

## Gensokyo-NewQQ 基线

目标兼容版本：

```text
https://github.com/Te-River/Gensokyo-NewQQ/releases/tag/Release006
```

所有群成员事件和 Markdown 回复行为必须以 `Release006` 为基线，不使用主分支后续行为作为默认假设。

Gensokyo 配置需要启用相关事件：

```yaml
text_intent:
  - "GroupMemberAddEventHandler"
  - "GroupMemberRemoveEventHandler"
```

Release006 的成员事件消息中可能包含：

```text
[CQ:member,type=add/remove,group_id=...,user_id=...]
```

该原始 CQ 段用于事件回复路由，目标实现中不得随意丢弃。

## 目标消息结构

### 入群

```text
原始 CQ:member
+ CQ:at
+ CQ:markdown
```

示例结构：

```text
[CQ:member,type=add,group_id=...,user_id=...]
[CQ:at,qq=<user_id>]
[CQ:markdown,data=<Base64 JSON>]
```

### 离群

```text
原始 CQ:member
+ CQ:markdown
```

示例结构：

```text
[CQ:member,type=remove,group_id=...,user_id=...]
[CQ:markdown,data=<Base64 JSON>]
```

离群默认不 at，因为成员已经不在群中。

## 离群事件规则

在当前 Gensokyo-NewQQ 场景中，不可靠区分：

- 主动退群。
- 管理员移除。
- 其他成员减少原因。

因此统一输出：

```text
成员离开群聊
```

禁止根据以下字段猜测原因：

```text
operator_id
sub_type
```

不得输出未经确认的“被踢”或“主动退出”。

## 身份边界

Welcome 事件直接使用：

```text
event.self_id
event.group_id
event.user_id
```

本插件不需要 qbind，也不应因为用户未绑定而拒绝欢迎或离群提示。

## 目标配置建议

```env
AMIA_WELCOME_ENABLED=true
AMIA_LEAVE_ENABLED=true
AMIA_WELCOME_IMAGE_PROBABILITY=0
AMIA_WELCOME_MARKDOWN=true
```

后续可扩展群级配置：

```yaml
groups:
  "123456":
    welcome_enabled: true
    leave_enabled: true
    welcome_template: default
```

第一版不要引入复杂数据库；JSON/YAML 配置即可。

## 推荐目录拆分

```text
__init__.py
config.py
renderer.py
events.py
templates/
  welcome.md
  leave.md
tests/
  test_renderer.py
  test_events.py
```

职责：

- `config.py`：开关和模板配置。
- `renderer.py`：Markdown JSON、Base64 和 CQ 组装。
- `events.py`：入群/离群事件处理。
- `templates/`：用户可见文案。

## 测试要求

至少覆盖：

- 机器人自身加入/离开时跳过。
- 入群消息顺序为 `member + at + markdown`。
- 离群消息顺序为 `member + markdown`。
- 原始 `event.message` 被保留。
- 离群不判断被踢。
- Markdown JSON 可被 Base64 解码。
- 模板中的特殊字符不会破坏 JSON。
- 图片不存在时仍能发送纯 Markdown。
- 配置关闭时不发送。

## 当前与目标差距

当前代码仍需要后续重构：

- 尚未保留 `CQ:member`。
- 尚未构造 `CQ:markdown`。
- 仍使用硬编码本地图片路径。
- 事件 matcher 仍是两个宽泛的 `on_notice()`。
- 缺少配置类和测试。

Codex 后续应按上述边界重构，但不要恢复踢出判断，也不要接入 qbind。

## 维护边界

- 不把本地图片绝对路径写进公共默认配置。
- 不在欢迎消息中堆放完整群规和帮助文本。
- 详细说明交给 Help 插件或文档站。
- 不根据不可靠字段判断离群原因。
- 不使用非 Release006 行为作为当前兼容承诺。
- 当前仓库尚未确定公开许可证。