import random
import time
from datetime import date
from glob import glob
from settings import API_KEY
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler

from google_sheet_pandas_reader import connect_to_google_sheet


def get_metrics_analytics():
    # Request metrics and get feedback

    metrics_df = connect_to_google_sheet()

    all_metrics = metrics_df["Metric name"]
    report_dict = dict()

    for metric in all_metrics:
        this_metric_df = metrics_df[metrics_df["Metric name"] == metric]
        metric_val = int(this_metric_df.Value)
        metric_min = int(this_metric_df.Lower_bound)
        metric_max = int(this_metric_df.Upper_bound)
        metric_dept = str(this_metric_df["Relevant department"].iloc[0])
        datestamp = date.today()

        if metric_val < metric_min:
            key_name = metric + " negative report"

            report_dict[key_name] = ["negative", metric_dept, metric, metric_min, metric_val, datestamp]
        elif metric_val >= metric_max:
            key_name = metric + " positive report"
            report_dict[key_name] = ["positive", metric_dept, metric, metric_max, metric_val, datestamp]
        else:
            pass

    return report_dict


def generate_metrics_report():
    # Works as report generator

    while True:
        report = get_metrics_analytics()
        print(report)
        time.sleep(3)


def get_picture_and_text(marker):
    # gets random pictures and texts for positive and negative cases

    if marker == "positive":
        picture = random.choice(glob("positive_pics/*.jpg"))
        text = random.choice(glob("positive_texts/*.txt"))
    else:
        picture = random.choice(glob("negative_pics/*.jpg"))
        text = random.choice(glob("negative_texts/*.txt"))

    return picture, text


def compile_message(update, context):
    marker = "positive"
    pict, text = get_picture_and_text(marker)
    text = open(text).read()
    text = text.format("Alina", "METRIC", 1, 0)
    context.bot.sendPhoto(chat_id="441488986", photo=open(pict, "rb"), caption=text)


def send_message():
    mybot = Updater(API_KEY, use_context=True)

    dp = mybot.dispatcher

    user_enquette = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.text, compile_message)
        ],
        states={},
        fallbacks=[]
    )

    dp.add_handler(user_enquette)

    mybot.start_polling()
    mybot.idle()


if __name__ == "__main__":
    send_message()
