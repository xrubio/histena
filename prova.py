#!/usr/bin/python3

import tkinter as tk
import sqlite3 as sq 

from tkinter import ttk

def sort_list():
    """
    function to sort listbox items case insensitive
    """
    temp_list = list(docsList.get(0, tk.END))
    temp_list.sort(key=str.lower)
    # delete contents of present listbox
    docsList.delete(1, tk.END)
    # load listbox with sorted data
    for item in temp_list:
        docsList.insert(tk.END, item)

def selectWork(ext):
    index = str(1+worksList.curselection()[0])
    docsList.delete(1, tk.END)
    records = c.execute("SELECT * from docs where id_work="+index)
    for row in records:
        print("row:",row[3])
        docsList.insert(1, row[3])

def selectDoc(evt):
    #value = docsList.get(docsList.curselection())
    # starts at 0
    index = str(1+docsList.curselection()[0])
#    value = int(docsList.get(tk.ANCHOR))
    records = c.execute("SELECT text from docs where ID="+index)
    text.delete("1.0", tk.END)
    for row in records:
        text.insert(tk.INSERT, row[0])

con = sq.connect("annot.db") #dB browser for sqlite needed
c = con.cursor() #SQLite command, to connect to db so 'execute' method can be called


#filename = "data/00_original.txt"


window = tk.Tk()
window.title("text annotation")   

tabs = ttk.Notebook(window)    
#configfile = tk.Text(root, width=800, height=600)
#configfile.pack()
    
#with open(filename, 'r') as f:
#    configfile.insert(tk.INSERT, f.read())

#T.insert(tk.END, "Just a text Widget\nin two lines\n")
#tk.mainloop()


docsTab = ttk.Frame(tabs)
worksTab = ttk.Frame(tabs)

tabs.add(docsTab, text="docs")
tabs.add(worksTab, text="add sources")
#docsTab.place(x=10,y=10)

worksList = tk.Listbox(docsTab, selectmode=tk.SINGLE, width = 20,font=("arial", 12)) 
worksList.pack(side = tk.LEFT, fill = tk.Y)
worksList.bind('<<ListboxSelect>>',selectWork)

records = c.execute("SELECT * FROM works")

for row in records:
    worksList.insert(1,row[1])
 

docsList = tk.Listbox(docsTab, selectmode=tk.SINGLE, width = 20,font=("arial", 12))
docsList.place(x=100, y=10)

docsList.pack(side = tk.LEFT, fill = tk.Y)
docsList.bind('<<ListboxSelect>>',selectDoc)

docsScroll = tk.Scrollbar(docsTab, orient = tk.VERTICAL) # set scroll bar to list box for when entries exceed size of list box
docsScroll.config(command = docsList.yview)
docsScroll.pack(side = tk.LEFT, fill = tk.Y)
docsList.config(yscroll= docsScroll.set)     

"""
records = c.execute("SELECT * FROM docs")

for row in records:
    docsList.insert(1,row[3])
    print("title",row[2])
    print("date",row[3])
    print("text",row[4])
"""

text = tk.Text(docsTab, width=150)
text.place(x=500, y=10)    

tabs.pack(expand=1, fill="both")
window.mainloop()


