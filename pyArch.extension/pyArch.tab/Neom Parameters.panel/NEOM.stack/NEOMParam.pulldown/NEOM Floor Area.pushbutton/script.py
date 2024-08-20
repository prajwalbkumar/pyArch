"""Value of the parameter room function should be filled before using the plugin. Otherwise it will fill value N/A"""
from Autodesk.Revit.DB import *
from pyrevit import forms
doc = __revit__.ActiveUIDocument.Document

E1=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()

t = Transaction(doc, "Update Parameter Value")
t.Start()

for x in E1:
    ExistingAreaParameter = x.Parameter[BuiltInParameter.ROOM_AREA].AsValueString()
    NFAParameter=x.LookupParameter('NEOM_Floor_Area')
    print(ExistingAreaParameter)
    NFAParameter.SetValueString(ExistingAreaParameter)
    print(ExistingAreaParameter ,NFAParameter)

t.Commit()
