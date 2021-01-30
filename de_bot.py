from datetime import datetime
from glob import glob
import logging
import pickle
import random
import time

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler
from telegram.ext.dispatcher import run_async

from settings import API_KEY
from user_enquette import start_user_enquette, user_enquette_full_name, user_enquette_department

'''
Spreadsheet is available on the following link:
https://docs.google.com/spreadsheets/d/16RUw4R-bTD3WvW7OPHFNJiMxXtW1V_818ZRMQqYt69c/edit?usp=sharing
'''


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    filename="de_bot.log",
                    level=logging.INFO)

url = "https://api.telegram.org/bot" + API_KEY + "/"


@run_async
def greet_user(update, context):
    # Greets user and gets his/her name
    print("Вызвана команда /start")

    user_first_name = update.message.chat.first_name

    context.user_data["chat_id"] = update.message.chat.id
    context.user_data["first_name"] = user_first_name
    context.user_data["username"] = update.message.chat.username

    welcome_text = "Привет, {}! Давай знакомиться? :)".format(user_first_name.capitalize())
    my_keyboard = ReplyKeyboardMarkup([["Давай!"]])
    update.message.reply_text(welcome_text, reply_markup=my_keyboard)
    print(context.user_data)


@run_async
def talk_to_user(update, context):
    # This function allows bot to talk to user

    user_text = update.message.text
    logging.info("User: %s, Chat id: %s, Message: %s", update.message.chat.username,
                 update.message.chat.id, user_text)

    print(context.user_data)


def get_picture_and_text(marker):
    # gets random pictures and texts for positive and negative cases

    if marker == "positive":
        picture = random.choice(glob("positive_pics/*.jpg"))
        text = random.choice(glob("positive_texts/*.txt"))
    else:
        picture = random.choice(glob("negative_pics/*.jpg"))
        text = random.choice(glob("negative_texts/*.txt"))

    return picture, text


@run_async
def generate_metrics_report(update, context):
    # Distributes metrics annoucement

    update.message.reply_text("Отлично! Теперь тебе сюда будут приходить оповещения о метриках")

    while True:

        # Establish connection to pickle file where data is updated
        with open("data", "rb") as p_file:
            report = pickle.load(p_file)
        print("REPORT:\n\n", report, "\n\n")

        time_now = datetime.now()
        today_10am = time_now.replace(hour=10, minute=0, second=0, microsecond=0)
        today_21am = time_now.replace(hour=22, minute=0, second=0, microsecond=0)

        if time_now < today_10am or time_now > today_21am:
            sleep_var = "\nDO NOT DISTURB mode is ON\n***"
        else:
            sleep_var = ""

            # Here goes the main part of the function
            for issue in report.keys():
                marker, depart, metric_name, metric_bound, metric_val, date_stamp = report[issue]
                user_name = context.user_data["full_name"]
                user_dept = context.user_data["department"]

                if user_dept != depart:
                    pass
                else:

                    user_cont = context.user_data["last_call"]
                    print(user_cont)

                    if [marker, metric_name, date_stamp] in user_cont:
                        pass
                    else:
                        pict, text = get_picture_and_text(marker)
                        text = open(text).read()
                        text = text.format(user_name.capitalize(), metric_name, metric_bound, metric_val)
                        context.bot.sendPhoto(chat_id=update.message.chat.id, photo=open(pict, "rb"), caption=text)

                        context.user_data["last_call"].append([marker, metric_name, date_stamp])
                        if len(context.user_data["last_call"]) > 5:
                            context.user_data["last_call"] = context.user_data["last_call"][1:]

        # informs us whether it is night time and "DO NOT DESTURB" mode is ON
        print("\n***\nTIME NOW: {}\n{}***\n".format(time_now, sleep_var))

        time.sleep(3)


def main():
    # Here cointains the main loop of the programm

    mybot = Updater(API_KEY, use_context=True)

    dp = mybot.dispatcher

    user_enquette = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex("^(Давай!)$"), start_user_enquette)
        ],
        states={
            "full_name": [MessageHandler(Filters.text, user_enquette_full_name)],
            "department": [MessageHandler(Filters.text, user_enquette_department)],
            "metrics": [MessageHandler(Filters.text, generate_metrics_report)]
        },
        fallbacks=[]
    )

    dp.add_handler(user_enquette)
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(MessageHandler(Filters.text, talk_to_user))

    mybot.start_polling()
    mybot.idle()


if __name__ == "__main__":
    main()



