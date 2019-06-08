#! /usr/bin/env python
# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

class Document(object):

    def __init__(self,filename):
        self.text = self.get_from_file(filename)
        self.size = len(self.text)
        self.buffer = None

    def show(self):
        print self.text

    def get_from_file(self,filename):
        file = open(filename, 'r')
        text = file.read()
        text = text[:len(text)-1]       #символ конца файла убираем
        strings = text.split('\n')
        file.close()
        return strings

    def write_to_file(self):
        file = open("redactorWork.txt",'w+')
        for string in self.text:
            file.write(string + '\n')
        file.close()

class Command(object):

    def execute(self):
        pass

    def unexecute(self):
        pass

    def check_position(self, stringNumber, startPosition, endPosition=None):
        if stringNumber > self.doc.size-1:                  #т.к нумерация строк начинается с 0
            raise Exception("Wrong string number")
        if startPosition > len(self.doc.text[stringNumber]):
            raise Exception("Wrong position")
        if endPosition != None and endPosition > len(self.doc.text[stringNumber]):
            raise Exception("Wrong position")


class InsertCommand(Command):
    def __init__(self, doc):
        self.doc = doc
        self.text = None
        self.position = None
        self.stringNumber = None

    def InsertCommand(self, text, stringNumber, position):
        self.check_position(stringNumber,position)
        self.text = text
        self.position = position
        self.stringNumber = stringNumber

    def execute(self):
        self.doc.text[self.stringNumber] = self.doc.text[self.stringNumber][:self.position] + self.text + self.doc.text[self.stringNumber][self.position:]

    def unexecute(self):
        index = self.position + len(self.text)
        self.doc.text[self.stringNumber] = self.doc.text[self.stringNumber][:self.position] + self.doc.text[self.stringNumber][index:]

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
        self.stringNumber = None

    def DeleteCommand(self,stringNumber, startPosition, endPosition):
        self.check_position(stringNumber, startPosition, endPosition)
        self.stringNumber = stringNumber
        self.startPosition = startPosition
        self.endPosition = endPosition
        self.deletedText = self.doc.text[self.stringNumber][self.startPosition:self.endPosition]


    def execute(self):
        self.doc.text[self.stringNumber] = self.doc.text[self.stringNumber][:self.startPosition] + self.doc.text[self.stringNumber][self.endPosition:]

    def unexecute(self):
        self.doc.text[self.stringNumber] = self.doc.text[self.stringNumber][:self.startPosition] + self.deletedText + self.doc.text[self.stringNumber][self.startPosition:]

class CopyCommand(Command):
    def __init__(self,doc):
        self.doc = doc
        self.startPosition = None
        self.endPosition = None
        self.stringNumber = None

    def CopyCommand(self,stringNumber, startPosition, endPosition):
        self.check_position(stringNumber,startPosition, endPosition)
        self.stringNumber = stringNumber
        self.startPosition = startPosition
        self.endPosition = endPosition

    def execute(self):
        self.doc.buffer = self.doc.text[self.stringNumber][self.startPosition:self.endPosition]

    #def unexecute(self):
    #    self.doc.buffer = None

class PasteCommand(Command):
    def __init__(self,doc):
        self.doc = doc
        self.position = None
        self.stringNumber = None

    def PasteCommand(self,stringNumber,position):
        self.check_position(stringNumber, position)
        self.stringNumber = stringNumber
        self.position = position

    def execute(self):
        if self.doc.buffer:
            self.doc.text[self.stringNumber] = self.doc.text[self.stringNumber][:self.position] + self.doc.buffer + self.doc.text[self.stringNumber][self.position:]
        else:
            print 'Nothing to paste'

    def unexecute(self):
        index = self.position + len(self.doc.buffer)
        self.doc.text[self.stringNumber] =  self.doc.text[self.stringNumber][:self.position] + self.doc.text[self.stringNumber][index:]

class Receiver(object):
    def __init__(self, doc, command_doc):
        self.doc = doc
        self.command_doc = command_doc

    def work(self):
        parser = CommandParser(self.command_doc)
        commands = parser.parse()
        #print commands
        invoker = Invoker(InsertCommand(self.doc), DeleteCommand(self.doc), UndoCommand(), RedoCommand(), CopyCommand(self.doc), PasteCommand(self.doc))
        try:
            for i in range(0,len(commands)):                    # у каждой команды своё число аргументов.
                action_name = commands[i][0]                    # синтаксис getattr - getattr(объект класса, метод класса)(аргументы метода)
                command_lenght = len(commands[i])               # getattr(invoker, 'copy')(1,3) = invoker.copy(1,3)
                if command_lenght == 4:                         #insert, copy,delete
                    action = getattr(invoker, action_name)(commands[i][1], commands[i][2], commands[i][3])
                elif command_lenght == 3:                       #paste
                    action = getattr(invoker, action_name)(commands[i][1],commands[i][2])
                elif command_lenght == 1:                       #redo,undo
                    action = getattr(invoker, action_name)()
                #self.doc.show()
        except Exception as e:
            print str(e)+ ' in ' + commands[i][0] + ' command'
            return


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

    def insert(self, text, stringNumber, position):
        self.insert_command.InsertCommand(text, stringNumber, position)
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

    def delete(self, stringNumber, startPosition, endPosition):
        self.delete_command.DeleteCommand(stringNumber, startPosition, endPosition)
        self.delete_command.execute()
        self.command_stack.append(self.delete_command)

    def copy(self, stringNumber, startPosition, endPosition):
        self.copy_command.CopyCommand(stringNumber, startPosition, endPosition)
        self.command_stack.append(self.copy_command)
        self.copy_command.execute()

    def paste(self, stringNumber, position):
        self.paste_command.PasteCommand(stringNumber, position)
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
                self.commands[i][3] = int(self.commands[i][3])
            elif self.commands[i][0] == 'delete':
                self.commands[i][1] = int(self.commands[i][1])
                self.commands[i][2] = int(self.commands[i][2])
                self.commands[i][3] = int(self.commands[i][3])
            elif self.commands[i][0] == 'copy':
                self.commands[i][1] = int(self.commands[i][1])
                self.commands[i][2] = int(self.commands[i][2])
                self.commands[i][3] = int(self.commands[i][3])
            elif self.commands[i][0] == 'paste':
                self.commands[i][1] = int(self.commands[i][1])
                self.commands[i][2] = int(self.commands[i][2])
        return self.commands

    def getTokens(self):
        strings = self.command_doc.text
        tokens = [command.split(' ') for command in strings]
        return tokens

def start(text_filename,commands_filename):
    doc = Document(text_filename)
    #doc.show()
    command_doc = Document(commands_filename)
    #command_doc.show()

    receiver = Receiver(doc, command_doc)
    receiver.work()
    doc.write_to_file()

start("text.txt","commands.txt")
