import asyncio
import os
import sys
import logging
import json
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.error import TelegramError

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot tokens
BOT1_TOKEN = os.getenv("BOT1_TOKEN")
BOT2_TOKEN = os.getenv("BOT2_TOKEN")

if not BOT1_TOKEN:
    logger.error("BOT1_TOKEN environment variable is not set!")
    sys.exit(1)

if not BOT2_TOKEN:
    logger.error("BOT2_TOKEN environment variable is not set!")
    sys.exit(1)

logger.info(f"BOT1_TOKEN loaded: {BOT1_TOKEN[:10]}...{BOT1_TOKEN[-10:]}")
logger.info(f"BOT2_TOKEN loaded: {BOT2_TOKEN[:10]}...{BOT2_TOKEN[-10:]}")

DELETE_AFTER_1 = 120  # 2 minutes for bot1
DELETE_AFTER_2 = 300  # 5 minutes for bot2
BATCH_DELAY = 0.5

# Statistics tracking files
STATS_FILE_1 = "bot1_stats.json"
STATS_FILE_2 = "bot2_stats.json"

# ============================================
# STATISTICS TRACKING FUNCTIONS
# ============================================
def load_stats(filename):
    """Load statistics from file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "total_users": 0,
            "total_uses": 0,
            "users": {},
            "daily_stats": {}
        }

def save_stats(filename, stats):
    """Save statistics to file"""
    try:
        with open(filename, 'w') as f:
            json.dump(stats, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save stats to {filename}: {e}")

def track_usage(stats, user_id, username, first_name, last_name):
    """Track user usage"""
    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().isoformat()
    
    user_key = str(user_id)
    
    # Update total uses
    stats["total_uses"] += 1
    
    # Update daily stats
    if today not in stats["daily_stats"]:
        stats["daily_stats"][today] = {"uses": 0, "unique_users": 0}
    stats["daily_stats"][today]["uses"] += 1
    
    # Update user info
    if user_key not in stats["users"]:
        stats["total_users"] += 1
        stats["daily_stats"][today]["unique_users"] += 1
        stats["users"][user_key] = {
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "first_seen": now,
            "last_seen": now,
            "total_uses": 1
        }
    else:
        stats["users"][user_key]["last_seen"] = now
        stats["users"][user_key]["total_uses"] += 1
        stats["users"][user_key]["username"] = username  # Update in case changed
        stats["users"][user_key]["first_name"] = first_name
        stats["users"][user_key]["last_name"] = last_name
    
    return stats

# Initialize stats
bot1_stats = load_stats(STATS_FILE_1)
bot2_stats = load_stats(STATS_FILE_2)

# ============================================
# BOT 1 DATA (File sender bot - 31 files)
# ============================================
BOT1_FILES = [
    "BQACAgQAAxkBAAFG9SBp2jDH8yzPdwAB8rp0aD6KwejscpQAAgQIAALv4OBT-OTF_YW72zU7BA",  # Part 1
    "BQACAgQAAxkBAAFG9R9p2jDHD2vfODRSftPUFL8rbIh_PQACBQgAAu_g4FNg2Q8dJr2zpzsE",  # Part 2
    "BQACAgQAAxkBAAFG9QJp2jDHeDJ0JVWw5oxGZ7z5C4ojBAACBwgAAu_g4FOBrrYAAVaUr6Q7BA",  # Part 3
    "BQACAgQAAxkBAAFG9QNp2jDHBXmzAAGXizGja7HaLkm64RsAAggIAALv4OBTugn-DeO-mKE7BA",  # Part 4
    "BQACAgQAAxkBAAFG9QRp2jDHvyG_oB3t3_iGvA6OkCbuagACCQgAAu_g4FPNWekrlvtvTDsE",  # Part 5
    "BQACAgQAAxkBAAFG9QVp2jDHRvIXcBJZaC6iIqyUWUDHfgACCggAAu_g4FMpO5ClgY7ygTsE",  # Part 6
    "BQACAgQAAxkBAAFG9QZp2jDH-dI3tTjMv6fCURLih56LSAACCwgAAu_g4FNm9Gttp1vxwzsE",  # Part 7
    "BQACAgQAAxkBAAFG9Qdp2jDHCz0lIs7a6dcfeDmixA4qlQACDAgAAu_g4FO_SYvlSaN3vzsE",  # Part 8
    "BQACAgQAAxkBAAFG9Qhp2jDHRu6kj5YQ8-234uIh-EkO8wACDggAAu_g4FNliw1Y7iK4BjsE",  # Part 9
    "BQACAgQAAxkBAAFG9Qlp2jDHSMyv63LPqOakq28cI28M8gACDwgAAu_g4FOwHwIqRg5RMjsE",  # Part 10
    "BQACAgQAAxkBAAFG9Qpp2jDHoICCu6ZgoyDYZ8IAAQNu4VUAAhAIAALv4OBTOmJ0SOcXHGw7BA",  # Part 11
    "BQACAgQAAxkBAAFG9Qtp2jDHD59qfOyZ66eSSsaHueVqeQACEQgAAu_g4FOJjf9pZfFB1zsE",  # Part 12
    "BQACAgQAAxkBAAFG9Qxp2jDHEWdEhBudbQetT4mvDyg3xgACEggAAu_g4FOn7eukwbCvOzsE",  # Part 13
    "BQACAgQAAxkBAAFG9Q1p2jDH8ygtAAExT9tkQdM2wkTbvYsAAhMIAALv4OBTmLtYbLgk7pQ7BA",  # Part 14
    "BQACAgQAAxkBAAFG9Q5p2jDHnVIy3w4MR0bm3PcTkZ8U_wACFQgAAu_g4FMaCSYdA5kPOjsE",  # Part 15
    "BQACAgQAAxkBAAFG9Q9p2jDHSb4depGtdYYgiT38MfgSYQACFggAAu_g4FPmuoYP0Ri1ozsE",  # Part 16
    "BQACAgQAAxkBAAFG9RBp2jDHWdKmBJ6rdP93MTOAbYq7HQACGQgAAu_g4FPUzloxg4xquTsE",  # Part 17
    "BQACAgQAAxkBAAFG9RFp2jDHC_gB_6IeT9psy_jC3__HqQACGwgAAu_g4FORveYi7-FrBDsE",  # Part 18
    "BQACAgQAAxkBAAFG9RJp2jDHBdyAeHMdgj863rpbz7Lz1gACHAgAAu_g4FPqHgbz6H_6wjsE",  # Part 19
    "BQACAgQAAxkBAAFG9RNp2jDHk2U3DJymODjK2yY9CG-1fQACIAgAAu_g4FP5h-MZPsV-zTsE",  # Part 20
    "BQACAgQAAxkBAAFG9RRp2jDH2PpW7OliRtHgX1DbaUhDiwACIggAAu_g4FOPk5XcPKhM3zsE",  # Part 21
    "BQACAgQAAxkBAAFG9RVp2jDHCcp-dIRdc97HX0DIr3NrNQACJQgAAu_g4FM7EBC1kw2XBzsE",  # Part 22
    "BQACAgQAAxkBAAFG9RZp2jDHOIlDRfBGQo_-Nc8BgQq1nQACKAgAAu_g4FPZibXhJClJ5TsE",  # Part 23
    "BQACAgQAAxkBAAFG9Rdp2jDH8TIgd_L63mZf6R6-M2sxbgACKQgAAu_g4FOAcsn4TbNorzsE",  # Part 24
    "BQACAgQAAxkBAAFG9Rhp2jDHTRb7ySF06u1N7klBBtBqTwACKwgAAu_g4FPIfq0y1uL3SDsE",  # Part 25
    "BQACAgQAAxkBAAFG9Rlp2jDHTWISHKaR_PRgqZTuw6GpawACLAgAAu_g4FM0uRx4_T0dbzsE",  # Part 26
    "BQACAgQAAxkBAAFG9Rpp2jDHCLSYp3RZ1oTm1Q3d9k1a_gACLQgAAu_g4FPxVanIQqZ9gTsE",  # Part 27
    "BQACAgQAAxkBAAFG9Rtp2jDHjh32dlmP_jCzGGMJzkBfeAACLggAAu_g4FPCabki_y4gxzsE",  # Part 28
    "BQACAgQAAxkBAAFG9Rxp2jDHvQzaHuIkdU3u1dGSLWm_fgACMQgAAu_g4FPyg4Mj1K-NujsE",  # Part 29
    "BQACAgQAAxkBAAFG9R1p2jDH3c1biME2CJuj9qP10biswQACMggAAu_g4FOIGscaoqW1KTsE",  # Part 30
    "BQACAgQAAxkBAAFG9R5p2jDHEaEVbim349CVIqGO8CgLnAACMwgAAu_g4FNURhB7jAXg5TsE",  # Part 31
]

# ============================================
# BOT 2 DATA (RDR2 Mixed Content Bot)
# ============================================
BOT2_DATA = [
    {"type":"photo","id":"AgACAgUAAxkBAAOVadyNDGkEhgHfZS4YuHrjRtbNvfYAAkKqMRuJb4lUkNAb7Ml8Q4MBAAMCAAN4AAM7BA"},
    {"type":"text","text":"America, 1899.\n\nArthur Morgan and the Van der Linde gang are outlaws on the run. With federal agents and the best bounty hunters in the nation massing on their heels, the gang must rob, steal and fight their way across the rugged heartland of America in order to survive. As deepening internal divisions threaten to tear the gang apart, Arthur must make a choice between his own ideals and loyalty to the gang who raised him.\n\nNow featuring additional Story Mode content and a fully-featured Photo Mode, Red Dead Redemption 2 also includes free access to the shared living world of Red Dead Online, where players take on an array of roles to carve their own unique path on the frontier as they track wanted criminals as a Bounty Hunter, create a business as a Trader, unearth exotic treasures as a Collector or run an underground distillery as a Moonshiner and much more.\n\nWith all new graphical and technical enhancements for deeper immersion, Red Dead Redemption 2 for PC takes full advantage of the power of the PC to bring every corner of this massive, rich and detailed world to life including increased draw distances; higher quality global illumination and ambient occlusion for improved day and night lighting; improved reflections and deeper, higher resolution shadows at all distances; tessellated tree textures and improved grass and fur textures for added realism in every plant and animal.\n\nRed Dead Redemption 2 for PC also offers HDR support, the ability to run high-end display setups with 4K resolution and beyond, multi-monitor configurations, widescreen configurations, faster frame rates and more."},
    {"type":"photo","id":"AgACAgUAAxkBAAOXadyNDFzBHddXnYOrBy4sMcSWZ-cAAjyqMRuJb4lULf2vXHp9ZOIBAAMCAAN4AAM7BA"},
    {"type":"photo","id":"AgACAgUAAxkBAAOYadyNDMqB6TgPkM8txDawGTCyJfcAAj2qMRuJb4lUviFIQxeipWcBAAMCAANtAAM7BA"},
    {"type":"photo","id":"AgACAgUAAxkBAAOZadyNDEMzjzNvhZDM6LGiHOZXLHMAAj6qMRuJb4lUO0DR1S6KI0gBAAMCAANtAAM7BA"},
    {"type":"photo","id":"AgACAgUAAxkBAAOaadyNDC4277_PQLou6uS1kG4tKTwAAj-qMRuJb4lUhQxktXFQUxYBAAMCAANtAAM7BA"},
    {"type":"photo","id":"AgACAgUAAxkBAAObadyNDI2NRWGdeU3i9hm3YYw1xB0AAkCqMRuJb4lUyJmEY-LZRI4BAAMCAANtAAM7BA"},
    {"type":"photo","id":"AgACAgUAAxkBAAOcadyNDJil2lQ4ssFohcwasOX0YssAAkGqMRuJb4lUY-YJ41Qp4XsBAAMCAANtAAM7BA"},
    {"type":"text","text":"Minimum Requirements:\n\nCPU: Intel Core i5-2500K / AMD FX-6300\nCPU Speed: Info\nRAM: 8 GB\nOS: Windows 7 SP1\nVideo Card: Nvidia GeForce GTX 770 2GB / AMD Radeon R9 280\nPixel Shader: 5.0\nVertex Shader: 5.0\nFree Disk Space: 150 GB\nDedicated Video RAM: 2048 MB\n\nRecommended Requirements:\n\nCPU: Intel Core i7-4770K / AMD Ryzen 5 1500X\nCPU Speed: Info\nRAM: 12 GB\nOS: Windows 10\nVideo Card: Nvidia GeForce GTX 1060 6GB / AMD Radeon RX 480 4GB\nPixel Shader: 5.1\nVertex Shader: 5.1\nFree Disk Space: 150 GB\nDedicated Video RAM: 3072 MB"},
]

BOT2_FILES = [
    "BQACAgUAAxkBAAMHadyLeDBk08V6ghNJ0szmS91qEzMAAn8BAAJJdJBUxb3iL52a-Ko7BA",
    "BQACAgUAAxkBAAMIadyLeDW9HZn2kuzogi9VOAOnngADggEAAkl0kFSEnOkCkBhQ4jsE",
    # ... (truncated for brevity - keep all your 67 file IDs here)
    "BQACAgQAAxkBAANJadyLeHs62JJAIDCzw-xGSjEGfFwAAtwIAALhK5BQzcP1girsROE7BA",
]

# ============================================
# STATS COMMAND HANDLERS
# ============================================
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE, bot_name: str, stats: dict, stats_file: str):
    """Generic stats command handler"""
    user = update.effective_user
    
    today = datetime.now().strftime("%Y-%m-%d")
    today_stats = stats["daily_stats"].get(today, {"uses": 0, "unique_users": 0})
    
    # Get top users (most active)
    sorted_users = sorted(
        stats["users"].items(), 
        key=lambda x: x[1]["total_uses"], 
        reverse=True
    )[:10]
    
    message = f"📊 **{bot_name} Statistics**\n\n"
    message += f"👥 **Total Unique Users:** {stats['total_users']}\n"
    message += f"🔄 **Total Uses:** {stats['total_uses']}\n\n"
    message += f"📅 **Today's Stats:**\n"
    message += f"   • Uses: {today_stats['uses']}\n"
    message += f"   • Unique Users: {today_stats['unique_users']}\n\n"
    
    if sorted_users:
        message += "🏆 **Top 10 Most Active Users:**\n"
        for i, (user_id, data) in enumerate(sorted_users, 1):
            name = data['first_name']
            if data['last_name']:
                name += f" {data['last_name']}"
            if data['username']:
                name += f" (@{data['username']})"
            message += f"{i}. {name}: {data['total_uses']} uses\n"
    
    # Add last 7 days summary
    message += "\n📈 **Last 7 Days:**\n"
    from datetime import timedelta
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        day_stats = stats["daily_stats"].get(date, {"uses": 0, "unique_users": 0})
        day_name = (datetime.now() - timedelta(days=i)).strftime("%a")
        message += f"   {day_name}: {day_stats['uses']} uses ({day_stats['unique_users']} users)\n"
    
    await update.message.reply_text(message, parse_mode="Markdown")

async def bot1_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot 1 stats command"""
    await stats_command(update, context, "File Sender Bot", bot1_stats, STATS_FILE_1)

