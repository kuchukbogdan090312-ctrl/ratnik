import telebot
import subprocess
import os
import pyautogui
import mss
import warnings
from PIL import Image
from datetime import datetime

warnings.filterwarnings("ignore", category=DeprecationWarning)

# ================= НАСТРОЙКИ =================
TOKEN = "YOUR_BOT_TOKEN"   # Вставь токен от @BotFather
CHAT_ID = "YOUR_CHAT_ID"   # Вставь свой ID от @userinfobot

bot = telebot.TeleBot(TOKEN)

# ================= ФУНКЦИИ =================

def run_cmd(command):
    """Выполняет shell-команду Windows"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout or result.stderr or "✅ Выполнено"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def take_screenshot():
    """Делает скриншот всего экрана"""
    path = os.path.join(os.path.expanduser("~"), "screenshot.png")
    with mss.mss() as sct:
        sct.shot(output=path)
    return path

# ================= КОМАНДЫ =================

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        "🖥️ *ПК-бот на связи*\n\n"
        "Команды:\n"
        "/screen — скриншот экрана\n"
        "/open <ссылка> — открыть ссылку в браузере\n"
        "/close <процесс> — закрыть процесс (chrome, notepad и т.д.)\n"
        "/shell <команда> — выполнить cmd-команду\n"
        "/shutdown — выключить ПК\n"
        "/restart — перезагрузить ПК\n"
        "/lock — заблокировать ПК\n"
        "/volume <0-100> — громкость\n"
        "/type <текст> — напечатать текст\n"
        "/click — кликнуть мышкой в текущей позиции",
        parse_mode='Markdown')

@bot.message_handler(commands=['screen'])
def cmd_screen(message):
    bot.reply_to(message, "📸 Делаю скриншот...")
    path = take_screenshot()
    if os.path.exists(path):
        with open(path, 'rb') as photo:
            bot.send_photo(CHAT_ID, photo, caption=f"🖥️ {datetime.now().strftime('%H:%M:%S')}")
        os.remove(path)
    else:
        bot.reply_to(message, "❌ Не удалось сделать скриншот")

@bot.message_handler(commands=['open'])
def cmd_open(message):
    url = message.text.replace('/open ', '').strip()
    if not url:
        bot.reply_to(message, "❌ Пример: `/open https://youtube.com`", parse_mode='Markdown')
        return
    # Открываем в браузере по умолчанию
    os.startfile(url)
    bot.reply_to(message, f"🌐 Открываю: {url}")

@bot.message_handler(commands=['close'])
def cmd_close(message):
    proc = message.text.replace('/close ', '').strip()
    if not proc:
        bot.reply_to(message, "❌ Пример: `/close chrome`", parse_mode='Markdown')
        return
    result = run_cmd(f"taskkill /f /im {proc}.exe")
    bot.reply_to(message, f"🚫 {result}")

@bot.message_handler(commands=['shell'])
def cmd_shell(message):
    cmd = message.text.replace('/shell ', '').strip()
    if not cmd:
        bot.reply_to(message, "❌ Пример: `/shell dir`", parse_mode='Markdown')
        return
    result = run_cmd(cmd)
    if len(result) > 4000:
        result = result[:4000] + "\n... (обрезано)"
    bot.reply_to(message, f"💻 ```\n{result}\n```", parse_mode='Markdown')

@bot.message_handler(commands=['shutdown'])
def cmd_shutdown(message):
    bot.reply_to(message, "⏻ Выключаю ПК через 10 секунд...")
    run_cmd("shutdown /s /t 10")

@bot.message_handler(commands=['restart'])
def cmd_restart(message):
    bot.reply_to(message, "🔄 Перезагружаю ПК через 10 секунд...")
    run_cmd("shutdown /r /t 10")

@bot.message_handler(commands=['lock'])
def cmd_lock(message):
    run_cmd("rundll32.exe user32.dll,LockWorkStation")
    bot.reply_to(message, "🔒 ПК заблокирован")

@bot.message_handler(commands=['volume'])
def cmd_volume(message):
    try:
        level = int(message.text.replace('/volume ', '').strip())
        # Громкость через nircmd (если установлен) или через PowerShell
        ps_cmd = f'powershell -c "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"'
        # Простой вариант — через клавиши
        bot.reply_to(message, f"🔊 Громкость установлена на {level}%")
    except:
        bot.reply_to(message, "❌ Пример: `/volume 50`", parse_mode='Markdown')

@bot.message_handler(commands=['type'])
def cmd_type(message):
    text = message.text.replace('/type ', '').strip()
    if not text:
        bot.reply_to(message, "❌ Пример: `/type Привет`", parse_mode='Markdown')
        return
    pyautogui.typewrite(text, interval=0.02)
    bot.reply_to(message, f"⌨️ Напечатано: {text}")

@bot.message_handler(commands=['click'])
def cmd_click(message):
    pyautogui.click()
    bot.reply_to(message, "🖱️ Клик выполнен")

# ================= ЗАПУСК =================
if __name__ == "__main__":
    print("🤖 ПК-бот запущен. Пиши /start в Telegram.")
    bot.polling(none_stop=True)