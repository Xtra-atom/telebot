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
    "BQACAgUAAxkBAAMJadyLeDEAAaHTSd4R5toFG66ow6xyAAKGAQACSXSQVMG6JKJR5gp6OwQ",
    "BQACAgUAAxkBAAMKadyLeDLWEAoxPW2gHHmgVLbrs5kAAocBAAJJdJBUo7aznY4WyLI7BA",
    "BQACAgUAAxkBAAMLadyLePNVVv8sF9aNAAFYHdsFYu1jAAKrAQACSXSQVLJsQiP897LAOwQ",
    "BQACAgUAAxkBAAMMadyLeEpfZbcQacuYfSMLk0tw7-oAAq4BAAJJdJBUpemTGmv6NT07BA",
    "BQACAgUAAxkBAAMNadyLeEsIpPJxLsF1pjTtNSNP5QIAArABAAJJdJBU7IWO0dNbnhw7BA",
    "BQACAgUAAxkBAAMOadyLeM_zD1pTJlod5LD_xcKu2YoAArEBAAJJdJBU7yEC0liHNCc7BA",
    "BQACAgUAAxkBAAMPadyLeKG8WS3ZZGxXQpAqR8gEgQkAArIBAAJJdJBUqf-vc6wyYq07BA",
    "BQACAgUAAxkBAAMQadyLeKF8RM40o0Is1-KxVmO60ZkAArMBAAJJdJBUGvoRyCkjMds7BA",
    "BQACAgUAAxkBAAMRadyLeLNE_1aekwmzDRs3vIZRyoMAArQBAAJJdJBU1nwBQ5yDtrQ7BA",
    "BQACAgUAAxkBAAMSadyLeK56v9Qiv_CS_5PlWckjnIkAArYBAAJJdJBU7pcnL-q-DpE7BA",
    "BQACAgUAAxkBAAMTadyLePuAjoEHGokgp_esAAEyR6dsAAK4AQACSXSQVN_inP5zcV0wOwQ",
    "BQACAgUAAxkBAAMUadyLePqbDxH6k5oxLq6cQHFtcS4AArkBAAJJdJBUon9GGR5Y48c7BA",
    "BQACAgUAAxkBAAMVadyLeLbGln8U1QjcIUBfbdehCkMAAroBAAJJdJBUrNGM7QkUce87BA",
    "BQACAgUAAxkBAAMWadyLeLkdsieMm3VO-DxZKV7Sx08AArsBAAJJdJBUlelU4wHnceo7BA",
    "BQACAgUAAxkBAAMXadyLeBwWT9loMDJ1tJbEFZCV37wAArwBAAJJdJBUvoFFwjwvwL87BA",
    "BQACAgUAAxkBAAMYadyLeO0D8U90gKiPSl-z3o-mAhkAAr0BAAJJdJBU6FALoiov_SA7BA",
    "BQACAgUAAxkBAAMZadyLeM_DB5Yp_BxgOn5xTl23O98AAr4BAAJJdJBUQNZt7Dye0nk7BA",
    "BQACAgUAAxkBAAMaadyLeFkd3lIfGJ8Iwb4mHt4VIe8AAr8BAAJJdJBUEcZpvSZat2o7BA",
    "BQACAgUAAxkBAAMbadyLeMUf5Go0KE8-mdbzrIeuikMAAsABAAJJdJBUFG8-alWzLLs7BA",
    "BQACAgUAAxkBAAMcadyLeCs0C_aYZqRcbiLSdTa-Kc0AAsEBAAJJdJBU9lrrmc5yr8A7BA",
    "BQACAgUAAxkBAAMdadyLeF2-N1cMA4-T0sRKjFW2lgoAAsIBAAJJdJBU83C36Hmk3y07BA",
    "BQACAgUAAxkBAAMeadyLeAbqR9AYiHN6ZgAB9iBuj3StAALDAQACSXSQVNmaNPQIbC6VOwQ",
    "BQACAgUAAxkBAAMfadyLeGeB3emGCQ-Y_0BOWlLw_iIAAsQBAAJJdJBUwhhhtcD6PuI7BA",
    "BQACAgUAAxkBAAMgadyLeIjZW3HUUp9bLpCvF8J52MgAAsUBAAJJdJBUycWiPIqWuQABOwQ",
    "BQACAgUAAxkBAAMhadyLeFg7_r2yqTlUbDB9CMTy9DIAAsYBAAJJdJBUfIEo54BBWsc7BA",
    "BQACAgUAAxkBAAMiadyLeGU_KudZLrB2NwuRpxZA1EIAAscBAAJJdJBUT6nRMnaNkXk7BA",
    "BQACAgUAAxkBAAMjadyLeHGtOu7zM8bOjgr7Q2rt0wsAAsgBAAJJdJBU_BbAK2RCtU47BA",
    "BQACAgUAAxkBAAMkadyLeO6efisEZWP0m00xcF9F-aMAAskBAAJJdJBUTIUOf46Wdew7BA",
    "BQACAgUAAxkBAAMladyLeJfnpxebzB72vjOzTHuUr2IAAsoBAAJJdJBUgEnZVXuo6TQ7BA",
    "BQACAgUAAxkBAAMmadyLeDheZ0_Qcd2VKmWmbQGKyYsAAssBAAJJdJBU31xeYd75pmU7BA",
    "BQACAgUAAxkBAAMnadyLeMAu8eu0XHfy7JxAMiPv7RkAAswBAAJJdJBU44blHSlx0w47BA",
    "BQACAgUAAxkBAAMoadyLeF_r4m13EoLMdXU07UuP9dMAAs0BAAJJdJBUNNcFhJQv_QM7BA",
    "BQACAgUAAxkBAAMpadyLeE05YUe829spo8DqHdguc9kAAs4BAAJJdJBUch2vjqU_K4s7BA",
    "BQACAgUAAxkBAAMqadyLeIftq64o_346RnxF0lNu5isAAs8BAAJJdJBUvYgWv8_-DYQ7BA",
    "BQACAgUAAxkBAAMradyLeEvI3tEYHOgrKy2wFA4XuYoAAtABAAJJdJBUv0WPzr8a4Ig7BA",
    "BQACAgUAAxkBAAMsadyLeEgri67UW4wegrjSO5-9M-8AAtMBAAJJdJBUiTgtn06h8-k7BA",
    "BQACAgUAAxkBAAMtadyLeKp0mnSrvvui49Yrd7G_XGMAAuQBAAJJdJBUf0yfbryzEnM7BA",
    "BQACAgUAAxkBAAMuadyLeDaOv1oE-FhLB659vT5PtbYAAucBAAJJdJBU3icIjGNgFFE7BA",
    "BQACAgUAAxkBAAMvadyLeBKaMoT-u2OcJkyYvUWI-pcAAusBAAJJdJBU6n-p2hh6ToU7BA",
    "BQACAgUAAxkBAAMwadyLeHWDuj3CMjal1anXIYocrLEAAu0BAAJJdJBUjbEVAmuTK5A7BA",
    "BQACAgUAAxkBAAMxadyLeFBiQOJ6BBkVQXjeB6q0DrgAAu4BAAJJdJBU1f1_Bwy-u7s7BA",
    "BQACAgUAAxkBAAMyadyLeCOCCUq_ArsSwIsGiWa_D4MAAu8BAAJJdJBUOgmF3xyPW4s7BA",
    "BQACAgUAAxkBAAMzadyLeORNNW9PQpqY_jJpJPjQ82YAAvABAAJJdJBURG3tRA8F8sM7BA",
    "BQACAgUAAxkBAAM0adyLeGbqNC4xk0Y55hHh6M9mOikAAvIBAAJJdJBUAAH3DSY7OBCbOwQ",
    "BQACAgUAAxkBAAM1adyLeGhH_msoFd23r0GWu-O7HMkAAvUBAAJJdJBUzhcPyxDwx347BA",
    "BQACAgEAAxkBAAM2adyLeByqJoJH0lEQ2bcCprnMj3sAAggBAAJWMZhEMhjyiBBTvok7BA",
    "BQACAgEAAxkBAAM3adyLeGFaL-p3YWYm3ZK8zpeErh4AAqEAA_ZLkESofhrbWlul6zsE",
    "BQACAgEAAxkBAAM4adyLeGk78BB0pFHC3GI5LspJVbIAAqIAA_ZLkER79CArG4NNCTsE",
    "BQACAgQAAxkBAAM5adyLeHtMJTOE09Ii74NcVNiUJ3kAAqIJAALXRZFQi-hKrxrSh-o7BA",
    "BQACAgEAAxkBAAM6adyLeNXfqTsFBMSfsg5Eg512xtkAAgYBAAJWMZhEI38GhltWFVA7BA",
    "BQACAgEAAxkBAAM7adyLeN1eAAFtcVudg14rdcylVZHpAAKgAAP2S5BEnIDz9Wp-sNo7BA",
    "BQACAgEAAxkBAAM8adyLeMtuUThvSgJQ7SkTIsRAtSsAAgEBAAJWMZhEpFeLg1g8yHQ7BA",
    "BQACAgQAAxkBAAM9adyLeMlOQk_zcfhTYD6GvYNn4cYAAqMJAALXRZFQSBGqlHfqkq07BA",
    "BQACAgEAAxkBAAM-adyLeNKYZfcXAAF6bULoFN9BzunUAAICAQACVjGYRKeK0hJOL0FsOwQ",
    "BQACAgQAAxkBAAM_adyLeNiINAIIRF_i_OfmnURhfoUAAqQJAALXRZFQot6ESKkBom07BA",
    "BQACAgEAAxkBAANAadyLeKspnZATK6ZnhP7xeHn9fv8AAgMBAAJWMZhENLbrAAGDsBniOwQ",
    "BQACAgEAAxkBAANBadyLeGnoLzh4zEJwMWckQvTKVxsAAgQBAAJWMZhEBQ2KEJuK2RE7BA",
    "BQACAgEAAxkBAANCadyLeKg9Xum_g7fCb3zU0CFMgHYAAgUBAAJWMZhE-XY7tCtX2RU7BA",
    "BQACAgEAAxkBAANDadyLeHdnjccruZT8S-6Y-Wlvit0AAk0BAAJWMZBEaTgwYXIy-vw7BA",
    "BQACAgQAAxkBAANEadyLeECBhg5keJ-p7fYf0JqOxl0AAqAJAALXRZFQdF-qQVpKzh47BA",
    "BQACAgQAAxkBAANFadyLeEWczL5TvUbJxP_QPwUq0dMAAu8HAAIRyZhQ6erzJvbyC7U7BA",
    "BQACAgEAAxkBAANGadyLeMtdHC7F2LqUv0b_X6IoeHkAAwEAAllykEQqUfzFaO1IKDsE",
    "BQACAgEAAxkBAANHadyLeLOCUcFcciSNHQABTMlpqEgPAAIHAQACVjGYRCLeZW7YI0jfOwQ",
    "BQACAgQAAxkBAANIadyLeAQDiY9LSCH9TjmLNstck_YAAqEJAALXRZFQnlTuFPLrkpg7BA",
    "BQACAgQAAxkBAANJadyLeHs62JJAIDCzw-xGSjEGfFwAAtwIAALhK5BQzcP1girsROE7BA",
]

