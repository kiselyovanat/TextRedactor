#! /usr/bin/env python
# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

class Document(object):

    def __init__(self,text):
        self.size = len(text)
        self.text = text

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

    def execute(self):
        self.doc.text = self.doc.text[:self.startPosition] + self.doc.text[self.endPosition:]

class Receiver(object):
    def __init__(self, insert, delete, undo, redo):
        self.insert_command = insert
        self.undo_command = undo
        self.redo_command = redo
        self.delete_command = delete

        self.command_stack = []
        self.redo_stack = []
        self.current_command = None

    def insert(self,text,position):
        self.current_command = self.insert_command
        self.current_command.InsertCommand(text,position)
        self.current_command.execute()
        self.command_stack.append(self.current_command)

    def undo(self):
        self.current_command = self.undo_command
        command = self.command_stack.pop()
        self.redo_stack.append(command)
        if command:
            self.current_command.execute(command)

        else:
            print "Nothing to undo"

    def redo(self):
        self.current_command = self.redo_command
        command = self.redo_stack.pop()
        if command:
            self.current_command.execute(command)
        else:
            print "Nothing to redo"

    def delete(self,startPosition, endPosition):
        self.current_command = self.delete_command
        self.current_command.DeleteCommand(startPosition, endPosition)
        self.current_command.execute()



doc = Document('natasha')
doc.show()
receiver = Receiver(InsertCommand(doc), DeleteCommand(doc), UndoCommand(), RedoCommand())
receiver.insert('love',3)
#receiver.insert('love',3)
doc.show()
receiver.undo()
doc.show()
receiver.redo()
doc.show()
receiver.delete(3,7)
doc.show()
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
