import random
import base64
from pathlib import Path
from nonebot import on_notice, logger
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupIncreaseNoticeEvent,
    GroupDecreaseNoticeEvent,
    MessageSegment
)

from .config import IMAGE_PROBABILITY, WELCOME_IMAGES

# ================= ⚙️ 配置区域 =================

# 进群欢迎文案 (Mizuki 风格)
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
    "欢迎加入大家庭，希望能在这里度过愉快的时光☆"
]

# 4. 离群/退群文案
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
    "这就走了吗？但我会一直在这里的哦。"
]

# ================= 🔧 辅助函数：图片转Base64 =================
def image_to_base64(path: Path) -> str:
    """读取本地文件并转换为 base64 字符串"""
    with open(path, "rb") as f:
        image_data = f.read()
        b64_str = base64.b64encode(image_data).decode()
        return f"base64://{b64_str}"

# ================= 🔧 代码逻辑区域 =================

welcome_handler = on_notice()
leave_handler = on_notice()

# --- 处理进群事件 ---
@welcome_handler.handle()
async def _(bot: Bot, event: GroupIncreaseNoticeEvent):
    if event.user_id == event.self_id:
        return

    # 1. 随机文案
    text = random.choice(WELCOME_TEXTS)
    
    # 2. 构建消息
    msg = MessageSegment.at(event.user_id) + f" {text}"

    # 3. 发送图片逻辑 (关键修改：转为Base64发送)
    if WELCOME_IMAGES and random.random() <= IMAGE_PROBABILITY:
        img_path_str = random.choice(WELCOME_IMAGES)
        try:
            img_path = Path(img_path_str)
            if img_path.exists() and img_path.is_file():
                # 核心改动：读取文件 -> 转Base64 -> 发送
                # 这样 Linux 的 NapCat 就能直接收到图片数据，而不是错误的路径
                b64_img = image_to_base64(img_path)
                msg += MessageSegment.image(b64_img)
                logger.info(f"正在发送欢迎图片(Base64模式): {img_path_str}")
            else:
                logger.warning(f"欢迎插件警告: 找不到图片 {img_path_str}")
        except Exception as e:
            logger.error(f"欢迎插件图片处理错误: {e}")

    await welcome_handler.finish(msg)


# --- 处理离群事件 ---
@leave_handler.handle()
async def _(bot: Bot, event: GroupDecreaseNoticeEvent):
    if event.user_id == event.self_id:
        return

    text = random.choice(LEAVE_TEXTS)
    msg = f"小伙伴({event.user_id}) 离开了我们... {text}"
    await leave_handler.finish(msg)
