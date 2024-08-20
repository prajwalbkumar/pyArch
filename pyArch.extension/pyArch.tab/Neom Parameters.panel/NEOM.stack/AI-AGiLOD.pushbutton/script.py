"""This addin will fill the value of parameters 'Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration',\
   'COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', \
      'COBie.System.Description'. The values will be filled for 10 Categories"""
from Autodesk.Revit.DB import *
from pyrevit import forms,script
doc = __revit__.ActiveUIDocument.Document

output = script.get_output()

def GetLists(x):
   if x== 'Casework':
      Description=['Desk', 'File cabinet', 'Kitchen', 'Office', 'Shelf', 'Table', 'Technical cabinet', 'Counter', 'Cabinet']
      NEOM_Component_Description=['Desk', 'File Cabinet', 'Kitchen Casework', 'Office Casework', 'Shelf', 'Table', 'Technical Cabinet', 'Counter', 'Cabinet']
      Ifc_Entity=['IfcFurniture', 'IfcFurniture', 'IfcFurniture', 'IfcFurniture', 'IfcFurniture', 'IfcFurniture', 'IfcFurniture', 'IfcFurniture', 'IfcFurniture']
      Ifc_Enumeration=['DESK', 'FILECABINET', 'USERDEFINED - Kitchen casework', 'USERDEFINED - Office casework', 'SHELF', 'TABLE', 'TECHNICALCABINET', 'USERDEFINED - Counter', 'USERDEFINED - Cabinet']
      COBieComponentDescription=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      NEOM_Operations_Class=['Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant']
      IfcExportAs=['IfcFurniture.DESK', 'IfcFurniture.FILECABINET', 'IfcFurniture.USERDEFINED', 'IfcFurniture.USERDEFINED', 'IfcFurniture.SHELF', 'IfcFurniture.TABLE', 'IfcFurniture.TECHNICALCABINET', 'IfcFurniture.USERDEFINED', 'IfcFurniture.USERDEFINED']
      NEOM_Clash_Test_Code=['IDN.03', 'IDN.03', 'IDN.03', 'IDN.03', 'IDN.03', 'IDN.03', 'IDN.03', 'IDN.03', 'IDN.03']
      COBieSystemName=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      COBieSystemDescription=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.
   

   elif x=='Ceiling':
      Description=['Ceiling', 'Ceiling coping', 'Ceiling insulation', 'Ceiling membrane', 'Ceiling molding', 'Suspended ceiling', 'Ceiling wrapping', 'Ceiling topping']
      NEOM_Component_Description=['Ceiling', 'Ceiling Coping', 'Ceiling Insulation', 'Ceiling Membrane', 'Ceiling Molding', 'Suspended Ceiling', 'Ceiling Wrapping', 'Ceiling Topping']
      Ifc_Entity=['IfcCovering', 'IfcCovering', 'IfcCovering', 'IfcCovering', 'IfcCovering', 'IfcCovering', 'IfcCovering', 'IfcCovering']
      Ifc_Enumeration=['CEILING', 'COPING', 'INSULATION', 'MEMBRANE', 'MOLDING', 'USERDEFINED - Suspended ceiling', 'WRAPPING', 'TOPPING']
      COBieComponentDescription=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      NEOM_Operations_Class=['Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant']
      IfcExportAs=['IfcCovering.CEILING', 'IfcCovering.COPING', 'IfcCovering.INSULATION', 'IfcCovering.MEMBRANE', 'IfcCovering.MOLDING', 'IfcCovering.USERDEFINED', 'IfcCovering.WRAPPING', 'IfcCovering.TOPPING']
      NEOM_Clash_Test_Code=['IDN.01', 'IDN.01', 'IDN.01', 'IDN.01', 'IDN.01', 'IDN.01', 'IDN.01', 'IDN.01'] 
      COBieSystemName=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      COBieSystemDescription=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.
   
   elif x=='Entourage':
      Description=['Chain link fence', 'Fence', 'Protection crash cushion', 'Slat fence', 'Vehicle', 'Vehicle cargo', 'Vehicle marine', 'Vehicle rollingstock', 'Vehicle tracked', 'Vehicle wheeled', 'Welded fence']
      NEOM_Component_Description=['Chain Link Fence', 'Fence', 'Protection Crash Cushion', 'Slat Fence', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'Welded Fence']
      Ifc_Entity=['IfcRailing', 'IfcRailing', 'IfcImpactProtectionDevice', 'IfcRailing', 'IfcVehicle', 'IfcVehicle', 'IfcVehicle', 'IfcVehicle', 'IfcVehicle', 'IfcVehicle', 'IfcRailing']
      Ifc_Enumeration=['FENCE', 'FENCE', 'CRASHCUSHION', 'FENCE', 'VEHICLE', 'CARGO', 'VEHICLEMARINE', 'ROLLINGSTOCK', 'VEHICLETRACKED', 'VEHICLEWHEELED', 'FENCE']
      COBieComponentDescription=['n/a', 'n/a', 'n/a', 'n/a', 'Vehicle', 'Cargo vehicle', 'Marine vehicle', 'Rollingstock vehicle', 'Tracked vehicle', 'Wheeled vehicle', 'n/a']
      NEOM_Operations_Class=['Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Maintainable', 'Maintainable', 'Maintainable', 'Maintainable', 'Maintainable', 'Maintainable', 'Not operationally significant']
      IfcExportAs=['IfcRailing.FENCE', 'IfcRailing.FENCE', 'IfcImpactProtectionDevice.CRASHCUSHION', 'IfcRailing.FENCE', 'IfcVehicle.VEHICLE', 'IfcVehicle.CARGO', 'IfcVehicle.VEHICLEMARINE', 'IfcVehicle.ROLLINGSTOCK', 'IfcVehicle.VEHICLETRACKED', 'IfcVehicle.VEHICLEWHEELED', 'IfcRailing.FENCE']
      NEOM_Clash_Test_Code=['LAN.01','LAN.01','LAN.04','LAN.01','n/a','n/a','n/a','n/a','n/a','n/a','LAN.01']
      COBieSystemName=['n/a', 'n/a', 'n/a', 'n/a', 'Transportation system', 'Transportation system', 'Transportation system', 'Transportation system', 'Transportation system', 'Transportation system', 'n/a']
      COBieSystemDescription=['n/a', 'n/a', 'n/a', 'n/a', 'Transportation system', 'Transportation system', 'Transportation system', 'Transportation system', 'Transportation system', 'Transportation system', 'n/a']   
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.

   elif x=='Furniture':
      Description=['Bed', 'Bench furniture', 'Chair', 'Desk', 'File cabinet', 'Free standing furniture (credenza, lectern, etc.)', 'Furniture accessories (Rug, etc.)', 'Gym equipment', 'Medical equipment', 'Office equipment', 'Security equipment', 'Shelf', 'Sofa', 'System furniture panel element', 'System furniture subrack element', 'System furniture worksurface element', 'System Furniture Bench', 'Table', 'Technical cabinet']
      NEOM_Component_Description=['Bed', 'Bench furniture', 'Chair', 'Desk', 'File Cabinet', 'Free Standing Furniture', 'Furniture Accessories', 'Gym Equipment', 'Medical Equipment', 'Office Equipment', 'Security Equipment', 'Shelf', 'Sofa', 'System Furniture Panel Element', 'System Furniture Subrack Element', 'System Furniture Worksurface Element', 'System Furniture Bench', 'Table', 'Technical Cabinet']
      Ifc_Entity=['IfcFurniture', 'IfcFurniture', 'IfcFurniture', 'IfcFurniture', 'IfcFurniture', 'IfcFurniture', 'IfcFurniture', 'IfcFurniture', 'IfcFurniture', 'IfcFurniture', 'IfcFurniture', 'IfcFurniture', 'IfcFurniture', 'IfcSystemFurnitureElement', 'IfcSystemFurnitureElement', 'IfcSystemFurnitureElement', 'IfcSystemFurnitureElement', 'IfcFurniture', 'IfcFurniture']
      Ifc_Enumeration=['BED', 'USERDEFINED - Bench furniture', 'CHAIR', 'DESK', 'FILECABINET', 'USERDEFINED - Free standing furniture (credenza, lectern, etc.)', 'USERDEFINED - Furniture accessories (Rug, etc.)', 'USERDEFINED - Gym equipment', 'USERDEFINED - Medical equipment', 'USERDEFINED - Office equipment', 'USERDEFINED - Security equipment', 'SHELF', 'SOFA', 'PANEL', 'SUBRACK', 'WORKSURFACE', 'USERDEFINED - System furniture bench', 'TABLE', 'TECHNICALCABINET']
      COBieComponentDescription=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      NEOM_Operations_Class=['Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant']
      IfcExportAs=['IfcFurniture.BED', 'IfcFurniture.USERDEFINED', 'IfcFurniture.CHAIR', 'IfcFurniture.DESK', 'IfcFurniture.FILECABINET', 'IfcFurniture.USERDEFINED', 'IfcFurniture.USERDEFINED', 'IfcFurniture.USERDEFINED', 'IfcFurniture.USERDEFINED', 'IfcFurniture.USERDEFINED', 'IfcFurniture.USERDEFINED', 'IfcFurniture.SHELF', 'IfcFurniture.SOFA', 'IfcSystemFurnitureElement.PANEL', 'IfcSystemFurnitureElement.SUBRACK', 'IfcSystemFurnitureElement.WORKSURFACE', 'IfcSystemFurnitureElement.BENCH', 'IfcFurniture.TABLE', 'IfcFurniture.TECHNICALCABINET']
      NEOM_Clash_Test_Code=['IDN.03', 'IDN.03', 'IDN.03', 'IDN.03', 'IDN.03', 'IDN.03', 'IDN.03', 'IDN.02', 'IDN.02', 'IDN.03', 'IDN.02', 'IDN.03', 'IDN.03', 'IDN.03', 'IDN.03', 'IDN.03', 'IDN.03', 'IDN.03', 'IDN.03']
      COBieSystemName=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      COBieSystemDescription=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']  
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.

   elif x=='Generic Model':
      Description=['Advertising signage', 'Escalator', 'Opening', 'Opening recess', 'Travelator / Moving walkway']
      NEOM_Component_Description=['Advertising Signage', 'n/a', 'Void Opening', 'Recess Opening', 'n/a']
      Ifc_Entity=['IfcSign', 'IfcTransportElement', 'IfcOpeningElement', 'IfcOpeningElement', 'IfcTransportElement']
      Ifc_Enumeration=['USERDEFINED - Advertising signage', 'ESCALATOR', 'OPENING', 'RECESS', 'MOVINGWALKWAY'] 
      COBieComponentDescription=['n/a', 'Escalator', 'n/a', 'n/a', 'Travelator / Moving walkway']
      NEOM_Operations_Class=['Not operationally significant', 'Maintainable', 'Not operationally significant', 'Not operationally significant', 'Maintainable']
      IfcExportAs=['IfcSign.USERDEFINED', 'IfcTransportElement.ESCALATOR', 'IfcOpeningElement.OPENING', 'IfcOpeningElement.RECESS', 'IfcTransportElement.MOVINGWALKWAY']
      NEOM_Clash_Test_Code=['IDN.06', 'IDN.02', 'n/a', 'n/a', 'IDN.02']
      COBieSystemName=['n/a', 'Conveying system', 'n/a', 'n/a', 'Conveying system']
      COBieSystemDescription=['n/a', 'Conveying system', 'n/a', 'n/a', 'Conveying system']
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.

   elif x=='Lighting Fixture':
      Description=['External lighting', 'Lighting fixture', 'Security lighting']
      NEOM_Component_Description=['n/a', 'n/a', 'n/a']
      Ifc_Entity=['IfcLightFixture', 'IfcLightFixture', 'IfcLightFixture']
      Ifc_Enumeration=['USERDEFINED - External lighting', 'USERDEFINED - Lighting fixture', 'SECURITYLIGHTING']   
      COBieComponentDescription=['External lighting', 'Lighting fixture', 'Security lighting']
      NEOM_Operations_Class=['Maintainable', 'Maintainable', 'Maintainable']
      IfcExportAs=['IfcLightFixture.USERDEFINED', 'IfcLightFixture.USERDEFINED', 'IfcLightFixture.SECURITYLIGHTING']
      NEOM_Clash_Test_Code=['ELE.05', 'ELE.05', 'ELE.05']
      COBieSystemName=['Lighting system', 'Lighting system', 'Lighting system']
      COBieSystemDescription=['Lighting system', 'Lighting system', 'Lighting system']
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.
   
   elif x=='Medical Equipment':
      Description=['Medical Equipment Fixed', 'Medical Equipment Partially Fixed', 'Medical Equipment Movable', 'Medical Equipment Infrequently Movable']
      NEOM_Component_Description=['n/a', 'n/a', 'n/a', 'n/a']
      Ifc_Entity=['IfcElectricAppliance', 'IfcElectricAppliance', 'IfcFurniture', 'IfcFurniture']
      Ifc_Enumeration=['USERDEFINED - Medical Equipment', 'USERDEFINED - Medical Equipment', 'USERDEFINED - Medical Equipment', 'USERDEFINED - Medical Equipment']
      COBieComponentDescription=['Fixed Medical Equipment', 'Partially fixed Medical Equipment', 'Movable Medical Equipment', 'Seldomly Movable Medical Equipment']
      NEOM_Operations_Class=['Maintainable', 'Maintainable', 'Maintainable', 'Maintainable']
      IfcExportAs=['IfcElectricAppliance.USERDEFINED', 'IfcElectricAppliance.USERDEFINED', 'IfcFurniture.USERDEFINED', 'IfcFurniture.USERDEFINED']
      NEOM_Clash_Test_Code=['IDN.02', 'IDN.02', 'IDN.02', 'IDN.02']
      COBieSystemName=['Medical system', 'Medical system', 'Medical system', 'Medical system']
      COBieSystemDescription=['Medical system', 'Medical system', 'Medical system', 'Medical system'] 
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.

   elif x=='Plumbing Fixture':
      Description=['Ablution spray', 'Bathtub', 'Bidet', 'Cistern', 'Faucet', 'Floor drain', 'Fountain (drinking, etc.)', 'Grab bar', 'Push button', 'Shower', 'Shower tray', 'Sink', 'Toilet pan', 'Trench', 'Urinal', 'Wash hand basin', 'WC seat', 'Gutter']
      NEOM_Component_Description=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      Ifc_Entity=['IfcSanitaryTerminal', 'IfcSanitaryTerminal', 'IfcSanitaryTerminal', 'IfcSanitaryTerminal', 'IfcSanitaryTerminal', 'IfcSanitaryTerminal', 'IfcSanitaryTerminal', 'IfcSanitaryTerminal', 'IfcSanitaryTerminal', 'IfcSanitaryTerminal', 'IfcSanitaryTerminal', 'IfcSanitaryTerminal', 'IfcSanitaryTerminal', 'IfcDistributionChamberElement', 'IfcSanitaryTerminal', 'IfcSanitaryTerminal', 'IfcSanitaryTerminal', 'IfcSanitaryTerminal']
      Ifc_Enumeration=['USERDEFINED - Ablution spray', 'BATH', 'BIDET', 'CISTERN', 'USERDEFINED - Faucet', 'USERDEFINED - Floor drain', 'SANITARYFOUNTAIN', 'USERDEFINED - Grab bar', 'USERDEFINED - Push button sanitary terminal', 'SHOWER', 'USERDEFINED - Shower tray', 'SINK', 'TOILETPAN', 'TRENCH', 'URINAL', 'WASHHANDBASIN', 'WCSEAT', 'USERDEFINED - Gutter']
      COBieComponentDescription= ['Ablution spray', 'Bathtub', 'Bidet', 'Cistern', 'Faucet', 'Floor drain', 'Sanitary fountain', 'Grab bar', 'Push button sanitary terminal', 'Shower', 'Shower tray', 'Sink', 'Toilet pan', 'Trench', 'Urinal', 'Wash hand basin', 'WC seat', 'Gutter']
      NEOM_Operations_Class=['Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant']
      IfcExportAs=['IfcSanitaryTerminal.USERDEFINED', 'IfcSanitaryTerminal.BATH', 'IfcSanitaryTerminal.BIDET', 'IfcSanitaryTerminal.CISTERN', 'IfcSanitaryTerminal.USERDEFINED', 'IfcSanitaryTerminal.USERDEFINED', 'IfcSanitaryTerminal.SANITARYFOUNTAIN', 'IfcSanitaryTerminal.USERDEFINED', 'IfcSanitaryTerminal.USERDEFINED', 'IfcSanitaryTerminal.SHOWER', 'IfcSanitaryTerminal.USERDEFINED', 'IfcSanitaryTerminal.SINK', 'IfcSanitaryTerminal.TOILETPAN', 'IfcDistributionChamberElement.TRENCH', 'IfcSanitaryTerminal.URINAL', 'IfcSanitaryTerminal.WASHHANDBASIN', 'IfcSanitaryTerminal.WCSEAT', 'IfcSanitaryTerminal.USERDEFINED']
      NEOM_Clash_Test_Code=['IDN.04', 'IDN.04', 'IDN.04', 'IDN.04', 'IDN.04', 'IDN.04', 'IDN.04', 'IDN.04', 'IDN.04', 'IDN.04', 'IDN.04', 'IDN.04', 'IDN.04', 'IDN.04', 'IDN.04', 'IDN.04', 'IDN.04', 'IDN.04']
      COBieSystemName=['Sanitary system', 'Sanitary system', 'Sanitary system', 'Sanitary system', 'Sanitary system', 'Sanitary system', 'Sanitary system', 'Sanitary system', 'Sanitary system', 'Sanitary system', 'Sanitary system', 'Sanitary system', 'Sanitary system', 'Plumbing distribution  system', 'Sanitary system', 'Sanitary system', 'Sanitary system', 'Sanitary system']
      COBieSystemDescription=['Sanitary system', 'Sanitary system', 'Sanitary system', 'Sanitary system', 'Sanitary system', 'Sanitary system', 'Sanitary system', 'Sanitary system', 'Sanitary system', 'Sanitary system', 'Sanitary system', 'Sanitary system', 'Sanitary system', 'Plumbing distribution  system', 'Sanitary system', 'Sanitary system', 'Sanitary system', 'Sanitary system']
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.

   elif x=='Signage':
      Description=['Advertising signage', 'Marker sign', 'Mirror sign', 'Pictoral sign', 'Service sign', 'Identification sign', 'Directional sign', 'Informational sign']
      NEOM_Component_Description=['Advertising Signage', 'Marker Sign', 'Mirror Sign', 'Pictoral Sign', 'Service Sign', 'Identification Sign', 'Directional Sign', 'Informational Sign']
      Ifc_Entity=['IfcSign', 'IfcSign', 'IfcSign', 'IfcSign', 'IfcSign', 'IfcSign', 'IfcSign', 'IfcSign']    
      Ifc_Enumeration=['USERDEFINED - Advertising signage', 'MARKER', 'MIRROR', 'PICTORAL', 'USERDEFINED - Service sign', 'USERDEFINED - Identification sign', 'USERDEFINED - Directional sign', 'USERDEFINED - Informational sign']
      COBieComponentDescription=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      NEOM_Operations_Class=['Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant']
      IfcExportAs=['IfcSign.USERDEFINED', 'IfcSign.MARKER', 'IfcSign.MIRROR', 'IfcSign.PICTORAL', 'IfcSign.USERDEFINED', 'IfcSign.USERDEFINED', 'IfcSign.USERDEFINED', 'IfcSign.USERDEFINED']
      NEOM_Clash_Test_Code=['IDN.06', 'IDN.06', 'IDN.06', 'IDN.06', 'IDN.06', 'IDN.06', 'IDN.06', 'IDN.06']
      COBieSystemName=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      COBieSystemDescription=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.

   elif x=='Site':
      Description=['Gate', 'Fence', 'Slat fence', 'Chain link fence', 'Welded fence', 'Shading structure']
      NEOM_Component_Description=['n/a', 'Fence', 'Slat Fence', 'Chain Link Fence', 'Welded Fence', 'Shading Structure'] 
      Ifc_Entity=['IfcDoor', 'IfcRailing', 'IfcRailing', 'IfcRailing', 'IfcRailing', 'IfcSystemFurnitureElement']
      Ifc_Enumeration=['GATE', 'FENCE', 'FENCE', 'FENCE', 'FENCE', 'USERDEFINED - Shading Structure']
      COBieComponentDescription=['Gate', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      NEOM_Operations_Class=['Operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant']
      IfcExportAs=['IfcDoor.GATE', 'IfcRailing.FENCE', 'IfcRailing.FENCE', 'IfcRailing.FENCE', 'IfcRailing.FENCE', 'IfcSystemFurnitureElement.USERDEFINED']
      NEOM_Clash_Test_Code=['LAN.01', 'LAN.01', 'LAN.01', 'LAN.01', 'LAN.01', 'LAN.04']
      COBieSystemName=['External partition system', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      COBieSystemDescription=['External partition system', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']  
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.

def UpdateParameterValue(elements, value, param_name):
#    print(elements)
    updated_count = 0
    t = Transaction(doc, "Update Parameter Value")
    t.Start()
    try:
        for element in elements:
            parameter = element.LookupParameter(param_name) #Lookupparameter returns none only if the parameter is not assigned to type or instance.
            if parameter!=None:
                parameter.Set(value)
#                print('a')
                updated_count += 1
            elif parameter==None:
                k=element.GetTypeId()
                ElementType=doc.GetElement(k)
                parameter_1=ElementType.LookupParameter(param_name)
                parameter_1.Set(value)
#                print('b')
                updated_count += 1
            else:
                print('Parameter does not exist or is not editable')
        print("Value of Parameter {} (Element ID: {}) is updated to {}".format(param_name, output.linkify(element.Id), value))
    except Exception as e:
        print('There was an error. The command is not executed. Parameter could not be found/NotEditable.')
        print(e)
    t.Commit()

def UParam(x,type,instance):#This function filter the elements(type/instances), the parameter name and its value.

   a=type#type

   EI=instance#instance

   #list of instances with its type name appended to list.
   E_L=[]
   for i in EI:
      d=doc.GetElement(i.GetTypeId())
      E_L.append(d.Parameter[BuiltInParameter.SYMBOL_NAME_PARAM].AsString())

   #list of types with its type name appended to list.
   E_D=[]
   for i in a:
       E_D.append(i.Parameter[BuiltInParameter.SYMBOL_NAME_PARAM].AsString())
   
   #list of intsances with its type name appended to the list an will only have one name per instance-type.
   E_inRevit=[]
   for i in E_D:
      if i in E_L:
         E_inRevit.append(i)
         

   a1=forms.SelectFromList.show(E_inRevit,button_name='select the ElementType that you want to move to a specific description category')
   if a1==None:
      print('You have opted to Exit. Parameters are not updated')
      import sys
      sys.exit()
   Description=GetLists(x)[0] #Description Categories
   
   b1=forms.SelectFromList.show(Description,button_name='select the description that you want the ElementType in')
   if b1==None:
      print('You have opted to Exit. Parameters are not updated')
      import sys
      sys.exit()

   indexD=Description.index(b1) #Gives you the index of all the parameter values

   NEOM_Component_Description=GetLists(x)[1]#Getting values of a single list from the nested list of the function return c
   Ifc_Entity=GetLists(x)[2]
   Ifc_Enumeration=GetLists(x)[3]
   COBieComponentDescription=GetLists(x)[4]
   NEOM_Operations_Class=GetLists(x)[5]
   IfcExportAs=GetLists(x)[6]
   NEOM_Clash_Test_Code=GetLists(x)[7]
   COBieSystemName=GetLists(x)[8]
   COBieSystemDescription=GetLists(x)[9]


   c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]#this is list of lists.
   c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']#this is the actual list with parameter names.
   #We are considering instance types because lookupparameter only work for instances in update parameter value.


   E1=[]

   for i in EI:#Collecting all the instances whos value have to be updated.
      d=doc.GetElement(i.GetTypeId())
      if d.Parameter[BuiltInParameter.SYMBOL_NAME_PARAM].AsString() == a1:
         E1.append(i)

   j1=0

   while j1<len(c):#considering the list length will be same for all the parameters. the list contain parameternamest
      z=c[j1] #Select the parameter name (which is a list) in nested list of parameters c.
      z1=z[indexD] # Selects the parameter value from the parameter name list
#      print(z1, c1[j1])
      UpdateParameterValue(E1, z1, c1[j1]) #names should be converted to strings
      j1=j1+1

Category_Name = ['Casework', 'Ceiling','Entourage','Furniture','Generic Model', 'Lighting Fixture', 'Medical Equipment', 'Plumbing Fixture', 'Signage', 'Site', 'Exit']

Selected_Category = forms.CommandSwitchWindow.show(Category_Name, message='Select the category for filling iLOD parameters')
if Selected_Category == 'Casework':
   UParam('Casework',FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Casework).WhereElementIsElementType(),FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Casework).WhereElementIsNotElementType())

