import sys
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker
from insulter import insults
import time
import datetime
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, \
    InlineQueryResultArticle, InputTextMessageContent, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

backup = 'groups.bsf'
"""
topic markup:
[timestamp] : {
    'id': topic id
    'fname': starter first name
    'lname': starter last name
    'username': username
    'msg_id': original message id
    'message': topic text
    ...
}
"""
# SQL stuff
Base = declarative_base()

class Groups(Base):
    __tablename__ = 'groups'

    chat_id = Column(String, primary_key=True)
    max_threads = Column(Integer)
    max_epics = Column(Integer)
    useless_counter = Column(Integer)

    def __repr__(self):
        return "<Groups(chat_id='%s', max_threads='%i', max_epics='%i', useless_counter='%i')>" % (
            self.chat_id, self.max_threads, self.max_epics, self.useless_counter)

class Threads(Base):
    __tablename__ = 'threads'

    chat_id = Column(String, ForeignKey('groups.chat_id'), primary_key=True)
    message_id = Column(String, primary_key=True)
    stamp = Column(Integer)
    username = Column(String)
    text = Column(String)

    def __repr__(self):
        return "<Threads(chat_id='%s', message_id='%s', stamp='%i', username='%s', text='%s')>" % (
            self.chat_id, self.message_id, self.stamp, self.username, self.text)

class Epics(Base):
    __tablename__ = 'epics'

    chat_id = Column(String, ForeignKey('groups.chat_id'), primary_key=True)
    message_id = Column(String, primary_key=True)
    stamp = Column(Integer)
    username = Column(String)
    text = Column(String)

    def __repr__(self):
        return "<Epics(chat_id='%s', message_id='%s', stamp='%i', username='%s', text='%s')>" % (
            self.chat_id, self.message_id, self.stamp, self.username, self.text)

class Requests(Base):
    __tablename__ = 'requests'

    chat_id = Column(String, ForeignKey('groups.chat_id'), primary_key=True)
    message_id = Column(String)
    stamp = Column(Integer)
    username = Column(String, primary_key=True)
    text = Column(String)

    def __repr__(self):
        return "<Requests(chat_id='%s', message_id='%s', stamp='%i', username='%s', text='%s')>" % (
            self.chat_id, self.message_id, self.stamp, self.username, self.text)


