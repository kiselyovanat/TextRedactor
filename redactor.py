#! /usr/bin/env python
# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

class Document(object):

    def __init__(self,text):
        self.size = len(text)
        self.text = text
        self.prevstate = []

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

    def execute(self,text,position):
        self.doc.prevstate.append(self.doc.text)
        self.doc.text = self.doc.text[:position] + text + self.doc.text[position:]

    def unexecute(self):
        #a = self.doc.text
        self.doc.text = self.doc.prevstate.pop()
        #self.doc.prevstate.append(a)


class Receiver(object):
    def __init__(self, insert):
        self.insert_command = insert
        self.command_stack = []
        self.current_command = None

    def insert(self,text,position):
        self.current_command = self.insert_command
        self.current_command.execute(text,position)
        self.command_stack.append(self.current_command)

    def undo(self):
        if self.command_stack:
            self.command_stack.pop().unexecute()
        else:
            print "Nothing to undo"


doc = Document('natashaaaaa')
doc.show()
receiver = Receiver(InsertCommand(doc))
receiver.insert('love',3)
receiver.insert('love',3)
doc.show()
receiver.undo()
doc.show()
receiver.undo()
doc.show()
receiver.redo()
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
