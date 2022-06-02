#!/usr/bin/env python
"""
    Module implementing the TableModel class that manages data for
    it's associated TableCanvas.

    Created Oct 2008
    Copyright (C) Damien Farrell

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 2
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

from __future__ import absolute_import, division, print_function
from .TableFormula import Formula
from . import Filtering
from types import *
from collections import OrderedDict
import operator
import string, types, copy
import pickle, os, sys, csv


# added by me **********************************************************************************************************
#from tkinter import *
#from tkinter.ttk import *
import _tkinter
import sys
# from _typeshed import StrOrBytesPath
from enum import Enum
from tkinter.constants import *
# from tkinter.font import _FontDescription
from types import TracebackType
from typing import Any, Callable, Generic, Mapping, Optional, Protocol, Sequence, TypeVar, Union, overload
# from typing_extensions import Literal, TypedDict
# **********************************************************************************************************************


from tkinter import *
from tkinter.ttk import *

class TableModel(object):
    """A base model for managing the data in a TableCanvas class"""

    keywords = {'columnnames':'columnNames', 'columntypes':'columntypes',
               'columnlabels':'columnlabels', 'columnorder':'columnOrder',
               'colors':'colors'}

    def __init__(self, newdict=None, rows=None, columns=None):
        """Constructor"""
        #print("TableModel__init__")
        self.initialiseFields()
        self.setupModel(newdict, rows, columns)
        return


    def setupModel(self, newdict, rows=None, columns=None):
        """Create table model"""
        #print("setupModel")

        if newdict != None:
            self.data = copy.deepcopy(newdict)
            for k in self.keywords:
                if k in self.data:
                    self.__dict__[self.keywords[k]] = self.data[k]
                    del self.data[k]
            #read in the record list order
            if 'reclist' in self.data:
                temp = self.data['reclist']
                del self.data['reclist']
                self.reclist = temp
            else:
                self.reclist = self.data.keys()
        else:
            #just make a new empty model
            self.createEmptyModel()
        if not set(self.reclist) == set(self.data.keys()):
            print ('reclist does not match data keys')
        #restore last column order
        if hasattr(self, 'columnOrder') and self.columnOrder != None:
            self.columnNames=[]
            for i in self.columnOrder.keys():
                self.columnNames.append(self.columnOrder[i])
                i=i+1
        self.defaulttypes = ['text', 'number']
        #setup default display for column types
        self.default_display = {'text' : 'showstring',
                                'number' : 'numtostring'}

        #set default sort order as first col
        if len(self.columnNames)>0:
            self.sortkey = self.columnNames[0]
        else:
            self.sortkey = None
        #add rows and cols if they are given in the constructor
        if newdict == None:
            if rows != None:
                self.autoAddRows(rows)
            if columns != None:
                self.autoAddColumns(columns)
        self.filteredrecs = None
        return

    def initialiseFields(self):
        """Create base fields, some of which are not saved"""
        #print("initialiseFields")
        self.data = None    # holds the table dict
        self.colors = {}    # holds cell colors
        self.colors['fg']={}
        self.colors['bg']={}
        #default types
        self.defaulttypes = ['text', 'number']
        #list of editable column types
        self.editable={}
        self.nodisplay = []
        self.columnwidths={}  #used to store col widths, not held in saved data
        return

    def createEmptyModel(self):
        """Create the basic empty model dict"""
        #print("createEmptyModel")
        self.data = {}
        # Define the starting column names and locations in the table.
        self.columnNames = []
        self.columntypes = {}
        self.columnOrder = None
        #record column labels for use in a table header
        self.columnlabels={}
        for colname in self.columnNames:
            self.columnlabels[colname]=colname
        self.reclist = list(self.data.keys())
        return

    def importCSV(self, filename, sep=','):
        """Import table data from a comma separated file."""
        #print("importCSV")
        if not os.path.isfile(filename) or not os.path.exists(filename):
            print ('no such file')
            return None

        #takes first row as field names
        dictreader = csv.DictReader(open(filename, "r"), delimiter=sep)
        dictdata = {}
        count=0
        for rec in dictreader:
            dictdata[count]=rec
            count=count+1
        self.importDict(dictdata)
        return

    def importDict(self, newdata):
        """Try to create a table model from a dict of the form
           {{'rec1': {'col1': 3, 'col2': 2}, ..}"""
        #print("importDict")
        #get cols from sub data keys
        colnames = []
        for k in newdata:
            fields = newdata[k].keys()
            for f in fields:
                if not f in colnames:
                    colnames.append(f)
        for c in colnames:
            self.addColumn(c)
        #add the data
        self.data.update(newdata)
        self.reclist = list(self.data.keys())
        return

    def getDefaultTypes(self):
        """Get possible field types for this table model"""
        #print("getDefaultTypes")
        return self.defaulttypes

    def getData(self):
        """Return the current data for saving"""
        #print("getData")
        data = copy.deepcopy(self.data)
        data['colors'] = self.colors
        data['columnnames'] = self.columnNames
        #we keep original record order
        data['reclist'] = self.reclist
        #record current col order
        data['columnorder']={}
        i=0
        for name in self.columnNames:
            data['columnorder'][i] = name
            i=i+1
        data['columntypes'] = self.columntypes
        data['columnlabels'] = self.columnlabels
        return data

    def getAllCells(self):
        """Return a dict of the form rowname: list of cell contents
          Useful for a simple table export for example"""
        #print("getAllCells")
        records={}
        for row in range(len(self.reclist)):
            recdata=[]
            for col in range(len(self.columnNames)):
                recdata.append(self.getValueAt(row,col))
            records[row]=recdata
        return records

    def getColCells(self, colIndex):
        """Get the viewable contents of a col into a list"""
        #print("getColCells")
        collist = []
        if self.getColumnType(colIndex) == 'Link':
            return ['xxxxxx']
        else:
            for row in range(len(self.reclist)):
                v = self.getValueAt(row, colIndex)
                collist.append(v)
        return collist

    def getlongestEntry(self, columnIndex):
        """Get the longest cell entry in the col"""
        #print("getlongestEntry")
        collist = self.getColCells(columnIndex)
        maxw=5
        for c in collist:
            try:
                w = len(str(c))
            except UnicodeEncodeError:
                pass
            if w > maxw:
                maxw = w
        #print 'longest width', maxw
        return maxw

    def getRecordAtRow(self, rowIndex):
        """Get the entire record at the specifed row."""
        #print("getRecordAtRow")
        name = self.getRecName(rowIndex)
        record = self.data[name]
        return record

    def getCellRecord(self, rowIndex, columnIndex):
        """Get the data held in this row and column"""
        #print("getCellRecord")
        value = None
        colname = self.getColumnName(columnIndex)
        coltype = self.columntypes[colname]
        name = self.getRecName(rowIndex)
        #print self.data[name]
        if colname in self.data[name]:
            celldata=self.data[name][colname]
        else:
            celldata=None
        return celldata

    def deleteCellRecord(self, rowIndex, columnIndex):
        """Remove the cell data at this row/column"""
        #print("deleteCellRecord")
        colname = self.getColumnName(columnIndex)
        coltype = self.columntypes[colname]
        name = self.getRecName(rowIndex)
        if colname in self.data[name]:
            del self.data[name][colname]
        return

    def getRecName(self, rowIndex):
        """Get record name from row number"""
        #print("getRecName")
        if len(self.reclist)==0:
            return None
        if self.filteredrecs != None:
            name = self.filteredrecs[rowIndex]
        else:
            name = self.reclist[rowIndex]
        return name

    def setRecName(self, newname, rowIndex):
        """Set the record name to another value - requires re-setting in all
           dicts that this rec is referenced"""
        #print("setRecName")
        if len(self.reclist)==0:
            return None
        currname = self.getRecName(rowIndex)
        self.reclist[rowIndex] = newname
        temp = copy.deepcopy(self.data[currname])
        self.data[newname] = temp
        #self.data[newname]['Name'] = newname
        del self.data[currname]
        for key in ['bg', 'fg']:
            if currname in self.colors[key]:
                temp = copy.deepcopy(self.colors[key][currname])
                self.colors[key][newname] = temp
                del self.colors[key][currname]
        print ('renamed')
        #would also need to resolve all refs to this rec in formulas here!

        return

    def getRecordAttributeAtColumn(self, rowIndex=None, columnIndex=None,
                                        recName=None, columnName=None):
         """Get the attribute of the record at the specified column index.
            This determines what will be displayed in the cell"""
         #print("getRecordAttributeAtColumn")
         value = None
         if columnName != None and recName != None:
             if columnName not in self.data[recName]:
                 return ''
             cell = self.data[recName][columnName]
         else:
             cell = self.getCellRecord(rowIndex, columnIndex)
             columnName = self.getColumnName(columnIndex)
         if cell == None:
             cell=''
         # Set the value based on the data record field
         coltype = self.columntypes[columnName]
         if Formula.isFormula(cell) == True:
             value = self.doFormula(cell)
             return value

         if not type(cell) is dict:
             if coltype == 'text' or coltype == 'Text':
                 value = cell
             elif coltype == 'number':
                 value = str(cell)
             else:
                 value = 'other'
         if value==None:
             value=''
         return value

    def getRecordIndex(self, recname):
        #print("getRecordIndex")
        rowIndex = int(self.reclist.index(recname))
        return rowIndex

    def setSortOrder(self, columnIndex=None, columnName=None, reverse=0):
        """Changes the order that records are sorted in, which will
           be reflected in the table upon redrawing"""
        #print("setSortOrder")
        if columnName != None and columnName in self.columnNames:
            self.sortkey = columnName
        elif columnIndex != None:
            self.sortkey = self.getColumnName(columnIndex)
        else:
            return
        self.reclist = list(self.createSortMap(self.reclist, self.sortkey, reverse))
        if self.filteredrecs != None:
            self.filteredrecs = self.createSortMap(self.filteredrecs, self.sortkey, reverse)
        return

    def createSortMap(self, names, sortkey, reverse=0):
        """Create a sort mapping for given list"""
        #print("createSortMap")
        recdata = []
        for rec in names:
            recdata.append(self.getRecordAttributeAtColumn(recName=rec, columnName=sortkey))
        #try create list of floats if col has numbers only
        try:
            recdata = self.toFloats(recdata)
        except:
            pass
        smap = zip(names, recdata)
        #sort the mapping by the second key
        smap = sorted(smap, key=operator.itemgetter(1), reverse=reverse)
        #now sort the main reclist by the mapping order
        sortmap = map(operator.itemgetter(0), smap)
        return sortmap

    def toFloats(self, l):
        #print("toFloats")
        x=[]
        for i in l:
            if i == '':
                x.append(0.0)
            else:
                x.append(float(i))
        return x

    '''def getSortIndex(self):
        """Return the current sort order index"""
        if self.sortcolumnIndex:
            return self.sortcolumnIndex
        else:
            return 0'''

    def moveColumn(self, oldcolumnIndex, newcolumnIndex):
        """Changes the order of columns"""
        #print("moveColumn")
        self.oldnames = self.columnNames
        self.columnNames=[]

        #write out a new column names list - tedious
        moved = self.oldnames[oldcolumnIndex]
        del self.oldnames[oldcolumnIndex]
        #print self.oldnames
        i=0
        for c in self.oldnames:
            if i==newcolumnIndex:
                self.columnNames.append(moved)
            self.columnNames.append(c)
            i=i+1
        #if new col is at end just append
        if moved not in self.columnNames:
            self.columnNames.append(moved)
        return

    def getNextKey(self):
        """Return the next numeric key in the dict"""
        #print("getNextKey")
        num = len(self.reclist)+1
        return num

    def addRow(self, key=None, **kwargs):
        """Add a row"""
        #print("addRow")
        if key == '':
            return
        if key==None:
            key = self.getNextKey()
        if key in self.data or key in self.reclist:
            print ('name already present!!')
            return
        self.data[key]={}
        for k in kwargs:
            if not k in self.columnNames:
                self.addColumn(k)
            self.data[key][k] = str(kwargs[k])
        self.reclist.append(key)
        return key


    # added by me ******************************************************************************************************
    '''
    def addRowOfCheckButtons(self, **kwargs):
        """Add a row"""
        #print("addRowOfCheckButtons")

        key = 0
        self.data[0]={}
        for k in kwargs:
            if not k in self.columnNames:
                self.addColumn(k)
            self.data[key][k] = str(kwargs[k])
        self.reclist.append(key)
        return key
    '''
    # ******************************************************************************************************************


    def deleteRow(self, rowIndex=None, key=None, update=True):
        """Delete a row"""
        #print("deleteRow")
        if key == None or not key in self.reclist:
            key = self.getRecName(rowIndex)
        del self.data[key]
        if update==True:
            self.reclist.remove(key)
        return

    def deleteRows(self, rowlist=None):
        """Delete multiple or all rows"""
        #print("deleteRows")
        if rowlist == None:
            rowlist = range(len(self.reclist))
        names = [self.getRecName(i) for i in rowlist]
        for name in names:
            self.deleteRow(key=name, update=True)
        return

    def addColumn(self, colname=None, coltype=None):
        """Add a column"""
        #print("addColumn")
        index = self.getColumnCount()+ 1
        if colname == None:
            colname=str(index)
        if colname in self.columnNames:
            #print 'name is present!'
            return
        self.columnNames.append(colname)
        self.columnlabels[colname] = colname
        # added by me ************************************************************************************************************
        '''
        root = Tk()
        CheckVar1 = IntVar()
        CheckVar2 = IntVar()
        C1 = Checkbutton(root, text="Music", variable=CheckVar1, onvalue=1, offvalue=0, width=20)
        C2 = Checkbutton(root, text="Video", variable=CheckVar2, onvalue=1, offvalue=0, width=20)
        #C1.pack()
        #C2.pack()
        btn = Button(text="Hello")
        canvas = Canvas()
        canvas.create_window()
        '''
        # ************************************************************************************************************************

        if coltype == None:
            self.columntypes[colname]='text'
        else:
            self.columntypes[colname]=coltype
        return



    # added by me ******************************************************************************************************
    @classmethod
    def setEventAsUnobservable(self, column_name=None):
        """Set the event as Unobservable - can be used in a table header"""
        #print("setEventAsUnobservable")

        if column_name == None:
            n = messagebox.askyesno("Setting",
                                    "Unobservable Event?",
                                    parent=self.parentframe)
            if n:
                # global dictcolObservableEvents

                current_col_index = self.getSelectedColumn()
                current_col_name = self.model.getColumnLabel(current_col_index)
                my_globals.dictcolObservableEvents[str(current_col_name)] = 0
                # print(current_col_index)
                # print(str(self.model.getColumnLabel(current_col_index)))
                #print("Observable events:", my_globals.dictcolObservableEvents)
        else:
            my_globals.dictcolObservableEvents[str(column_name)] = 0

    # ******************************************************************************************************************

    # added by me ******************************************************************************************************
    @classmethod
    def setEventAsObservable(self, column_name=None):
        """Set the event as Observable - can be used in a table header"""
        #print("setEventAsObservable")

        if column_name == None:

            n = messagebox.askyesno("Setting",
                                    "Observable Event?",
                                    parent=self.parentframe)
            if n:
                # global dictcolObservableEvents
                current_col_index = self.getSelectedColumn()
                current_col_name = self.model.getColumnLabel(current_col_index)
                my_globals.dictcolObservableEvents[str(current_col_name)] = 1
                # print(current_col_index)
                # print(str(self.model.getColumnLabel(current_col_index)))
                #print("Observable events:", my_globals.dictcolObservableEvents)
        else:
            my_globals.dictcolObservableEvents[str(column_name)] = 1
            # print(current_col_index)
            # print(str(self.model.getColumnLabel(current_col_index)))
            #print("Observable events:", my_globals.dictcolObservableEvents)

    # ******************************************************************************************************************

    # added by me ******************************************************************************************************
    @classmethod
    def setEventAsUncontrollable(self, column_name=None):
        """Set the event as Uncontrollable - can be used in a table header"""
        #print("setEventAsUncontrollable")

        if column_name == None:

            n = messagebox.askyesno("Setting",
                                    "Uncontrollable Event?",
                                    parent=self.parentframe)
            if n:
                # global dictcolControllableEvents
                current_col_index = self.getSelectedColumn()
                current_col_name = self.model.getColumnLabel(current_col_index)
                my_globals.dictcolControllableEvents[str(current_col_name)] = 0
                # print(current_col_index)
                # print(str(self.model.getColumnLabel(current_col_index)))
                #print("Controllable events:", my_globals.dictcolControllableEvents)
        else:
            my_globals.dictcolControllableEvents[str(column_name)] = 0

    # ******************************************************************************************************************

    # added by me ******************************************************************************************************
    @classmethod
    def setEventAsControllable(self, column_name=None):
        """Set the event as Controllable - can be used in a table header"""
        #print("setEventAsControllable")

        if column_name == None:

            n = messagebox.askyesno("Setting",
                                    "Controllable Event?",
                                    parent=self.parentframe)
            if n:
                # global dictcolControllableEvents
                current_col_index = self.getSelectedColumn()
                current_col_name = self.model.getColumnLabel(current_col_index)
                my_globals.dictcolControllableEvents[str(current_col_name)] = 1
                # print(current_col_index)
                # print(str(self.model.getColumnLabel(current_col_index)))
                #print("Controllable events:", my_globals.dictcolControllableEvents)
        else:
            my_globals.dictcolControllableEvents[str(column_name)] = 1

    # ******************************************************************************************************************

    # added by me ******************************************************************************************************
    @classmethod
    def setEventAsFaulty(self, column_name=None):
        """Set the event as Faulty - can be used in a table header"""
        #print("setEventAsFaulty")

        if column_name == None:
            n = messagebox.askyesno("Setting",
                                    "Faulty Event?",
                                    parent=self.parentframe)
            if n:
                # global dictcolFaultyEvents

                current_col_index = self.getSelectedColumn()
                current_col_name = self.model.getColumnLabel(current_col_index)
                my_globals.dictcolFaultyEvents[str(current_col_name)] = 1
                # print(current_col_index)
                # print(str(self.model.getColumnLabel(current_col_index)))
                #print("Faulty events:", my_globals.dictcolFaultyEvents)
        else:
            my_globals.dictcolFaultyEvents[str(column_name)] = 1

    # ******************************************************************************************************************

    # added by me ******************************************************************************************************
    @classmethod
    def setEventAsUnfaulty(self, column_name=None):
        """Set the event as Unfaulty - can be used in a table header"""
        #print("setEventAsUnfaulty")

        if column_name == None:

            n = messagebox.askyesno("Setting",
                                    "Observable Event?",
                                    parent=self.parentframe)
            if n:
                # global dictcolFaultyEvents
                current_col_index = self.getSelectedColumn()
                current_col_name = self.model.getColumnLabel(current_col_index)
                my_globals.dictcolFaultyEvents[str(current_col_name)] = 0
                # print(current_col_index)
                # print(str(self.model.getColumnLabel(current_col_index)))
                #print("Faulty events:", my_globals.dictcolFaultyEvents)
        else:
            my_globals.dictcolFaultyEvents[str(column_name)] = 0
            # print(current_col_index)
            # print(str(self.model.getColumnLabel(current_col_index)))
            #print("Faulty events:", my_globals.dictcolFaultyEvents)

    # ******************************************************************************************************************

    # added by me *******************************************************************************************************
    @classmethod
    def fromTableToJson(self):
        """Convert the current table content into a Json file"""
        #print("fromTableToJson")
        # Algorithm of conversion of the current table to a json file
        n = messagebox.askyesno("Convert",
                                "Convert table to json file?",
                                parent=self.parentframe)
        if n:
            #print("columnlabels:", self.model.columnlabels.values())
            # rows start from 0, columns start from 0

            json_dict = {"X": {}, "E": {}, "delta": {}}
            dict_X = {}
            dict_E = {}
            dict_delta = {}
            current_state = ""
            iter_ascii_delta = 65  # decimal value of the ASCII character 'A'
            num_rows = self.model.getRowCount()
            num_cols = len(self.model.columnlabels)
            for iter_row in range(num_rows):
                for iter_col in range(num_cols):
                    #print("iter_row,iter_col:" + str(iter_row) + "," + str(iter_col))
                    if self.model.getCellRecord(iter_row, iter_col) != None:
                        current_cell = self.model.getCellRecord(iter_row, iter_col)
                        #print("current_cell: ", current_cell)
                        if iter_col == 0:
                            if current_cell[0] and current_cell[0] != '_':
                                if current_cell.endswith("_i_f_p") or current_cell.endswith(
                                        "_i_p_f") or current_cell.endswith("_f_i_p") or current_cell.endswith(
                                    "_f_p_i") or current_cell.endswith("_p_f_i") or current_cell.endswith(
                                    "_p_i_f"):
                                    string_lenght = len(current_cell)
                                    substring_to_remove = current_cell[-6:]
                                    current_state = current_cell.replace(str(substring_to_remove), "")
                                    current_state.replace(" ", "")
                                    dict_X.update(
                                        {str(current_state): {"isInit": "1", "isFinal": "1", "isProhibited": "1"}})
                                elif current_cell.endswith("_i_f"):
                                    current_state = current_cell.replace("_i_f", "")
                                    current_state.replace(" ", "")
                                    dict_X.update(
                                        {str(current_state): {"isInit": "1", "isFinal": "1", "isProhibited": "0"}})
                                elif current_cell.endswith("_f_i"):
                                    current_state = current_cell.replace("_f_i", "")
                                    current_state.replace(" ", "")
                                    dict_X.update(
                                        {str(current_state): {"isInit": "1", "isFinal": "1", "isProhibited": "0"}})
                                elif current_cell.endswith("_i_p"):
                                    current_state = current_cell.replace("_i_p", "")
                                    current_state.replace(" ", "")
                                    dict_X.update(
                                        {str(current_state): {"isInit": "1", "isFinal": "0", "isProhibited": "1"}})
                                elif current_cell.endswith("_p_i"):
                                    current_state = current_cell.replace("_p_i", "")
                                    current_state.replace(" ", "")
                                    dict_X.update(
                                        {str(current_state): {"isInit": "1", "isFinal": "0", "isProhibited": "1"}})
                                elif current_cell.endswith("_p_f"):
                                    current_state = current_cell.replace("_p_f", "")
                                    current_state.replace(" ", "")
                                    dict_X.update(
                                        {str(current_state): {"isInit": "0", "isFinal": "1", "isProhibited": "1"}})
                                elif current_cell.endswith("_f_p"):
                                    current_state = current_cell.replace("_f_p", "")
                                    current_state.replace(" ", "")
                                    dict_X.update(
                                        {str(current_state): {"isInit": "0", "isFinal": "1", "isProhibited": "1"}})
                                elif current_cell.endswith("_i"):
                                    current_state = current_cell.replace("_i", "")
                                    current_state.replace(" ", "")
                                    dict_X.update(
                                        {str(current_state): {"isInit": "1", "isFinal": "0", "isProhibited": "0"}})
                                elif current_cell.endswith("_f"):
                                    current_state = current_cell.replace("_f", "")
                                    current_state.replace(" ", "")
                                    dict_X.update(
                                        {str(current_state): {"isInit": "0", "isFinal": "1", "isProhibited": "0"}})
                                elif current_cell.endswith("_p"):
                                    current_state = current_cell.replace("_p", "")
                                    current_state.replace(" ", "")
                                    dict_X.update(
                                        {str(current_state): {"isInit": "0", "isFinal": "0", "isProhibited": "1"}})
                                else:
                                    current_state = current_cell
                                    current_state.replace(" ", "")
                                    dict_X.update(
                                        {str(current_state): {"isInit": "0", "isFinal": "0", "isProhibited": "0"}})
                            else:
                                #print("cell(" + str(iter_row) + "," + str(iter_col) + " is not a valid name for a state.\nPlease insert a valid one.")
                                pass
                        else:
                            current_delta_ends = current_cell.split("-")
                            flag_end_while = 0
                            while (flag_end_while == 0):
                                if '' in current_delta_ends:
                                    current_delta_ends.remove('')
                                else:
                                    flag_end_while = 1

                            for i in range(len(current_delta_ends)):
                                dict_delta.update({str(chr(iter_ascii_delta)): {"start": str(current_state),
                                                                                "name": str(self.model.getColumnLabel(
                                                                                    iter_col)),
                                                                                "ends": str(current_delta_ends[i])}})
                                #print("dict_delta", dict_delta)
                                current_key_event = str(self.model.getColumnLabel(iter_col))
                                dict_E.update({current_key_event: {
                                    "isObs": str(my_globals.dictcolObservableEvents[current_key_event]),
                                    "isContr": str(my_globals.dictcolControllableEvents[current_key_event]),
                                    "isFaulty": str(my_globals.dictcolFaultyEvents[current_key_event])}})
                                iter_ascii_delta += 1

                            print(current_delta_ends)
                    else:
                        pass

            json_dict["X"] = dict_X
            json_dict["delta"] = dict_delta
            json_dict["E"] = dict_E
            print(json_dict)

            with open("sample.json", "w") as outfile:
                # json_object = json.dumps(json_dict, outfile, indent=4 )
                json.dump(json_dict, outfile, indent=4)

            # #print("cella 1,1", self.model.getCellRecord(1,1))

            outfile.close()
            #print("Tabella convertita in un json file")

        return


    # *****************************************************************************************************************





    def deleteColumn(self, columnIndex):
        """delete a column"""
        #print("deleteColumn")
        colname = self.getColumnName(columnIndex)
        self.columnNames.remove(colname)
        del self.columnlabels[colname]
        del self.columntypes[colname]
        #remove this field from every record
        for recname in self.reclist:
            if colname in self.data[recname]:
                del self.data[recname][colname]
        if self.sortkey != None:
            currIndex = self.getColumnIndex(self.sortkey)
            if columnIndex == currIndex:
                self.setSortOrder(0)
        #print 'column deleted'
        #print 'new cols:', self.columnNames
        return

    def deleteColumns(self, cols=None):
        """Remove all cols or list provided"""
        #print("deleteColumns")
        if cols == None:
            cols = self.columnNames
        if self.getColumnCount() == 0:
            return
        for col in cols:
            self.deleteColumn(col)
        return

    def autoAddRows(self, numrows=None):
        """Automatically add x number of records"""
        #print("autoAddRows")
        rows = self.getRowCount()
        ints = [i for i in self.reclist if isinstance(i, int)]
        if len(ints)>0:
            start = max(ints)+1
        else:
            start = 0
        #we don't use addRow as it's too slow
        keys = range(start,start+numrows)
        #make sure no keys are present already
        keys = list(set(keys)-set(self.reclist))
        newdata = {}
        for k in keys:
            newdata[k] = {}
        self.data.update(newdata)
        self.reclist.extend(newdata.keys())
        return keys

    def autoAddColumns(self, numcols=None):
        """Automatically add x number of cols"""
        #print("autoAddColumns")
        #alphabet = string.lowercase[:26]
        alphabet = string.ascii_lowercase
        currcols=self.getColumnCount()
        #find where to start
        start = currcols + 1
        end = currcols + numcols + 1
        new = []
        for n in range(start, end):
            new.append(str(n))
        #check if any of these colnames present
        common = set(new) & set(self.columnNames)
        extra = len(common)
        end = end + extra
        for x in range(start, end):
            # ORIGINAL *************************************************************************************************
            # self.addColumn(str(x))
            # **********************************************************************************************************

            # added by me **********************************************************************************************
            if x == start:
                self.addColumn("State")
            else:
                self.addColumn("event" + str(x-1))
            # **********************************************************************************************************
        return


    def relabel_Column(self, columnIndex, newname):
        """Change the column label - can be used in a table header"""
        #print("relabel_Column")
        colname = self.getColumnName(columnIndex)
        self.columnlabels[colname]=newname
        return

    def getColumnType(self, columnIndex):
        """Get the column type"""
        #print("getColumnType")
        colname = self.getColumnName(columnIndex)
        coltype = self.columntypes[colname]
        return coltype

    def getColumnCount(self):
         """Returns the number of columns in the data model."""
         #print("getColumnCount")
         return len(self.columnNames)

    def getColumnName(self, columnIndex):
         """Returns the name of the given column by columnIndex."""
         #print("getColumnName")
         return self.columnNames[columnIndex]

    def getColumnLabel(self, columnIndex):
        """Returns the label for this column"""
        #print("getColumnLabel")
        colname = self.getColumnName(columnIndex)
        return self.columnlabels[colname]

    def getColumnIndex(self, columnName):
        """Returns the column index for this column"""
        #print("getColumnIndex")
        colindex = self.columnNames.index(columnName)
        return colindex

    def getColumnData(self, columnIndex=None, columnName=None, filters=None):
        """Return the data in a list for this col,
            filters is a tuple of the form (key,value,operator,bool)"""
        #print("getColumnData")
        if columnIndex != None and columnIndex < len(self.columnNames):
            columnName = self.getColumnName(columnIndex)
        names = Filtering.doFiltering(searchfunc=self.filterBy,
                                         filters=filters)
        coldata = [self.data[n][columnName] for n in names]
        return coldata

    def getColumns(self, colnames, filters=None, allowempty=True):
        """Get column data for multiple cols, with given filter options,
            filterby: list of tuples of the form (key,value,operator,bool)
            allowempty: boolean if false means rows with empty vals for any
            required fields are not returned
            returns: lists of column data"""
        #print("getColumns")
        def evaluate(l):
            for i in l:
                if i == '' or i == None:
                    return False
            return True
        coldata=[]
        for c in colnames:
            vals = self.getColumnData(columnName=c, filters=filters)
            coldata.append(vals)
        if allowempty == False:
            result = [i for i in zip(*coldata) if evaluate(i) == True]
            coldata = zip(*result)
        return coldata

    def getDict(self, colnames, filters=None):
        """Get the model data as a dict for given columns with filter options"""
        #print("getDict")
        data={}
        names = self.reclist
        cols = self.getColumns(colnames, filters)
        coldata = zip(*cols)
        for name,cdata in zip(names, coldata):
            data[name] = dict(zip(colnames,cdata))
        return data

    def filterBy(self, filtercol, value, op='contains', userecnames=False,
                     progresscallback=None):
        """The searching function that we apply to the model data.
           This is used in Filtering.doFiltering to find the required recs
           according to column, value and an operator"""
        #print("filterBy")

        funcs = Filtering.operatornames
        floatops = ['=','>','<']
        func = funcs[op]
        data = self.data
        #coltype = self.columntypes[filtercol]
        names=[]
        for rec in self.reclist:
            if filtercol in data[rec]:
                #try to do float comparisons if required
                if op in floatops:
                    try:
                        #print float(data[rec][filtercol])
                        item = float(data[rec][filtercol])
                        v = float(value)
                        if func(v, item) == True:
                            names.append(rec)
                        continue
                    except:
                        pass
                if filtercol == 'name' and userecnames == True:
                    item = rec
                else:
                    item = str(data[rec][filtercol])
                if func(value, item):
                    names.append(rec)
        return names

    def getRowCount(self):
         """Returns the number of rows in the table model."""
         #print("getRowCount")
         return len(self.reclist)

    def getValueAt(self, rowIndex, columnIndex):
         """Returns the cell value at location specified
             by columnIndex and rowIndex."""
         #print("getValueAt")
         value = self.getRecordAttributeAtColumn(rowIndex, columnIndex)
         return value

    def setValueAt(self, value, rowIndex, columnIndex):
        """Changed the dictionary when cell is updated by user"""
        #print("setValueAt")
        name = self.getRecName(rowIndex)
        colname = self.getColumnName(columnIndex)
        coltype = self.columntypes[colname]
        if coltype == 'number':
            try:
                if value == '': #need this to allow deletion of values
                    self.data[name][colname] = ''
                else:
                    self.data[name][colname] = float(value)
            except:
                pass
        else:
            self.data[name][colname] = value
        return

    def setFormulaAt(self, f, rowIndex, columnIndex):
        """Set a formula at cell given"""
        #print("setFormulaAt")
        name = self.getRecName(rowIndex)
        colname = self.getColumnName(columnIndex)
        coltype = self.columntypes[colname]
        rec = {}
        rec['formula'] = f
        self.data[name][colname] = rec
        return

    def getColorAt(self, rowIndex, columnIndex, key='bg'):
        """Return color of that record field for the table"""
        #print("getColorAt")
        name = self.getRecName(rowIndex)
        colname = self.getColumnName(columnIndex)
        if name in self.colors[key] and colname in self.colors[key][name]:
            return self.colors[key][name][colname]
        else:
            return None

    def setColorAt(self, rowIndex, columnIndex, color, key='bg'):
        """Set color"""
        #print("setColorAt")
        name = self.getRecName(rowIndex)
        colname = self.getColumnName(columnIndex)
        if not name in self.colors[key]:
            self.colors[key][name] = {}
        self.colors[key][name][colname] = str(color)
        return

    def resetcolors(self):
        """Remove all color formatting"""
        #print("resetcolors")
        self.colors={}
        self.colors['fg']={}
        self.colors['bg']={}
        return

    def getRecColNames(self, rowIndex, ColIndex):
        """Returns the rec and col name as a tuple"""
        #print("getRecColNames")
        recname = self.getRecName(rowIndex)
        colname = self.getColumnName(ColIndex)
        return (recname, colname)

    def getRecAtRow(self, recname, colname, offset=1, dim='y'):
        """Get the record name at a specified offset in the current
           table from the record given, by using the current sort order"""
        #print("getRecAtRow")
        thisrow = self.getRecordIndex(recname)
        thiscol = self.getColumnIndex(colname)
        #table goto next row
        if dim == 'y':
            nrow = thisrow + offset
            ncol = thiscol
        else:
            nrow = thisrow
            ncol = thiscol + offset

        newrecname, newcolname = self.getRecColNames(nrow, ncol)
        print ('recname, colname', recname, colname)
        print ('thisrow, col', thisrow, thiscol)
        return newrecname, newcolname

    def appendtoFormula(self, formula, rowIndex, colIndex):
        """Add the input cell to the formula"""
        #print("appendtoFormula")
        cellRec = getRecColNames(rowIndex, colIndex)
        formula.append(cellRec)
        return

    def doFormula(self, cellformula):
        """Evaluate the formula for a cell and return the result"""
        #print("doFormula")
        value = Formula.doFormula(cellformula, self.data)
        return value

    def copyFormula(self, cellval, row, col, offset=1, dim='y'):
        """Copy a formula down or across, using the provided offset"""
        #print("copyFormula")
        import re
        frmla = Formula.getFormula(cellval)
        #print 'formula', frmla

        newcells=[]
        cells, ops = Formula.readExpression(frmla)

        for c in cells:
            print (c)
            if type(c) is not ListType:
                nc = c
            else:
                recname = c[0]
                colname = c[1]
                nc = list(self.getRecAtRow(recname, colname, offset, dim=dim))
            newcells.append(nc)
        newformula = Formula.doExpression(newcells, ops, getvalues=False)
        return newformula

    def merge(self, model, key='name', fields=None):
        """Merge another table model with this one based on a key field,
           we only add records from the new model where the key is present
           in both models"""
        #print("merge")
        if fields == None: fields = model.columnNames
        for rec in self.reclist:
            if not key in self.data[rec]:
                continue
            for new in model.reclist:
                if not key in model.data[new]:
                    continue
                if self.data[rec][key] == model.data[new][key]:
                #if new == rec:
                    for f in fields:
                        if not f in model.data[rec]:
                            continue
                        if not f in self.columnNames:
                            self.addColumn(f)
                        self.data[rec][f] = model.data[rec][f]
        return

    def save(self, filename=None):
        """Save model to file"""
        #print("save")
        if filename == None:
            return
        data = self.getData()
        fd = open(filename,'wb')
        pickle.dump(data,fd)
        fd.close()
        return

    def load(self, filename):
        """Load model from pickle file"""
        #print("load")
        fd=open(filename,'rb')
        data = pickle.load(fd)
        self.setupModel(data)
        return

    def copy(self):
        """Return a copy of this model"""
        #print("copy")
        M = TableModel()
        data = self.getData()
        M.setupModel(data)
        return M



    '''
    # added by me ******************************************************************************************************

    class IntVar(Variable):
        """Value holder for integer variables."""
        _default = 0

        def __init__(self, master=None, value=None, name=None):
            """Construct an integer variable.

            MASTER can be given as master widget.
            VALUE is an optional value (defaults to 0)
            NAME is an optional Tcl name (defaults to PY_VARnum).

            If NAME matches an existing variable and VALUE is omitted
            then the existing value is retained.
            """
            Variable.__init__(self, master, value, name)
            self._tk = None

        def get(self):
            """Return the value of the variable as an integer."""
            value = self._tk.globalgetvar(self._name)
            try:
                return self._tk.getint(value)
            except (TypeError, TclError):
                return int(self._tk.getdouble(value))

    # ******************************************************************************************************************
    '''



    def __repr__(self):
        return 'Table Model with %s rows' %len(self.reclist)
