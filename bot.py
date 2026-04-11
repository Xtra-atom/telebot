import asyncio
import os
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

# Get bot token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    logger.error("BOT_TOKEN environment variable is not set!")
    raise ValueError("BOT_TOKEN environment variable is not set!")

DELETE_AFTER = 120  # 2 minutes
BATCH_SIZE = 5  # Send files in batches to avoid rate limits
BATCH_DELAY = 1  # Seconds between batches

FILES = [
    "BQACAgQAAxkBAAFG9SBp2jDH8yzPdwAB8rp0aD6KwejscpQAAgQIAALv4OBT-OTF_YW72zU7BA",
    "BQACAgQAAxkBAAFG9R9p2jDHD2vfODRSftPUFL8rbIh_PQACBQgAAu_g4FNg2Q8dJr2zpzsE",
    "BQACAgQAAxkBAAFG9QJp2jDHeDJ0JVWw5oxGZ7z5C4ojBAACBwgAAu_g4FOBrrYAAVaUr6Q7BA",
    "BQACAgQAAxkBAAFG9QNp2jDHBXmzAAGXizGja7HaLkm64RsAAggIAALv4OBTugn-DeO-mKE7BA",
    "BQACAgQAAxkBAAFG9QRp2jDHvyG_oB3t3_iGvA6OkCbuagACCQgAAu_g4FPNWekrlvtvTDsE",
    "BQACAgQAAxkBAAFG9QVp2jDHRvIXcBJZaC6iIqyUWUDHfgACCggAAu_g4FMpO5ClgY7ygTsE",
    "BQACAgQAAxkBAAFG9QZp2jDH-dI3tTjMv6fCURLih56LSAACCwgAAu_g4FNm9Gttp1vxwzsE",
    "BQACAgQAAxkBAAFG9Qdp2jDHCz0lIs7a6dcfeDmixA4qlQACDAgAAu_g4FO_SYvlSaN3vzsE",
    "BQACAgQAAxkBAAFG9Qhp2jDHRu6kj5YQ8-234uIh-EkO8wACDggAAu_g4FNliw1Y7iK4BjsE",
    "BQACAgQAAxkBAAFG9Qlp2jDHSMyv63LPqOakq28cI28M8gACDwgAAu_g4FOwHwIqRg5RMjsE",
    "BQACAgQAAxkBAAFG9Qpp2jDHoICCu6ZgoyDYZ8IAAQNu4VUAAhAIAALv4OBTOmJ0SOcXHGw7BA",
    "BQACAgQAAxkBAAFG9Qtp2jDHD59qfOyZ66eSSsaHueVqeQACEQgAAu_g4FOJjf9pZfFB1zsE",
    "BQACAgQAAxkBAAFG9Qxp2jDHEWdEhBudbQetT4mvDyg3xgACEggAAu_g4FOn7eukwbCvOzsE",
    "BQACAgQAAxkBAAFG9Q1p2jDH8ygtAAExT9tkQdM2wkTbvYsAAhMIAALv4OBTmLtYbLgk7pQ7BA",
    "BQACAgQAAxkBAAFG9Q5p2jDHnVIy3w4MR0bm3PcTkZ8U_wACFQgAAu_g4FMaCSYdA5kPOjsE",
    "BQACAgQAAxkBAAFG9Q9p2jDHSb4depGtdYYgiT38MfgSYQACFggAAu_g4FPmuoYP0Ri1ozsE",
    "BQACAgQAAxkBAAFG9RBp2jDHWdKmBJ6rdP93MTOAbYq7HQACGQgAAu_g4FPUzloxg4xquTsE",
    "BQACAgQAAxkBAAFG9RFp2jDHC_gB_6IeT9psy_jC3__HqQACGwgAAu_g4FORveYi7-FrBDsE",
    "BQACAgQAAxkBAAFG9RJp2jDHBdyAeHMdgj863rpbz7Lz1gACHAgAAu_g4FPqHgbz6H_6wjsE",
    "BQACAgQAAxkBAAFG9RNp2jDHk2U3DJymODjK2yY9CG-1fQACIAgAAu_g4FP5h-MZPsV-zTsE",
    "BQACAgQAAxkBAAFG9RRp2jDH2PpW7OliRtHgX1DbaUhDiwACIggAAu_g4FOPk5XcPKhM3zsE",
    "BQACAgQAAxkBAAFG9RVp2jDHCcp-dIRdc97HX0DIr3NrNQACJQgAAu_g4FM7EBC1kw2XBzsE",
    "BQACAgQAAxkBAAFG9RZp2jDHOIlDRfBGQo_-Nc8BgQq1nQACKAgAAu_g4FPZibXhJClJ5TsE",
    "BQACAgQAAxkBAAFG9Rdp2jDH8TIgd_L63mZf6R6-M2sxbgACKQgAAu_g4FOAcsn4TbNorzsE",
    "BQACAgQAAxkBAAFG9Rhp2jDHTRb7ySF06u1N7klBBtBqTwACKwgAAu_g4FPIfq0y1uL3SDsE",
    "BQACAgQAAxkBAAFG9Rlp2jDHTWISHKaR_PRgqZTuw6GpawACLAgAAu_g4FM0uRx4_T0dbzsE",
    "BQACAgQAAxkBAAFG9Rpp2jDHCLSYp3RZ1oTm1Q3d9k1a_gACLQgAAu_g4FPxVanIQqZ9gTsE",
    "BQACAgQAAxkBAAFG9Rtp2jDHjh32dlmP_jCzGGMJzkBfeAACLggAAu_g4FPCabki_y4gxzsE",
    "BQACAgQAAxkBAAFG9Rxp2jDHvQzaHuIkdU3u1dGSLWm_fgACMQgAAu_g4FPyg4Mj1K-NujsE",
    "BQACAgQAAxkBAAFG9R1p2jDH3c1biME2CJuj9qP10biswQACMggAAu_g4FOIGscaoqW1KTsE",
    "BQACAgQAAxkBAAFG9R5p2jDHEaEVbim349CVIqGO8CgLnAACMwgAAu_g4FNURhB7jAXg5TsE"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    logger.info(f"User {user.id} (@{user.username}) requested files in chat {chat_id}")
    
    # Send initial notification
    status_msg = await update.message.reply_text(
        f"📤 Sending {len(FILES)} files... They will be deleted in 2 minutes."
    )
    
    sent_messages = [status_msg.message_id]
    failed_files = 0

    try:
        # Send files in batches to avoid hitting rate limits
        for i in range(0, len(FILES), BATCH_SIZE):
            batch = FILES[i:i + BATCH_SIZE]
            
            for j, file_id in enumerate(batch):
                try:
                    file_num = i + j + 1
                    msg = await update.message.reply_document(
                        document=file_id,
                        caption=f"📄 Part {file_num}/{len(FILES)}"
                    )
                    sent_messages.append(msg.message_id)
                    await asyncio.sleep(0.05)  # Small delay between messages
                    
                except TelegramError as e:
                    logger.error(f"Failed to send file {file_num}: {e}")
                    failed_files += 1
            
            # Delay between batches
            if i + BATCH_SIZE < len(FILES):
                await asyncio.sleep(BATCH_DELAY)
        
        # Update status with completion info
        if failed_files > 0:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_msg.message_id,
                text=f"✅ Sent {len(FILES) - failed_files}/{len(FILES)} files. "
                     f"Failed: {failed_files}. Deleting in 2 minutes..."
            )
        else:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_msg.message_id,
                text=f"✅ All {len(FILES)} files sent successfully! Deleting in 2 minutes..."
            )
        
        # Wait for deletion timer
        await asyncio.sleep(DELETE_AFTER)
        
        # Delete all sent messages
        deleted_count = 0
        for msg_id in sent_messages:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
                deleted_count += 1
                await asyncio.sleep(0.05)  # Small delay to avoid rate limits
            except TelegramError as e:
                logger.debug(f"Could not delete message {msg_id}: {e}")
        
        logger.info(f"Deleted {deleted_count}/{len(sent_messages)} messages for user {user.id}")
        
    except Exception as e:
        logger.error(f"Error in start command for user {user.id}: {e}")
        try:
            await update.message.reply_text("❌ An error occurred. Please try again later.")
        except:
            pass

async def health_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simple health check command"""
    await update.message.reply_text("✅ Bot is running!")

if __name__ == "__main__":
    # Log startup
    logger.info("Starting Telegram bot...")
    logger.info(f"Loaded {len(FILES)} file IDs")
    
    # Build application
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("health", health_check))
    
    # Start polling
    logger.info("Bot is polling for updates...")
    app.run_polling(drop_pending_updates=True)
