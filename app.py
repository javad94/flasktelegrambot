from queue import Queue
from threading import Thread
from flask import Flask, request
from telegram.ext import MessageHandler, Filters

from telegram import Bot,Update
from telegram.ext import Dispatcher
import logging
import sys
import os

file_handler = logging.FileHandler(filename='log.txt',encoding='utf-8')
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,handlers=handlers)

logger = logging.getLogger(__name__)

TOKEN = "Your token from @Botfather"
NAME = "The name of your app on Heroku"
PORT = int(os.environ.get('PORT', '8443'))

bot = Bot(TOKEN)

def echo(update, context):
    text = update.message.text
    update.message.reply_text(text)

def setup(TOKEN):
    # update queue and dispatcher instances
    update_queue = Queue()

    dispatcher = Dispatcher(bot, update_queue, use_context=True)

    ##### Register handlers here #####
    echo_handler = MessageHandler(Filters.text, echo)
    dispatcher.add_handler(echo_handler)

    # Start the thread
    bot.setWebhook("https://{}.herokuapp.com/{}".format(NAME, TOKEN))
    thread = Thread(target=dispatcher.start, name='dispatcher')
    thread.start()

    return update_queue
    # you might want to return dispatcher as well,
    # to stop it at server shutdown, or to register more handlers:
    # return (update_queue, dispatcher)

app = Flask(__name__)
update_queue = setup(token)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/' + TOKEN, methods=['GET','POST'])
def pass_update():
    new_update = Update.de_json(request.get_json(force=True),bot)
    update_queue.put(new_update)
    return "ok"

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=PORT,debug=True)