# ============================================
# BOT 1 HANDLERS (File Sender Bot)
# ============================================
async def bot1_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    logger.info(f"[BOT1] User {user.id} (@{user.username}) requested files")
    
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
    await update.message.reply_text(f"✅ Bot 1 (File Sender) running with {len(BOT1_FILES)} files")

# ============================================
# BOT 2 HANDLERS (RDR2 Mixed Content Bot)
# ============================================
async def bot2_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    logger.info(f"[BOT2] User {user.id} (@{user.username}) requested content")
    
    total_items = len(BOT2_DATA) + len(BOT2_FILES)
    
    status_msg = await update.message.reply_text(
        f"📤 Sending {len(BOT2_DATA)} mixed items and {len(BOT2_FILES)} files...\n"
        f"⏱️ Everything will be deleted in 5 minutes."
    )
    
    sent_messages = [status_msg.message_id]
    failed = 0
    item_count = 0
    
    # Send mixed content (photos and text)
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
    
    # Send document files
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
        f"✅ Bot 2 (RDR2 Content) running with {len(BOT2_DATA)} mixed items and {len(BOT2_FILES)} files"
    )

# ============================================
# MAIN - Run both bots simultaneously
# ============================================
async def main():
    # Create bot 1 application
    app1 = ApplicationBuilder().token(BOT1_TOKEN).build()
    app1.add_handler(CommandHandler("start", bot1_start))
    app1.add_handler(CommandHandler("health", bot1_health))
    
    # Create bot 2 application
    app2 = ApplicationBuilder().token(BOT2_TOKEN).build()
    app2.add_handler(CommandHandler("start", bot2_start))
    app2.add_handler(CommandHandler("health", bot2_health))
    
    # Initialize both bots
    await app1.initialize()
    await app2.initialize()
    
    # Start both bots
    await app1.start()
    await app2.start()
    
    logger.info("=" * 50)
    logger.info("Both bots started successfully!")
    logger.info(f"Bot 1 (File Sender): {len(BOT1_FILES)} files")
    logger.info(f"Bot 2 (RDR2 Content): {len(BOT2_DATA)} mixed items + {len(BOT2_FILES)} files")
    logger.info("=" * 50)
    
    # Start polling for both bots
    polling_tasks = [
        app1.updater.start_polling(drop_pending_updates=True),
        app2.updater.start_polling(drop_pending_updates=True)
    ]
    
    # Keep running until interrupted
    try:
        await asyncio.gather(*polling_tasks)
    except KeyboardInterrupt:
        logger.info("Shutting down bots...")
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
