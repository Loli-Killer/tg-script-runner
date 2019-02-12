import logging, os, telegram, subprocess, re, time
import config
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, error

TOKEN = config.TOKEN
group_id = config.group_id
custom_name = ""
task_list = []

updater = Updater(TOKEN)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

logger = logging.getLogger(name=__name__)

def get_name(bot, update):

    if update.message.chat.id not in group_id:
        logger.info("Unauthorized usage tried by: {} -- {}".format(update.message.from_user.username, update.message.from_user.id))
        bot.send_message(update.message.chat_id, "Who are you?")
        return

    bot.send_message(update.message.chat_id, "Send custom name for the script.")
    return get_path

def get_path(bot, update):

    global custom_name
    custom_name = update.message.text
    bot.send_message(update.message.chat_id, "Send full path of script to run.")
    return run_cmd

def run_cmd(bot, update):

    global task_list, custom_name

    fname = update.message.text

    if os.path.isfile(fname):
        path = fname.rsplit("\\",1)[0]
        start = bot.send_message(update.message.chat_id, "Starting script ...")
        subprocess.Popen(['start', 'cmd', '/K', 'cd {} && py {}'.format(path, fname)], shell=True)
        time.sleep(5)
        p = get_processes_running()
        process = "py  {}".format(fname)

        for x in p:
            if process in x['window_title']:
                new_process = {
                    'name' : custom_name,
                    'title' : x['window_title'],
                    'pid' : x['pid']
                }
                task_list.append(new_process)
        bot.edit_message_text("Script started.", update.message.chat_id, start.message_id)
        return ConversationHandler.END
    else:
        bot.send_message(update.message.chat_id, "Script doesn't exist. Try again.")
        return run_cmd

def list_process(bot, update):

    global task_list
    if update.message.chat.id not in group_id:
        logger.info("Unauthorized usage tried by: {} -- {}".format(update.message.from_user.username, update.message.from_user.id))
        bot.send_message(update.message.chat_id, "Who are you?")
        return

    if not len(task_list):
        bot.send_message(update.message.chat_id, "No task running.")
        return

    index = 1

    process_list = "Process ran by script\n\n"
    for x in task_list:
        process_list += "{}. {} - {}\n".format(index, x['name'], x['pid'])
        index += 1
    bot.send_message(update.message.chat_id, process_list)

def choose_process_to_kill(bot, update):

    global task_list
    if update.message.chat.id not in group_id:
        logger.info("Unauthorized usage tried by: {} -- {}".format(update.message.from_user.username, update.message.from_user.id))
        bot.send_message(update.message.chat_id, "Who are you?")
        return

    if not len(task_list):
        bot.send_message(update.message.chat_id, "No task running.")
        return ConversationHandler.END

    index = 1

    process_list = "Choose process to kill\n\n"
    for x in task_list:
        process_list += "{}. {} - {}\n".format(index, x['name'], x['pid'])
        index += 1
    bot.send_message(update.message.chat_id, process_list)
    return kill_process

def kill_process(bot, update):

    global task_list
    index = int(update.message.text)-1

    try:
        task_list[index]
    except:
        return kill_process

    pid = task_list[index]['pid']
    task_list.pop(index)
    subprocess.Popen('taskkill /F /T /PID {} && exit'.format(pid), shell=True)
    bot.send_message(update.message.chat_id, "Process killed.")
    return ConversationHandler.END

def cancel(bot, update):

    logger.info("Command cancelled by: {} -- {}".format(update.message.from_user.username, update.message.from_user.id))
    update.message.reply_text('Canceled')
    return ConversationHandler.END

def get_processes_running():
    tasks = subprocess.check_output(['tasklist', '/V', '/FO', 'CSV']).decode('utf8').split("\r\n")
    p = []
    for task in tasks:
        task = task.replace('\"', "")
        m = re.match("(.*?),(.*?),(.*?),(.*?),(.*?K),(.*?),(.*?),(.*?),(.*)",task)
        if m is not None:
            p.append({
                    "image":m.group(1),
                    "pid":m.group(2),
                    "session_name":m.group(3),
                    "session_num":m.group(4),
                    "mem_usage":m.group(5),
                    "status":m.group(6),
                    "user_name":m.group(7),
                    "cpu_time":m.group(8),
                    "window_title":m.group(9)
                })
    return p

run = ConversationHandler(
    entry_points=[CommandHandler('run', get_name)],
    states={
        get_path: [MessageHandler(Filters.text, get_path)],
        run_cmd: [MessageHandler(Filters.text, run_cmd)],
        }, 
    fallbacks=[CommandHandler('cancel', cancel)]
)
kill = ConversationHandler(
    entry_points=[CommandHandler('kill', choose_process_to_kill)],
    states={
        kill_process: [MessageHandler(Filters.text, kill_process)],
        }, 
    fallbacks=[CommandHandler('cancel', cancel)]
)

dispatcher.add_handler(run)
dispatcher.add_handler(kill)

dispatcher.add_handler(CommandHandler('list', list_process))

logger.info("Bot Started.")
updater.start_polling()
updater.idle()
