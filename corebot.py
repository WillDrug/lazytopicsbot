import time
import pickle
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
from telepot.helper import Answerer

class Context:
    def __init__(self):
        self.buttons = {'Help': None}

    def get_buttons(self):
        return [q for q in self.buttons.keys()]

    def parse_chat(self, inputlist):
        return None

    def parse_callback_query(self, inputlist):
        return None

class Topics(Context):
    def __init__(self):
        self.buttons = {
            'Lookup Thread': self.get_topic,
            'Remove Thread': self.remove_topic
        }
        self.topics = dict()

    def parse(self, inputlist):
        msg = inputlist[0]
        (content_type, chat_type, chat_id) = telepot.glance(msg, 'chat')
        """inputlist[1].sendMessage(chat_id=chat_id, text='Glance fuckers',
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                        [InlineKeyboardButton(text='Callback - show notification', callback_data='notification')],
                                        [InlineKeyboardButton(text='Callback - edit message', callback_data='edit')],
                                        [dict(text='Switch to using bot inline', callback_data='initial query')],
                                        ])
                                 )"""
        if msg['text'] in self.buttons.keys():
            self.buttons[msg['text']](inputlist)
        elif msg['text'][0:4] == '/add':
            if msg['text'][5:] == '':
                inputlist[1].sendMessage(chat_id=chat_id, text='Fuck you')
            self.topics[msg['text'][5:]] = {
                'id': msg['message_id']
            }
            print('adding shit')

    def parse_callback_query(self, inputlist):
        msg = inputlist[0]
        chat_id = msg['message']['chat']['id']
        text = msg['data']
        if text[0:3] == 'lnk':
            if text[3:] in self.topics.keys():
                inputlist[1].sendMessage(chat_id=chat_id, reply_to_message_id=self.topics[text[3:]]['id'], text='Here ya go')
        elif text[0:3] == 'del':
            if text[3:] in self.topics.keys():
                dict.__delitem__(self.topics, text[3:])
                inputlist[1].sendMessage(chat_id=chat_id, text='Deleted')
        else:
            print('some other shit')

        return True

    def get_topic(self, inputlist):
        (content_type, chat_type, chat_id) = telepot.glance(inputlist[0], 'chat')
        if self.topics.keys().__len__() == 0:
            inputlist[1].sendMessage(chat_id=chat_id, text='No topics found, try adding some with /add topic')
            return True
        markup = InlineKeyboardMarkup(inline_keyboard = [])
        for i in self.topics.keys():
            markup.inline_keyboard.append([InlineKeyboardButton(text=i, callback_data='lnk'+i)])
        inputlist[1].sendMessage(chat_id=chat_id, text='Choose a topic',
                                 reply_markup=markup)

    def remove_topic(self, inputlist):
        (content_type, chat_type, chat_id) = telepot.glance(inputlist[0], 'chat')
        if self.topics.keys().__len__() == 0:
            inputlist[1].sendMessage(chat_id=chat_id, text='No topics found, try adding some with /add topic')
            return True
        markup = InlineKeyboardMarkup(inline_keyboard=[])
        for i in self.topics.keys():
            markup.inline_keyboard.append([InlineKeyboardButton(text=i, callback_data='del' + i)])
        inputlist[1].sendMessage(chat_id=chat_id, text='Choose a topic',
                                 reply_markup=markup)



class BotContext:
    def __init__(self, id):
        self.id = id
        self.level = 0
        self.context_classes = [
            'Topics'
        ]
        self.Topics = Topics()

        self.update_context('root')

    def update_context(self, context):
        print('updating context %s' % context)
        if context == 'root':
            self.current_context = 'root'
            self.keyboard_markup = self.generate_keyboard(self.context_classes)
            return True
        try:
            self.current_context = context
            self.keyboard_markup = self.generate_keyboard(self.get_current_context().get_buttons())
            return True
        except NameError:
            return False

    def get_current_context(self):
        if self.current_context == 'root':
            return 'root'
        return eval('self.'+self.current_context)

    def get_current_buttons(self):
        return self.keyboard_markup

    def generate_keyboard(self, buttons):
        keyboard_markup = list()

        for i in buttons:
            keyboard_markup.append(i)
        keyboard_markup.append('Reset')
        return keyboard_markup



