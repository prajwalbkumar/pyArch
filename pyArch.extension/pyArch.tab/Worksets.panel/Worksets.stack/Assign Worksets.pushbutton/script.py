# -*- coding: utf-8 -*-
'''Assign Worksets'''
__title__ = "Assign Worksets"
__author__ = "prakritisrimal"

from pyrevit import forms
from Autodesk.Revit.DB import *
doc=__revit__.ActiveUIDocument.Document

t = Transaction(doc, "Set Element Workset")
t.Start()
#Elements=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).WhereElementIsNotElementType()
E=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsNotElementType()
Ws = FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset).ToWorksets()

def CheckExisting(str):
   for i in Ws:
      if i.Name==str:
         return True
      else:
         pass

def RevitValue(str):
   for i in Ws:
      if i.Name==str:
         return i
         
Exw=[z.Name for z in Ws]
a=forms.SelectFromList.show(Exw,button_name='select the workset to which you want to move all the floors')         

try:
   for x in E:
      worksetParam = x.Parameter[BuiltInParameter.ELEM_PARTITION_PARAM]
      if CheckExisting(a):
         if worksetParam and not worksetParam.IsReadOnly:
            j=RevitValue(a)
            worksetParam.Set(j.Id.IntegerValue)
            print('Elements have been moved to workset',j.Name)
      else:
         print('Workset do not exist')
except:
   print('Task not completed. There was an error')
   t.Rollback()
t.Commit()