import pymysql
import logging
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler, CallbackQueryHandler, Handler )

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='88213009h', db='telegram_db', autocommit=True,use_unicode=True, charset="utf8")
TELEGRAM_HTTP_API_TOKEN = '420852520:AAHwTY-YRwTog5Hzc3o8p36pzwSyCi16FP4'


def start(bot, update):
    print('im in start state')
    text = "خوش آمدید"
    update.message.reply_text(text)
    chat_id=update.message.chat_id
    print(chat_id)
    sql="create table if not exists messages(chat_id INT NOT NULL PRIMARY KEY , state INT NOT NULL )"
    cursor = conn.cursor()
    cursor.execute(sql)
    sql="select state from messages where chat_id=%d" %chat_id
    cursor.execute(sql)
    last_state=cursor.fetchone()
    print(last_state)
    if last_state==None:
        print('adding user to database')
        sql="insert into messages VALUES (%d,0)" %chat_id
        cursor.execute(sql)
        last_state=0
    else:
        last_state=last_state[0]
    first_state(bot,update,last_state)



def intermediate_state(bot,update):
    print('i am in the intermediate state')
    print(update)
    query = update.callback_query
    chat_id=query.message.chat.id
    option=int(query.data)
    cursor = conn.cursor()
    sql='update messages set state=%d where chat_id=%d;' %(option,chat_id)
    cursor.execute(sql)
    first_state(bot,update,option)


def cancel_state(bot,update):
    cursor = conn.cursor()
    print(update)
    if update.callback_query:
        query=update.callback_query
    else:
        query=update
    chat_id = query.message.chat_id
    user = query.message.from_user
    logger.info(u"User %s canceled the conversation.", user.first_name)
    query.message.reply_text(u'باز هم به ما سر بزن!',
                                  reply_markup=ReplyKeyboardRemove())
    sql = "delete from messages where chat_id=%d " % (chat_id)
    cursor.execute(sql)
    return ConversationHandler.END


def option_state(bot,update):
    if update.callback_query:
        query=update.callback_query
    else:
        query=update
    keyboard = [
        [InlineKeyboardButton(u"فهمیدم", callback_data='3')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text(
        u"'این یک بات برای درج،جستوجو و حذف آگهی خودرو است'",
        reply_markup=reply_markup
    )
    #intermediate_state(bot,update)



def first_state(bot,update,last_state):
    print('im in first state')
    print(last_state)
    if last_state==0:
        keyboard = [
            [InlineKeyboardButton(u"امکانات", callback_data='2')],
            [InlineKeyboardButton(u"انصراف", callback_data='3')]
                ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
                u"برای دیدن امکانات بات گزینه مورد نظر را انتخاب کنید",
                reply_markup=reply_markup
        )
        #intermediate_state(bot,update)
    if last_state==3:
        cancel_state(bot,update)
    if last_state==2:
        option_state(bot,update)



def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(TELEGRAM_HTTP_API_TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(intermediate_state))
    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
