#!/usr/bin/python3

import tkinter as tk
import sqlite3 as sq 

from tkinter import ttk

# not used yet
"""
def sort_list():

    # function to sort listbox items case insensitive

    temp_list = list(docsList.get(0, tk.END))
    temp_list.sort(key=str.lower)
    # delete contents of present listbox
    docsList.delete(1, tk.END)
    # load listbox with sorted data
    for item in temp_list:
        docsList.insert(tk.END, item)
"""

dbConnection = sq.connect("annot.db")
db = dbConnection.cursor()

class PersonAnnotation(tk.Toplevel):

    # signal to main window that it needs to update citations
    signalCreatePersonAnnotation = None

    def __init__(self, parent):
        super().__init__(parent)
        self.geometry("400x600+300+300")
        self.title("person annotation")

        frame1 = tk.Frame(self, padx=5, pady=5, relief=tk.RAISED, borderwidth=1)
        frame1.pack(fill=tk.X)
        lbl1 = tk.Label(frame1, text="Search", width=6)
        lbl1.pack(side=tk.LEFT, padx=5, pady=5)
    
        self._searchPerson = tk.StringVar()
        self._searchPerson.trace_add("write", self.filterPersonList)
        entry1 = tk.Entry(frame1, textvariable=self._searchPerson)
        entry1.pack(fill=tk.X, padx=5, side=tk.LEFT, expand=True)
        addPerson = tk.Button(frame1, text ="add new", command=self.addPerson)
        addPerson.pack(side=tk.RIGHT, padx=5, pady=5)
 
        frame2 = tk.Frame(self, padx=5, pady=5, borderwidth=1, relief=tk.RAISED)
        frame2.pack(fill=tk.BOTH, expand=True)
        lbl2 = tk.Label(frame2, text="Entries", width=6)
        lbl2.pack(side=tk.LEFT, anchor=tk.N, padx=5, pady=5)
        self._personEntries = tk.Listbox(frame2, exportselection=False, selectmode=tk.SINGLE, width = 20, font=("arial", 12))
        self._personEntries.pack(fill = tk.BOTH, expand=True)
        self.updatePersonEntries("")
        self._personEntries.bind('<<ListboxSelect>>',self.selectPerson)
       
        frame3 = tk.Frame(self, padx=5, pady=5, relief=tk.RAISED, borderwidth=1)
        frame3.pack(fill=tk.X)
        cancelButton = tk.Button(frame3, text ="cancel",command=self.cancelPerson)
        cancelButton.pack(side=tk.RIGHT)
        # change for okButton
        self._okAddAnnotation = tk.Button(frame3, text ="ok",command=self.okPerson)
        self._okAddAnnotation.pack(side=tk.RIGHT)
        self._okAddAnnotation.config(state=tk.DISABLED)

    def addPerson(self):
        self._addPerson = PersonInsertion(self, self._searchPerson.get())
        self._addPerson.signalPersonAdded = self.personAdded

    def personAdded(self):
        self._searchPerson.set("")
        self.updatePersonEntries("")

    def updatePersonEntries(self, txt):
        records = db.execute("SELECT * from persons")

        self._personEntriesList= []
        self._personEntries.delete(0, tk.END)
        for row in records:
            personName = row[1]
            # filter if search is being used
            if txt!="" and personName.lower().find(txt.lower())==-1:
                continue
                
            self._personEntries.insert(1,personName)
            self._personEntriesList.append(str(row[0]))

    def selectPerson(self, event):
        self._okAddAnnotation.config(state=tk.NORMAL)

    def cancelPerson(self):
        self._annotPerson.destroy();

    def filterPersonList(self, var, index, mode):
        self.updatePersonEntries(self._searchPerson.get())
    
    def okPerson(self): 
        # get person id
        idPerson = self._personEntriesList[self._personEntries.curselection()[0]]
        self.signalCreatePersonAnnotation(idPerson)

        # close window
        self.destroy()

