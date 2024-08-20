"""Value of parameter room function should be filled before using the plugin. Otherwise it will fill value N/A"""
from Autodesk.Revit.DB import *
from pyrevit import forms
doc = __revit__.ActiveUIDocument.Document

#This function will add value to the parameter for instance of the element. If not found will find the type and the value to the parameter of the type.

def UpdateParameterValue(elements, value, param_name):
    updated_count = 0
    t = Transaction(doc, "Update Parameter Value")
    t.Start()
    try:
        for element in elements:
            parameter = element.LookupParameter(param_name)
            print(parameter)
            if parameter!=None:
                parameter.Set(value)
                updated_count += 1
                print(updated_count)
            elif parameter==None:
                k=element.GetTypeId()
                ElementType=doc.GetElement(k)
                parameter_1=ElementType.LookupParameter(param_name)
                parameter_1.Set(value)
                updated_count += 1
                print(updated_count)
            else:
                print('Parameter does not exist or is not editable')
        print('No. of types whose value updated are', updated_count)
    except Exception as e:
        print('There was an error. Some of the values are not updated. Check if the parameter is assigned to the category or not')
        print(e)
    t.Commit()

E1=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()

def ReturnParamValue(elements, param_name='Room_Function'):#Get the Room_Function of elements.
    RF=[]
    for element in elements:
        parameter = element.LookupParameter(param_name)
        if parameter.AsValueString()!=None:
            RF.append(parameter.AsValueString())
        elif parameter.AsValueString()==None:
            RF.append('N/A')
    return RF


RF1=ReturnParamValue(E1)#Get the Room_Function of elements as list.

for i in range(len(RF1)):#Fill vales to 'NEOM_RoomSpace_Type'
    if RF1[i]!='N/A':
        print(E1[i], RF1[i])
        E2=[E1[i]]#To solve iteration over non-sequence of type
        UpdateParameterValue(E2, RF1[i], 'NEOM_RoomSpace_Type')
    elif RF1[i]=='N/A':
        E2=[E1[i]]#To solve iteration over non-sequence of type
        UpdateParameterValue(E2, RF1[i], 'NEOM_RoomSpace_Type')