# BOT CLASS
# this is bot class, contains the bot itself and various handler functions;
# creating an instance starts a bot with token provided
class TopicsBot:
    def __init__(self, token, filename):
        engine = create_engine('sqlite:///groups_test.bsf')
        Base.metadata.create_all(engine)
        self.session = sessionmaker(bind=engine)()

        # https://t.me/lazytopicsbot?start=chat_id
        self.logging = True
        self.keep_alive = True
        self.token = token
        self.core = telepot.Bot(self.token)
        MessageLoop(self.core, self.handler).run_as_thread()

    def log(self, text):
        if self.logging:
            print(str(datetime.datetime.fromtimestamp(time.time()).strftime(
                '%Y-%m-%d %H:%M:%S')) + ': ' + text)

    def handler(self, msg):
        flavor = telepot.flavor(msg)
        try:
            eval('self.' + flavor)(msg)
        except AttributeError as e:
            self.log(e)

    def check_privilege(self, chat_id, username):
        if username == 'WillDrug':
            return True
        try:
            admins = self.core.getChatAdministrators(chat_id)
            for i in admins:
                if i['username'] == username:
                    return True
        except telepot.exception.TelegramError as e:
            self.log('check privilege died with: ' + e.__str__())
            pass
        return False

    def check_group(self, chat_id):
        group_exists = self.session.query(self.session.query(Groups).filter(Groups.chat_id == chat_id).exists()).\
            scalar()
        if not group_exists:
            self.session.add(Groups(chat_id=chat_id, max_threads=10, max_epics=10, useless_counter=0))
        return True


    def append_thread(self, chat_id, message_id, stamp, username, text):
        #check group
        self.check_group(chat_id)

        #add or extend object
        thread_object = self.session.query(Threads).filter(Threads.chat_id == chat_id, Threads.message_id == message_id).first()
        if not thread_object:
            thread_object = Threads(chat_id=chat_id, message_id=message_id, stamp=stamp, username=username, text=text)
            self.session.add(thread_object)
        else:
            thread_object.text = text

        #delete previous if needed
        max_threads = self.session.query(Groups).filter(Groups.chat_id == chat_id).first().max_threads
        thread_count = self.session.query(Threads).count()
        if thread_count > max_threads:
            self.session.query(Threads).filter(Threads.message_id == self.session.query(Threads).order_by(Threads.stamp).first().message_id).delete()

        #COMMIT!
        self.session.commit()
        return True

    def append_epic(self, chat_id, message_id, stamp, username, text):
        #check group
        self.check_group(chat_id)

        #add or extend object
        thread_object = self.session.query(Epics).filter(Epics.chat_id == chat_id, Epics.message_id == message_id).first()
        if not thread_object:
            thread_object = Epics(chat_id=chat_id, message_id=message_id, stamp=stamp, username=username, text=text)
            self.session.add(thread_object)
        else:
            thread_object.text = text

        #delete previous if needed
        max_epics = self.session.query(Groups).filter(Groups.chat_id == chat_id).first().max_epics
        thread_count = self.session.query(Epics).count()
        if thread_count > max_epics:
            self.session.query(Epics).filter(Epics.message_id == self.session.query(Epics).order_by(Epics.stamp).first().message_id).delete()

        #COMMIT!
        self.session.commit()
        return True

    def append_request(self, chat_id, message_id, stamp, username, text):
        #check group
        self.check_group(chat_id)

        #add or extend object
        thread_object = self.session.query(Requests).filter(Requests.chat_id == chat_id, Requests.username == username)
        if thread_object.count() == 0:
            thread_object = Requests(chat_id=chat_id, message_id=message_id, stamp=stamp, username=username, text=text)
            self.session.add(thread_object)
        elif text == '':
            thread_object.delete()
        else:
            thread_object.first().text = text

        #COMMIT!
        self.session.commit()
        return True

    def get_commands(self, msg):
        commands = list()
        main_command = ''
        main_has_at = False
        if 'entities' in msg.keys():
            for i in msg['entities']:
                if i['type'] == 'bot_command':
                    commands.append(
                        msg['text'][int(i['offset']):int(i['offset']) + int(i['length'])].replace('@lazytopicsbot', ''))
                    if int(i['offset']) == 0:
                        main_command = msg['text'][int(i['offset']):int(i['offset']) + int(i['length'])]
                        if '@lazytopicsbot' in main_command:
                            main_command = main_command.replace('@lazytopicsbot', '')
                            main_has_at = True
                continue
        return commands, main_command, main_has_at

    def chat(self, msg):
        (content_type, chat_type, msg_id) = telepot.glance(msg, 'chat')
        # cheat
        if chat_type == 'group':
            chat_type = 'supergroup'

        try:
            eval('self.' + chat_type + '_' + content_type)(msg)
        except AttributeError as e:
            self.log('There was no function to parse this; ' + e.__str__())

    def supergroup_text(self, msg):
        commands, main_command, main_has_at = self.get_commands(msg)
        if main_command == '':
            return True
        text = msg['text'].replace(main_command, '')
        if main_has_at:
            text = text[15:]
        if main_command == '/givemeabutton':
            self.send_useless_button(msg['chat']['id'])
        elif main_command == '/thread':
            self.append_thread(msg['chat']['id'], msg['message_id'], msg['date'], msg['from']['username'], text)
            self.log('Appended thread to ' + msg['chat']['title'])
            return True
        elif main_command == '/epic':
            self.append_epic(msg['chat']['id'], msg['message_id'], msg['date'], msg['from']['username'], text)
            self.log('Appended epic to ' + msg['chat']['title'])
            return True
        elif main_command == '/request':
            self.append_request(msg['chat']['id'], msg['message_id'], msg['date'], msg['from']['username'], text)
            self.log('Appended request to ' + msg['chat']['title'] + ' from '+msg['from']['username'])
            return True
        elif main_command == '/max_epics':
            try:
                maxepics = int(text)
            except ValueError:
                self.core.sendMessage(chat_id=msg['chat']['id'], text='I want an integer')
                pass
                return True
            if self.check_privilege(msg['chat']['id'], msg['from']['username']):
                self.check_group(msg['chat']['id'])
                self.session.query(Groups).filter(Groups.chat_id == str(msg['chat']['id'])).first().max_epics = maxepics
                self.session.commit()
                self.log('Set max epics as {} in {}'.format(maxepics, msg['chat']['title']))
            else:
                self.get_fucked(msg['chat']['id'], msg['from']['username'])
            return True
        elif main_command == '/max_threads':
            try:
                maxthreads = int(text)
            except ValueError:
                self.core.sendMessage(chat_id=msg['chat']['id'], text='I want an integer')
                pass
                return True
            if self.check_privilege(msg['chat']['id'], msg['from']['username']):
                self.check_group(msg['chat']['id'])
                self.session.query(Groups).filter(Groups.chat_id == str(msg['chat']['id'])).first().max_threads = maxthreads
                self.log('Set max threads as {} in {}'.format(maxthreads, msg['chat']['title']))
            else:
                self.get_fucked(msg['chat']['id'], msg['from']['username'])
            return True
        elif main_command == '/summon':
            try:
                self.send_info(msg['from']['id'], msg['chat']['id'])
            except telepot.exception.TelegramError as e:
                self.log('Couldn''t summon: ' + e.__str__())
                self.core.sendMessage(chat_id=msg['chat']['id'],
                                      text='Sorry, can''t write you first. '
                                           'Use this link and press start: '
                                           'https://t.me/lazytopicsbot?start=' + str(msg['chat']['id']))
                pass
            return True
        elif main_command == '/kill':
            self.session.query(Groups).filter(Groups.chat_id == str(msg['chat']['id'])).delete()
            self.session.query(Threads).filter(Threads.chat_id == str(msg['chat']['id'])).delete()
            self.session.query(Epics).filter(Epics.chat_id == str(msg['chat']['id'])).delete()
            self.session.query(Requests).filter(Requests.chat_id == str(msg['chat']['id'])).delete()
            self.session.commit()
            #dict.__delitem__(self.groups, )
            self.check_group(str(msg['chat']['id']))
        else:
            return True

        return True

    def send_info(self, to_chat, for_chat):
        self.check_group(for_chat)
        self.core.sendMessage(chat_id=to_chat,
                              text='------------SEPARATOR----------\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n '
                                   'Hello! Here''s what''s been going on in your abscence in "{}"!'.format(
                                  self.core.getChat(for_chat)['title']
                              ))
        failed = 0
        # 1. send threads
        text = 'Here''s the activity that people noticed.\n ' \
               'Press the corresponding button to get link to this message in group chat:'
        markup = InlineKeyboardMarkup(inline_keyboard=[[]])
        target_line = 0
        threads_query = self.session.query(Threads).filter(Threads.chat_id == str(for_chat))
        if threads_query.count() > 0:
            for i, cnt in zip(threads_query.all(), range(1, threads_query.count()+1)):
                text += '\n{}. @{} noticed something at {} and wrote "{}"'.format(
                    str(cnt),
                    str(i.username),
                    str(datetime.datetime.fromtimestamp(float(i.stamp)).strftime('%Y-%m-%d %H:%M:%S')),
                    str(i.text)
                )
                if markup.inline_keyboard[target_line].__len__()>5:
                    markup.inline_keyboard.append([])
                    target_line += 1
                markup.inline_keyboard[target_line].append(
                    InlineKeyboardButton(text=str(cnt), callback_data='thread,'+str(for_chat)+','+str(i.message_id))
                )
            self.core.sendMessage(chat_id=to_chat, text=text, reply_markup=markup)
        else:
            failed += 1

        # 2. send epics
        text = 'Here''s what people found to be EPIC.\n' \
               'Press the corresponding button to get link to this in group chat:'
        markup = InlineKeyboardMarkup(inline_keyboard=[[]])
        target_line = 0
        epics_query = self.session.query(Epics).filter(Epics.chat_id == str(for_chat))
        if epics_query.count() > 0:
            for i, cnt in zip(epics_query.all(), range(1, epics_query.count()+1)):
                text += '\n{}. @{} found something epic at {} and wrote "{}"'.format(
                    str(cnt),
                    str(i.username),
                    str(datetime.datetime.fromtimestamp(float(i.stamp)).strftime('%Y-%m-%d %H:%M:%S')),
                    str(i.text)
                )
                if markup.inline_keyboard[target_line].__len__()>5:
                    markup.inline_keyboard.append([])
                    target_line += 1
                markup.inline_keyboard[target_line].append(
                    InlineKeyboardButton(text=str(cnt), callback_data='epic,'+str(for_chat)+','+str(i.message_id))
                )
            self.core.sendMessage(chat_id=to_chat, text=text, reply_markup=markup)
        else:
            failed += 1

        # 3. send requests
        text = 'Here''s what people have requested\n' \
               'Press the corresponding button to alert the person that you want to reply them in group chat:'
        markup = InlineKeyboardMarkup(inline_keyboard=[[]])
        target_line = 0
        requests_query = self.session.query(Requests).filter(Requests.chat_id == str(for_chat))
        if requests_query.count() > 0:
            for i, cnt in zip(requests_query.all(), range(1, requests_query.count() + 1)):
                text += '\n{}. @{} requested:\n"{}"\n--at {}"'.format(
                    str(cnt),
                    str(i.username),
                    str(i.text),
                    str(datetime.datetime.fromtimestamp(float(i.stamp)).strftime('%Y-%m-%d %H:%M:%S'))
                )
                if markup.inline_keyboard[target_line].__len__() > 5:
                    markup.inline_keyboard.append([])
                    target_line += 1
                markup.inline_keyboard[target_line].append(
                    InlineKeyboardButton(text=str(cnt), callback_data='request,' + str(for_chat) + ',' + str(i.username))
                )
            self.core.sendMessage(chat_id=to_chat, text=text, reply_markup=markup)
        else:
            failed += 1

        if failed == 3:
            self.core.sendMessage(chat_id=to_chat, text='Seems that nothing happened... \nTry marking user activity '
                                                        'with /thread [comment],\n epic moments with /epic [comment]\n'
                                                        'and request things with /request text')

    def private_text(self, msg):
        commands, main_command, main_has_at = self.get_commands(msg)
        text = msg['text'].replace(main_command, '')
        text = text[1:]
        if main_command == '/shutdown':
            if msg['from']['username'] == 'WillDrug':
                self.log('Processing shutdown')
                self.keep_alive = False
            else:
                self.get_fucked(msg['from']['id'], msg['from']['username'])
        elif main_command == '/start':
            try:
                chat_id = int(text)
            except ValueError:
                self.core.sendMessage(chat_id=msg['from']['id'],
                                      text='That id doesn''t seem right to me... Try /summon in group chat again')
            self.send_info(msg['from']['id'], chat_id)
        elif main_command == '/givemeabutton':
            self.send_useless_button(msg['chat']['id'])
        return True

    def send_useless_button(self, chat_id):
        self.core.sendMessage(chat_id=chat_id, text='This does nothing',
                              reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                  [
                                      InlineKeyboardButton(text='Useless', callback_data='useless,0,0')
                                  ]
                              ]))
    def callback_query(self, msg):
        msg_id, from_id, data = telepot.glance(msg, 'callback_query')
        command, chat_id, parm = data.split(',')
        self.check_group(chat_id)
        if command == 'useless':
            chat_row = self.session.query(Groups).filter(Groups.chat_id == chat_id).first()
            chat_row.useless_counter += 1
            self.session.commit()
            self.core.answerCallbackQuery(callback_query_id=msg_id,
                                          text='Press {}'.format(chat_row.useless_counter))
            self.log(msg['from']['username']+' did something useless')
        elif command == 'thread':
            try:
                self.core.sendMessage(chat_id=chat_id, reply_to_message_id=parm,
                                      text='Hey, @{}, here''s the thread you requested'.format(msg['from']['username']))
            except telepot.exception.TelegramError as e:
                self.log('Callback '+str(command)+' '+str(chat_id)+' '+str(parm)+' failed because of '+e.__str__())
                self.session.query(Threads).filter(Threads.chat_id == chat_id, Threads.message_id == parm).delete()
                self.session.commit()
                return True
        elif command == 'epic':
            try:
                self.core.sendMessage(chat_id=chat_id, reply_to_message_id=parm,
                                      text='@{} wants to check out this epic moment!'.format(msg['from']['username']))
            except telepot.exception.TelegramError as e:
                self.log('Callback '+str(command)+' '+str(chat_id)+' '+str(parm)+' failed because of '+e.__str__())
                self.session.query(Epics).filter(Epics.chat_id == chat_id, Epics.message_id == parm).delete()
                self.session.commit()
                return True
        elif command == 'request':
            try:
                to_reply_id = self.session.query(Requests).filter(Requests.chat_id == chat_id, Requests.username == parm).first().message_id
                self.core.sendMessage(chat_id=chat_id, reply_to_message_id=to_reply_id,
                                      text='@{} wants to answer @{} this one!'.format(msg['from']['username'],
                                                                                         parm))
            except telepot.exception.TelegramError as e:
                self.log('Callback '+str(command)+' '+str(chat_id)+' '+str(parm)+' failed because of '+e.__str__())
                return True
        else:
            return True

    def inline_query(self, msg):
        (query_id, from_id, query) = telepot.glance(msg, flavor='inline_query')
        articles = [InlineQueryResultArticle(
            id='insultme',
            title='Insult Me',
            input_message_content=InputTextMessageContent(
                message_text=insults.get_insult('I am a')
            )
        ),
            InlineQueryResultArticle(
                id='insultother',
                title='Insult written (wait a bit for it to load)',
                input_message_content=InputTextMessageContent(
                    message_text=insults.get_insult(query+' is a')
                )
            )
        ]
        self.core.answerInlineQuery(query_id, articles)
        return True

    def chosen_inline_result(self, msg):
        return True

    def get_fucked(self, chat_id, username='Thou'):
        self.core.sendMessage(chat_id=chat_id, text=insults.get_insult(username + ' art a'))


key = sys.argv[1]
bot = TopicsBot(key, backup)

while bot.keep_alive:
    time.sleep(5)