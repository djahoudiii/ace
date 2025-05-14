import os
import zipfile
import tempfile
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ✅ قراءة آمنة للتوكن من المتغيرات
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise Exception("❌ TOKEN environment variable not found. Please set it in Railway Variables.")

PROJECTS_DIR = "codes"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    projects = [f for f in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, f))]
    if not projects:
        await update.message.reply_text("🚫 No projects available currently.")
        return
    buttons = [[p] for p in projects]
    markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text("👋 Please select a project to download its files:", reply_markup=markup)

async def send_project_zip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    project_name = update.message.text.strip()
    project_path = os.path.join(PROJECTS_DIR, project_name)
    if not os.path.isdir(project_path):
        await update.message.reply_text("⚠️ Project not found!")
        return
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        zip_path = tmp.name
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for root, _, files in os.walk(project_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, project_path)
                    zipf.write(file_path, arcname)
    await update.message.reply_document(document=open(zip_path, "rb"), filename=f"{project_name}.zip")
    os.remove(zip_path)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_project_zip))

if __name__ == "__main__":
    app.run_polling()
