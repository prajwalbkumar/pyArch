"""This plugin will fill the value of parameters COBie Type Name and COBie Component Name"""
from Autodesk.Revit.DB import *
doc = __revit__.ActiveUIDocument.Document
from pyrevit import script

output = script.get_output()

#This function will add value to the parameter for instance of the element. If not found will find the type and the value to the parameter of the type.

def UpdateParameterValue(elements, value, param_name):
    updated_count = 0
    t = Transaction(doc, "Update Parameter Value")
    t.Start()
    try:
        for element in elements:
            script.get_output().update_progress(elements.index(element), len(elements)-1)#Progress message.
            parameter = element.LookupParameter(param_name)
            if parameter!=None:
                parameter.Set(value)
                updated_count += 1
#                print(element.Name,values)
            elif parameter==None:
                k=element.GetTypeId()
                ElementType=doc.GetElement(k)
                parameter_1=ElementType.LookupParameter(param_name)
                parameter_1.Set(value)
                updated_count += 1
#                print(element.Name,updated_count)
            else:
                print('Parameter does not exist or is not editable')
        
        print("Value of Parameter: {} (ID: {},{}:{}) is updated to {}".format(param_name, output.linkify(element.Id),element.Category.Name,element.Name, value))

    except Exception as e:
        print('There was an error. Some of the values are not updated. Check if the parameter is assigned to the category or not')
        print(e)
    t.Commit()

