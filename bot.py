import logging
import os
import re
import tempfile
from pathlib import Path

import yt_dlp
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
WRITE_TIMEOUT = 60
READ_TIMEOUT = 60
BOT_TOKEN = os.environ["BOT_TOKEN"]
TARGET_CHAT_ID = int(os.environ["TARGET_CHAT_ID"])
ALLOWED_USER_IDS = {
    int(x) for x in os.environ.get("ALLOWED_USER_IDS", "").split(",") if x.strip()
}
MAX_UPLOAD_MB = 49  # Telegram Bot API hard limit is 50MB

URL_RE = re.compile(r"https?://\S+")
SUPPORTED_DOMAINS = ("twitter.com", "x.com", "t.co")


def is_supported_url(url: str) -> bool:
    return any(d in url for d in SUPPORTED_DOMAINS)


def has_audio(info: dict) -> bool:
    """Whether the downloaded media actually has an audio track.

    yt-dlp doesn't consistently mark 'no audio' the same way: for a single
    fallback format it's usually the string "none", but for a merged
    video+audio download the top-level acodec is often plain None instead -
    which broke a naive `!= "none"` check (None != "none" is True, so a
    silent GIF was misread as having audio). This checks every actual
    stream involved (falling back to the info dict itself when there's no
    separate requested_formats list) and only tags it as having audio if
    ANY of them report a real codec - not None, and not the string "none".
    """
    formats_to_check = info.get("requested_formats") or [info]
    return any(f.get("acodec") not in (None, "none") for f in formats_to_check)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send me a twitter/x link and I'll drop the video into the group."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if ALLOWED_USER_IDS and user_id not in ALLOWED_USER_IDS:
        logger.info("Ignoring message from unauthorized user %s", user_id)
        return

    text = update.message.text or ""
    urls = [u for u in URL_RE.findall(text) if is_supported_url(u)]
    if not urls:
        return

    for url in urls:
        await process_url(update, context, url)


async def process_url(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
    status_msg = await update.message.reply_text("Downloading...")
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        outtmpl = str(Path(tmpdir) / "%(id)s.%(ext)s")
        ydl_opts = {
            "outtmpl": outtmpl,
            "format": "bv*+ba/b",
            "merge_output_format": "mp4",
            "quiet": True,
            "no_warnings": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
        except Exception as e:
            logger.exception("Download failed for %s", url)
            await status_msg.edit_text(f"Failed to download: {e}")
            return

        files = [p for p in Path(tmpdir).iterdir() if p.is_file()]
        if not files:
            await status_msg.edit_text("Download failed: no file was produced.")
            return
        file_path = files[0]

        size_mb = file_path.stat().st_size / (1024 * 1024)
        if size_mb > MAX_UPLOAD_MB:
            await status_msg.edit_text(
                f"File too big ({size_mb:.1f}MB) — Telegram bot upload limit is 50MB."
            )
            return

        caption = None
        try:
            if has_audio(info):
                with open(file_path, "rb") as f:
                    await context.bot.send_video(
                        chat_id=TARGET_CHAT_ID,
                        video=f,
                        caption=caption,
                        supports_streaming=True,
                    )
            else:
                with open(file_path, "rb") as f:
                    await context.bot.send_animation(
                        chat_id=TARGET_CHAT_ID,
                        animation=f,
                        caption=caption,
                    )
        except Exception as e:
            logger.exception("Upload failed")
            await status_msg.edit_text(f"Failed to send to group: {e}")
            return

    await status_msg.edit_text("Posted \u2705")


def main():
    app = Application.builder().token(BOT_TOKEN).read_timeout(READ_TIMEOUT).write_timeout(WRITE_TIMEOUT).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Bot starting (polling)...")
    app.run_polling()


if __name__ == "__main__":
    main()