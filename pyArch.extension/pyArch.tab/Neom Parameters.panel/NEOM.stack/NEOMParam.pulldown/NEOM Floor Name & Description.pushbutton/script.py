"""This tool will fill the value of parameters NEOM floor name and NEOM floor description for not operationally significant element"""
from Autodesk.Revit.DB import *
from pyrevit import forms
doc = __revit__.ActiveUIDocument.Document

def UpdateParameterValue(elements, value, param_name):
    updated_count = 0
    t = Transaction(doc, "Update Parameter Value")
    t.Start()
    try:
        for element in elements:
            parameter = element.LookupParameter(param_name)
            if parameter!=None:
                parameter.Set(value)
                updated_count += 1
            elif parameter==None:
                k=element.GetTypeId()
                ElementType=doc.GetElement(k)
                parameter_1=ElementType.LookupParameter(param_name)
                parameter_1.Set(value)
                updated_count += 1
            else:
                print('Parameter does not exist or is not editable')
        print('No. of types whose value updated are', updated_count)
    except Exception as e:
        print('There was an error. The command is not executed.')
        print(e)
    t.Commit()
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#NEOM Floor Name
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
E=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
E1=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_CurtainWallPanels).WhereElementIsNotElementType().ToElements()
E2=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_CurtainWallMullions).WhereElementIsNotElementType().ToElements()
E3=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Columns).WhereElementIsNotElementType().ToElements()
E4=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElements()
E5=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StairsRailing).WhereElementIsNotElementType().ToElements()
E6=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Ramps).WhereElementIsNotElementType().ToElements()
E7=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Roofs).WhereElementIsNotElementType().ToElements()
E8=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StairsRuns).WhereElementIsNotElementType().ToElements()
E9=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StairsLandings).WhereElementIsNotElementType().ToElements()
E10=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Stairs).WhereElementIsNotElementType().ToElements()
E11=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()
E12=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).WhereElementIsNotElementType().ToElements()
E13=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_SpecialityEquipment).WhereElementIsNotElementType().ToElements()
E14=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().ToElements()
E15=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Casework).WhereElementIsNotElementType().ToElements()
E16=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Ceilings).WhereElementIsNotElementType().ToElements()
E17=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Entourage).WhereElementIsNotElementType().ToElements()
E18=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Furniture).WhereElementIsNotElementType().ToElements()
E19=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()
E20=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Signage).WhereElementIsNotElementType().ToElements()
E21=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Site).WhereElementIsNotElementType().ToElements()

#E8 and E9 are excluded because they have no level values.
EC=[E,E1,E2,E3,E4,E5,E6,E7,E10,E11,E12,E13,E14,E15,E16,E17,E18,E19,E20,E21]#list of lists

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
            if parameter.AsValueString()=='Not operationally significant':
                ENOS.append(element)

        elif parameter==None:
            k=element.GetTypeId()
            ElementType=doc.GetElement(k)
            parameter_1=ElementType.LookupParameter(param_name)
            if parameter_1!=None:
                if parameter_1.AsValueString()=='Not operationally significant':
                    ENOS.append(element)
        else:
            print('Parameter does not exist or is not editable')
            
    return ENOS

ENOS1=CheckParam(EC2)#Not operationally significant elements-list

print('Total Not Operationally Significant Elements filtered',len(ENOS1))

for i in ENOS1:
    print (i.Name)
#    print i.IsValidObject
    Value1=i.LookupParameter('Level')
    if Value1==None:
        Value01=i.LookupParameter('Base Constraint')
        if Value01!=None:
            v01=Value01.AsValueString()
            print(v01)
            a=[]
            a.append(i)
            UpdateParameterValue(a, v01, param_name='NEOM_Floor_Name')
            vid=i.LevelId
            ele=doc.GetElement(vid)
            Ln=ele.LookupParameter('COBie.Floor.Description').AsValueString()
            UpdateParameterValue(a, Ln, param_name='NEOM_Floor_Description')
        elif Value01==None:
            Value02=i.LookupParameter('Base Level')
            v02=Value02.AsValueString()
            print(v02)
            a=[]
            a.append(i)
            UpdateParameterValue(a, v02, param_name='NEOM_Floor_Name')
            El=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
            for j in El:
                if i.LookupParameter('Base Level').AsValueString() == j.Name:
                    vid=j.Id
                    ele=doc.GetElement(vid)
                    if ele!=None:
                       Ln=ele.LookupParameter('COBie.Floor.Description').AsValueString()
                       UpdateParameterValue(a, Ln, param_name='NEOM_Floor_Description')

    elif Value1!=None:
        v1=Value1.AsValueString()
        print(v1)
        a=[]
        a.append(i)
        UpdateParameterValue(a, v1, param_name='NEOM_Floor_Name')
        vid=i.LevelId
        ele=doc.GetElement(vid)
        Ln=ele.LookupParameter('COBie.Floor.Description').AsValueString()
        UpdateParameterValue(a, Ln, param_name='NEOM_Floor_Description')