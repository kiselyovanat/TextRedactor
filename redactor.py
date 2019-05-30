#! /usr/bin/env python
# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

class Document(object):

    def __init__(self,text):
        self.size = len(text)
        self.text = text
        self.buffer = None

    def show(self):
        print self.text

class Command(object):

    def execute(self):
        pass

    def unexecute(self):
        pass

class InsertCommand(Command):
    def __init__(self, doc):
        self.doc = doc
        self.text = None
        self.position = None

    def InsertCommand(self, text, position):
        self.text = text
        self.position = position

    def execute(self):
        self.doc.text = self.doc.text[:self.position] + self.text + self.doc.text[self.position:]

    def unexecute(self):
        index = self.position + len(self.text)
        self.doc.text = self.doc.text[:self.position] + self.doc.text[index:]

class UndoCommand(Command):
    def __init__(self):
        self.command = None

    def execute(self,command):
        self.command = command
        self.command.unexecute()

class RedoCommand(Command):
    def __init__(self):
        self.command = None

    def execute(self,command):
        self.command = command
        self.command.execute()

class DeleteCommand(Command):
    def __init__(self,doc):
        self.doc = doc
        self.startPosition = None
        self.endPosition = None

    def DeleteCommand(self,startPosition, endPosition):
        self.startPosition = startPosition
        self.endPosition = endPosition
        self.deletedText = self.doc.text[self.startPosition:self.endPosition]

    def execute(self):
        self.doc.text = self.doc.text[:self.startPosition] + self.doc.text[self.endPosition:]

    def unexecute(self):
        #print 'print ',self.doc.text
        self.doc.text = self.doc.text[:self.startPosition] + self.deletedText + self.doc.text[self.startPosition:]

class CopyCommand(Command):
    def __init__(self,doc):
        self.doc = doc
        self.startPosition = None
        self.endPosition = None

    def CopyCommand(self,startPosition, endPosition):
        self.startPosition = startPosition
        self.endPosition = endPosition

    def execute(self):
        self.doc.buffer = self.doc.text[self.startPosition:self.endPosition]

    #def unexecute(self):
    #    self.doc.buffer = None

class PasteCommand(Command):
    def __init__(self,doc):
        self.doc = doc
        self.position = None

    def PasteCommand(self,position):
        self.position = position

    def execute(self):
        if self.doc.buffer:
            self.doc.text = self.doc.text[:self.position] + self.doc.buffer + self.doc.text[self.position:]
        else:
            print 'Nothing to paste'

    def unexecute(self):
        index = self.position + len(self.doc.buffer)
        self.doc.text =  self.doc.text[:self.position] + self.doc.text[index:]



class Receiver(object):
    def __init__(self, insert, delete, undo, redo, copy, paste):
        self.insert_command = insert
        self.undo_command = undo
        self.redo_command = redo
        self.delete_command = delete
        self.copy_command = copy
        self.paste_command = paste

        self.command_stack = []
        self.redo_stack = []

    def insert(self,text,position):
        self.insert_command.InsertCommand(text,position)
        self.insert_command.execute()
        self.command_stack.append(self.insert_command)

    def undo(self):
        if self.command_stack:
            command = self.command_stack.pop()
            self.redo_stack.append(command)
            self.undo_command.execute(command)

        else:
            print "Nothing to undo"

    def redo(self):
        if  self.redo_stack:
            command = self.redo_stack.pop()
            self.command_stack.append(command)
            self.redo_command.execute(command)
        else:
            print "Nothing to redo"

    def delete(self,startPosition, endPosition):
        self.delete_command.DeleteCommand(startPosition, endPosition)
        self.delete_command.execute()
        self.command_stack.append(self.delete_command)

    def copy(self, startPosition, endPosition):
        self.copy_command.CopyCommand(startPosition, endPosition)
        self.command_stack.append(self.copy_command)
        self.copy_command.execute()

    def paste(self, position):
        self.paste_command.PasteCommand(position)
        self.command_stack.append(self.paste_command)
        self.paste_command.execute()


class CommandParser(object):

    def __init__(self,command_doc):
        self.command_doc = command_doc
        self.commands = []

    def parse(self):
        self.commands = self.getTokens()
        '''for i in range(0, len(tokens)):
            if tokens[i][0] == "insert":
                self.commands.append([tokens[i][0],tokens[i][1], int(tokens[i][2]) )
            elif tokens[i][0] == 'delete':
                self.commands.append('delete' + '(' + tokens[i][1] + ',' + tokens[i][2] + ')')
            elif tokens[i][0] == 'undo':
                self.commands.append('undo()')
            elif tokens[i][0] == 'redo':
                self.commands.append('redo()')
            elif tokens[i][0] == 'copy':
                self.commands.append('copy' + '(' + tokens[i][1] + ',' + tokens[i][2] + ')')
            elif tokens[i][0] == 'paste':
                self.commands.append('paste' + '(' + tokens[i][1] + ')')'''
        return self.commands

    def getTokens(self):
        strings = self.command_doc.text.split('\n')
        tokens = [command.split(' ') for command in strings]
        return tokens


doc = Document('natasha')
doc.show()
receiver = Receiver(InsertCommand(doc), DeleteCommand(doc), UndoCommand(), RedoCommand(), CopyCommand(doc), PasteCommand(doc))
f = open("commands.txt", 'r')
text = f.read()
command_doc = Document(text)
command_doc.show()
parser = CommandParser(command_doc)
commands = parser.parse()
print commands
for i in range(0,len(commands)):
    action_name = commands[i][0]
    action = getattr(receiver, action_name)()
    doc.show()


'''receiver = Receiver(InsertCommand(doc), DeleteCommand(doc), UndoCommand(), RedoCommand(), CopyCommand(doc), PasteCommand(doc))
receiver.insert('love',3)
doc.show()
receiver.undo()
doc.show()
receiver.redo()
doc.show()
receiver.delete(0,4)
doc.show()
receiver.undo()
doc.show()
receiver.redo()
doc.show()
receiver.undo()
doc.show()'''

'''    Реализовать примитивный текстовый редактор, способный производить ряд операций над одной строкой, с использование шаблона проектирования “Команда”
    Тесктовый редактор работает с двумя текстовыми файлами. В первом находится строка, над которой он проводит все операции. Во втором - последовательность команд, которые нужно выполнить. Необходимо реализовать поддержку следующих команд:
    • copy idx1 idx2 - скопировать в буффер обмена символы с позиции idx1 до позиции idx2
    • paste idx - вставить содержимое буффера обмена в позицию idx
    • insert “string” idx - вставить строку “string” в позицию idx
    • delete idx1 idx2 - удалить все символы с позиции idx1 до позиции idx2
    • undo - отменить предыдущую команду
    • redo - выполнить отмененную команду заново
    Пример тесктового файла комманд:
    copy 1, 3
    insert "hello", 1
    paste 6
    undo
    redo
    delete 2, 7
    undo
    undo
    redo
    redo
    Необходимо:
    • Реализовать систему классов, необходимую для патерна “Команда”: общий интерфейс комманд + классы для каждой из комманд
    • Реализовать класс текстового процессора, хранящий строку и способный выполнять все необходимые операции над ней
    • Реализовать класс-парсер, считывающий последовательность комманд из файла и интерпретирующий их
    • Реализовать класс, выполняющий последовательность комманд (полученных от парсера) и реализующий механизм undo/redo

'''
