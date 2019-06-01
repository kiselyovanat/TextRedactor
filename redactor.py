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
    def __init__(self, doc, command_doc):
        self.doc = doc
        self.command_doc = command_doc

    def work(self):
        parser = CommandParser(self.command_doc)
        commands = parser.parse()
        #print commands
        invoker = Invoker(InsertCommand(self.doc), DeleteCommand(self.doc), UndoCommand(), RedoCommand(), CopyCommand(self.doc), PasteCommand(self.doc))
        for i in range(0,len(commands)):                    # у каждой команды своё число аргументов.
            action_name = commands[i][0]                    # синтаксис getattr - getattr(объект класса, метод класса)(аргументы метода)
            command_lenght = len(commands[i])               # getattr(invoker, 'copy')(1,3) = invoker.copy(1,3)
            if command_lenght == 3:
                action = getattr(invoker, action_name)(commands[i][1], commands[i][2])
            elif command_lenght == 2:
                action = getattr(invoker, action_name)(commands[i][1])
            elif command_lenght == 1:
                action = getattr(invoker, action_name)()
            self.doc.show()

class Invoker(object):
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
        for i in range(0, len(self.commands)):              # у каждой команды разные типы входных переменных.
            if self.commands[i][0] == "insert":             # после getTokens() все аргументы типа sting.
                self.commands[i][2] = int(self.commands[i][2])
            elif self.commands[i][0] == 'delete':
                self.commands[i][1] = int(self.commands[i][1])
                self.commands[i][2] = int(self.commands[i][2])
            elif self.commands[i][0] == 'copy':
                self.commands[i][1] = int(self.commands[i][1])
                self.commands[i][2] = int(self.commands[i][2])
            elif self.commands[i][0] == 'paste':
                self.commands[i][1] = int(self.commands[i][1])
        return self.commands

    def getTokens(self):
        strings = self.command_doc.text.split('\n')
        tokens = [command.split(' ') for command in strings]
        return tokens

def start(commands_filename):
    doc = Document('abra cadabra')

    f = open(commands_filename, 'r')
    text = f.read()
    f.close()
    text = text[:len(text)-1]
    command_doc = Document(text)
    #command_doc.show()

    receiver = Receiver(doc, command_doc)
    receiver.work()

start("commands.txt")
