#!/usr/bin/python3

import tkinter as tk
import sqlite3 as sq 

def sort_list():
    """
    function to sort listbox items case insensitive
    """
    temp_list = list(Lb.get(0, tk.END))
    temp_list.sort(key=str.lower)
    # delete contents of present listbox
    Lb.delete(0, tk.END)
    # load listbox with sorted data
    for item in temp_list:
        Lb.insert(tk.END, item)

def CurSelet(evt):
    #value = Lb.get(Lb.curselection())
    # starts at 0
    index = str(1+Lb.curselection()[0])
#    value = int(Lb.get(tk.ANCHOR))
    records = c.execute("SELECT text from docs where ID="+index)
    text.delete("1.0", tk.END)
    for row in records:
        text.insert(tk.INSERT, row[0])

con = sq.connect("annot.db") #dB browser for sqlite needed
c = con.cursor() #SQLite command, to connect to db so 'execute' method can be called

records = c.execute("SELECT * FROM docs")

#filename = "data/00_original.txt"


window = tk.Tk()
    
#configfile = tk.Text(root, width=800, height=600)
#configfile.pack()
    
#with open(filename, 'r') as f:
#    configfile.insert(tk.INSERT, f.read())

#T.insert(tk.END, "Just a text Widget\nin two lines\n")
#tk.mainloop()



frame = tk.Frame(window)
frame.place(x=10,y=10)

Lb = tk.Listbox(frame, selectmode=tk.SINGLE, height = 20, width = 25,font=("arial", 12)) 
Lb.pack(side = tk.LEFT, fill = tk.Y)
Lb.bind('<<ListboxSelect>>',CurSelet)

scroll = tk.Scrollbar(frame, orient = tk.VERTICAL) # set scrollbar to list box for when entries exceed size of list box
scroll.config(command = Lb.yview)
scroll.pack(side = tk.RIGHT, fill = tk.Y)
Lb.config(yscrollcommand = scroll.set)     

for row in records:
    Lb.insert(1,row[3])
    print("title",row[2])
    print("date",row[3])
    print("text",row[4])

text = tk.Text(window, width=200, height=50)
text.place(x=100, y=10)    

window.mainloop()


