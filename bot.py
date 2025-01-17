import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ConversationHandler, ContextTypes

import random
from predictions import predictions

# Определение состояний
WAITING_FOR_NUM_DICE, WAITING_FOR_SIDES = range(2)

# Список возможных вариантов количества кубиков
NUM_DICE_OPTIONS = ["1", "2", "3"]

# Список возможных вариантов количества граней
SIDES_OPTIONS = ["4", "6", "8", "10", "12", "20"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "Привет! Я ваш личный оракул. Чтобы получить предсказание, отправьте команду /predict.\n"
        "Также вы можете:\n"
        " - Подбросить кубики: используйте /roll, чтобы выбрать кубики.\n"
        " - Подбросить монету: используйте /coinflip, чтобы узнать, орел это или решка."
    )
    await update.message.reply_text(welcome_message)

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prediction = random.choice(predictions)
    await update.message.reply_text(prediction)

async def roll_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(text=num, callback_data=f"num_{num}") for num in NUM_DICE_OPTIONS]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Сколько кубиков вы хотите кинуть?', reply_markup=reply_markup)
    return WAITING_FOR_NUM_DICE

async def get_num_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    num_dice = int(query.data.split("_")[1])
    context.user_data['num_dice'] = num_dice

    keyboard = [
        [InlineKeyboardButton(text=side, callback_data=f"side_{side}") for side in SIDES_OPTIONS]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text='Сколько граней у кубика?', reply_markup=reply_markup)
    return WAITING_FOR_SIDES

async def get_dice_sides(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    sides = int(query.data.split("_")[1])
    num_dice = context.user_data.get('num_dice')
    rolls = [random.randint(1, sides) for _ in range(num_dice)]
    await query.edit_message_text(f'Вы бросили {num_dice} кубиков по {sides} граням: {rolls}.')
    context.user_data.clear()  # Очищаем данные пользователя после завершения
    return ConversationHandler.END

async def coin_flip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = "Орел" if random.choice([True, False]) else "Решка"
    await update.message.reply_text(f'Вы подбросили монету и получили: {result}.')

if __name__ == '__main__':
    application = ApplicationBuilder().token("BOTTOKEN").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('roll', roll_dice)],
        states={
            WAITING_FOR_NUM_DICE: [CallbackQueryHandler(get_num_dice, pattern="^num_")],
            WAITING_FOR_SIDES: [CallbackQueryHandler(get_dice_sides, pattern="^side_")]
        },
        fallbacks=[]
    )

    start_handler = CommandHandler('start', start)
    predict_handler = CommandHandler('predict', predict)
    coin_flip_handler = CommandHandler('coinflip', coin_flip)

    application.add_handler(conv_handler)
    application.add_handler(start_handler)
    application.add_handler(predict_handler)
    application.add_handler(coin_flip_handler)
    print("Бот запущен...")

try:
    asyncio.run(application.run_polling())
except asyncio.CancelledError:
    print("Задача была отменена.")
except KeyboardInterrupt:
    print("Приложение остановлено пользователем.")
except Exception as e:
    print(f"Произошла ошибка: {e}")
finally:
    print("Приложение завершило работу.")