elif Selected_Category == 'Ceiling':
   UParam('Ceiling',FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Ceilings).WhereElementIsElementType(),FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Ceilings).WhereElementIsNotElementType())

elif Selected_Category == 'Entourage':
   UParam('Entourage',FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Entourage).WhereElementIsElementType(),FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Entourage).WhereElementIsNotElementType())

elif Selected_Category == 'Furniture':
   UParam('Furniture',FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Furniture).WhereElementIsElementType(),FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Furniture).WhereElementIsNotElementType())

elif Selected_Category == 'Generic Model':
   UParam('Generic Model',FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_GenericModel).WhereElementIsElementType(),FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType())

elif Selected_Category == 'Lighting Fixture':
   UParam('Lighting Fixture',FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_LightingFixtures).WhereElementIsElementType(),FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_LightingFixtures).WhereElementIsNotElementType())

elif Selected_Category == 'Medical Equipment':
   UParam('Medical Equipment',FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_MedicalEquipment).WhereElementIsElementType(),FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_MedicalEquipment).WhereElementIsNotElementType())

elif Selected_Category == 'Plumbing Fixture':
   UParam('Plumbing Fixture',FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PlumbingFixtures).WhereElementIsElementType(),FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PlumbingFixtures).WhereElementIsNotElementType())

elif Selected_Category == 'Signage':
   UParam('Signage',FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Signage).WhereElementIsElementType(),FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Signage).WhereElementIsNotElementType())

elif Selected_Category == 'Site':
   UParam('Site',FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Site).WhereElementIsElementType(),FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Site).WhereElementIsNotElementType())


else:
   print('Parameters are not updated. Your selected option is Exit.')






