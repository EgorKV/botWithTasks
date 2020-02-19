import telebot
import config
import re
from telebot import types

from tasks import TasksManagement, Task


class Bot:
    def __init__(self):
        self.tasks = TasksManagement()
        self.bot = telebot.TeleBot(config.TOKEN) 

        @self.bot.message_handler(commands=["start"])
        def speak(message):    
            markup = self._startMenuMarkup()
            self.bot.send_message(
                chat_id=message.chat.id, 
                text="Menu", 
                reply_markup=markup)
        
        @self.bot.callback_query_handler(func=lambda call: True)
        def callback(call):
            try:
                if call.message:
                    if 'tasks choose from all' in call.data:
                        number = self._getNum(call.data)
                        count = self.tasks.tasks[number].number
                        markup = types.InlineKeyboardMarkup(row_width=2)
                        
                        # for i in range(5):
                        #     markup.add(
                        #         types.InlineKeyboardButton(
                        #             self.tasks.tasks[number].number, 
                        #             callback_data="number " + str(self.tasks.tasks[number].number)),
                        #         types.InlineKeyboardButton(
                        #             self.tasks.tasks[number+1].number, 
                        #             callback_data="number " + str(self.tasks.tasks[number+1].number))
                        #         )
                        #     number += 2
                        # markup.add(
                        #     types.InlineKeyboardButton(
                        #         'next',
                        #         callback_data='tasks choose from all ' + str(number)),
                        #     types.InlineKeyboardButton(
                        #         'prev',
                        #         callback_data='tasks choose from all ' + str(count - 10))    
                        #     )  
                        self._addNextPrev(markup, self.tasks.tasks, number, 'tasks choose from all ')                     
                        self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='choose', reply_markup=markup)
                        self.bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="")

                    if 'number' in call.data:
                        number = self._getNum(call.data)
                        markup = types.InlineKeyboardMarkup(row_width=1)
                        markup.add(types.InlineKeyboardButton('back', callback_data="menu"))
                        self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'company {self.tasks.tasksByNumber[number].company}, difficulty {self.tasks.tasksByNumber[number].difficulty}\n {self.tasks.tasksByNumber[number].task}', reply_markup=markup)
                        self.bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="")
                    
                    if call.data == 'menu':
                        markup = self._startMenuMarkup()
                        self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='menu', reply_markup=markup)
                        self.bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="")
                    if call.data == 'tasks choose by company':
                        markup = types.InlineKeyboardMarkup(row_width=1)
                        for company in self.tasks.companyNames:
                            markup.add(
                                types.InlineKeyboardButton(
                                    str(company), callback_data="company name " + str(company) + " "+ str(0)
                                ))
                        markup.add(types.InlineKeyboardButton('back', callback_data="menu"))                
                        self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='companies', reply_markup=markup)
                        self.bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="")
                    if "company name" in call.data:
                        number = self._getNum(call.data)
                        name = call.data[len("company name "):call.data.find(str(number))-1]
                        tasks = self.tasks.tasksByCompany[name]
                        print(call.data)
                        markup = types.InlineKeyboardMarkup(row_width=2)
                        # end = (number+1)*10-1
                        # print(0 if number == (len(tasks)-1)//10 else number + 1)
                        # if len(tasks)-end <= 0:
                        #     end = len(tasks)
                        # for task in tasks[number*10: end]:
                        #     print(task.number)
                        #     markup.add(
                        #         types.InlineKeyboardButton(
                        #             task.number, 
                        #             callback_data="number " + str(task.number
                        #             )))
                        self._addNextPrev(markup, tasks, number, 'company name ' + name + " ")
                        # markup.add(types.InlineKeyboardButton('back', callback_data="menu"))
                        self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=name, reply_markup=markup)
                        self.bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="")
                    if call.data == 'tasks choose by difficulty':
                        markup = types.InlineKeyboardMarkup(row_width=1)
                        # number = self._getNum(call.data)
                        for difficulty in list(self.tasks.tasksByDifficulty.keys()):
                            markup.add(
                                types.InlineKeyboardButton(
                                    str(difficulty), callback_data="difficulty " + str(difficulty) + " "+ str(0)
                                ))
                        markup.add(types.InlineKeyboardButton('back', callback_data="menu"))
                        self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='choose difficulty', reply_markup=markup)
                        self.bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="")
                    elif "difficulty " in call.data:
                        number = self._getNum(call.data)
                        difficulty = call.data[len("difficulty "):call.data.find(str(number))-1]
                        print(self.tasks.tasksByDifficulty)
                        tasks = self.tasks.tasksByDifficulty[difficulty]
                        markup = types.InlineKeyboardMarkup(row_width=1)
                        print(difficulty)
                        print(tasks)
                        self._addNextPrev(markup, tasks, number, 'difficulty ' + difficulty + ' ')
                        self.bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='cose difficulty', reply_markup=markup)
                        self.bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="")

            except Exception as e:
                print(repr(e))

    def startPolling(self):
        self.bot.polling(none_stop=True)
    
    def _getNum(self, text):
        return [int(s) for s in re.findall(r'\b\d+\b', text)][0]

    def _startMenuMarkup(self):
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton(
                "Task by number", callback_data="tasks choose from all 0"
            ), 
            types.InlineKeyboardButton(
                "Tasks by company", callback_data="tasks choose by company"),
            types.InlineKeyboardButton(
                "Tasks by difficulty", callback_data="tasks choose by difficulty"
            ))

        return markup

    def _addNextPrev(self, markup, tasks, number, call_back):
        end = (number+1)*10-1
        if len(tasks)-end <= 0:
            end = len(tasks)
        for task in tasks[number*10: end]:
            print(task.number)
            markup.add(
                types.InlineKeyboardButton(
                    task.number, 
                    callback_data="number " + str(task.number
            )))
        if len(tasks) >= 10:
            if number == 0:
                markup.add(
                    types.InlineKeyboardButton(
                        'next',
                        callback_data=call_back + str(number + 1))
                    )
            elif number == (len(tasks)-1)//10:
                markup.add(
                    types.InlineKeyboardButton(
                        'prev',
                        callback_data=call_back + str(number - 1))
                    )
            else:
                markup.add(
                    types.InlineKeyboardButton(
                        'next',
                        callback_data=call_back + str(number + 1)),
                    types.InlineKeyboardButton(
                        'prev',
                        callback_data=call_back + str(number - 1))    
                    )
        markup.add(types.InlineKeyboardButton('back', callback_data="menu"))




bot = Bot()
print('start')
bot.startPolling()

print('test')