class BotCore:
    def __init__(self, BSF):
        self.lock = False
        self.log = True
        self.shutdown = False
        self.contexts = BSF
        self.token = '447645569:AAEJju9bNSukaJdQk74b4n7M9xKBPFVCmgM'
        self.core = telepot.Bot(self.token)
        MessageLoop(self.core, self.handler).run_as_thread()
        if self.log: print('Initialized chat thread')

    def get_current_keyboard(self, chat_id):
        markup = ReplyKeyboardMarkup(keyboard=[[]])
        for i in self.contexts[chat_id].keyboard_markup:
                markup[0][0].append(KeyboardButton(text=i))
        return markup

    def handler(self, msg):
        if self.log: print('Got message')
        flavor = telepot.flavor(msg)
        return eval('self.' + flavor)(msg)

    def chat(self, msg):
        (content_type, chat_type, chat_id) = telepot.glance(msg, flavor='chat')
        if self.log: print('Entered chat flavor')
        self.core.sendMessage(chat_id=chat_id, text='/restart')
        if chat_id not in self.contexts.keys():
            if self.log: print('new context')
            self.contexts[chat_id] = BotContext(chat_id)
            self.core.sendMessage(chat_id, 'Hello! I''ve got your context now!',
                                  reply_markup=self.get_current_keyboard(chat_id)
                                  )
            return True
        try:
            if self.log: print('Old context')
            return eval('self.'+content_type)(msg, content_type, chat_type, chat_id)
            """[text, audio, document, game, photo, sticker, video, voice, video_note, contact, location, venue,
             new_chat_member, left_chat_member, new_chat_title, new_chat_photo, delete_chat_photo, group_chat_created,
             supergroup_chat_created, channel_chat_created, migrate_to_chat_id, migrate_from_chat_id, pinned_message,
             new_chat_members, invoice, successful_payment]"""
        except AttributeError as e:
            print(e)
            return self.generic_type(msg, content_type, chat_type, chat_id)
            pass

    def text(self, msg, content_type, chat_type, chat_id):
        if self.log: print('Got %s chat type' % chat_type)
        if msg['text'] == 'Lock':
            if msg['from']['username'] != 'WillDrug':
                self.core.sendMessage(chat_id=chat_id, text='No way Jose!',
                                      reply_markup=self.get_current_keyboard(chat_id))
            else:
                self.lock = not self.lock
                if self.log: print('Locking is %s' % str(self.lock))
        elif msg['text'] == 'Reset' and not self.lock:
            self.contexts[chat_id].update_context('root')
            self.core.sendMessage(chat_id=chat_id, reply_markup=self.get_current_keyboard(chat_id),
                                 text='You''re in the main menu again')
        elif msg['text'] == 'Hard Reset':
            if msg['from']['username'] == 'WillDrug':
                dict.__delitem__(self.contexts, chat_id)
                self.core.sendMessage(reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='/start')]]),
                                      chat_id=chat_id,
                                      text='I''ve killed you!')
            else:
                self.core.sendMessage(reply_markup=self.get_current_keyboard(chat_id),
                                      chat_id=chat_id,
                                      text='No dice!')
        elif msg['text'] == 'Shutdown':
            if msg['from']['username'] == 'WillDrug':
                self.shutdown = True
            else:
                self.core.sendMessage(text='Fuck you, bro', chat_id=chat_id)
        elif msg['text'] in self.contexts[chat_id].context_classes:
            self.contexts[chat_id].update_context(msg['text'])
            self.core.sendMessage(reply_markup=self.get_current_keyboard(chat_id), chat_id=chat_id,
                                  text='You are in %s menu now!' % msg['text'])
        elif self.contexts[chat_id].current_context != 'root':
            self.contexts[chat_id].get_current_context().parse([msg, self.core])
        else:
            self.core.sendMessage(chat_id=chat_id, reply_markup=self.get_current_keyboard(chat_id),
                                  text='Press a button first, fucker')
        return True

    def generic_type(self, msg, content_type, chat_type, chat_id):
        if self.log: print('Parsing %s content type as generic!' % content_type)
        return True

    def callback_query(self, msg):
        chat_id = msg['message']['chat']['id']
        if chat_id not in self.contexts.keys():
            return False
        if self.contexts[chat_id].current_context == 'root':
            self.core.sendMessage(chat_id=chat_id, text='How the fuck did you do that?')
        else:
            self.contexts[chat_id].get_current_context().parse_callback_query([msg, self.core])
        return True

    def inline_query(self, msg):
        (query_id, from_id, query) = telepot.glance(msg, flavor='inline_query')
        self.articles = [InlineQueryResultArticle(
            id='threadstart',
            title='Basic Bark',
            input_message_content=InputTextMessageContent(
                message_text='Hello, fuckers!'
            )
        )
        ]
        if self.log: print('Got %s inline query' % query)
        self.core.answerInlineQuery(query_id, self.articles)
        return self.articles

    def chosen_inline_result(self, msg):
        result_id, from_id, query = telepot.glance(msg, 'chosen_inline_result')
        print('chosen', msg)


    def shipping_query(self, msg):
        print('shipping')

    def pre_checkout_query(self, msg):
        print('pre checkout')

import threading

try:
    f = open('WillDrugBot.bsf', 'rb+')
    BSF = pickle._load(f)
    f.close()
except (EOFError, FileNotFoundError, AttributeError):
    BSF = dict()
    pass

WillDrugBot = BotCore(BSF)
while 1:
    time.sleep(5)
    if WillDrugBot.shutdown:
        break

f = open('WillDrugBot.bsf', 'wb+')
pickle._dump(WillDrugBot.contexts, f)
f.close()
