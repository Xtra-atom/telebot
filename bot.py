import asyncio
import os
import sys
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.error import TelegramError

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("BOT_TOKEN environment variable is not set!")
    sys.exit(1)

DELETE_AFTER = 120  # 2 minutes
BATCH_DELAY = 0.5  # Seconds between files

# ============================================
# PASTE THE GENERATED FILES LIST HERE
# ============================================
FILES = [
    "BQACAgQAAxkBAAMLadpDkeRzuUrSYGb5nqMHTRPODcAAAgQIAALv4OBTtxZD8bpT_iw7BA",  # Part 1
    "BQACAgQAAxkBAAMNadpDllhzKAYJwkFo9A5ZbH-sTs8AAgUIAALv4OBTkvqlzX52iUw7BA",  # Part 2
    "BQACAgQAAxkBAAMPadpDodm-ufoZjqWgeNSmFHONdr4AAgcIAALv4OBTltTkfEnYV247BA",  # Part 3
    "BQACAgQAAxkBAAMRadpDpEZIaQElpV-eLre6BI8-YnwAAggIAALv4OBTfGvUMGo59hA7BA",  # Part 4
    "BQACAgQAAxkBAAMTadpDp-nVc88MW1V7DEWPEfmT09gAAgkIAALv4OBT5HoUWuCSzns7BA",  # Part 5
    "BQACAgQAAxkBAAMVadpDq2QBw1yK_21ygGRWzJxgW-0AAgoIAALv4OBT9svyK9OwCFw7BA",  # Part 6
    "BQACAgQAAxkBAAMXadpDsBjkeCOnTWGUznM5Z1ux5lIAAgsIAALv4OBTaUMlzokt7Gs7BA",  # Part 7
    "BQACAgQAAxkBAAMZadpDtNYH0upsd69yrVXHKZNhsbIAAgwIAALv4OBT0ZJzeUR_gTI7BA",  # Part 8
    "BQACAgQAAxkBAAMbadpDuXJRH1dDEL11LTagT2tq8FcAAg4IAALv4OBTehDPX2a5WZQ7BA",  # Part 9
    "BQACAgQAAxkBAAMdadpDv4NncAK4pi6EMUbw0IqWLh4AAg8IAALv4OBTalqVpSU7-HA7BA",  # Part 10
    "BQACAgQAAxkBAAMfadpDw5uqN1QS6wVjBk7R_UP7jC8AAhAIAALv4OBTZkiy_sgVnWE7BA",  # Part 11
    "BQACAgQAAxkBAAMhadpDxh620pM6HAnsYjsEqryWqdcAAhEIAALv4OBTIUMTkVbEFVo7BA",  # Part 12
    "BQACAgQAAxkBAAMjadpDzJJHWtvSzgXQYtcizap3_KAAAhIIAALv4OBTsGd073Lgh647BA",  # Part 13
    "BQACAgQAAxkBAAMladpD0OyDTTWqAeGj6J6oP__wd5QAAhMIAALv4OBTMlx66_v-Z9s7BA",  # Part 14
    "BQACAgQAAxkBAAMnadpD1PUIuwUFadTZ_8tlUwoJDl8AAhUIAALv4OBToOL_216fCcQ7BA",  # Part 15
    "BQACAgQAAxkBAAMpadpD1yZlUwz_9csyZ2LrOnWIfHkAAhYIAALv4OBTMe16dMaDIIU7BA",  # Part 16
    "BQACAgQAAxkBAAMradpD3M519I9KrNSXvgk4D-aDFa4AAhkIAALv4OBT72EF6urua8M7BA",  # Part 17
    "BQACAgQAAxkBAAMtadpD4eDA166QKF3vB0n4BfLfmcoAAhsIAALv4OBTQqfccOR1FMk7BA",  # Part 18
    "BQACAgQAAxkBAAMvadpD5LghjyUQr2UWXrKpi0WMH5AAAhwIAALv4OBT8sVD5y7sMLE7BA",  # Part 19
    "BQACAgQAAxkBAAMxadpD6ecHQdTzbV50U1VGWd4WR-wAAiAIAALv4OBTPg27l55dAoQ7BA",  # Part 20
    "BQACAgQAAxkBAAMzadpD7RoxMHm-N7SRT8Cvy6etpJcAAiIIAALv4OBTY04YOH8bFsY7BA",  # Part 21
    "BQACAgQAAxkBAAM1adpD8vqwMSO7aVxGYpIwlmHzbFcAAiUIAALv4OBTElWM2LBlEUQ7BA",  # Part 22
    "BQACAgQAAxkBAAM3adpD9i9RKr4PXZvPpOHjB464UtMAAigIAALv4OBTcFbOPOyoPVQ7BA",  # Part 23
    "BQACAgQAAxkBAAM5adpD_YyRFtlPGoYEzKN_WjieNjsAAikIAALv4OBTZ0wm8FgKjRg7BA",  # Part 24
    "BQACAgQAAxkBAAM7adpEA2lnmNaPmn40u0RMDlHHdUcAAisIAALv4OBTi1oGzQdmcCY7BA",  # Part 25
    "BQACAgQAAxkBAAM9adpEBl545ljOCDAwebKzVk3rwWwAAiwIAALv4OBTr4XTvJxkFSw7BA",  # Part 26
    "BQACAgQAAxkBAAM_adpECr42AAHxsdowGrjx1ka_yVz7AAItCAAC7-DgU-ZA4SE4eVYHOwQ",  # Part 27
    "BQACAgQAAxkBAANBadpEDZ2GHhaH20fYLLMZFk72-WoAAi4IAALv4OBTzp3OZyELpl87BA",  # Part 28
    "BQACAgQAAxkBAANDadpEEoAURTHXe-LNj79NnpyVJjMAAjEIAALv4OBTyInl4UUZ0qQ7BA",  # Part 29
    "BQACAgQAAxkBAANFadpEFzba228_KGMHohhiygABe50PAAIyCAAC7-DgU64i4YxTLuxJOwQ",  # Part 30
    "BQACAgQAAxkBAANHadpEG0tfB3QLOfDH61GrvAIYMVIAAjMIAALv4OBTq6j6EYKhrbo7BA",  # Part 31
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    logger.info(f"User {user.id} (@{user.username}) requested files")
    
    if not FILES:
        await update.message.reply_text("❌ No files configured yet!")
        return
    
    status_msg = await update.message.reply_text(
        f"📤 Sending {len(FILES)} files...\n"
        f"⏱️ Files will be deleted in 2 minutes.password:https://t.me/pc_game_down"
    )
    
    sent_messages = [status_msg.message_id]
    failed = 0
    
    for i, file_id in enumerate(FILES, 1):
        try:
            msg = await update.message.reply_document(
                document=file_id,
                caption=f"📄 Part {i}/{len(FILES)}"
            )
            sent_messages.append(msg.message_id)
            await asyncio.sleep(BATCH_DELAY)
        except Exception as e:
            logger.error(f"Failed to send file {i}: {e}")
            failed += 1
    
    await status_msg.edit_text(
        f"✅ Sent {len(FILES) - failed}/{len(FILES)} files.\n"
        f"⏱️ Deleting in 2 minutes..."
    )
    
    await asyncio.sleep(DELETE_AFTER)
    
    for msg_id in sent_messages:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
            await asyncio.sleep(0.05)
        except:
            pass

async def health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"✅ Bot running with {len(FILES)} files")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("health", health))
    
    logger.info(f"Bot started with {len(FILES)} files")
    app.run_polling(drop_pending_updates=True)
