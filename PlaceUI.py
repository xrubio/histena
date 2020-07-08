#!/usr/bin/python3

import tkinter as tk
import sqlite3 as sq 

from tkinter import ttk

import dbAnnot
from dbAnnot import *

class PlaceInsertion (tk.Toplevel):   

    # signal/callback to update person entries
    signalAdded = None
        
    _old_value = ''

    def validate_float(self, var):
        new_value = var.get()
        try:
            new_value == '' or float(new_value)
            self._old_value = new_value
        except:
            var.set(self._old_value)    

    def __init__(self, parent, initialText):
        super().__init__(parent)
        self.geometry("400x300+800+300")
        self.title("add custom place")

        frame1 = tk.Frame(self)
        frame1.pack(fill=tk.X)

        lbl1 = tk.Label(frame1, text="Name", width=10)
        lbl1.pack(side=tk.LEFT, padx=5, pady=5)
        
        self._placeName = tk.StringVar()
        self._placeName.set(initialText)
        self._placeName.trace_add("write", self.enableEntry)
        
        entry1 = tk.Entry(frame1, textvariable=self._placeName)
        entry1.pack(fill=tk.X, padx=5, expand=True)

        frame2 = tk.Frame(self)
        frame2.pack(fill=tk.X)

        lbl2 = tk.Label(frame2, text="latitude", width=10)
        lbl2.pack(side=tk.LEFT, padx=5, pady=5)

        self._lat = tk.StringVar()
        self._lat.trace('w', lambda nm, idx, mode, var=self._lat: self.validate_float(var))
        entry2 = tk.Entry(frame2, textvariable=self._lat)
        entry2.pack(fill=tk.X, padx=5, expand=True)

        frame3 = tk.Frame(self)
        frame3.pack(fill=tk.X)

        lbl3 = tk.Label(frame3, text="longitude", width=10)
        lbl3.pack(side=tk.LEFT, padx=5, pady=5)

        self._long = tk.StringVar()
        self._long.trace('w', lambda nm, idx, mode, var=self._long: self.validate_float(var))
        entry3 = tk.Entry(frame3, textvariable=self._long)
        entry3.pack(fill=tk.X, padx=5, expand=True)

        frame4 = tk.Frame(self, padx=5, pady=5, borderwidth=1)
        frame4.pack(fill=tk.X, expand=True)
        cancelButton = tk.Button(frame4, text ="cancel",command=self.cancel)
        cancelButton.pack(side=tk.RIGHT)
        self._okButton = tk.Button(frame4, text ="ok",command=self.ok)
        self._okButton.pack(side=tk.RIGHT)
        self._okButton.config(state=tk.DISABLED)

        # check state of ok button
        self.enableEntry(0,0,0)

    def cancel(self):
        self.destroy();

    def ok(self):
        sql = 'INSERT INTO places (name, lat, long) VALUES (?,?,?)'
        values = (self._placeName.get(), float(self._lat.get()), float(self._long.get()))
        dbAnnot.db.execute(sql, values)
        dbAnnot.conn.commit()

        self.signalAdded()
        self.destroy()

    def enableEntry(self, var, index, mode):
        if self._placeName.get()=="":
            self._okButton.config(state=tk.DISABLED)
        else:
            self._okButton.config(state=tk.NORMAL)


class PlaceAnnotation(tk.Toplevel):

    # signal to main window that it needs to update citations
    signalAdd = None
    _ids = {}

    def __init__(self, parent, quote):
        super().__init__(parent)
        self.geometry("400x600+300+300")
        self.title("place annotation")

        frame1 = tk.Frame(self, padx=5, pady=5, relief=tk.RAISED, borderwidth=1)
        frame1.pack(fill=tk.X)
        lbl1 = tk.Label(frame1, text="Search", width=6)
        lbl1.pack(side=tk.LEFT, padx=5, pady=5)
    
        self._search = tk.StringVar()
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
        self._entries .pack(fill = tk.BOTH, expand=True)
        self._entries.bind('<<ListboxSelect>>',self.select)
       
        frame3 = tk.Frame(self, padx=5, pady=5, relief=tk.RAISED, borderwidth=1)
        frame3.pack(fill=tk.X)
        cancel = tk.Button(frame3, text ="cancel",command=self.cancel)
        cancel.pack(side=tk.RIGHT)
        # change for okButton
        self._ok = tk.Button(frame3, text ="ok",command=self.ok)
        self._ok.pack(side=tk.RIGHT)
        self._ok .config(state=tk.DISABLED)
              
        self._search.set(quote)

    def addNew(self):
        self._add = PlaceInsertion(self, self._search.get())
        self._add.signalAdded = self.added

    def added(self):
        self.filterList(0,0,0)

    def updateEntries(self, txt):        
        
        self._entries.delete(0, tk.END)
        # dictionary with name as key and id as value
        self._ids = {}
        records = None

        if len(txt)<3:
            return

        records = dbAnnot.db.execute("SELECT * from places where name LIKE '%"+txt+"%' OR alternate LIKE '%"+txt+"%'")

        numRows = 0
        for row in records:
            name = row[2]
            geoId = row[1]

            rowText = name
            # if the places com from geonames
            if geoId!=None:
                featureClass = row[6]
                featureCode = row[7]
                country = row[8]
                pos = str(row[4])+"/"+str(row[5])

                rowText += " ("+country+")"
                if featureClass=="P":
                    rowText += ", settlement"
                elif featureClass=="A":
                    rowText += ", region"  
                # no SPOTS to avoid businesses               
                elif featureClass!="S":                
                    rowText += ", class:"+featureClass+", code:"+featureCode
                else:
                    continue 
                rowText += " ["+pos+"]"

            else:
                rowText += " (custom place)"
                
            self._ids[rowText] = row[0]
            self._entries.insert(1,rowText)
            #print("result",numRows,"name:",name,"alternate:",alternate,"id:",row[0],"geoid:",row[1],"country:",row[8],"class/code:",row[6],"/",row[7],"pos:",row[4],"/",row[5])
            numRows += 1

        print("query for place",txt,"returned:",numRows,"results")

    def select(self, event):
        index = self._entries.curselection()[0]
        print("index:",index,"id:",self._ids[self._entries.get(index)])
        self._ok.config(state=tk.NORMAL)

    def cancel(self):
        self.destroy();
 
    def filterList(self, var, index, mode):
        self.updateEntries(self._search.get())
    
    def ok(self): 
        # get person id
        index = self._entries.curselection()[0]
        idPlace = self._ids[self._entries.get(index)]
        self.signalAdd(idPlace)

        # close window
        self.destroy()


