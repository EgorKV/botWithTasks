from email.parser import Parser
import email
import re
import imaplib
import config
from html.parser import HTMLParser


class Task:
    def __init__(self, taskList):
        if taskList == '':
            return
        self.number = [int(s) for s in re.findall(r'\b\d+\b', taskList[1])][0]
        self.company = ''
        if 'asked by ' in taskList[4]:
            if taskList[4][taskList[4].find('asked by') + len('asked by') + 1] in [' ', '=', '\n']:
                self.company = taskList[4][taskList[4].find('asked by') + len('asked by') + 3: taskList[4].find('.')]
            else:
                self.company = taskList[4][taskList[4].find('asked by') + len('asked by') + 1: taskList[4].find('.')]
        self.task = ''
        i = 4
        while 'premium' not in taskList[i] and "liked this problem, feel free to forward" not in taskList[i] and 'Ready to interview?' not in taskList[i] and i < len(taskList)-1:
            taskList[i] = re.sub('=\n', '\n', taskList[i])
            self.task += taskList[i]
            i += 1
        # print(self.task)

        
class TasksManagement:
    def __init__(self):
        """ """
        self.tasks = self.update()
        self.tasksByNumber = {}
        self.tasksByCompany = {}
        for task in self.tasks:
            self.tasksByNumber[task.number]  = task
        for task in self.tasks:
            if task.company in self.tasksByCompany:
                self.tasksByCompany[task.company].append(task)
            else:
                self.tasksByCompany[task.company] = [task]
        self.companyNames = list(self.tasksByCompany.keys())
        self.companyNames.sort()

    def update(self):
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(config.EMAIL, config.PASSWORD)
        mail.list()
        mail.select('inbox')
        result = []
        n = 0
        result.append(n)
        retcode, messages = mail.search(
            None, '(SUBJECT "' + 'Daily Coding Problem' + '")')
        taskList = []
        if retcode == "OK":
            for num in messages[0].split():
                check, data = mail.fetch(num, '(RFC822)')
                if check == "OK":
                    original = email.message_from_string(
                        data[0][1].decode('utf-8'))
                    parser = MyHTMLParser()
                    parser.start()
                    parser.feed(original.get_payload()[1].as_string())
                    check, task = createTaskFromMail(parser.getResult())
                    parser.close()
                    print(check)
                    if check:
                        taskList.append(task)
        mail.close()
        return taskList


def createTaskFromMail(taskList):
    # print(taskList[1])
    if len(taskList) < 1:
        return False, Task('')
    if "Daily Coding Problem: Problem" in taskList[1]:
        return True, Task(taskList)
    else:
        return False, Task('')


class MyHTMLParser(HTMLParser):
    def handle_data(self, data):
        if data[:1] != "\n":
            self.result.append(data)

    def start(self):
        self.result = []

    def getResult(self):
        return self.result







def get_text(msg, fallback_encoding='utf-8', errors='replace'):
    """Extract plain text from email."""
    text = []
    for part in msg.walk():
        if part.get_content_type() == 'text/plain':
            p = part.get_payload(decode=True)
            if p is not None:
                text.append(p.decode(part.get_charset() or fallback_encoding,
                                     errors))
    return "\n".join(text)


task = TasksManagement()
print(task.tasksByCompany)
print(task.tasksByCompany[''][0].task)