class PersonInsertion(tk.Toplevel):   

    # signal/callback to update person entries
    signalPersonAdded = None
    
    def __init__(self, parent, initialText):
        super().__init__(parent)
        self.geometry("400x300+800+300")
        self.title("add new person")

        frame1 = tk.Frame(self)
        frame1.pack(fill=tk.X)

        lbl1 = tk.Label(frame1, text="Name", width=6)
        lbl1.pack(side=tk.LEFT, padx=5, pady=5)
        
        self._personName = tk.StringVar()
        self._personName.set(initialText)
        self._personName.trace_add("write", self.enablePersonEntry)
        
        entry1 = tk.Entry(frame1, textvariable=self._personName)
        entry1.pack(fill=tk.X, padx=5, expand=True)

        frame2 = tk.Frame(self)
        frame2.pack(fill=tk.BOTH, expand=True)

        lbl2 = tk.Label(frame2, text="Info", width=6)
        lbl2.pack(side=tk.LEFT, anchor=tk.N, padx=5, pady=5)

        self._personInfo = tk.Text(frame2, width=20, height=10)
        self._personInfo.pack(fill=tk.BOTH, pady=5, padx=5, expand=True)

        frame3 = tk.Frame(self, padx=5, pady=5, borderwidth=1)
        frame3.pack(fill=tk.X, expand=True)
        cancelButton = tk.Button(frame3, text ="cancel",command=self.cancelAddPerson)
        cancelButton.pack(side=tk.RIGHT)
        self._okButton = tk.Button(frame3, text ="ok",command=self.okAddPerson)
        self._okButton.pack(side=tk.RIGHT)
        self._okButton.config(state=tk.DISABLED)

        # check state of ok button
        self.enablePersonEntry(0,0,0)

    def cancelAddPerson(self):
        self.destroy();

    def okAddPerson(self):
        sql = 'INSERT INTO persons (name, info) VALUES (?,?)'
        values = (self._personName.get(), self._personInfo.get(1.0,tk.END))
        db.execute(sql, values)
        dbConnection.commit()

        self.signalPersonAdded()
        self.destroy()

    def enablePersonEntry(self, var, index, mode):
        if self._personName.get()=="":
            self._okButton.config(state=tk.DISABLED)
        else:
            self._okButton.config(state=tk.NORMAL)

