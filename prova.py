#!/usr/bin/python3

import tkinter as tk
import sqlite3 as sq 

from tkinter import ttk

from Tooltip import *

import dbAnnot
from dbAnnot import *
from PersonUI import *
from PlaceUI import *
from KeywordUI import *

class UI(object):

    _works = []
    _docs = []
    _typeSelected = "no selection"
    _annotations = []

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
        records = dbAnnot.db.execute("SELECT * from docs where id_work="+workId)
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

        records = dbAnnot.db.execute("SELECT text from docs where ID="+docId)
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
        selectedText = self._text.get(*self._rangeSelected)
        if self._typeSelected=="person":
            self._annotPerson = PersonAnnotation(self._window, selectedText)
            self._annotPerson .signalAdd = self.addPerson
            return
        if self._typeSelected=="place":
            self._annotPlace = PlaceAnnotation(self._window, selectedText)
            self._annotPlace.signalAdd = self.addPlace
            return
        if self._typeSelected=="keyword":
            self._annotKeyword = KeywordAnnotation(self._window, selectedText)
            self._annotKeyword.signalAdd = self.addKeyword
            return


    def resetTags(self):       
        self._annotations = []

        # clear tags before adding them
        self._text.tag_delete("keyword")
        self._text.tag_delete("place")
        self._text.tag_delete("person")

        self._text.tag_config("keyword",  background="green", foreground="black", font=("arial", "12", "bold"))
        self._text.tag_config("place", background="yellow", foreground="black", font=("arial", "12", "bold"))
        self._text.tag_config("person", background="red", foreground="black", font=("arial", "12", "bold"))

    def updateAnnotations(self):   
        self.resetTags()

        docId = self._docs[self._docsList.curselection()[0]]
        records = dbAnnot.db.execute("SELECT * from annotations where id_doc="+docId)

        for row in records:
            typeAnnotation = row[1]
            begin = row[2]
            end = row[3]
            self._text.tag_add(typeAnnotation, begin, end)
            self._annotations.append(row)

    
    def createDocsTab(self):
        self._docsTab = ttk.Frame(self._tabs)
        self._docsTab.pack(fill=tk.BOTH, expand=True)

        self._tabs.add(self._docsTab, text="annotate")

        self._worksList = tk.Listbox(self._docsTab, exportselection=False, selectmode=tk.SINGLE, width = 20,font=("arial", 12)) 
        self._worksList.bind('<<ListboxSelect>>',self.selectWork)
        
        records = dbAnnot.db.execute("SELECT * FROM works")
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

    def getKeywordTooltip(self, idAnnotation):
        # get idKeyword linked to this idAnnotation
        records = dbAnnot.db.execute("SELECT id_keyword from annotationPerson where id_annotation="+str(idAnnotation))
        idKeyword = records.fetchone()[0]

        # get person info
        records = dbAnnot.db.execute("SELECT * from keywords where id="+str(idKeyword))
        keyword = records.fetchone()

        # build text
        return "keyword: "+keyword[1]+"\n\ninfo: "+keyword[2]

    def getPersonTooltip(self, idAnnotation):
        # get idPerson linked to this idAnnotation
        records = dbAnnot.db.execute("SELECT id_person from annotationPerson where id_annotation="+str(idAnnotation))
        idPerson = records.fetchone()[0]

        # get person info
        records = dbAnnot.db.execute("SELECT * from persons where id="+str(idPerson))
        person = records.fetchone()

        #print("id annotation:",idAnnotation,"id person:",idPerson,"name:",person[1])
        # build text
        return "person: "+person[1]+"\n\ninfo: "+person[2]

    def getPlaceTooltip(self, idAnnotation):
        # get idPlace linked to this idAnnotation
        records = dbAnnot.db.execute("SELECT id_place from annotationPlace where id_annotation="+str(idAnnotation))
        idPlace = records.fetchone()[0]

        # get person info
        records = dbAnnot.db.execute("SELECT * from places where id="+str(idPlace))
        place = records.fetchone()

        #print("id annotation:",idAnnotation,"id person:",idPerson,"name:",person[1])
        # build text
        text = "place: "+place[2]+"\n\ninfo:"
        if place[1]==None:
            text += "(custom place)"
        # from geonames
        else:
            featureClass = place[6]
            featureCode = place[7]
            country = place[8]
            pos = str(place[4])+"/"+str(place[5])

            text+= " ("+country+")"
            if featureClass=="P":
                text += ", settlement"
            elif featureClass=="A":
                text += ", region"  
            # no SPOTS to avoid businesses               
            elif featureClass!="S":                
                text += ", class:"+featureClass+", code:"+featureCode
                
            text += " ["+pos+"]"        
        return text

    def setTooltipText(self):
        # get range index for mouse
        #x = self._text.winfo_pointerx() - self._text.winfo_rootx()
        #y = self._text.winfo_pointery() - self._text.winfo_rooty()
        #index1 = self._text.index("@"+str(x)+","+str(y))
        #index2 = 
        #hoverText = self._text.get( "@"+str(x+20)+","+str(y))
        #hoverText = self._text.get("1.0",tk.END)
        currentIndex = self._text.index(tk.CURRENT)
        for annotation in self._annotations:
            if currentIndex>=annotation[2] and currentIndex<=annotation[3]:
                if annotation[1]=="person":
                    return self.getPersonTooltip(annotation[0])
                elif annotation[1]=="place":
                    return self.getPlaceTooltip(annotation[0])

        return "" 

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
        tooltipText = Tooltip(self._text, wraplength=200)
        tooltipText.signalSetTooltipText = self.setTooltipText

        self.resetTags()
        self._citedTextFrame = tk.Frame(self._texts)
        self._citedTextFrame.pack(fill=tk.X, expand=True, pady=5)
        
        self._citedText = tk.Text(self._citedTextFrame, font=("arial","12","italic"))
        self._citedText.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # options for the new annotation
        self._options = tk.Frame(self._texts, relief=tk.RAISED, borderwidth=1)
        self._options.pack(side=tk.RIGHT, fill=tk.Y)
    
        # type of annotation
        annotTypes = [("keyword", 2, "green"), ("place", 1, "yellow"), ("person", 3, "red") ]

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

    def addKeyword(self, idKeyword):
        # insert annotation
        sql = 'INSERT INTO annotations (type,begin,end,id_doc) VALUES (?,?,?,?)'

        docId = self._docs[self._docsList.curselection()[0]]
        values = (self._typeSelected, str(self._rangeSelected[0]), str(self._rangeSelected[1]), docId)
        dbAnnot.db.execute(sql, values)
        dbAnnot.conn.commit()
        
        # get annotation id 
        records = dbAnnot.db.execute("SELECT last_insert_rowid()")
        idAnnot = records.fetchone()[0]
        
        # insert person-annotation ids
        sql = 'INSERT INTO annotationKeyword (id_annotation,id_keyword) VALUES (?,?)'
        values = (idAnnot, idKeyword)
        dbAnnot.db.execute(sql, values)
        dbAnnot.conn.commit()

        self.updateAnnotations()

    def addPerson(self, idPerson):
        # insert annotation
        sql = 'INSERT INTO annotations (type,begin,end,id_doc) VALUES (?,?,?,?)'

        docId = self._docs[self._docsList.curselection()[0]]
        values = (self._typeSelected, str(self._rangeSelected[0]), str(self._rangeSelected[1]), docId)
        dbAnnot.db.execute(sql, values)
        dbAnnot.conn.commit()
        
        # get annotation id 
        records = dbAnnot.db.execute("SELECT last_insert_rowid()")
        idAnnot = records.fetchone()[0]
        
        # insert person-annotation ids
        sql = 'INSERT INTO annotationPerson (id_annotation,id_person) VALUES (?,?)'
        values = (idAnnot, idPerson)
        dbAnnot.db.execute(sql, values)
        dbAnnot.conn.commit()

        self.updateAnnotations()

    def addPlace(self, idPlace):
        # insert annotation
        sql = 'INSERT INTO annotations (type,begin,end,id_doc) VALUES (?,?,?,?)'

        docId = self._docs[self._docsList.curselection()[0]]
        values = (self._typeSelected, str(self._rangeSelected[0]), str(self._rangeSelected[1]), docId)
        dbAnnot.db.execute(sql, values)
        dbAnnot.conn.commit()
        
        # get annotation id 
        records = dbAnnot.db.execute("SELECT last_insert_rowid()")
        idAnnot = records.fetchone()[0]
        
        # insert place-annotation ids
        sql = 'INSERT INTO annotationPlace (id_annotation,id_place) VALUES (?,?)'
        values = (idAnnot, idPlace)
        dbAnnot.db.execute(sql, values)
        dbAnnot.conn.commit()

        self.updateAnnotations()

    def run(self):
        self._window.mainloop()


def main():

    dbAnnot.init()

    ui = UI()
    ui.run();

if __name__ == "__main__":
    main()

