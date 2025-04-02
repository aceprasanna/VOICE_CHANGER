import os
import subprocess
import librosa
import soundfile as sf
from pydub import AudioSegment
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("Missing TELEGRAM_BOT_TOKEN in .env file!")

def fix_mp3(input_mp3, output_mp3):
    """Fix corrupted MP3 using FFmpeg."""
    command = f'ffmpeg -y -i "{input_mp3}" -acodec libmp3lame -q:a 2 "{output_mp3}"'
    subprocess.run(command, shell=True, check=True)
    return output_mp3

def convert_mp3_to_wav(mp3_path, wav_path):
    """Convert MP3 to WAV using pydub."""
    audio = AudioSegment.from_mp3(mp3_path)
    audio.export(wav_path, format="wav")
    return wav_path

def change_voice(input_mp3, output_mp3, pitch_shift=4):
    """Modify the pitch of the voice and save as MP3."""
    fixed_mp3 = "fixed_voice.mp3"
    temp_wav = "temp.wav"

    # Fix MP3
    fix_mp3(input_mp3, fixed_mp3)

    # Convert MP3 to WAV
    convert_mp3_to_wav(fixed_mp3, temp_wav)

    # Apply pitch shift
    y, sr = librosa.load(temp_wav, sr=None)
    y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=pitch_shift)

    # Save processed WAV
    processed_wav = "processed.wav"
    sf.write(processed_wav, y_shifted, sr)

    # Convert back to MP3
    processed_audio = AudioSegment.from_wav(processed_wav)
    processed_audio.export(output_mp3, format="mp3")

    # Cleanup
    for file in [temp_wav, processed_wav, fixed_mp3]:
        if os.path.exists(file):
            os.remove(file)

    return output_mp3

async def start(update: Update, context: CallbackContext):
    """Handle the /start command."""
    await update.message.reply_text("Send me a voice message, and I'll change it!")

async def process_audio(update: Update, context: CallbackContext):
    """Handles voice messages and processes them."""
    voice = update.message.voice or update.message.audio
    if not voice:
        await update.message.reply_text("Please send a valid voice message.")
        return

    file = await voice.get_file()
    input_file = "input_voice.mp3"
    
    await file.download(input_file)  # Correct method

    await update.message.reply_text("Processing your voice...")

    # Convert voice and save as female voice
    output_file = "female_voice.mp3"
    change_voice(input_file, output_file)

    with open(output_file, "rb") as audio:
        await update.message.reply_audio(audio)

    # Cleanup
    os.remove(input_file)
    os.remove(output_file)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, process_audio))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
