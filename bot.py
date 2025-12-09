import telebot
from yt_dlp import YoutubeDL
import subprocess
import json
from vosk import Model, KaldiRecognizer

TOKEN = "8144462344:AAFiz6pUKmwuu0otFNNQBbq4acCXR3_chCw"

bot = telebot.TeleBot(TOKEN)

# Vosk modeli yuklash
model = Model("model")  # model papkasini yuklash kerak

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! Instagram video linkini yuboring.")

@bot.message_handler(func=lambda m: True)
def download_video(message):
    url = message.text

    bot.reply_to(message, "Yuklanmoqda...")

    ydl_opts = {
        'format': 'best',
        'outtmpl': '%(title)s.%(ext)s'
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file = ydl.prepare_filename(info)

    # audio ga aylash
    audio_file = "audio.wav"
    subprocess.call(["ffmpeg", "-y", "-i", file, audio_file])

    # Matnni chiqarish (speech-to-text)
    rec = KaldiRecognizer(model, 16000)

    import wave
    wf = wave.open(audio_file, "rb")

    text = ""

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            text += res.get("text", "") + " "

    final = json.loads(rec.FinalResult())
    text += final.get("text", "")

    # audio yuborish
    audio = open(audio_file, "rb")
    bot.send_audio(message.chat.id, audio)
    audio.close()

    # text yuborish
    bot.reply_to(message, "📌 Matn:\n" + text)

bot.polling()
