class Document(object):

    def __init__(self,text):
        self.size = len(text)
        self.data = text
        self.prevstate = None

class Command(object):

    def execute(self):
        pass

    def unexecute(self):
        pass

class Insert(Command):
    def __init__(self, doc):
        self.doc = doc

    def execute(self,text,position):
        self.doc.prevstate = self.doc.data
        self.doc.data = self.doc.data[:position] + text + self.doc.data[position:]

    def unexecute(self):
        if self.doc.prevstate is not None:
            self.doc.data, self.doc.prevstate = self.doc.prevstate, self.doc.data
        else:
            print 'Error. Nothing was insert.'

doc = Document('natashaaaaa')
print doc.size
