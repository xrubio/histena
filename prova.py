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

def prepareDB():
    con = sq.connect("annot.db") #dB browser for sqlite needed
    return con.cursor() #SQLite command, to connect to db so 'execute' method can be called

class UI:

    _works = []
    _docs = []

    # callbacks
    def selectWork(self, ext):
        self._docs = []
        # pick value at index of mouse click
        workId = self._works[self._worksList.curselection()[0]]
        self._docsList.delete(0, tk.END)
        records = self._db.execute("SELECT * from docs where id_work="+workId)
        for row in records:
            print("row:",row[3])
            self._docs.append(str(row[0]))
            self._docsList.insert(1, row[3])

    def selectDoc(self, evt):
        #value = docsList.get(docsList.curselection())
        # starts at 0
        docId = self._docs[self._docsList.curselection()[0]]
        # value = int(docsList.get(tk.ANCHOR))
        records = self._db.execute("SELECT text from docs where ID="+docId)
        self._text.delete("1.0", tk.END)
        for row in records:
            self._text.insert(tk.INSERT, row[0])

    # constructor
    def __init__(self, db):
        self._window = tk.Tk()

        self._window.title("text annotation")   
        self._window.geometry("1800x1000")
        self._tabs = ttk.Notebook(self._window)    

        self._db = db
        self.createDocsTab();
        
        self._worksTab = ttk.Frame(self._tabs)
        self._tabs.add(self._worksTab, text="add sources")

        self._tabs.pack(expand=1, fill="both")

    def createDocsTab(self):
        self._docsTab = ttk.Frame(self._tabs)
        self._tabs.add(self._docsTab, text="docs")

        self._worksList = tk.Listbox(self._docsTab, exportselection=False, selectmode=tk.SINGLE, width = 20,font=("arial", 12)) 
        self._worksList.pack(side = tk.LEFT, fill = tk.Y)
        self._worksList.bind('<<ListboxSelect>>',self.selectWork)

        records = self._db.execute("SELECT * FROM works")
        for row in records:
            self._works.append(str(row[0]))
            self._worksList.insert(1,row[1])
     
        self._docsList = tk.Listbox(self._docsTab, exportselection=False, selectmode=tk.SINGLE, width = 20,font=("arial", 12))
        self._docsList.place(x=100, y=10)

        self._docsList.pack(side = tk.LEFT, fill = tk.Y)
        self._docsList.bind('<<ListboxSelect>>',self.selectDoc)

        # set scroll bar to list box for when entries exceed size of list box
        self._docsScroll = tk.Scrollbar(self._docsTab, orient = tk.VERTICAL)
        self._docsScroll.config(command = self._docsList.yview)
        self._docsScroll.pack(side = tk.LEFT, fill = tk.Y)
        self._docsList.config(yscroll= self._docsScroll.set)     
        
        self._text = tk.Text(self._docsTab, width=150)
        self._text.place(x=500, y=10)    

    def run(self):
        self._window.mainloop()


def main():

    db = prepareDB()
    ui = UI(db)
    ui.run();

if __name__ == "__main__":
    main()

    # callbacks
"""        
        

"""


