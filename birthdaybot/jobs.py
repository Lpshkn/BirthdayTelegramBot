"""
This module contains the function to get, set and process jobs in the JobQueue instance.
This module contains the callable functions.
"""
import telegram.ext
import datetime as dt
import telegram
import pytz
import logging
from birthdaybot.db.database import Database, Entry
from birthdaybot.localization import localization
from telegram.ext import JobQueue


def recall_send_callback(context: telegram.ext.CallbackContext):
    """
    This is a callback function that will be called when a job will be handled.
    This function send to a user the recall about his friends' birthday.
    """
    entry = context.job.context
    context.bot.sendMessage(chat_id=entry.chat_id,
                            text=localization.recall_message(entry.language_code).format(entry.name),
                            parse_mode=telegram.ParseMode.HTML)


def process_entries_callback(context: telegram.ext.CallbackContext):
    """
    This is a callback function that will called every 24 hours to update entries from the database and
    run new jobs.
    """
    bot = None

    if isinstance(context, telegram.ext.CallbackContext):
        bot = context.job.context
        bot.start_time = dt.datetime.now(tz=pytz.timezone('Europe/Moscow'))
        bot.finish_time = dt.datetime.now(tz=pytz.timezone('Europe/Moscow')) + dt.timedelta(days=1)
    else:
        logging.error("Not CallbackContext was passed into the 'callback_check_entries' function")
        exit(-1)

    run_entries_jobs(bot.job_queue, bot.database, bot.start_time, bot.finish_time)


def run_entries_jobs(job_queue: JobQueue, database: Database, start_time: dt.datetime, finish_time: dt.datetime):
    """
    Function will get entries from the database between the specific period and
    run new jobs that will call the function of recalling about events.

    :param job_queue: the JobQueue instance
    :param database: the Database instance
    :param start_time: the start time of the period
    :param finish_time: the end time of the period
    """
    entries = database.get_entries(start_time, finish_time)
    for entry in entries:
        job_queue.run_once(callback=recall_send_callback,
                           when=entry.entry_date,
                           context=entry)


def process_inserting_entry_callback(job_queue: JobQueue, database: Database, finish_time: dt.datetime):
    """
    This callback function will be called, when an Insert operation will be occurred in the database.
    """
    jobs = job_queue.jobs()
    entries = database.get_entries(dt.datetime.now(), finish_time)
    for entry in entries:
        ran = False
        # Check that entry wasn't ran and put into the job_queue
        for job in jobs:
            if isinstance(job.context, Entry):
                if job.context.chat_id == entry.chat_id and job.context.name == entry.name:
                    ran = True
                    break
        if not ran:
            job_queue.run_once(callback=recall_send_callback,
                               when=entry.entry_date,
                               context=entry)


def process_updating_entry_callback(job_queue: JobQueue, database: Database, finish_time: dt.datetime):
    """
    This callback function will be called, when an Update operation will be occurred in the database.
    """
    jobs = job_queue.jobs()
    entries = database.get_entries(dt.datetime.now(), finish_time)
    for job in jobs:
        if isinstance(job.context, Entry):
            exist = False
            for entry in entries:
                if job.context.note_id == entry.note_id:
                    if job.context.chat_id == entry.chat_id and job.context.name == entry.name:
                        if job.context.entry_date == entry.entry_date:
                            exist = True
                            break
                        else:
                            job.schedule_removal()
                            if entry.entry_date <= finish_time:
                                job_queue.run_once(callback=recall_send_callback,
                                                   when=entry.entry_date,
                                                   context=entry)
                            break
                    else:
                        job.schedule_removal()
                        if entry.entry_date <= finish_time:
                            job_queue.run_once(callback=recall_send_callback,
                                               when=entry.entry_date,
                                               context=entry)
                        break

            if not exist:
                job.schedule_removal()


def process_deleting_entry_callback(job_queue: JobQueue, database: Database, finish_time: dt.datetime):
    """
    This callback function will be called, when a Delete operation will be occurred in the database.
    """
    jobs = job_queue.jobs()
    entries = database.get_entries(dt.datetime.now(), finish_time)
    for job in jobs:
        if isinstance(job.context, Entry):
            exist = False
            for entry in entries:
                if job.context.note_id == entry.note_id:
                    if job.context.chat_id == entry.chat_id and job.context.name == entry.name:
                        exist = True
                        break
            if not exist:
                job.schedule_removal()
