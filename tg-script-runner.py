import logging, os, telegram, subprocess
import config
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, error

TOKEN = config.TOKEN
group_id = config.group_id

updater = Updater(TOKEN)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

logger = logging.getLogger(name=__name__)

def run_cmd(bot, update):

    if update.message.chat.id not in group_id:
        logger.info("Unauthorized usage tried by: {} -- {}".format(update.message.from_user.username, update.message.from_user.id))
        bot.send_message(update.message.chat_id, "Who are you?")
        return

    message = update.message.text.split(" ", 1)

    if len(message) < 2:
        bot.send_message(update.message.chat_id, "Usage is /run <path_to_script>")
        return

    fname = message[1]
    if os.path.isfile(fname):
        path = fname.rsplit("\\",1)[0]
        subprocess.Popen(['start', 'cmd', '/K', 'cd {} && py {}'.format(path, fname)], shell=True).pid
        bot.send_message(update.message.chat_id, "Script started.")
    else:
        bot.send_message(update.message.chat_id, "Script doesn't exist.")

dispatcher.add_handler(CommandHandler('run', run_cmd))

logger.info("Bot Started.")
updater.start_polling()
updater.idle()
