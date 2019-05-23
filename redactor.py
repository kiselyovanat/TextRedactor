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
        command = self.command_stack.pop()
        self.redo_stack.append(command)
        if command:
            self.undo_command.execute(command)

        else:
            print "Nothing to undo"

    def redo(self):
        command = self.redo_stack.pop()
        self.command_stack.append(command)
        if command:
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


doc = Document('natasha')
doc.show()
receiver = Receiver(InsertCommand(doc), DeleteCommand(doc), UndoCommand(), RedoCommand(), CopyCommand(doc), PasteCommand(doc))
receiver.insert('love',3)
#receiver.insert('love',3)
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
receiver.copy(0,4)
print 'buffer ', doc.buffer
receiver.paste(0)
doc.show()
receiver.undo()
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