async def bot2_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot 2 stats command"""
    await stats_command(update, context, "RDR2 Content Bot", bot2_stats, STATS_FILE_2)

# ============================================
# BOT 1 HANDLERS (File Sender Bot)
# ============================================
async def bot1_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Track usage
    global bot1_stats
    bot1_stats = track_usage(
        bot1_stats, 
        user.id, 
        user.username, 
        user.first_name, 
        user.last_name
    )
    save_stats(STATS_FILE_1, bot1_stats)
    
    logger.info(f"[BOT1] User {user.id} (@{user.username}) requested files (Use #{bot1_stats['users'][str(user.id)]['total_uses']})")
    
    if not BOT1_FILES:
        await update.message.reply_text("❌ No files configured yet!")
        return
    
    status_msg = await update.message.reply_text(
        f"📤 Sending {len(BOT1_FILES)} files...\n"
        f"⏱️ Files will be deleted in 2 minutes."
    )
    
    sent_messages = [status_msg.message_id]
    failed = 0
    
    for i, file_id in enumerate(BOT1_FILES, 1):
        try:
            msg = await update.message.reply_document(
                document=file_id,
                caption=f"📄 Part {i}/{len(BOT1_FILES)}"
            )
            sent_messages.append(msg.message_id)
            await asyncio.sleep(BATCH_DELAY)
        except Exception as e:
            logger.error(f"[BOT1] Failed to send file {i}: {e}")
            failed += 1
    
    await status_msg.edit_text(
        f"✅ Sent {len(BOT1_FILES) - failed}/{len(BOT1_FILES)} files.\n"
        f"⏱️ Deleting in 2 minutes..."
    )
    
    await asyncio.sleep(DELETE_AFTER_1)
    
    for msg_id in sent_messages:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
            await asyncio.sleep(0.05)
        except:
            pass

async def bot1_health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"✅ Bot 1 (File Sender) running\n"
        f"📊 Files: {len(BOT1_FILES)}\n"
        f"👥 Total users: {bot1_stats['total_users']}\n"
        f"🔄 Total uses: {bot1_stats['total_uses']}"
    )

# ============================================
# BOT 2 HANDLERS (RDR2 Mixed Content Bot)
# ============================================
async def bot2_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Track usage
    global bot2_stats
    bot2_stats = track_usage(
        bot2_stats, 
        user.id, 
        user.username, 
        user.first_name, 
        user.last_name
    )
    save_stats(STATS_FILE_2, bot2_stats)
    
    logger.info(f"[BOT2] User {user.id} (@{user.username}) requested content (Use #{bot2_stats['users'][str(user.id)]['total_uses']})")
    
    total_items = len(BOT2_DATA) + len(BOT2_FILES)
    
    status_msg = await update.message.reply_text(
        f"📤 Sending {len(BOT2_DATA)} mixed items and {len(BOT2_FILES)} files...\n"
        f"⏱️ Everything will be deleted in 5 minutes."
    )
    
    sent_messages = [status_msg.message_id]
    failed = 0
    item_count = 0
    
    for item in BOT2_DATA:
        item_count += 1
        try:
            if item["type"] == "photo":
                msg = await update.message.reply_photo(
                    photo=item["id"],
                    caption=f"🖼️ Item {item_count}/{total_items}"
                )
                sent_messages.append(msg.message_id)
            elif item["type"] == "text":
                msg = await update.message.reply_text(text=item["text"])
                sent_messages.append(msg.message_id)
            await asyncio.sleep(BATCH_DELAY)
        except Exception as e:
            logger.error(f"[BOT2] Failed to send DATA item {item_count}: {e}")
            failed += 1
    
    for i, file_id in enumerate(BOT2_FILES, 1):
        item_count += 1
        try:
            msg = await update.message.reply_document(
                document=file_id,
                caption=f"📄 File {i}/{len(BOT2_FILES)} (Total: {item_count}/{total_items})"
            )
            sent_messages.append(msg.message_id)
            await asyncio.sleep(BATCH_DELAY)
        except Exception as e:
            logger.error(f"[BOT2] Failed to send file {i}: {e}")
            failed += 1
    
    await status_msg.edit_text(
        f"✅ Sent {total_items - failed}/{total_items} items.\n"
        f"⏱️ Deleting in 5 minutes..."
    )
    
    await asyncio.sleep(DELETE_AFTER_2)
    
    for msg_id in sent_messages:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
            await asyncio.sleep(0.05)
        except:
            pass

async def bot2_health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"✅ Bot 2 (RDR2 Content) running\n"
        f"📊 Mixed items: {len(BOT2_DATA)}, Files: {len(BOT2_FILES)}\n"
        f"👥 Total users: {bot2_stats['total_users']}\n"
        f"🔄 Total uses: {bot2_stats['total_uses']}"
    )

# ============================================
# MAIN
# ============================================
async def main():
    app1 = ApplicationBuilder().token(BOT1_TOKEN).build()
    app1.add_handler(CommandHandler("start", bot1_start))
    app1.add_handler(CommandHandler("health", bot1_health))
    app1.add_handler(CommandHandler("stats", bot1_stats))
    
    app2 = ApplicationBuilder().token(BOT2_TOKEN).build()
    app2.add_handler(CommandHandler("start", bot2_start))
    app2.add_handler(CommandHandler("health", bot2_health))
    app2.add_handler(CommandHandler("stats", bot2_stats))
    
    await app1.initialize()
    await app2.initialize()
    await app1.start()
    await app2.start()
    
    logger.info("=" * 50)
    logger.info("Both bots started successfully!")
    logger.info(f"Bot 1 (File Sender): {len(BOT1_FILES)} files | Users: {bot1_stats['total_users']} | Uses: {bot1_stats['total_uses']}")
    logger.info(f"Bot 2 (RDR2 Content): {len(BOT2_DATA)} items + {len(BOT2_FILES)} files | Users: {bot2_stats['total_users']} | Uses: {bot2_stats['total_uses']}")
    logger.info("=" * 50)
    
    await app1.updater.start_polling(drop_pending_updates=True)
    await app2.updater.start_polling(drop_pending_updates=True)
    
    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        logger.info("Received cancellation signal")
    finally:
        logger.info("Shutting down bots...")
        await app1.updater.stop()
        await app2.updater.stop()
        await app1.stop()
        await app2.stop()
        await app1.shutdown()
        await app2.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bots stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
