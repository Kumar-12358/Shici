# -*- coding: utf-8 -*-
"""每日李白诗自动推送（独立版，不依赖 WorkBuddy）。

选诗：读 poems.json + history.json，排除已发过的作品，按北京日期的「年内第几天」索引选一首未发的。
生成六段正文，调用 PushPlus 推送，成功后把今天记录写回 history.json。

用法：
  python daily_poem.py            # 真实推送（需 PUSHPLUS_TOKEN 环境变量，或同目录 config.json 的 token）
  python daily_poem.py --dry-run  # 只生成正文并打印，不推送、不写历史（用于本地预览/调试）
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
POEMS = os.path.join(BASE, "poems.json")
HISTORY = os.path.join(BASE, "history.json")
CONFIG = os.path.join(BASE, "config.json")
API = "https://www.pushplus.plus/send"


def beijing_now():
    # GitHub Actions runner 默认 UTC，统一用北京时间判断「今天」与「年内第几天」
    return datetime.now(timezone(timedelta(hours=8)))


def load_token():
    # 优先环境变量（GitHub Actions 用 secret 注入 PUSHPLUS_TOKEN）
    t = os.environ.get("PUSHPLUS_TOKEN", "").strip()
    if t:
        return t
    try:
        with open(CONFIG, encoding="utf-8") as f:
            return json.load(f).get("token", "").strip()
    except Exception:
        return ""


def load_poems():
    with open(POEMS, encoding="utf-8") as f:
        return json.load(f).get("poems", [])


def load_history():
    if not os.path.exists(HISTORY):
        return {"sent": []}
    try:
        with open(HISTORY, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"sent": []}


def already_sent_today(hist):
    today = beijing_now().strftime("%Y-%m-%d")
    return any(i.get("date") == today for i in hist.get("sent", []))


def choose_poem(poems, hist):
    sent = {i.get("work", "") for i in hist.get("sent", [])}
    candidates = [p for p in poems if p.get("work") not in sent]
    if not candidates:
        candidates = list(poems)  # 放宽：全发过了就重选
    doy = beijing_now().timetuple().tm_yday  # 年内第几天，保证每天不同、可预期
    return candidates[doy % len(candidates)]


def build_body(poem):
    lines = "\n".join(poem["lines"])
    return (
        f"{poem['title']}· 唐 · 李白\n\n"
        f"{lines}\n\n"
        f"一句大白话：{poem['plain']}\n\n"
        f"写作时间：{poem['time']}\n\n"
        f"当时发生了什么：{poem['background']}\n"
    )


def push(title, content):
    token = load_token()
    if not token:
        print("还没配置 token：请设置环境变量 PUSHPLUS_TOKEN，或在同目录放 config.json（含 token）。")
        return False
    payload = {
        "token": token,
        "title": title[:100],
        "content": content,
        "template": "txt",
        "channel": "wechat",
    }
    req = urllib.request.Request(
        API,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            res = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print("推送失败（网络/接口问题）：", e)
        return False
    if res.get("code") == 200:
        print("服务器已收下（code 200，渠道=wechat）：", res)
        print("提示：code 200 只代表服务器收下单子，不代表手机真的收到；若没消息去 pushplus.plus 查「最新的请求」。")
        return True
    print("推送失败，服务端返回：", res)
    return False


def remember(title, poem, hist):
    hist.setdefault("sent", [])
    today = beijing_now().strftime("%Y-%m-%d")
    if any(i.get("date") == today for i in hist["sent"]):
        return
    hist["sent"].append({"date": today, "title": title, "work": poem.get("work", "")})
    with open(HISTORY, "w", encoding="utf-8") as f:
        json.dump(hist, f, ensure_ascii=False, indent=2)


def main():
    dry = "--dry-run" in sys.argv
    poems = load_poems()
    hist = load_history()
    if not dry and already_sent_today(hist):
        print("今天已经推送过，跳过。")
        return
    poem = choose_poem(poems, hist)
    now = beijing_now()
    title = f"早安诗词 · {now.month}月{now.day}日 ·{poem['title']}"
    body = build_body(poem)
    print("==== 今日诗词预览 ====")
    print(title)
    print(body)
    print("======================")
    if dry:
        print("[dry-run] 未实际推送，也未写历史。")
        return
    if push(title, body):
        remember(title, poem, hist)
        print("已记录到 history.json。")


if __name__ == "__main__":
    main()
