# Amia-plugin-welcome

`Amia-plugin-welcome` 是 Mizuki Bot 的群成员加入与离开提示插件。

当前仓库仍是旧版 OneBot V11 实现；Gensokyo 成员事件与 Markdown 回复仍需按已部署版本的实际事件契约继续适配。

本文将“当前已经运行的功能”和“后续目标实现”分开说明，避免开发者把规划内容误认为现状。

## 插件作用

```text
群成员加入 / 离开事件
          ↓
Amia-plugin-welcome
          ↓
欢迎或离开提示
```

本插件只负责成员事件提示，不负责：

- qbind；
- 入群审批；
- 群权限管理；
- 踢出判断；
- 长篇群规和帮助菜单。

## 当前已实现

监听：

```text
GroupIncreaseNoticeEvent
GroupDecreaseNoticeEvent
```

### 入群

当前行为：

- 忽略机器人自身加入；
- 随机选择欢迎文案（Mizuki 风格 20 条）；
- 使用 `[CQ:at,qq=<user_id>]` 作为独立段保留于 markdown 之前；
- 调用 Gensokyo `get_avatar` API 获取正确头像 CDN 直链；
- 使用 `[CQ:markdown,data=<Base64 JSON>]` 发送卡片消息；
- Markdown 内容中头像图片置于顶部，指定 `#35px #35px` 尺寸，与 @ 并列；
- 不发送本地图片。

### 离群

当前行为：

- 忽略机器人自身离群；
- 随机选择离群文案（10 条）；
- 使用 `[CQ:markdown]` 卡片消息；
- 包含头像图片；
- 不区分主动退群、管理员移除或其他原因。

## 当前配置问题

图片配置现在通过环境变量提供，默认不发送本地图片：

```env
AMIA_WELCOME_IMAGES=data/welcome/1.jpg,data/welcome/2.jpg
AMIA_WELCOME_IMAGE_PROBABILITY=0
```

该实现存在以下问题：

- 修改文案必须改代码；
- 无法按群控制开关和模板；
- 图片全部转 Base64，增加内存和消息体积；
- 尚未按群配置开关和模板。

配置路径使用逗号分隔，路径不存在时只记录警告，不会阻止文字欢迎消息发送。

## 离线测试

```bash
python -m compileall -q .
python -m unittest discover -s tests -v
```

后续应迁移到 NoneBot 配置与独立模板文件。

## Release006 适配基线

目标版本：

```text
Te-River/Gensokyo-NewQQ Release006
```

成员事件和 Markdown 回复必须以 Release006 的实际行为为准，不使用主分支或其他版本行为作为默认假设。

Gensokyo 侧需要启用：

```yaml
text_intent:
  - "GroupMemberAddEventHandler"
  - "GroupMemberRemoveEventHandler"
```

成员事件消息中可能包含：

```text
[CQ:member,type=add/remove,group_id=...,user_id=...]
```

该原始 `CQ:member` 段用于事件回复路由。目标实现必须保留它，不能只提取 user_id 后重新发送普通消息。

## 目标消息结构

### 入群

```text
原始 CQ:member
+ CQ:at
+ CQ:markdown
```

示例：

```text
[CQ:member,type=add,group_id=...,user_id=...]
[CQ:at,qq=<user_id>]
[CQ:markdown,data=<Base64 JSON>]
```

推荐用户可见文案：

```text
欢迎新成员 @xxx 加入群聊！
```

### 离群

```text
原始 CQ:member
+ CQ:markdown
```

示例：

```text
[CQ:member,type=remove,group_id=...,user_id=...]
[CQ:markdown,data=<Base64 JSON>]
```

离群默认不 at，因为成员已经不在群内。

## 离群事件规则

在当前 Gensokyo-NewQQ 场景中，无法可靠区分：

- 主动退出；
- 管理员移除；
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

不得输出未经确认的“被踢出”或“主动退群”。

## 身份边界

Welcome 直接使用事件字段：

```text
event.self_id
event.group_id
event.user_id
```

本插件不需要 qbind，也不能因为用户没有绑定 canonical ID 而拒绝发送欢迎或离群消息。

## 目标配置

第一阶段建议配置：

```env
AMIA_WELCOME_ENABLED=true
AMIA_LEAVE_ENABLED=true
AMIA_WELCOME_IMAGE_PROBABILITY=0
AMIA_WELCOME_MARKDOWN=true
```

后续可以增加简单群级配置：

```yaml
groups:
  "123456":
    welcome_enabled: true
    leave_enabled: true
    welcome_template: default
```

第一版不需要数据库。JSON 或 YAML 配置已经足够。

## 推荐目录

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

- `config.py`：全局和群级配置；
- `renderer.py`：Markdown JSON、Base64 和 CQ 拼接；
- `events.py`：成员加入与离开事件；
- `templates/`：用户可见文案；
- `tests/`：事件和渲染测试。

## 目标处理流程

```text
收到成员事件
      ↓
确认不是机器人自身
      ↓
读取群级与全局开关
      ↓
保留原始 CQ:member
      ↓
渲染 Markdown JSON
      ↓
Base64 编码
      ↓
按固定顺序组合 CQ 段并发送
```

图片不存在或 Markdown 渲染失败时，应有明确降级策略，至少不能让整个事件处理器崩溃。

## 测试要求

必须覆盖：

- 机器人自身加入时跳过；
- 机器人自身离开时跳过；
- 入群顺序为 `member + at + markdown`；
- 离群顺序为 `member + markdown`；
- 原始 `CQ:member` 被保留；
- 离群不判断被踢；
- Markdown JSON 可以正确 Base64 解码；
- 特殊字符不会破坏 JSON；
- 图片缺失时可以降级；
- 配置关闭时不发送；
- 群级配置不会影响其他群。

## 当前与目标差距

当前代码尚未完成：

- 配置类；
- 模板文件；
- 群级开关；
- 自动化测试；
- 移除硬编码图片路径。

因此当前仓库不能宣称已经完成 Release006 Markdown 适配。

## 推荐开发顺序

1. 固定 Release006 事件样本；
2. 拆分配置、渲染和事件处理；
3. 实现并测试 `CQ:member` 保留；
4. 实现 Markdown JSON 和 Base64；
5. 增加入群与离群测试；
6. 移除绝对路径；
7. 最后增加群级模板配置。

## 维护边界

- 不把本地绝对路径写进公共默认配置；
- 不接入 qbind；
- 不判断主动离群或被踢；
- 不在欢迎消息中堆放完整群规；
- 不使用非 Release006 行为作为兼容承诺；
- 当前仓库尚未确定公开许可证。
