"""This addin will fill the value of parameter Neom target LOD"""
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
E2=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Furniture).WhereElementIsNotElementType().ToElements()
E3=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
E4=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_CurtainWallPanels).WhereElementIsNotElementType().ToElements()
E5=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_CurtainWallMullions).WhereElementIsNotElementType().ToElements()
E6=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Columns).WhereElementIsNotElementType().ToElements()
E7=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElements()
E8=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StairsRailing).WhereElementIsNotElementType().ToElements()
E9=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Ramps).WhereElementIsNotElementType().ToElements()
E10=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Roofs).WhereElementIsNotElementType().ToElements()
E11=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StairsRuns).WhereElementIsNotElementType().ToElements()
E12=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StairsLandings).WhereElementIsNotElementType().ToElements()
E13=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Stairs).WhereElementIsNotElementType().ToElements()
E14=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Parking).WhereElementIsNotElementType().ToElements()
E15=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_SpecialityEquipment).WhereElementIsNotElementType().ToElements()
E16=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Planting).WhereElementIsNotElementType().ToElements()
E17=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().ToElements()
E18=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Casework).WhereElementIsNotElementType().ToElements()
E19=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Ceilings).WhereElementIsNotElementType().ToElements()
E20=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Entourage).WhereElementIsNotElementType().ToElements()
E21=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Furniture).WhereElementIsNotElementType().ToElements()
E22=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()
E23=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_LightingFixtures).WhereElementIsNotElementType().ToElements()
E24=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_MedicalEquipment).WhereElementIsNotElementType().ToElements()
E25=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PlumbingFixtures).WhereElementIsNotElementType().ToElements()
E27=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Signage).WhereElementIsNotElementType().ToElements()
E26=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Site).WhereElementIsNotElementType().ToElements()

#Get a single list:
EC=[E,E1,E2,E3,E4,E5,E6,E7,E8,E9,E10,E11,E12,E13,E14,E15,E16,E17,E18,E19,E20,E21,E22,E23,E24,E25,E26,E27]#list of lists

def Appendlist(y):#will return single list of elements
   EC1=[]
   for i in EC:
       for j in i:
           EC1.append(j)
   return EC1

EC2=Appendlist(EC)


#Get stage of design from user.
ops=['Stage 3A(Concept Design): 100','Stage 3B(Developed Design): 200','Stage 3C(Detailed Design): 300','Stage 3D(Tender Design): 300', 'Exit']
a=forms.CommandSwitchWindow.show(ops, message='Select the stage of design')
print('Your selected option is:', a)
if a =='Stage 3A(Concept Design): 100':
    UpdateParameterValue(EC2, '100')

elif a=='Stage 3B(Developed Design): 200':
    UpdateParameterValue(EC2, '200')

elif a=='Stage 3C(Detailed Design): 300':
    UpdateParameterValue(EC2, '300')

elif a=='Stage 3D(Tender Design): 300':
    UpdateParameterValue(EC2, '300')

else:
   print('Parameters are not updated. Your selected option is Exit.')