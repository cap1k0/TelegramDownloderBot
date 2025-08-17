from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from telegram import ChatMember
import instaloader
import re
import asyncio

TOKEN = "Your Token Place "
ADMIN_ID = 8050163445  # 
L = instaloader.Instaloader()

queue = asyncio.Queue()
busy = False

def get_shortcode(link):
    match = re.search(r"instagram\.com/(p|reel|tv)/([^/]+)/", link)
    return match.group(2) if match else None

async def process_post(shortcode, update):
    global busy
    try:
        msg = await update.message.reply_text("⏳ Downloading…")
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        if post.is_video:
            await update.message.reply_video(post.video_url)
        else:
            await update.message.reply_photo(post.url)
        await msg.delete()
    except Exception as e:
        await update.message.reply_text("❌Fail!ا")
        print("Error:", e)
    finally:
        busy = False

async def handle_queue():
    global busy
    while True:
        update, shortcode = await queue.get()
        busy = True
        await process_post(shortcode, update)
        queue.task_done()

async def handle_message(update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    text = update.message.text

    # فقط ادمین‌ها در گروه
    if chat_type != "private" and user_id != ADMIN_ID:
        return

    shortcode = get_shortcode(text)
    if shortcode:
        global busy
        if busy:
            await update.message.reply_text("⚠️ w8…")
        else:
            await queue.put((update, shortcode))
    else:
        await update.message.reply_text("⚠️ Send me vaild link ( IGTV).")

async def welcome(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 سلام! من ربات اینستاگرام هستم، لینک پست/ریل/IGTV بفرست تا ویدیو یا عکسشو برات بفرستم!")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))


app.job_queue.run_repeating(lambda ctx: asyncio.create_task(handle_queue()), interval=1, first=1)

print("🚀 Bot started...")
app.run_polling()
