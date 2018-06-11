import telebot
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)
sheet = client.open("FOOTBIK").sheet1

token = '609556125:AAFnvY4cM-xcuGn7aYpauQ2W7riw_JVmbJU'
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start', 'help'])
def start_message(message):
    sent = bot.reply_to(message, 'Привет! Добро пожаловать в FOOTBIK Bot!\n\n'
                          'Список правил:\n'
                          'добавиться в основной канал FOOTBIK;\n'
                          'добавить свой кошелек;\n'
                          'добавить свою почту;\n'
                          'не выходить из канала до окончания ICO и начисления токенов\n\n'
                          'Пожалуйста, введите свой email:')
    bot.register_next_step_handler(sent, email_input)


def is_valid_email(email):
    if len(email) > 7:
        return bool(re.match(
                    "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email))


def is_valid_wallet(wallet):
        return bool(re.match(
                    "^0x\w{40}$", wallet))


def email_input(message):
    if is_valid_email(message.text):
        email_list = sheet.col_values(1)
        if message.text in email_list:
            email_duplicate = bot.reply_to(message, 'Данный email уже зарегистрирован. Введите другой.')
            bot.register_next_step_handler(email_duplicate, email_input)
        else:
            sheet.insert_row([message.text, ], 2)
            email_success = bot.reply_to(message, 'Введите адрес ERC кошелька:')
            bot.register_next_step_handler(email_success, erc_input)
    else:
        email_error = bot.reply_to(message, 'Введите верный email:')
        bot.register_next_step_handler(email_error, email_input)


def erc_input(message):
        if is_valid_wallet(message.text):
            sheet.update_cell(2, 2, message.text)
            bot.reply_to(message, 'Благодарю за участие. Вы получаете 20 токенов.')
        else:
            wallet_error = bot.reply_to(message, 'Введите верный адрес кошелька (0x...). Он содержит 42 символа.')
            bot.register_next_step_handler(wallet_error, erc_input)


if __name__ == '__main__':
    bot.polling(none_stop=True)
