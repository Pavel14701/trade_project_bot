import asyncio
from telebot.async_telebot import  AsyncTeleBot
import telebot
from fastapi import FastAPI, Request

TOKEN = "YOUR_BOT_TOKEN"
WEBHOOK_URL = "https://yourdomain.com/webhook"

bot = AsyncTeleBot(TOKEN)
app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    """Асинхронная обработка вебхука"""
    data = await request.json()
    update = telebot.types.Update.de_json(data)
    await bot.process_new_updates([update])
    return {"status": "ok"}

@bot.message_handler(commands=['start'])
async def start(message):
    await bot.send_message(message.chat.id, "Привет! Я работаю асинхронно через вебхук.")

@bot.message_handler(func=lambda message: True)
async def echo_all(message):
    await bot.send_message(message.chat.id, message.text)

async def main():
    await bot.set_webhook(url=WEBHOOK_URL)
    await bot.infinity_polling()

if name == "main":
    asyncio.run(main())
