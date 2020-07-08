#!/usr/bin/python3

import tkinter as tk
import sqlite3 as sq 

from tkinter import ttk

import dbAnnot
from dbAnnot import *

class PersonAnnotation(tk.Toplevel):

    # signal to main window that it needs to update citations
    signalAdd = None
    _ids = {}

    def __init__(self, parent, quote):
        super().__init__(parent)
        self.geometry("400x600+300+300")
        self.title("person annotation")

        frame1 = tk.Frame(self, padx=5, pady=5, relief=tk.RAISED, borderwidth=1)
        frame1.pack(fill=tk.X)
        lbl1 = tk.Label(frame1, text="Search", width=6)
        lbl1.pack(side=tk.LEFT, padx=5, pady=5)
    
        self._search= tk.StringVar()
        self._search.trace_add("write", self.filterList)
        entry1 = tk.Entry(frame1, textvariable=self._search)
        entry1.pack(fill=tk.X, padx=5, side=tk.LEFT, expand=True)
        addButton = tk.Button(frame1, text ="add new", command=self.addNew)
        addButton.pack(side=tk.RIGHT, padx=5, pady=5)
 
        frame2 = tk.Frame(self, padx=5, pady=5, borderwidth=1, relief=tk.RAISED)
        frame2.pack(fill=tk.BOTH, expand=True)
        lbl2 = tk.Label(frame2, text="Entries", width=6)
        lbl2.pack(side=tk.LEFT, anchor=tk.N, padx=5, pady=5)
        self._entries = tk.Listbox(frame2, exportselection=False, selectmode=tk.SINGLE, width = 20, font=("arial", 12))
        self._entries.pack(fill = tk.BOTH, expand=True)
        self._entries.bind('<<ListboxSelect>>',self.select)
       
        frame3 = tk.Frame(self, padx=5, pady=5, relief=tk.RAISED, borderwidth=1)
        frame3.pack(fill=tk.X)
        cancelButton = tk.Button(frame3, text ="cancel",command=self.cancel)
        cancelButton.pack(side=tk.RIGHT)
        # change for okButton
        self._ok = tk.Button(frame3, text ="ok",command=self.ok)
        self._ok.pack(side=tk.RIGHT)
        self._ok.config(state=tk.DISABLED)

        self._search.set(quote)

    def addNew(self):
        self._add = PersonInsertion(self, self._search.get())
        self._add.signalAdded = self.added

    def added(self):
        self._search.set("")

    # XRC TODO fer-ho com amb places basat en select, és molt més ràpid
    def updateEntries(self, txt):
        records = dbAnnot.db.execute("SELECT * from persons")

        self._entries.delete(0, tk.END)
        # dictionary with name as key and id as value
        self._ids = {}

        for row in records:
            personName = row[1]
            # filter if search is being used
            if txt!="" and personName.lower().find(txt.lower())==-1:
                continue
                
            self._ids[personName] = row[0]
            self._entries.insert(1,personName)

    def select(self, event):
        index = self._entries.curselection()[0]
        self._ok.config(state=tk.NORMAL)

    def cancel(self):
        self.destroy();

    def filterList(self, var, index, mode):
        self.updateEntries(self._search.get())
    
    def ok(self): 
        # get person id
        index = self._entries.curselection()[0]
        idPerson = self._ids[self._entries.get(index)]
        self.signalAdd(idPerson)

        # close window
        self.destroy()

class PersonInsertion(tk.Toplevel):   

    # signal/callback to update person entries
    signalAdded = None
    
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
        self._personName.trace_add("write", self.enableEntry)
        
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
        cancelButton = tk.Button(frame3, text ="cancel",command=self.cancel)
        cancelButton.pack(side=tk.RIGHT)
        self._okButton = tk.Button(frame3, text ="ok",command=self.ok)
        self._okButton.pack(side=tk.RIGHT)
        self._okButton.config(state=tk.DISABLED)

        # check state of ok button
        self.enableEntry(0,0,0)

    def cancel(self):
        self.destroy();

    def ok(self):
        sql = 'INSERT INTO persons (name, info) VALUES (?,?)'
        values = (self._personName.get(), self._personInfo.get(1.0,tk.END))
        dbAnnot.db.execute(sql, values)
        dbAnnot.conn.commit()

        self.signalAdded()
        self.destroy()

    def enableEntry(self, var, index, mode):
        if self._personName.get()=="":
            self._okButton.config(state=tk.DISABLED)
        else:
            self._okButton.config(state=tk.NORMAL)


