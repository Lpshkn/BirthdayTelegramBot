"""
Module for all the handlers which will be processed by the ConversationHandler
"""
import re
import telegram
import birthdaybot.menus as menus
import logging
from birthdaybot.db.database import Database
from birthdaybot.localization import localization, date
from telegram.ext import Updater, JobQueue
from datetime import datetime

# Define all the states of the bot
MAIN_MENU, ADD_LISTS = range(2)


def start_handler(update: telegram.Update, context: telegram.ext.CallbackContext):
    """
    The handler to /start command. This handler send an localization message to the user.
    """
    chat_id = update.effective_chat.id
    code = update.effective_user.language_code
    context.bot.sendMessage(chat_id=chat_id,
                            text=localization.start_info(code),
                            parse_mode=telegram.ParseMode.HTML,
                            disable_web_page_preview=True,
                            reply_markup=menus.get_main_menu(code))

    update_chat_data(update, context)
    update_user_data(update, context)

    return MAIN_MENU


def update_chat_data(update: telegram.Update, context: telegram.ext.CallbackContext):
    """
    Function to update the chat_data receiving from the user.
    """
    context.chat_data['title'] = update.effective_chat.title
    context.chat_data['description'] = update.effective_chat.description
    context.chat_data['photo'] = update.effective_chat.photo
    context.chat_data['type'] = update.effective_chat.type


def update_user_data(update: telegram.Update, context: telegram.ext.CallbackContext):
    """
    Function to update the user_data receiving from the user.
    """
    context.user_data['chat_id'] = update.effective_chat.id
    context.user_data['username'] = update.effective_user.username
    context.user_data['first_name'] = update.effective_user.first_name
    context.user_data['last_name'] = update.effective_user.last_name
    context.user_data['is_bot'] = update.effective_user.is_bot
    context.user_data['language_code'] = update.effective_user.language_code


def stop_bot_handler(update: telegram.Update, context: telegram.ext.CallbackContext):
    """
    The handler to /stop command. This handler stops the bot and remove all data about the user
    """
    code = update.effective_user.language_code
    context.bot.sendMessage(chat_id=update.effective_chat.id,
                            text=localization.stop_bot_info(code),
                            parse_mode=telegram.ParseMode.HTML,
                            disable_web_page_preview=True,
                            reply_markup=menus.remove_keyboard())

    return telegram.ext.ConversationHandler.END


def main_menu_handler(update: telegram.Update, context: telegram.ext.CallbackContext):
    """
    The handler for the main menu. This handler process commands for the main menu.
    """
    # Get language code and get the dictionary of the main menu
    code = update.effective_user.language_code
    main_menu = localization.main_menu(code)

    # Get the text of the message and compare it with the name of buttons
    text = update.message.text
    if text == main_menu[menus.STOP_BOT_BUTTON]:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text=localization.stop_bot_info(code),
                                parse_mode=telegram.ParseMode.HTML,
                                disable_web_page_preview=True,
                                reply_markup=menus.remove_keyboard())
        return telegram.ext.ConversationHandler.END

    elif text == main_menu[menus.ADD_LIST_BUTTON]:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text=localization.add_lists_info(code),
                                parse_mode=telegram.ParseMode.HTML,
                                disable_web_page_preview=True,
                                reply_markup=menus.accept_cancel_keyboard(code))
        return ADD_LISTS


def process_entries(text: str, update: telegram.Update, context: telegram.ext.CallbackContext) -> set:
    """
    Method processes the text received from the user and checks that entries are correct.
    This method will be called by add_lists_handler that processes adding new lists of entries.

    Returns a list of tuples that contain the name of an entry and the date.
    """
    language_code = update.effective_user.language_code if update.effective_user.language_code == 'ru' else 'en'

    incorrect_lines = set()
    entries = set()
    for line in text.splitlines():
        # Check the line matches the pattern
        if not re.match(
                r"^[\w ]+ *- *((0?[1-9])|([1-2][0-9])|(3[0-1]))(( +[а-яА-Яa-zA-Z]{3,9})|([./]((0?[1-9])|(1[0-2]))))$",
                line, re.IGNORECASE):
            incorrect_lines.add(line)
        else:
            # Get the name and the date of an entry
            name, date_entry = [x.strip() for x in line.split('-')]
            day, month = re.split(r'[ ./]+', date_entry, maxsplit=1)
            if re.match(r'^[a-zA-Zа-яА-Я]+$', month):
                month = date.MONTHS[language_code].get(month, 0)

            # A day or a month may be incorrect
            try:
                date_entry = datetime.strptime("{} {}".format(day, month), "%d %m")
                entries.add((name, date_entry))
            except ValueError:
                incorrect_lines.add(line)

    # Send incorrect lines to the user
    if incorrect_lines:
        chat_id = update.effective_chat.id
        code = update.effective_user.language_code
        context.bot.sendMessage(chat_id=chat_id,
                                text=localization.error_adding_entry(code).format('\n'.join(incorrect_lines)),
                                parse_mode=telegram.ParseMode.HTML)
    return entries


def recall_send_callback(context: telegram.ext.CallbackContext):
    """
    This is a callback function that will be called when a job will be handled.
    This function send to a user the recall about his friends' birthday.
    """
    chat_id, name, entry_date, language_code = context.job.context
    context.bot.sendMessage(chat_id=chat_id,
                            text=localization.recall_message(language_code).format(name),
                            parse_mode=telegram.ParseMode.HTML)


def process_entries_callback(context):
    """
    This is a callback function to get entries from the database and run new jobs.

    :param context: can be CallbackContext or just a dictionary that containing arguments
    """
    job_queue = None
    start_time = None
    finish_time = None
    database = None

    if isinstance(context, telegram.ext.CallbackContext):
        start_time, finish_time, database = context.job.context
        job_queue = context.job_queue
    elif isinstance(context, dict):
        job_queue = context['context']
        start_time = context['start_time']
        finish_time = context['finish_time']
        database = context['database']
    else:
        logging.error("Not CallbackContext or JobQueue was passed into the 'callback_check_entries' function")
        exit(-1)

    run_entries_jobs(job_queue, database, start_time, finish_time)


def run_entries_jobs(job_queue: JobQueue, database: Database, start_time: datetime, finish_time: datetime):
    """
    Function will get entries from the database between the specific period and
    run new jobs that will call the function of recalling about events.

    :param job_queue: the JobQueue instance
    :param database: the Database instance
    :param start_time: the start time of the period
    :param finish_time: the end time of the period
    """
    entries = database.get_entries(start_time, finish_time)
    for chat_id, name, entry_date, language_code in entries:
        job_queue.run_once(callback=recall_send_callback,
                           when=entry_date,
                           context=(chat_id, name, entry_date, language_code))