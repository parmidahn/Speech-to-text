import os
import tempfile
import speech_recognition as sr
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import os

TOKEN = "8184434233:AAFxr6o-A1LjI3Eb40AmvUuCDX6e1ycO03s"

# Default language is Persian
DEFAULT_LANGUAGE = "fa-IR"

# Conversation states
SELECTING_LANGUAGE = 0


async def transcribe_audio(audio_file_path, language):
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_file_path) as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data, language=language)
        return text
    except sr.UnknownValueError:
        if language == "fa-IR":
            return "صدا قابل تشخیص نبود"
        else:
            return "Could not understand audio"
    except sr.RequestError:
        if language == "fa-IR":
            return "خطا در ارتباط با سرویس تشخیص گفتار"
        else:
            return "API Error"


# Create language selection keyboard
def get_language_keyboard():
    keyboard = [
        [KeyboardButton("فارسی"), KeyboardButton("English")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


# Command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Initialize user data if not exists
    if not context.user_data.get('language'):
        context.user_data['language'] = DEFAULT_LANGUAGE

    welcome_text = "Please select your language / لطفا زبان خود را انتخاب کنید"
    await update.message.reply_text(welcome_text, reply_markup=get_language_keyboard())
    return SELECTING_LANGUAGE


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = context.user_data.get('language', DEFAULT_LANGUAGE)

    if language == "fa-IR":
        help_text = (
            "دستورات موجود:\n"
            "/start - شروع کار با ربات و انتخاب زبان\n"
            "/help - نمایش راهنما\n"
            "/language - تغییر زبان\n\n"
            "برای تبدیل گفتار به متن، یک فایل صوتی یا پیام صوتی بفرستید."
        )
    else:
        help_text = (
            "Available commands:\n"
            "/start - Start the bot and select language\n"
            "/help - Show help\n"
            "/language - Change language\n\n"
            "To convert speech to text, send an audio file or voice message."
        )

    await update.message.reply_text(help_text)
    return ConversationHandler.END


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Select your language / زبان خود را انتخاب کنید",
        reply_markup=get_language_keyboard()
    )
    return SELECTING_LANGUAGE


# Handle language selection
async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "فارسی":
        language = "fa-IR"
        response = "زبان فارسی انتخاب شد. می‌توانید فایل صوتی یا پیام صوتی خود را ارسال کنید."
    elif text == "English":
        language = "en-US"
        response = "English language selected. You can now send your voice message or audio file."
    else:
        # If the user sends something else, ask again
        if context.user_data.get('language') == "fa-IR":
            response = "لطفا یکی از گزینه‌های موجود را انتخاب کنید."
        else:
            response = "Please select one of the available options."
        await update.message.reply_text(response, reply_markup=get_language_keyboard())
        return SELECTING_LANGUAGE

    context.user_data['language'] = language
    await update.message.reply_text(response)
    return ConversationHandler.END


# Handle voice messages
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = context.user_data.get('language', DEFAULT_LANGUAGE)

    if language == "fa-IR":
        processing_message = await update.message.reply_text("در حال پردازش صدا...")
    else:
        processing_message = await update.message.reply_text("Processing audio...")

    # Get the voice message file
    voice_file = await context.bot.get_file(update.message.voice.file_id)

    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp_file:
        temp_file_path = temp_file.name

    await voice_file.download_to_drive(temp_file_path)

    wav_file_path = temp_file_path + ".wav"
    os.system(f'ffmpeg -i {temp_file_path} {wav_file_path}')

    transcription = await transcribe_audio(wav_file_path, language)

    if language == "fa-IR":
        await update.message.reply_text(f"متن تشخیص داده شده:\n{transcription}")
    else:
        await update.message.reply_text(f"Transcription:\n{transcription}")

    # Delete the temporary files
    os.remove(temp_file_path)
    os.remove(wav_file_path)

    await processing_message.delete()


# Handle audio files
async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = context.user_data.get('language', DEFAULT_LANGUAGE)

    if language == "fa-IR":
        processing_message = await update.message.reply_text("در حال پردازش فایل صوتی...")
    else:
        processing_message = await update.message.reply_text("Processing audio file...")

    # Get the audio file
    audio_file = await context.bot.get_file(update.message.audio.file_id)

    # Create a temporary file to save the audio
    with tempfile.NamedTemporaryFile(suffix=".audio", delete=False) as temp_file:
        temp_file_path = temp_file.name

    # Download the audio to the temporary file
    await audio_file.download_to_drive(temp_file_path)

    # Convert to .wav (FFmpeg is required for this)
    wav_file_path = temp_file_path + ".wav"
    os.system(f'ffmpeg -i {temp_file_path} {wav_file_path}')

    # Transcribe the audio
    transcription = await transcribe_audio(wav_file_path, language)

    # Send the transcription back to the user
    if language == "fa-IR":
        await update.message.reply_text(f"متن تشخیص داده شده:\n{transcription}")
    else:
        await update.message.reply_text(f"Transcription:\n{transcription}")

    # Delete the temporary files
    os.remove(temp_file_path)
    os.remove(wav_file_path)

    # Delete the "processing" message
    await processing_message.delete()


# Handle text messages (when not in a conversation)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = context.user_data.get('language', DEFAULT_LANGUAGE)

    if language == "fa-IR":
        await update.message.reply_text(
            "لطفاً یک فایل صوتی یا پیام صوتی بفرستید تا آن را به متن تبدیل کنم."
        )
    else:
        await update.message.reply_text(
            "Please send a voice message or audio file to convert it to text."
        )


# Main function
def main():
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add conversation handler for language selection
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start_command),
            CommandHandler("language", language_command)
        ],
        states={
            SELECTING_LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_language_selection)]
        },
        fallbacks=[CommandHandler("help", help_command)]
    )

    application.add_handler(conv_handler)

    # Add other command handlers
    application.add_handler(CommandHandler("help", help_command))

    # Add message handlers
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