def OtherParamValue(x):
    if x=='Windows':
        Description=['Lightdome', 'Fixed external window', 'Fixed internal window', 'Hung external window', 'Hung internal window', 'Opening as window', 'Revolving external window', 'Revolving internal window', 'Rolling shutter external window', 'Rolling shutter internal window', 'Skylight', 'Sliding external window', 'Sliding internal window']
        AssetSystemAbbreviation=['AR', 'AR', 'AR', 'AR', 'AR', 'n/a', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR']
        AssetSubSystemAbbreviation=['WN', 'WN', 'WN', 'WN', 'WN', 'n/a', 'WN', 'WN', 'WN', 'WN', 'WN', 'WN', 'WN']
        AssetComponentAbbreviation=['DM','FX','FX','HN','HN','n/a','RE','RE','RS','RS','SK','SL','SL']
        c= [Description, AssetSystemAbbreviation, AssetSubSystemAbbreviation, AssetComponentAbbreviation]
        return c
    
    elif x=='Doors':
        Description=['Access panel external', 'Access panel internal', 'Bifold external door', 'Bifold internal door', 'Boom barrier door', 'Double acting external door', 'Double acting internal door', 'Double egress external door', 'Double egress internal door', 'Gate', 'Generic external door', 'Generic internal door', 'One way hinged external door', 'One way hinged internal door', 'Opening as door', 'Revolving external door', 'Revolving internal door', 'Rolling shutter external door', 'Rolling shutter internal door', 'Sliding external door', 'Sliding internal door', 'Trapdoor external', 'Trapdoor internal', 'Turnstile external door', 'Turnstile internal door']
        AssetSystemAbbreviation=['AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'LN', 'AR', 'AR', 'AR', 'AR', 'n/a', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR']
        AssetSubSystemAbbreviation=['DO', 'DO', 'DO', 'DO', 'DO', 'DO', 'DO', 'DO', 'DO', 'DO', 'DO', 'DO', 'DO', 'DO', 'n/a', 'DO', 'DO', 'DO', 'DO', 'DO', 'DO', 'DO', 'DO', 'DO', 'DO']
        AssetComponentAbbreviation=['AP','AP','BI','BI','BMBR','DA','DA','DE','DE','GT','GR','GR','HD','HD','n/a','RE','RE','RS','RS','SL','SL','TR','TR','TU','TU']  
        c= [Description, AssetSystemAbbreviation, AssetSubSystemAbbreviation, AssetComponentAbbreviation]
        return c
    
    elif x=='Planting':
        Description=['Bedding', 'Bush', 'External potted plant', 'Grasses', 'Green roof planting', 'Internal potted plant', 'Planted green wall', 'Planter', 'Shrub', 'Tree', 'Groundcover', 'Succulents']
        AssetSystemAbbreviation=['LN', 'LN', 'LN', 'LN', 'LN', 'LN', 'LN', 'LN', 'LN', 'LN', 'LN', 'LN']
        AssetSubSystemAbbreviation=['PT', 'PT', 'PT', 'PT', 'PT', 'PT', 'PT', 'PT', 'PT', 'PT', 'PT', 'PT']
        AssetComponentAbbreviation=['BEDD','BUSH','EPTP','GRS','GR','IPTP','GRW','PLR','SHB','TRE','GRC','GRC']
        c= [Description, AssetSystemAbbreviation, AssetSubSystemAbbreviation, AssetComponentAbbreviation]
        return c
    
    elif x=='Parking':
        Description=['Boom barrier door', 'Parking bumper', 'Protection crash cushion', 'Traffic calming device']
        AssetSystemAbbreviation=['AR', 'n/a', 'n/a', 'n/a']
        AssetSubSystemAbbreviation=['DO', 'n/a', 'n/a', 'n/a']
        AssetComponentAbbreviation=['BMBR','n/a','n/a','n/a']
        c= [Description, AssetSystemAbbreviation, AssetSubSystemAbbreviation, AssetComponentAbbreviation]
        return c
   
    elif x=='Entourage':
        Description=['Chain link fence', 'Fence', 'Protection crash cushion', 'Slat fence', 'Vehicle', 'Vehicle cargo', 'Vehicle marine', 'Vehicle rollingstock', 'Vehicle tracked', 'Vehicle wheeled', 'Welded fence']
        AssetSystemAbbreviation=['n/a','n/a','n/a','n/a','AR','AR','AR','AR','AR','AR','n/a']
        AssetSubSystemAbbreviation=['n/a','n/a','n/a','n/a','EG','EG','EG','EG','EG','EG','n/a']
        AssetComponentAbbreviation=['n/a','n/a','n/a','n/a','VH','VH','VH','VH','VH','VH','n/a']
        c= [Description, AssetSystemAbbreviation, AssetSubSystemAbbreviation, AssetComponentAbbreviation]
        return c
    
    elif x=='Specialty Equipment':
        Description=['Advertising panel', 'Bldg element bin composting', 'Bldg element bin general', 'Bldg element bin recycling', 'Bldg element bollard', 'Bldg element cavity barrier', 'Bldg element fire / smoke curtain', 'Bldg element soap dispenser', 'Bldg element swimming pool', 'Bldg element toilet fixture', 'Chimney flue', 'Chimney pot', 'Conveyor baggage', 'Conveyor belt', 'Conveyor bucket', 'Conveyor chute', 'Conveyor escape chutes', 'Conveyor linen chutes', 'Conveyor refuse chutes', 'Conveyor screw', 'Craneway', 'Elec. cold room', 'Elec. cooker', 'Elec. dishwasher', 'Elec. freestanding electric heater', 'Elec. freestanding fan', 'Elec. ice making machine', 'Elec.freestanding water cooler', 'Elec.freestanding water heater', 'Elec.freezer', 'Elec.fridge freezer', 'Elec.hand dryer', 'Elec.kitchen machine', 'Elec.microwave', 'Elec.photocopier', 'Elec.refrigerator', 'Elec.tumble dryer machine', 'Elec.vending machine', 'Elec.washing machine', 'TV', 'Telephone', 'Elevator', 'Escalator', 'Gym equipment', 'Ladder', 'Medical equipment', 'Office equipment', 'Protection bumper', 'Protection crash cushion', 'Protection for column', 'Safety cage ladder', 'Security equipment', 'Solar panel', 'Specialty equipment', 'Travelator / Moving walkway', 'Window treatments (curtain, Blind, etc.)', 'Fall Arrest']
        AssetSystemAbbreviation=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'ID', 'ID', 'ID', 'ID', 'ID', 'ID', 'ID', 'ID', 'ID', 'ID', 'ID', 'ID', 'ID', 'ID', 'ID', 'ID', 'ID', 'AR', 'AR', 'AR', 'AR', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'AR', 'n/a', 'AR', 'n/a', 'AR']
        AssetSubSystemAbbreviation=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'SP', 'SP', 'SP', 'SP', 'SP', 'SP', 'SP', 'SP', 'SP', 'SP', 'SP', 'SP', 'SP', 'SP', 'SP', 'SP', 'SP', 'SP', 'SP', 'SP', 'SP', 'SP', 'SP', 'SP', 'SP', 'SP', 'SP', 'SP', 'SP', 'SP', 'SP', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'SP', 'n/a', 'SP', 'n/a', 'SP']
        AssetComponentAbbreviation=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a','CNVR','CNVR','CNVR','CNVR','CNVR','CNVR','CNVR','CNVR','CRAN','CLDR','COKR','DWSH','HETER','FAN','ICEM','WCLR','WHTR','FRZR','FFRZ','HNDR','KCHM','MCRO','PHTO','RFGR','TDRM','VNDM','WSHM','TV','TEL','ELEV','ESCL','n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a','SOLP','n/a','TRAV','n/a','FALL',]
        c= [Description, AssetSystemAbbreviation, AssetSubSystemAbbreviation, AssetComponentAbbreviation]
        return c
    
    elif x=='Generic Models':
        Description=['Advertising signage', 'Escalator', 'Opening', 'Opening recess', 'Travelator / Moving walkway']
        AssetSystemAbbreviation=['n/a', 'AR', 'n/a', 'n/a', 'AR']
        AssetSubSystemAbbreviation=['n/a', 'SP', 'n/a', 'n/a', 'SP']
        AssetComponentAbbreviation=['n/a','ESCL','n/a','n/a','TRAV']
        c= [Description, AssetSystemAbbreviation, AssetSubSystemAbbreviation, AssetComponentAbbreviation]
        return c
    
    elif x=='Lighting Fixtures':
        Description=['External lighting', 'Lighting fixture', 'Security lighting']
        AssetSystemAbbreviation=['AR', 'AR', 'AR']
        AssetSubSystemAbbreviation=['LF', 'LF', 'LF']
        AssetComponentAbbreviation=['LIGF','LIGF','LIGF']
        c= [Description, AssetSystemAbbreviation, AssetSubSystemAbbreviation, AssetComponentAbbreviation]
        return c
    
    elif x=='Medical Equipment':
        Description=['Medical Equipment Fixed', 'Medical Equipment Partially Fixed', 'Medical Equipment Movable', 'Medical Equipment Infrequently Movable']
        AssetSystemAbbreviation=['AR', 'AR', 'AR', 'AR']
        AssetSubSystemAbbreviation=['MD', 'MD', 'MD', 'MD']
        AssetComponentAbbreviation=['ML','ML','ML','ML']
        c= [Description, AssetSystemAbbreviation, AssetSubSystemAbbreviation, AssetComponentAbbreviation]
        return c
    
    elif x=='Plumbing Fixtures':
        Description=['Ablution spray', 'Bathtub', 'Bidet', 'Cistern', 'Faucet', 'Floor drain', 'Fountain (drinking, etc.)', 'Grab bar', 'Push button', 'Shower', 'Shower tray', 'Sink', 'Toilet pan', 'Trench', 'Urinal', 'Wash hand basin', 'WC seat', 'Gutter']
        AssetSystemAbbreviation=['ID', 'ID', 'ID', 'ID', 'ID', 'ID', 'ID', 'ID', 'ID', 'ID', 'ID', 'ID', 'ID', 'AR', 'ID', 'ID', 'ID', 'AR']
        AssetSubSystemAbbreviation=['PL', 'PL', 'PL', 'PL', 'PL', 'PL', 'PL', 'PL', 'PL', 'PL', 'PL', 'PL', 'PL', 'PL', 'PL', 'PL', 'PL', 'PL']
        AssetComponentAbbreviation=['ABSP','BATB','BIDT','CTRN','FC','FD','FNTN','GRBR','PUSH','SHWR','SHTR','SINK','WCPN','TRN','URIN','WHBS','WCST','GTTR']
        c= [Description, AssetSystemAbbreviation, AssetSubSystemAbbreviation, AssetComponentAbbreviation]
        return c
    
    elif x=='Site':
        Description=['Gate', 'Fence', 'Slat fence', 'Chain link fence', 'Welded fence', 'Shading structure']
        AssetSystemAbbreviation=['LN', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
        AssetSubSystemAbbreviation=['DO', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
        AssetComponentAbbreviation=['GT','n/a','n/a','n/a','n/a','n/a']
        c= [Description, AssetSystemAbbreviation, AssetSubSystemAbbreviation, AssetComponentAbbreviation]
        return c


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
EC=[E,E1,E2,E3,E5,E6,E7,E8,E9,E10]#list of lists

#Returns a unique list of instances and duplicate list of instances used in the project
def ReturnTypenInstanceUsedinProject(x):#Pass only instances.
    Uel=[]#Unique element list.
    Enl=[]#Element human readable name list
    Del=[]#Duplicate element list.
    for i in x:
        for j in i:
            if len(Uel)==0:
                Uel.append(j)
                Enl.append(doc.GetElement(j.GetTypeId()).Id)
            elif len(Uel)!=0:
                if doc.GetElement(j.GetTypeId()).Id not in Enl:
                    Uel.append(j)
                    Enl.append(doc.GetElement(j.GetTypeId()).Id)
                else:
                    Del.append(j)
    return Uel, Del #Unique element list and #Duplicate element list.

Uel1=ReturnTypenInstanceUsedinProject(EC)[0]#Unique element list.
Uel2=ReturnTypenInstanceUsedinProject(EC)[1]#Duplicate element list.
#print(Uel1,Uel2)

def CheckParam(elements, param_name='NEOM_Operations_Class'):#Filter not operationally significant elements
    ENOS=[]
    for element in elements:
        parameter = element.LookupParameter(param_name)
        if parameter!=None:
            if parameter.AsValueString()=='Operationally significant' or parameter.AsValueString()=='Maintainable':
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

ENOS1=CheckParam(Uel1)#Not operationally significant elements
print(len(ENOS1))

def PrintTypeFamilyName(x):
    for i in x:
        print('FamilyName:',doc.GetElement(i.GetTypeId()).FamilyName,'TypeName:',i.Name)
#PrintTypeFamilyName(ENOS1)

def GetAssetCAL(x):
    el=[]
    acal=[]
    for i in x:
        y=i.Category.Name
        print(y)
        b=OtherParamValue(y)
        y1=doc.GetElement(i.GetTypeId()).LookupParameter('Description').AsValueString()
        if y1 in b[0]:
            indexD=b[0].index(y1)
            el.append(i)
            acal.append(b[3][indexD])
        else:
            print('Description didnt match')

    return el, acal
        
#print('qqqqqqqqqqqqqqq',ENOS1[0])
aca1=GetAssetCAL(ENOS1)
#print(aca1)

#for i in aca1[0]:
#    print(i.Name,aca1[1][aca1[0].index(i)])


EA = [chr(ord('A') + i) for i in range(26)]
EA1= [chr(ord('A') + i) for i in range(26)]
EA2=[]
for i in EA:# to get a list of AA, AB,......BA,BB.........ZZ
    for j in EA1:
        EA2.append(i+j)


#**********************Fill COBie Type Name values(This is a type parameter)************************


ela=aca1[0]#Elements list
acal1=aca1[1]#Asset component abbreviation list
a=[]#Appending component type name values.
b=[]#Appending asset component abbreviation values
j1=ela[0]#for comparison in elif statement
i1=0
elp=[]
for i in ela:
    if len(a)==0:
        UpdateParameterValue([i], acal1[ela.index(i)]+'-'+EA2[0], 'COBie.Type.Name')
        a.append(acal1[ela.index(i)]+'-'+EA2[0])
        b.append([acal1[ela.index(i)]])
        elp.append(i)
#        print(a,b)
        i1+=1
    elif i!=j1:
#        print(i,j1)
        c=0
        for j in b:
            c+=1
            if acal1[ela.index(i)] in j:
                l=len(j)
                a.append(acal1[ela.index(i)]+'-'+EA2[l])
                UpdateParameterValue([i], acal1[ela.index(i)]+'-'+EA2[l], 'COBie.Type.Name')
#                print('fffff',a,b)
                j.append(acal1[ela.index(i)])
                elp.append(i)
                i1+=1
                break
            elif c==len(b):
                a.append(acal1[ela.index(i)]+'-'+EA2[0])
#                print('hhhhhh',a,b)
                UpdateParameterValue([i], acal1[ela.index(i)]+'-'+EA2[0], 'COBie.Type.Name')
                b.append([acal1[ela.index(i)]])
                elp.append(i)
                i1+=1
                break
#print (a,[i.Name for i in elp])


#**********************Fill COBie Component Name values(This is an instance parameter)************************
print("*******",'COBie.Component.Name')
def Appendlist(y):#will return single list of elements
   EC1=[]
   for i in EC:
       for j in i:
           EC1.append(j)
   return EC1

EC2=Appendlist(EC)#list of elements

ENOS2=CheckParam(EC2)#Maintainable and operationally significant elements-list
print(len(ENOS2))

def GetAL(x):#Get list of all values.
    el=[]#for element instances
    Ea=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_ProjectInformation).ToElements()#Get Project Information
    str=Ea[0].LookupParameter('COBie.Facility.Name').AsValueString()#Get COBie Facility Name value
    cfn=str[len(str)-3]+str[len(str)-2]+str[len(str)-1]#get the last 3 digits of cobie facility name as string.
    ccs=[]#List of Instance parameter-COBie component space
    asa=[]#List of Asset system abbreviation
    assa=[]#List of Asset sub system abbreviation
    ctn=[]#list of COBie Type Name
    for i in x:
        y=i.Category.Name
        b=OtherParamValue(y)
        y1=doc.GetElement(i.GetTypeId()).LookupParameter('Description').AsValueString()
        if y1 in b[0]:
            indexD=b[0].index(y1)
            el.append(i)
            if i.LookupParameter('COBie.Component.Space')==None:
                print("COBie.Component.Space for {} {} (ID:{}) is empty.Kindly fill that value and run the addin again".format(i.Category.Name,i.Name,output.linkify(i.Id)))
                import sys
                sys.exit()
            ccs.append(i.LookupParameter('COBie.Component.Space').AsValueString())
            asa.append(b[1][indexD])
            assa.append(b[2][indexD])
            ctn.append(doc.GetElement(i.GetTypeId()).LookupParameter('COBie.Type.Name').AsValueString())
        else:
            print('Description didnt match')

    return el, cfn, ccs, asa, assa, ctn

CCNL=GetAL(ENOS2)
#print(CCNL)
cs=[]#list of combined values string
for i in CCNL[0]:
    indexd=CCNL[0].index(i)
    cs.append(CCNL[1]+'-'+CCNL[2][indexd]+'-'+CCNL[3][indexd]+'-'+CCNL[4][indexd]+'-'+CCNL[5][indexd])
#    print(i.Name,cs)
#print(cs)
els=CCNL[0]#List of elements.

n=[]#Empty list for creating number series.   
for i in range(1, len(els)):#Start from 1 to length of els
   fn ="{:03}".format(i)#Format the number to be three digits, zero-padded
   n.append(fn)#Convert the formatted number to a list of digits
print(n)

el1=[]#Value to be updated in revit
el2=[]#Value for cross checking in the below code
el3=els[0]#for comparison in elif statement
for i in els:
    x=0
    indx=els.index(i)
    if len(el1)==0:
        el1.append(cs[indx]+n[0])
        el2.append([cs[indx]])
        UpdateParameterValue([i], cs[indx]+n[0], 'COBie.Component.Name')
#        print(el1,el2)
    elif i!=el3:
        c=0
        for j in el2:
            c+=1
            if cs[indx] in j:
                l=len(j)
                el1.append(cs[indx]+n[l])
                j.append(cs[indx])
                UpdateParameterValue([i], cs[indx]+n[l], 'COBie.Component.Name')
#                print(el1,el2)
                break
            elif c==len(el2):
                el1.append(cs[indx]+n[0])
                el2.append([cs[indx]])
                UpdateParameterValue([i], cs[indx]+n[0], 'COBie.Component.Name')
#                print(el1,el2)
                break
#print(el1,el2)