class UI(object):

    _works = []
    _docs = []
    _typeSelected = "no selection"

    # constructor
    def __init__(self):
        self._window = tk.Tk()

        self._window.title("text annotation")   
        self._window.geometry("1800x1000")
        self._tabs = ttk.Notebook(self._window)    

        self.createDocsTab();
        self.createCiteFrame();
        
        self._worksTab = ttk.Frame(self._tabs)
        self._tabs.add(self._worksTab, text="add sources")

        self._tabs.pack(expand=1, fill="both")

    # callbacks
    def selectWork(self, event):
        self._docs = []
        self.clearAnnotation()
        # pick value at index of mouse click
        workId = self._works[self._worksList.curselection()[0]]
        self._docsList.delete(0, tk.END)
        records = db.execute("SELECT * from docs where id_work="+workId)
        for row in records:
            self._docs.append(str(row[0]))
            self._docsList.insert(1, row[3])
        self._docsList.pack(side = tk.LEFT, fill = tk.Y)

    def selectDoc(self, event):
        #value = docsList.get(docsList.curselection())
        # starts at 0
        self.clearAnnotation()
        # value = int(docsList.get(tk.ANCHOR))
        docId = self._docs[self._docsList.curselection()[0]]

        records = db.execute("SELECT text from docs where ID="+docId)
        self._text.config(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        for row in records:
            self._text.insert(tk.INSERT, row[0])
        self._text.config(state=tk.DISABLED)

        self.updateAnnotations()

    def mouseUp(self, event):
        self.clearAnnotation()
        ranges = self._text.tag_ranges(tk.SEL)
        if ranges:
            self._annotate.config(state=tk.NORMAL)
            self._citedText.insert(tk.INSERT, self._text.get(*ranges))

    def clearAnnotation(self):
        self._citedText.delete("1.0", tk.END)
        self._annotate.config(state=tk.DISABLED)


    def addAnnotation(self):
        self._rangeSelected = self._text.tag_ranges(tk.SEL)
        self._annotPerson = PersonAnnotation(self._window)
        self._annotPerson .signalCreatePersonAnnotation = self.createPersonAnnotation

    def resetTags(self):       

        # clear tags before adding them
        self._text.tag_delete("place")
        self._text.tag_delete("event")
        self._text.tag_delete("person")

        self._text.tag_config("place", background="yellow", foreground="black", font=("arial", "12", "bold"))
        self._text.tag_config("event",  background="green", foreground="black", font=("arial", "12", "bold"))
        self._text.tag_config("person", background="red", foreground="black", font=("arial", "12", "bold"))

    def updateAnnotations(self):   
        self.resetTags()

        docId = self._docs[self._docsList.curselection()[0]]
        records = db.execute("SELECT * from annotations where id_doc="+docId)

        for row in records:
            typeAnnotation = row[1]
            begin = row[2]
            end = row[3]
            self._text.tag_add(typeAnnotation, begin, end) 
    
    def createDocsTab(self):
        self._docsTab = ttk.Frame(self._tabs)
        self._docsTab.pack(fill=tk.BOTH, expand=True)

        self._tabs.add(self._docsTab, text="annotate")

        self._worksList = tk.Listbox(self._docsTab, exportselection=False, selectmode=tk.SINGLE, width = 20,font=("arial", 12)) 
        self._worksList.bind('<<ListboxSelect>>',self.selectWork)
        
        records = db.execute("SELECT * FROM works")
        for row in records:
            self._works.append(str(row[0]))
            self._worksList.insert(1,row[1])
        
        self._worksList.pack(side = tk.LEFT, fill = tk.Y)
     
        self._docsList = tk.Listbox(self._docsTab, exportselection=False, selectmode=tk.SINGLE, width = 20,font=("arial", 12))
        self._docsList.pack(side = tk.LEFT, fill = tk.Y)

        self._docsList.bind('<<ListboxSelect>>',self.selectDoc)

        # set scroll bar to list box for when entries exceed size of list box
        self._docsScroll = tk.Scrollbar(self._docsTab, orient = tk.VERTICAL)
        self._docsScroll.config(command = self._docsList.yview)
        self._docsScroll.pack(side = tk.LEFT, fill = tk.Y)
        self._docsList.config(yscroll= self._docsScroll.set)     
        
    def selectType(self, text, v):
        self._typeSelected = text

    def createCiteFrame(self):

        self._texts = tk.Frame(self._docsTab)
        self._texts.pack(fill=tk.BOTH, expand=True)
   
        self._textFrame = tk.Frame(self._texts)
        self._textFrame.pack(fill=tk.BOTH, expand=True)
        self._text = tk.Text(self._textFrame, font=("arial","12"))
        self._text.pack(fill=tk.BOTH, expand=True)
        self._text.bind("<ButtonRelease-1>", self.mouseUp)
        self._text.config(wrap=tk.WORD)
        self._text.config(state=tk.DISABLED)

        self.resetTags()
        self._citedTextFrame = tk.Frame(self._texts)
        self._citedTextFrame.pack(fill=tk.X, expand=True, pady=5)
        
        self._citedText = tk.Text(self._citedTextFrame, font=("arial","12","italic"))
        self._citedText.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # options for the new annotation
        self._options = tk.Frame(self._texts, relief=tk.RAISED, borderwidth=1)
        self._options.pack(side=tk.RIGHT, fill=tk.Y)
    
        # type of annotation
        annotTypes = [("place", 1, "yellow"), ("event", 2, "green"), ("person", 3, "red") ]

        varType = tk.IntVar()
        # first selection before any click
        varType.set(annotTypes[0][1])
        self._typeSelected = annotTypes[0][0]

        for name, idName,color in annotTypes:
            tk.Radiobutton(self._options, text=name, bg=color, variable=varType, value=idName, command=lambda t=name, v=varType: self.selectType(t, v)).pack(side=tk.LEFT)
            
        # ok button
        self._annotate = tk.Button(self._options, text ="annotate",command=self.addAnnotation)
        self._annotate.pack(side=tk.RIGHT, padx=5, pady=5)
        self._annotate.config(state=tk.DISABLED)

    def createPersonAnnotation(self, idPerson):
        # insert annotation
        sql = 'INSERT INTO annotations (type,begin,end,id_doc) VALUES (?,?,?,?)'

        docId = self._docs[self._docsList.curselection()[0]]
        values = (self._typeSelected, str(self._rangeSelected[0]), str(self._rangeSelected[1]), docId)
        db.execute(sql, values)
        dbConnection.commit()
        
        # get annotation id 
        records = db.execute("SELECT last_insert_rowid()")
        idAnnot = records.fetchone()[0]
        
        # insert person-annotation ids
        sql = 'INSERT INTO annotationPerson (id_annotation,id_person) VALUES (?,?)'
        values = (idAnnot, idPerson)
        db.execute(sql, values)
        dbConnection.commit()


        self.updateAnnotations()

    def run(self):
        self._window.mainloop()


def main():

    ui = UI()
    ui.run();

if __name__ == "__main__":
    main()

