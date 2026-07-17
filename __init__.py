import base64
import json
import logging

from nonebot import on_notice
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupDecreaseNoticeEvent,
    GroupIncreaseNoticeEvent,
    Message,
    MessageSegment,
)

logger = logging.getLogger("nonebot.plugin.member_notice")

member_handler = on_notice(priority=1, block=False)


async def _member_profile(bot: Bot, event) -> tuple[str, str]:
    """Resolve the display name and avatar used by the welcome message."""
    user_id = int(event.user_id)
    name = str(user_id)
    try:
        info = await bot.get_group_member_info(
            group_id=event.group_id,
            user_id=user_id,
            no_cache=False,
        )
        name = info.get("card") or info.get("nickname") or name
    except Exception:
        # A member who has just left may no longer be queryable.  The QQ
        # avatar endpoint still gives us a useful fallback in that case.
        logger.debug("无法读取群成员资料: group=%s user=%s", event.group_id, user_id, exc_info=True)

    avatar = ""
    try:
        result = await bot.call_api("get_avatar", user_id=user_id)
        avatar = result["message"]
    except Exception:
        logger.debug("无法获取头像: group=%s user=%s", event.group_id, user_id, exc_info=True)
        avatar = f"https://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
    return name, avatar


def _build_message(
    event: GroupIncreaseNoticeEvent | GroupDecreaseNoticeEvent,
    name: str,
    avatar: str,
) -> Message:
    user_id = int(event.user_id)
    if isinstance(event, GroupIncreaseNoticeEvent):
        text = f" 欢迎{name}加入本群！请先看看群规，有问题可以直接问管理员。"
    else:
        text = f" {name}已离开本群。"

    # Build markdown content with avatar image
    md_content = f"{text}\n\n![#80px #80px]({avatar})"
    md_data = json.dumps({"markdown": {"content": md_content}}, ensure_ascii=False)
    md_b64 = base64.b64encode(md_data.encode("utf-8")).decode("utf-8")
    md_cq = f"[CQ:markdown,data={md_b64}]"

    return Message(f"[CQ:at,qq={user_id}] {md_cq}")


@member_handler.handle()
async def handle_member_notice(
    bot: Bot,
    event: GroupIncreaseNoticeEvent | GroupDecreaseNoticeEvent,
):
    name, avatar = await _member_profile(bot, event)
    await bot.send_group_msg(
        group_id=event.group_id,
        message=_build_message(event, name, avatar),
    )
    logger.info(
        "已发送成员变动消息: group=%s user=%s type=%s name=%s",
        event.group_id,
        event.user_id,
        "add" if isinstance(event, GroupIncreaseNoticeEvent) else "remove",
        name,
    )
