import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import os

TOKEN = os.getenv("BOT_TOKEN") or "8333531773:AAGp3uuIIZe7FJWMq8jHMs1uUZLgKQ0TYlA"

# Визуализация раскроя (как раньше)
def make_cut_image(sheet_w, sheet_h, area_w, area_h):
    nx_full = area_w // sheet_w
    ny_full = area_h // sheet_h
    rem_x = area_w % sheet_w
    rem_y = area_h % sheet_h

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(0, area_w)
    ax.set_ylim(0, area_h)
    ax.set_aspect('equal')

    for i in range(nx_full):
        for j in range(ny_full):
            ax.add_patch(patches.Rectangle(
                (i * sheet_w, j * sheet_h),
                sheet_w, sheet_h,
                linewidth=1,
                edgecolor='black',
                facecolor='lightblue'
            ))

    if rem_x > 0:
        for j in range(ny_full):
            ax.add_patch(patches.Rectangle(
                (nx_full * sheet_w, j * sheet_h),
                rem_x, sheet_h,
                linewidth=1,
                edgecolor='green',
                facecolor='lightgreen'
            ))
    if rem_y > 0:
        for i in range(nx_full):
            ax.add_patch(patches.Rectangle(
                (i * sheet_w, ny_full * sheet_h),
                sheet_w, rem_y,
                linewidth=1,
                edgecolor='green',
                facecolor='lightgreen'
            ))
    if rem_x > 0 and rem_y > 0:
        ax.add_patch(patches.Rectangle(
            (nx_full * sheet_w, ny_full * sheet_h),
            rem_x, rem_y,
            linewidth=1,
            edgecolor='green',
            facecolor='lightgreen'
        ))

    ax.add_patch(patches.Rectangle((0, 0), area_w, area_h, linewidth=2, edgecolor='red', facecolor='none'))
    ax.set_title("Оптимальный раскрой")
    ax.set_xlabel("см (ширина)")
    ax.set_ylabel("см (высота)")
    plt.grid(True, linestyle="--", alpha=0.4)

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 👋 Отправь размеры в формате:\n`лист ширина высота | покрытие ширина высота`\nПример: `лист 30 60 | покрытие 400 400`",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    try:
        left, right = text.split("|")
        sheet_parts = [int(x) for x in left.replace("лист", "").split()]
        area_parts = [int(x) for x in right.replace("покрытие", "").split()]
        sheet_w, sheet_h = sheet_parts
        area_w, area_h = area_parts
        buf = make_cut_image(sheet_w, sheet_h, area_w, area_h)

        nx_full = area_w // sheet_w
        ny_full = area_h // sheet_h
        rem_x = area_w % sheet_w
        rem_y = area_h % sheet_h
        full_sheets = nx_full * ny_full
        extra_sheets = 0
        if rem_x > 0: extra_sheets += ny_full
        if rem_y > 0: extra_sheets += nx_full
        if rem_x > 0 and rem_y > 0: extra_sheets += 1
        total = full_sheets + extra_sheets

        text_reply = (f"📐 Размер листа: {sheet_w}×{sheet_h} см\n"
                      f"📏 Площадь покрытия: {area_w}×{area_h} см\n\n"
                      f"🧩 Целых листов: {full_sheets}\n"
                      f"✂️ Разрезанных листов: {extra_sheets}\n"
                      f"🔢 Всего листов: {total}")

        await update.message.reply_photo(photo=buf, caption=text_reply)
    except Exception:
        await update.message.reply_text("⚠️ Ошибка. Пример: `лист 30 60 | покрытие 400 400`", parse_mode="Markdown")

# Async main для python-telegram-bot v21+
async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Бот запущен...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())