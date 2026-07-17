import base64
import json
import logging
import random

from nonebot import on_notice
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupDecreaseNoticeEvent,
    GroupIncreaseNoticeEvent,
    Message,
    MessageSegment,
)

logger = logging.getLogger("nonebot.plugin.member_notice")

# ================= ⚙️ 随机文案 =================

WELCOME_TEXTS = [
    "呀，又有新朋友加入了呢！欢迎来到这里，不用太拘束，尽情聊天吧♪",
    "哼哼~ 欢迎加入！这里有很多有趣的人哦，希望能和你好好相处呢☆",
    "好耶！群里变得更热闹了呢。欢迎你哦，把这里当成自己的秘密基地也没关系~",
    "欢迎光临！既然来了，就留下来陪大家一起玩吧，瑞希很期待你的发言哦✨",
    "啊，你来啦！等你很久了呢~ 这里的大家都很亲切，不用担心哦♪",
    "喔？是新的面孔呢。欢迎欢迎~ 要不要先做个自我介绍呀？开玩笑的啦♪",
    "哇，捕捉到新成员！快坐下，瑞希正准备给大家讲有趣的事情呢♪",
    "终于来啦？一直在等你呢（开玩笑的）。欢迎加入~",
    "欢迎加入。只要不违反群规，在这里做什么都可以哦（大概）~",
    "既然进来了，就别想轻易离开哦？毕竟这里很有趣嘛☆",
    "喔？看来是迷路的小猫咪呢。欢迎加入我们~",
    "啊，手机响了，原来是有新人呀。欢迎来到这个小天地~",
    "嗯哼~ 欢迎新朋友。如果感到无聊的话，随时可以来找我聊天哦。",
    "随便找个位置坐吧，这里很自由的~",
    "又变热闹了一点呢。你好呀，请多关照。",
    "这里可是有很多不可思议的事情发生哦，你要做好心理准备呢♪",
    "欢迎~ 祝你在群里玩得开心！",
    "新大佬！群地位-1（确信）。",
    "检测到高能反应！原来是新人进群了！",
    "欢迎加入大家庭，希望能在这里度过愉快的时光☆",
]

LEAVE_TEXTS = [
    "啊……有人离开了呢。大概是去寻找别的可爱事物了吧？虽然有点寂寞，但祝他好运吧♪",
    "欸？刚刚那是离群的消息吗？真是遗憾，希望我们还能在别的地方相遇呢~",
    "少了一位朋友呢……不过没关系，留下来的大家要更开心地聊天哦☆",
    "有人悄悄离开了。再见啦，不知名的朋友~",
    "哎呀，这就走了吗？明明刚才还觉得这人挺有趣的呢。",
    "无论是相遇还是离别，都是常有的事呢。拜拜~",
    "虽然不知道理由，但还是挥手告别吧。路上小心哦♪",
    "只是短暂的离别而已，说不定哪天又会见面呢。",
    "检测到成员离开。如果是手滑退群的话，记得回来哦。",
    "这就走了吗？但我会一直在这里的哦。",
]

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
        text = " " + random.choice(WELCOME_TEXTS)
    else:
        text = " " + random.choice(LEAVE_TEXTS)

    # Build markdown content with avatar image at the top
    md_content = f"![#35px #35px]({avatar}) {text}"
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
