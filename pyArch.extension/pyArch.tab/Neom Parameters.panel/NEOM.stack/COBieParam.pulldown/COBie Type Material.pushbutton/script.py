"""This addin will fill the value of parameter COBie type material"""
from Autodesk.Revit.DB import *

doc = __revit__.ActiveUIDocument.Document

#This function will add value to the parameter for instance of the element. If not found will find the type and the value to the parameter of the type.


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

ENOS1=CheckParam(EC2)#Maintainable and operationally significant elements-list

print('Total elements filtered',len(ENOS1))

t = Transaction(doc, "Update Parameter Value")
t.Start()

for i in ENOS1:
    k=i.GetTypeId()
    j=doc.GetElement(k)
    MID=j.GetMaterialIds(False)
    for x in MID:
        MN=doc.GetElement(x)
        parameter = j.LookupParameter('COBie.Type.Material')
        if parameter!=None:
            parameter.Set(MN.Name)
        print(MID,len(MID),MN.Name)
        print(MN.Name)

t.Commit()
  