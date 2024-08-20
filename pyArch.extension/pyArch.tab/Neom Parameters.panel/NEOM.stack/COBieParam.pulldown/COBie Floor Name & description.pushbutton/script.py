"""This Addin will fill the value of parameters COBie floor name and COBie floor description.Kindly note that COBie floor description of Level should be filled befor running this addin"""
from Autodesk.Revit.DB import *
from pyrevit import forms
doc = __revit__.ActiveUIDocument.Document

#This function will add value to the parameter for instance of the element. If not found will find the type and the value to the parameter of the type.

def UpdateParameterValue(elements, value, param_name='NEOM_Target_LOD'):
    updated_count = 0
    t = Transaction(doc, "Update Parameter Value")
    t.Start()
    try:
        for element in elements:
            parameter = element.LookupParameter(param_name)
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


#Get elements:
E=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).WhereElementIsNotElementType().ToElements()
E1=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()
E2=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Planting).WhereElementIsNotElementType().ToElements()
E3=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Parking).WhereElementIsNotElementType().ToElements()
E4=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Entourage).WhereElementIsNotElementType().ToElements()
E5=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_SpecialityEquipment).WhereElementIsNotElementType().ToElements()
E6=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()
E7=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_LightingFixtures).WhereElementIsNotElementType().ToElements()
E8=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_MedicalEquipment).WhereElementIsNotElementType().ToElements()
E9=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PlumbingFixtures).WhereElementIsNotElementType().ToElements()
E10=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Site).WhereElementIsNotElementType().ToElements()
        
E11=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()

#Get a single list:
EC=[E,E1,E2,E3,E4,E5,E6,E7,E8,E9,E10]#list of lists

def Appendlist(y):#will return single list of elements
   EC1=[]
   for i in EC:
       for j in i:
           EC1.append(j)
   return EC1

EC2=Appendlist(EC)#list of elements

def CheckParam(elements, param_name='NEOM_Operations_Class'):#Filter not operationally significant elements
    ENOS=[]
    for element in elements:
        parameter = element.LookupParameter(param_name)
        if parameter!=None:
            if parameter.AsValueString()=='Operationally significant' or parameter.AsValueString()=='Maintainable':
                print('hi')
                ENOS.append(element)

        elif parameter==None:
            k=element.GetTypeId()
            ElementType=doc.GetElement(k)
            parameter_1=ElementType.LookupParameter(param_name)
            if parameter_1!=None:
                if parameter_1.AsValueString()=='Operationally significant' or parameter_1.AsValueString()=='Maintainable':
                    ENOS.append(element)
        else:
            print('Parameter does not exist or is not editable')
            
    return ENOS

ENOS1=CheckParam(EC2)#Not operationally significant elements-list

for i in E11:
    ENOS1.append(i)#list including rooms

print('Total elements filtered',len(ENOS1))

for i in ENOS1:
    print i.IsValidObject
    Value1=i.LookupParameter('Level').AsValueString()
    print(Value1)
    a=[]
    a.append(i)
    UpdateParameterValue(a, Value1, param_name='COBie.Floor.Name')
    Value0=i.LevelId
    ele=doc.GetElement(Value0)
    print(Value0,ele)
    if ele!=None:
        Value2=ele.LookupParameter('COBie.Floor.Description').AsValueString()
        UpdateParameterValue(a, Value2, param_name='COBie.Floor.Description')
    if ele==None:
        Value01=i.LookupParameter('Schedule Level').AsElementId()
        ele=doc.GetElement(Value01)
        Value2=ele.LookupParameter('COBie.Floor.Description').AsValueString()
        UpdateParameterValue(a, Value2, param_name='COBie.Floor.Description')

    