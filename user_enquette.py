from datetime import date
from glob import glob
import pandas as pd
import os
import time

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

from google_sheet_pandas_reader import connect_to_google_sheet


def start_user_enquette(update, context):
    # Makes entry point for bot
    update.message.reply_text("Как мне к тебе обращаться?", reply_markup=ReplyKeyboardRemove())

    return "full_name"


def user_enquette_full_name(update, context):
    # Checks whether input in correct

    user_name = update.message.text

    if len(user_name) < 2:
        update.message.reply_text("Пожалуйста, введи хотя бы имя")
        return "full_name"
    else:
        context.user_data["full_name"] = user_name
        dept_keyboard = [get_departments()]
        update.message.reply_text(
            "В каком отделе трудишься?",
            reply_markup=ReplyKeyboardMarkup(dept_keyboard, one_time_keyboard=True)
        )
        return "department"


def user_enquette_department(update, context):
    # Adds department and shows metrics

    user_dept = update.message.text
    context.user_data["department"] = user_dept

    metrics_df = connect_to_google_sheet()
    metrics_df = metrics_df[metrics_df["Relevant department"] == user_dept]
    metrics = metrics_df["Metric name"].unique()
    metrics_string = ", ".join(metrics)

    user_name = context.user_data["full_name"].capitalize()
    update.message.reply_text("Ну, {} из отдела {}, вот мы и познакомились! :)".format(user_name, user_dept))
    time.sleep(2)
    update.message.reply_text("Мы можем отправлять тебе оповещения "
                              "о состоянии ключевых метрик из списка: {}. ".format(metrics_string))
    time.sleep(1)
    update.message.reply_text("Для некоторого увесиления мы добавили в оповещения картинки")
    update.message.reply_text("Надеюсь, тебе понравиться))")
    time.sleep(1)
    update.message.reply_text("Если согласен, напиши 'Хорошо'")

    add_user_to_csv(
        user_dept,
        context.user_data["username"],
        user_name,
        context.user_data["chat_id"],
        context.user_data["full_name"]
    )

    context.user_data["last_call"] = [[None, None, date.today()]]

    return "metrics"


def add_user_to_csv(department, username, first_name, chat_id, full_name):
    # Builds employee list

    file_name = "departments/" + department + "/employees.csv"

    try:
        this_df = pd.read_csv(file_name)
        this_df.drop(columns=["Unnamed: 0"], inplace=True)
        if chat_id not in this_df.chat_id.unique():
            this_df = this_df.append({"username": username,
                                      "first_name": first_name,
                                      "chat_id": chat_id,
                                      "full_name": full_name},
                                     ignore_index=True)
            this_df.to_csv(file_name)
    except FileNotFoundError:
        this_df = pd.DataFrame(columns=["username", "first_name", "chat_id", "full_name"])
        this_df = this_df.append({"username": username,
                                  "first_name": first_name,
                                  "chat_id": chat_id,
                                  "full_name": full_name},
                                 ignore_index=True)
        this_df.to_csv(file_name)


def get_departments():
    # Returns all departments

    department_list = glob("departments/*")
    department_list = [i.split("/")[1] for i in department_list]

    metrics_df = connect_to_google_sheet()
    met_depts = metrics_df["Relevant department"].unique()
    met_depts = [i for i in met_depts]

    for i in met_depts:
        if i in department_list:
            pass
        else:
            os.mkdir("departments/{}".format(i))

    return met_depts