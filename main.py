import requests
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TELEGRAM_TOKEN = "6373007275:AAGfzPCchH20DG9quPYDHEWTm2IUo6HveCc"

# Словарь для хранения портфолио каждого пользователя.
# Ключ - это ID пользователя, значение - это словарь с его портфолио.
user_portfolios = {}

# Сопоставление кодов монет и их идентификаторов на CoinGecko.
coin_map = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "BNB": "binancecoin"
}

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Привет! Я бот для отслеживания вашего портфолио криптовалют.\n"
                              "Укажите свое портфолио в формате:\n"
                              "BTC 0.5\nETH 2\nBNB 10")

def get_crypto_price(coin_name: str) -> float:
    api_url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_name}&vs_currencies=usd"
    response = requests.get(api_url)
    response_json = response.json()
    return response_json[coin_name]['usd']

def portfolio(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    text = update.message.text.upper()

    portfolio_data = {}
    lines = text.split('\n')
    for line in lines:
        parts = line.split()
        if len(parts) != 2:
            update.message.reply_text("Некорректный формат ввода. Пожалуйста, введите данные в формате:\n"
                                      "BTC 0.5\nETH 2\nBNB 10")
            return
        coin = coin_map.get(parts[0])
        if not coin:
            update.message.reply_text(f"Неизвестная монета: {parts[0]}. Доступные монеты: BTC, ETH, BNB.")
            return
        amount = float(parts[1])
        portfolio_data[coin] = amount

    user_portfolios[user_id] = portfolio_data
    update.message.reply_text("Портфолио сохранено!")

def show_portfolio(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if user_id not in user_portfolios:
        update.message.reply_text("Сначала укажите свое портфолио.")
        return

    portfolio = user_portfolios[user_id]
    response = "Ваше портфолио:\n"
    total_value = 0

    for coin, amount in portfolio.items():
        price = get_crypto_price(coin)
        value = price * amount
        total_value += value
        coin_name = [key for key, value in coin_map.items() if value == coin][0]
        response += f"{coin_name}: {amount} монет. Текущая стоимость: ${value:.2f}\n"

    response += f"\nОбщая стоимость портфолио: ${total_value:.2f}"
    update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

def main() -> None:
    updater = Updater(token=TELEGRAM_TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("portfolio", show_portfolio))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, portfolio))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
