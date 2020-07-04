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



"""
records = c.execute("SELECT * FROM docs")

for row in records:
    docsList.insert(1,row[3])
    print("title",row[2])
    print("date",row[3])
    print("text",row[4])
"""

class UI(object):

    _works = []
    _docs = []
    _typeSelected = "no selection"

    # constructor
    def __init__(self, db):
        self._window = tk.Tk()

        self._window.title("text annotation")   
        self._window.geometry("1800x1000")
        self._tabs = ttk.Notebook(self._window)    

        self._dbConnection = sq.connect(db)
        self._db = self._dbConnection.cursor()

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
        records = self._db.execute("SELECT * from docs where id_work="+workId)
        for row in records:
            self._docs.append(str(row[0]))
            self._docsList.insert(1, row[3])
        self._docsList.pack(side = tk.LEFT, fill = tk.Y)

    def selectDoc(self, event):
        #value = docsList.get(docsList.curselection())
        # starts at 0
        self.clearAnnotation()
        docId = self._docs[self._docsList.curselection()[0]]
        # value = int(docsList.get(tk.ANCHOR))
        records = self._db.execute("SELECT text from docs where ID="+docId)
        self._text.config(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        for row in records:
            self._text.insert(tk.INSERT, row[0])
        self._text.config(state=tk.DISABLED)

        self.updateAnnotations()

    def mouseUp(self, event):
        ranges = self._text.tag_ranges(tk.SEL)
        self.clearAnnotation()
        if ranges:
            self._annotate.config(state=tk.NORMAL)
            self._citedText.insert(tk.INSERT, self._text.get(*ranges))

    def clearAnnotation(self):
        self._citedText.delete("1.0", tk.END)
        self._annotate.config(state=tk.DISABLED)

    def addAnnotation(self):
        sql = 'INSERT INTO annotations (type,begin,end,id_doc) VALUES (?,?,?,?)'
    
        ranges = self._text.tag_ranges(tk.SEL)
        docId = self._docs[self._docsList.curselection()[0]]

        values = (self._typeSelected, str(ranges[0]), str(ranges[1]), docId)
        self._db.execute(sql, values)
        self._dbConnection.commit()
        self.updateAnnotations()

    def updateAnnotations(self):
        
        docId = self._docs[self._docsList.curselection()[0]]
        records = self._db.execute("SELECT * from annotations where id_doc="+docId)
        for row in records:
            typeAnnotation = row[1]
            begin = row[2]
            end = row[3]
            self._text.tag_add(typeAnnotation, begin, end) 
    
    def createDocsTab(self):
        self._docsTab = ttk.Frame(self._tabs)
        self._docsTab.pack(fill=tk.BOTH, expand=True)

        self._tabs.add(self._docsTab, text="docs")

        self._worksList = tk.Listbox(self._docsTab, exportselection=False, selectmode=tk.SINGLE, width = 20,font=("arial", 12)) 
        self._worksList.bind('<<ListboxSelect>>',self.selectWork)
        
        records = self._db.execute("SELECT * FROM works")
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

        self._text.tag_config("place", background="yellow", foreground="black", font=("arial", "12", "bold"))
        self._text.tag_config("event",  background="green", foreground="black", font=("arial", "12", "bold"))
        self._text.tag_config("person", background="red", foreground="black", font=("arial", "12", "bold"))

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

    def run(self):
        self._window.mainloop()


def main():

    ui = UI("annot.db")
    ui.run();

if __name__ == "__main__":
    main()

