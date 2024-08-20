"""This addin will fill the value of parameters 'Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration',\
   'COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', \
      'COBie.System.Description'. The values will be filled for 18 Categories"""
from Autodesk.Revit.DB import *
from pyrevit import forms,script
doc = __revit__.ActiveUIDocument.Document

output = script.get_output()

def GetLists(x):
   if x== 'Wall':
      Description=['Bund wall', 'Chain link fence', 'Elemented wall', 'Fence', 'Flood barrier wall', 'Internal glazed wall', 'Movable wall',\
                'Parapet', 'Partitioning', 'Plumbing wall', 'Polygonal wall', 'Retaining wall', 'Shear wall', 'Skirting board', 'Slat fence',\
                'Solid wall', 'Standard wall', 'Wall cladding', 'Wall coping', 'Wall insulation', 'Wall membrane', 'Wall molding', 'Wall topping',\
                'Wave wall', 'Welded fence', 'Wrapping wall']
      NEOM_Component_Description=['Bund Wall', 'Chain Link Fence', 'Elemented Wall', 'Fence', 'Flood Barrier Wall', 'Internal Glazed Wall', 'Movable Wall', 'Parapet', 'Partitioning', 'Plumbing Wall', 'Polygonal Wall', 'Retaining Wall', 'Shear Wall', 'Skirting Board', 'Slat Fence', 'Solid Wall', 'Standard Wall', 'Wall Cladding', 'Wall Coping', 'Wall Insulation', 'Wall Membrane', 'Wall Molding', 'Wall Topping', 'Wave Wall', 'Welded Fence', 'Wrapping Wall']
      Ifc_Entity=['IfcWall', 'IfcRailing', 'IfcWall', 'IfcRailing', 'IfcWall', 'IfcWall', 'IfcWall', 'IfcWall', 'IfcWall', 'IfcWall', 'IfcWall', 'IfcWall', 'IfcWall', 'IfcCovering', 'IfcRailing', 'IfcWall', 'IfcWall', 'IfcCovering', 'IfcCovering', 'IfcCovering', 'IfcCovering', 'IfcCovering', 'IfcCovering', 'IfcWall', 'IfcRailing', 'IfcCovering']
      Ifc_Enumeration=['USERDEFINED - Bund wall', 'FENCE', 'ELEMENTEDWALL', 'FENCE', 'USERDEFINED - Flood barrier wall', 'USERDEFINED - Internal glazed wall', 'MOVABLE', 'PARAPET', 'PARTITIONING', 'PLUMBINGWALL', 'POLYGONAL', 'RETAININGWALL', 'SHEAR', 'SKIRTINGBOARD', 'FENCE', 'SOLIDWALL', 'STANDARD', 'CLADDING', 'COPING', 'INSULATION', 'MEMBRANE', 'MOLDING', 'TOPPING', 'WAVEWALL', 'FENCE', 'WRAPPING']
      COBieComponentDescription=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      NEOM_Operations_Class=['Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant']
      IfcExportAs=['IfcWall.USERDEFINED', 'IfcRailing.FENCE', 'IfcWall.ELEMENTEDWALL', 'IfcRailing.FENCE', 'IfcWall.USERDEFINED', 'IfcWall.USERDEFINED', 'IfcWall.MOVABLE', 'IfcWall.PARAPET', 'IfcWall.PARTITIONING', 'IfcWall.PLUMBINGWALL', 'IfcWall.POLYGONAL', 'IfcWall.RETAININGWALL', 'IfcWall.SHEAR', 'IfcCovering.SKIRTINGBOARD', 'IfcRailing.FENCE', 'IfcWall.SOLIDWALL', 'IfcWall.STANDARD', 'IfcCovering.CLADDING', 'IfcCovering.COPING', 'IfcCovering.INSULATION', 'IfcCovering.MEMBRANE', 'IfcCovering.MOLDING', 'IfcCovering.TOPPING', 'IfcWall.WAVEWALL', 'IfcRailing.FENCE', 'IfcCovering.WRAPPING']
      NEOM_Clash_Test_Code=['ARC.09', 'LAN.01', 'ARC.09', 'LAN.01', 'ARC.09', 'ARC.09', 'ARC.09', 'ARC.09', 'ARC.09', 'ARC.09', 'ARC.09', 'STR.05', 'ARC.09', 'ARC.09', 'LAN.01', 'ARC.09', 'ARC.09', 'IDN.07', 'ARC.09', 'ARC.09', 'ARC.09', 'ARC.09', 'ARC.09', 'ARC.09', 'LAN.01', 'ARC.09']
      COBieSystemName=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      COBieSystemDescription=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.
   
   elif x=='Curtain Wall':
      Description=['Chain link fence', 'Curtain wall', 'Curtain wall aluminum', 'Curtain wall glazed', 'Curtain wall insulation', 'Curtain wall metal', 'Fence', 'Slat fence', 'Welded fence']
      NEOM_Component_Description=['Chain Link Fence', 'Curtain Wall', 'Curtain Wall Aluminum', 'Curtain Wall Glazed', 'Curtain Wall Insulation', 'Curtain Wall Metal', 'Fence', 'Slat Fence', 'Welded Fence']
      Ifc_Entity=['IfcRailing', 'IfcCurtainWall', 'IfcCurtainWall', 'IfcCurtainWall', 'IfcCurtainWall', 'IfcCurtainWall', 'IfcRailing', 'IfcRailing', 'IfcRailing']
      Ifc_Enumeration=['FENCE', 'USERDEFINED - Non glazed curtain wall', 'USERDEFINED - Aluminum curtain wall', 'USERDEFINED - Glazed curtain wall', 'USERDEFINED - Insulation curtain wall', 'USERDEFINED - Metal curtain wall', 'FENCE', 'FENCE', 'FENCE']
      COBieComponentDescription=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']   
      NEOM_Operations_Class=['Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant']
      IfcExportAs=['IfcRailing.FENCE', 'IfcCurtainWall.USERDEFINED', 'IfcCurtainWall.USERDEFINED', 'IfcCurtainWall.USERDEFINED', 'IfcCurtainWall.USERDEFINED', 'IfcCurtainWall.USERDEFINED', 'IfcRailing.FENCE', 'IfcRailing.FENCE', 'IfcRailing.FENCE']
      NEOM_Clash_Test_Code=['LAN.01', 'ARC.01', 'ARC.01', 'ARC.01', 'ARC.01', 'ARC.01', 'LAN.01', 'LAN.01', 'LAN.01']
      COBieSystemName=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']   
      COBieSystemDescription=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']   
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.

   elif x=='Curtain Panel':
      Description=['Curtain panel']
      NEOM_Component_Description=['Curtain Panel']
      Ifc_Entity=['IfcPlate']
      Ifc_Enumeration=['CURTAIN_PANEL']
      COBieComponentDescription=['n/a']
      NEOM_Operations_Class=['Not operationally significant']
      IfcExportAs=['IfcPlate.CURTAIN_PANEL']
      NEOM_Clash_Test_Code=['ARC.01']
      COBieSystemName=['n/a']
      COBieSystemDescription=['n/a']
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.
   
   elif x=='Curtain Mullion':
      Description=['Curtain mullion']
      NEOM_Component_Description=['Curtain Mullion']
      Ifc_Entity=['IfcMember']
      Ifc_Enumeration=['MULLION']
      COBieComponentDescription=['n/a']
      NEOM_Operations_Class=['Not operationally significant']
      IfcExportAs=['IfcMember.MULLION']
      NEOM_Clash_Test_Code=['ARC.01']
      COBieSystemName=['n/a']
      COBieSystemDescription=['n/a']    
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.

   elif x=='Column':
      Description=['Column cladding', 'Column protection', 'Column skirting board', 'Decorative column']
      NEOM_Component_Description=['Column Cladding', 'Column Guards', 'Column Skirting Board', 'Decorative Column']
      Ifc_Entity=['IfcCovering', 'IfcCovering', 'IfcCovering', 'IfcColumn']
      Ifc_Enumeration=['CLADDING', 'USERDEFINED - Column guards', 'SKIRTINGBOARD', 'COLUMN']
      COBieComponentDescription=['n/a', 'n/a', 'n/a', 'n/a']
      NEOM_Operations_Class=['Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant']
      IfcExportAs=['IfcCovering.CLADDING', 'IfcCovering.USERDEFINED', 'IfcCovering.SKIRTINGBOARD', 'IfcColumn.COLUMN']
      NEOM_Clash_Test_Code=['ARC.08', 'ARC.08', 'ARC.08', 'ARC.08']
      COBieSystemName=['n/a', 'n/a', 'n/a', 'n/a']
      COBieSystemDescription=['n/a', 'n/a', 'n/a', 'n/a']     
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.

   elif x=='Floor':
      Description=['Carpet flooring', 'Floor', 'Floor coping', 'Floor insulation', 'Floor membrane', 'Floor paving', 'Floor pedestals', 'Floor screed', 'Floor sidewalk', 'Floor stringers', 'Floor tiles', 'Floor topping', 'Floor wrapping', 'Geographic soil boring point', 'Geographic terrain', 'Geographic vegetation', 'Pavement flexible', 'Pavement rigid', 'Ramp flight spiral', 'Ramp flight straight', 'Ramp half turn ', 'Ramp quarter turn ', 'Ramp spiral ', 'Ramp straight run ', 'Ramp two quarter turn ', 'Ramp two straight run ', 'Ramp landing floor', 'Stair landing floor']
      NEOM_Component_Description=['Carpet Flooring', 'Floor', 'Floor Coping', 'Floor Insulation', 'Floor Membrane', 'Floor Paving', 'Floor Pedestals', 'Screed Flooring', 'Floor Sidewalk', 'Floor Stringers', 'Floor Tiles', 'Floor Topping', 'Floor Wrapping', 'Geographic Soil Boring Point', 'Geographic Terrain', 'Geographic Vegetation', 'Flexible Pavement', 'Rigid Pavement', 'Ramp Flight Spiral', 'Ramp Flight Straight', 'Half Turn Ramp', 'Quarter Turn Ramp', 'Spiral Ramp', 'Straight Run Ramp', 'Two Quarter Turn Rramp', 'Two Straight Run Ramp', 'Ramp Landing Floor', 'Stair Landing Floor']
      Ifc_Entity=['IfcCovering', 'IfcCovering', 'IfcCovering', 'IfcCovering', 'IfcCovering', 'IfcSlab', 'IfcCovering', 'IfcCovering', 'IfcSlab', 'IfcCovering', 'IfcCovering', 'IfcCovering', 'IfcCovering', 'IfcGeographicElement', 'IfcGeographicElement', 'IfcGeographicElement', 'IfcPavement', 'IfcPavement', 'IfcRampFlight', 'IfcRampFlight', 'IfcRamp', 'IfcRamp', 'IfcRamp', 'IfcRamp', 'IfcRamp', 'IfcRamp', 'IfcSlab', 'IfcSlab']
      Ifc_Enumeration=['USERDEFINED - Carpet flooring', 'FLOORING', 'COPING', 'INSULATION', 'MEMBRANE', 'PAVING', 'USERDEFINED - Floor pedestals', 'USERDEFINED - Screed flooring', 'SIDEWALK', 'USERDEFINED - Floor stringers', 'USERDEFINED - Floor tiles', 'TOPPING', 'WRAPPING', 'SOIL_BORING_POINT', 'TERRAIN', 'VEGETATION', 'FLEXIBLE', 'RIGID', 'SPIRAL', 'STRAIGHT', 'HALF_TURN_RAMP', 'QUARTER_TURN_RAMP', 'SPIRAL_RAMP', 'STRAIGHT_RUN_RAMP', 'TWO_QUARTER_TURN_RAMP', 'TWO_STRAIGHT_RUN_RAMP', 'LANDING', 'LANDING']
      COBieComponentDescription=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      NEOM_Operations_Class=['Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant']
      IfcExportAs=['IfcCovering.USERDEFINED', 'IfcCovering.FLOORING', 'IfcCovering.COPING', 'IfcCovering.INSULATION', 'IfcCovering.MEMBRANE', 'IfcSlab.PAVING', 'IfcCovering.USERDEFINED', 'IfcCovering.USERDEFINED', 'IfcSlab.SIDEWALK', 'IfcCovering.USERDEFINED', 'IfcCovering.USERDEFINED', 'IfcCovering.TOPPING', 'IfcCovering.WRAPPING', 'IfcGeographicElement.USERDEFINED', 'IfcGeographicElement.USERDEFINED', 'IfcGeographicElement.USERDEFINED', 'IfcPavement.FLEXIBLE', 'IfcPavement.RIGID', 'IfcRampFlight.SPIRAL', 'IfcRampFlight.STRAIGHT', 'IfcRamp.HALF_TURN_RAMP', 'IfcRamp.QUARTER_TURN_RAMP', 'IfcRampFlight.SPIRAL_RAMP', 'IfcRamp.STRAIGHT_RUN_RAMP', 'IfcRamp.TWO_QUARTER_TURN_RAMP', 'IfcRamp.TWO_STRAIGHT_RUN_RAMP', 'IfcSlab.LANDING', 'IfcSlab.LANDING']
      NEOM_Clash_Test_Code=['IDN.05', 'IDN.05', 'IDN.05', 'IDN.05', 'IDN.05', 'LAN.05', 'IDN.05', 'IDN.05', 'LAN.05', 'IDN.05', 'IDN.05', 'IDN.05', 'IDN.05', 'IDN.05', 'IDN.05', 'IDN.05', 'IDN.05', 'IDN.05', 'ARC.11', 'ARC.11', 'ARC.11', 'ARC.11', 'ARC.11', 'ARC.11', 'ARC.11', 'ARC.11', 'ARC.11', 'ARC.06']
      COBieSystemName=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      COBieSystemDescription=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.

   elif x=='Railing':
      Description=['Balustrade', 'Chain link fence', 'Fence', 'Guardrail', 'Handrail', 'Slat fence', 'Welded fence']
      NEOM_Component_Description=['Balustrade', 'Chain Link Fence', 'Fence', 'Guardrail', 'Handrail', 'Slat Fence', 'Welded Fence']
      Ifc_Entity=['IfcRailing', 'IfcRailing', 'IfcRailing', 'IfcRailing', 'IfcRailing', 'IfcRailing', 'IfcRailing']
      Ifc_Enumeration=['BALUSTRADE', 'FENCE', 'FENCE', 'GUARDRAIL', 'HANDRAIL', 'FENCE', 'FENCE']
      COBieComponentDescription=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      NEOM_Operations_Class=['Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant']
      IfcExportAs=['IfcRailing.BALUSTRADE', 'IfcRailing.FENCE', 'IfcRailing.FENCE', 'IfcRailing.GUARDRAIL', 'IfcRailing.HANDRAIL', 'IfcRailing.FENCE', 'IfcRailing.FENCE']
      NEOM_Clash_Test_Code=['ARC.03', 'LAN.01', 'LAN.01', 'LAN.01', 'ARC.03', 'LAN.01', 'LAN.01']
      COBieSystemName=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      COBieSystemDescription=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.
   
   elif x=='Ramp':
      Description=['Half turn ramp', 'Quarter turn ramp', 'Ramp flight spiral', 'Ramp flight straight', 'Ramp landing floor', 'Spiral ramp', 'Straight run ramp', 'Two quarter turn ramp', 'Two straight run ramp']
      NEOM_Component_Description=['Half Turn Ramp', 'Quarter Turn Ramp', 'Ramp Flight Spiral', 'Ramp Flight Straight', 'Ramp Landing Floor', 'Spiral Ramp', 'Straight Run Ramp', 'Two Quarter Turn Ramp', 'Two Straight Run Ramp']
      Ifc_Entity=['IfcRamp', 'IfcRamp', 'IfcRampFlight', 'IfcRampFlight', 'IfcSlab', 'IfcRamp', 'IfcRamp', 'IfcRamp', 'IfcRamp']
      Ifc_Enumeration=['HALF_TURN_RAMP', 'QUARTER_TURN_RAMP', 'SPIRAL', 'STRAIGHT', 'LANDING', 'SPIRAL_RAMP', 'STRAIGHT_RUN_RAMP', 'TWO_QUARTER_TURN_RAMP', 'TWO_STRAIGHT_RUN_RAMP']
      COBieComponentDescription=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']  
      NEOM_Operations_Class=['Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant']
      IfcExportAs=['IfcRamp.HALF_TURN_RAMP', 'IfcRamp.QUARTER_TURN_RAMP', 'IfcRampFlight.SPIRAL', 'IfcRampFlight.STRAIGHT', 'IfcSlab.LANDING', 'IfcRampFlight.SPIRAL_RAMP', 'IfcRamp.STRAIGHT_RUN_RAMP', 'IfcRamp.TWO_QUARTER_TURN_RAMP', 'IfcRamp.TWO_STRAIGHT_RUN_RAMP']
      NEOM_Clash_Test_Code=['ARC.11', 'ARC.11', 'ARC.11', 'ARC.11', 'ARC.11', 'ARC.11', 'ARC.11', 'ARC.11', 'ARC.11']
      COBieSystemName=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']  
      COBieSystemDescription=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']    
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.

   elif x=='Roof':
      Description=['Barrel roof', 'Butterfly roof', 'Dome roof', 'Flat roof', 'Freeform roof', 'Gable roof', 'Gambrel roof', 'Hip roof', 'Hipped gable roof', 'Mansard roof', 'Pavilion roof', 'Rainbow roof', 'Roof covering', 'Roof insulation', 'Roof membrane', 'Roof molding', 'Roof coping', 'Shed roof', 'Roof topping', 'Pent House']
      NEOM_Component_Description=['Barrel Roof', 'Butterfly Roof', 'Dome Roof', 'Flat Roof', 'Freeform Roof', 'Gable Roof', 'Gambrel Roof', 'Hip Roof', 'Hipped Gable Roof', 'Mansard Roof', 'Pavilion Roof', 'Rainbow Roof', 'Roof Covering', 'Roof Insulation', 'Roof Membrane', 'Roof Molding', 'Roof Coping', 'Shed Roof', 'Roof Topping', 'Pent House']
      Ifc_Entity=['IfcRoof', 'IfcRoof', 'IfcRoof', 'IfcRoof', 'IfcRoof', 'IfcRoof', 'IfcRoof', 'IfcRoof', 'IfcRoof', 'IfcRoof', 'IfcRoof', 'IfcRoof', 'IfcCovering', 'IfcCovering', 'IfcCovering', 'IfcCovering', 'IfcCovering', 'IfcRoof', 'IfcCovering', 'IfcRoof']
      Ifc_Enumeration=['BARREL_ROOF', 'BUTTERFLY_ROOF', 'DOME_ROOF', 'FLAT_ROOF', 'FREEFORM', 'GABLE_ROOF', 'GAMBREL_ROOF', 'HIP_ROOF', 'HIPPED_GABLE_ROOF', 'MANSARD_ROOF', 'PAVILION_ROOF', 'RAINBOW_ROOF', 'ROOFING', 'INSULATION', 'MEMBRANE', 'MOLDING', 'COPING', 'SHED_ROOF', 'TOPPING', 'PENT_HOUSE']
      COBieComponentDescription=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      NEOM_Operations_Class=['Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant']
      IfcExportAs=['IfcRoof.BARREL_ROOF', 'IfcRoof.BUTTERFLY_ROOF', 'IfcRoof.DOME_ROOF', 'IfcRoof.FLAT_ROOF', 'IfcRoof.FREEFORM', 'IfcRoof.GABLE_ROOF', 'IfcRoof.GAMBREL_ROOF', 'IfcRoof.HIP_ROOF', 'IfcRoof.HIPPED_GABLE_ROOF', 'IfcRoof.MANSARD_ROOF', 'IfcRoof.PAVILION_ROOF', 'IfcRoof.RAINBOW_ROOF', 'IfcCovering.ROOFING', 'IfcCovering.INSULATION', 'IfcCovering.MEMBRANE', 'IfcCovering.MOLDING', 'IfcCovering.COPING', 'IfcRoof.SHED_ROOF', 'IfcCovering.TOPPING', 'IfcRoof.PENT_HOUSE']
      NEOM_Clash_Test_Code=['ARC.04', 'ARC.04', 'ARC.04', 'ARC.04', 'ARC.04', 'ARC.04', 'ARC.04', 'ARC.04', 'ARC.04', 'ARC.04', 'ARC.04', 'ARC.04', 'ARC.04', 'ARC.04', 'ARC.04', 'ARC.04', 'ARC.04', 'ARC.04', 'ARC.04', 'ARC.04']  
      COBieSystemName=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      COBieSystemDescription=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']    
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.

   elif x=='Stair Run':
      Description=['Stair flight curved', 'Stair flight freedom', 'Stair flight spiral', 'Stair flight straight', 'Stair flight winder']
      NEOM_Component_Description=['Curved Stair Flight', 'Freedom Stair Flight', 'Spiral Stair Flight', 'Straight Stair Flight', 'Winder Stair Flight']
      Ifc_Entity=['IfcStairFlight', 'IfcStairFlight', 'IfcStairFlight', 'IfcStairFlight', 'IfcStairFlight']
      Ifc_Enumeration=['CURVED', 'FREEFORM', 'SPIRAL', 'STRAIGHT', 'WINDER']
      COBieComponentDescription=['n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      NEOM_Operations_Class=['Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant']
      IfcExportAs=['IfcStairFlight.CURVED', 'IfcStairFlight.FREEFORM', 'IfcStairFlight.SPIRAL', 'IfcStairFlight.STRAIGHT', 'IfcStairFlight.WINDER']
      NEOM_Clash_Test_Code=['ARC.06', 'ARC.06', 'ARC.06', 'ARC.06', 'ARC.06']
      COBieSystemName=['n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      COBieSystemDescription=['n/a', 'n/a', 'n/a', 'n/a', 'n/a']     
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.
   
   elif x=='Stair Landing':
      Description=['Stair landing floor']
      NEOM_Component_Description=['Stair Landing Floor']
      Ifc_Entity=['IfcSlab']
      Ifc_Enumeration=['LANDING']
      COBieComponentDescription=['n/a']
      NEOM_Operations_Class=['Not operationally significant']
      IfcExportAs=['IfcSlab.LANDING']
      NEOM_Clash_Test_Code=['ARC.06']
      COBieSystemName=['n/a']
      COBieSystemDescription=['n/a']
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.
   
   elif x=='Stair':
      Description=['Curved run stair', 'Double return stair', 'Half turn stair', 'Half winding stair', 'Quarter turn stair', 'Quarter winding stair', 'Spiral stair', 'Straight run stair', 'Three quarter turn stair', 'Three quarter winding stair', 'Two curved run stair', 'Two quarter turn stair', 'Two quarter winding stair', 'Two straight run stair']
      NEOM_Component_Description=['Curved Run Stair', 'Double Return Stair', 'Half Turn Stair', 'Half Winding Stair', 'Quarter Turn Stair', 'Quarter Winding Stair', 'Spiral Stair', 'Straight Run Stair', 'Three Quarter Turn Stair', 'Three Quarter Winding Stair', 'Two Curved Run Stair', 'Two Quarter Turn Stair', 'Two Quarter Winding Stair', 'Two Straight Run Stair']
      Ifc_Entity=['IfcStair', 'IfcStair', 'IfcStair', 'IfcStair', 'IfcStair', 'IfcStair', 'IfcStair', 'IfcStair', 'IfcStair', 'IfcStair', 'IfcStair', 'IfcStair', 'IfcStair', 'IfcStair']
      Ifc_Enumeration=['CURVED_RUN_STAIR', 'DOUBLE_RETURN_STAIR', 'HALF_TURN_STAIR', 'HALF_WINDING_STAIR', 'QUARTER_TURN_STAIR', 'QUARTER_WINDING_STAIR', 'SPIRAL_STAIR', 'STRAIGHT_RUN_STAIR', 'THREE_QUARTER_TURN_STAIR', 'THREE_QUARTER_WINDING_STAIR', 'TWO_CURVED_RUN_STAIR', 'TWO_QUARTER_TURN_STAIR', 'TWO_QUARTER_WINDING_STAIR', 'TWO_STRAIGHT_RUN_STAIR']
      COBieComponentDescription=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      NEOM_Operations_Class=['Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant']
      IfcExportAs=['IfcStair.CURVED_RUN_STAIR', 'IfcStair.DOUBLE_RETURN_STAIR', 'IfcStair.HALF_TURN_STAIR', 'IfcStair.HALF_WINDING_STAIR', 'IfcStair.QUARTER_TURN_STAIR', 'IfcStair.QUARTER_WINDING_STAIR', 'IfcStair.SPIRAL_STAIR', 'IfcStair.STRAIGHT_RUN_STAIR', 'IfcStair.THREE_QUARTER_TURN_STAIR', 'IfcStair.THREE_QUARTER_WINDING_STAIR', 'IfcStair.TWO_CURVED_RUN_STAIR', 'IfcStair.TWO_QUARTER_TURN_STAIR', 'IfcStair.TWO_QUARTER_WINDING_STAIR', 'IfcStair.TWO_STRAIGHT_RUN_STAIR']
      NEOM_Clash_Test_Code=['ARC.06', 'ARC.06', 'ARC.06', 'ARC.06', 'ARC.06', 'ARC.06', 'ARC.06', 'ARC.06', 'ARC.06', 'ARC.06', 'ARC.06', 'ARC.06', 'ARC.06', 'ARC.06']
      COBieSystemName=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      COBieSystemDescription=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.

   elif x=='Door':
      Description=['Access panel external', 'Access panel internal', 'Bifold external door', 'Bifold internal door', 'Boom barrier door', 'Double acting external door', 'Double acting internal door', 'Double egress external door', 'Double egress internal door', 'Gate', 'Generic external door', 'Generic internal door', 'One way hinged external door', 'One way hinged internal door', 'Opening as door', 'Revolving external door', 'Revolving internal door', 'Rolling shutter external door', 'Rolling shutter internal door', 'Sliding external door', 'Sliding internal door', 'Trapdoor external', 'Trapdoor internal', 'Turnstile external door', 'Turnstile internal door']
      NEOM_Component_Description=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'Opening As Door', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a'] 
      Ifc_Entity=['IfcDoor', 'IfcDoor', 'IfcDoor', 'IfcDoor', 'IfcDoor', 'IfcDoor', 'IfcDoor', 'IfcDoor', 'IfcDoor', 'IfcDoor', 'IfcDoor', 'IfcDoor', 'IfcDoor', 'IfcDoor', 'IfcOpeningElement', 'IfcDoor', 'IfcDoor', 'IfcDoor', 'IfcDoor', 'IfcDoor', 'IfcDoor', 'IfcDoor', 'IfcDoor', 'IfcDoor', 'IfcDoor']
      Ifc_Enumeration=['USERDEFINED - Access hatch', 'USERDEFINED - Access hatch', 'DOOR', 'DOOR', 'BOOM_BARRIER', 'DOOR', 'DOOR', 'DOOR', 'DOOR', 'GATE', 'DOOR', 'DOOR', 'DOOR', 'DOOR', 'OPENING', 'DOOR', 'DOOR', 'DOOR', 'DOOR', 'DOOR', 'DOOR', 'TRAPDOOR', 'TRAPDOOR', 'TURNSTILE', 'TURNSTILE']
      COBieComponentDescription=['Access panel external', 'Access panel internal', 'Bifold external door', 'Bifold internal door', 'Boom barrier door', 'Double acting external door', 'Double acting internal door', 'Double egress external door', 'Double egress internal door', 'Gate', 'Generic external door', 'Generic internal door', 'One way hinged external door', 'One way hinged internal door', 'Opening as door', 'Revolving external door', 'Revolving internal door', 'Rolling shutter external door', 'Rolling shutter internal door', 'Sliding external door', 'Sliding internal door', 'Trapdoor external', 'Trapdoor internal', 'Turnstile external door', 'Turnstile internal door']
      NEOM_Operations_Class=['Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Not operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant']
      IfcExportAs=['IfcDoor.USERDEFINED', 'IfcDoor.USERDEFINED', 'IfcDoor.DOOR', 'IfcDoor.DOOR', 'IfcDoor.BOOM_BARRIER', 'IfcDoor.DOOR', 'IfcDoor.DOOR', 'IfcDoor.DOOR', 'IfcDoor.DOOR', 'IfcDoor.GATE', 'IfcDoor.DOOR', 'IfcDoor.DOOR', 'IfcDoor.DOOR', 'IfcDoor.DOOR', 'IfcOpeningElement.OPENING', 'IfcDoor.DOOR', 'IfcDoor.DOOR', 'IfcDoor.DOOR', 'IfcDoor.DOOR', 'IfcDoor.DOOR', 'IfcDoor.DOOR', 'IfcDoor.TRAPDOOR', 'IfcDoor.TRAPDOOR', 'IfcDoor.TURNSTILE', 'IfcDoor.TURNSTILE']
      NEOM_Clash_Test_Code=['ARC.02', 'ARC.02', 'ARC.02', 'ARC.02', 'ARC.02', 'ARC.02', 'ARC.02', 'ARC.02', 'ARC.02', 'LAN.01', 'ARC.02', 'ARC.02', 'ARC.02', 'ARC.02', 'n/a', 'ARC.02', 'ARC.02', 'ARC.02', 'ARC.02', 'ARC.02', 'ARC.02', 'ARC.02', 'ARC.02', 'ARC.02', 'ARC.02']
      COBieSystemName=['External partition system', 'Internal partition system', 'External partition system', 'Internal partition system', 'External partition system', 'External partition system', 'Internal partition system', 'External partition system', 'Internal partition system', 'External partition system', 'External partition system', 'Internal partition system', 'External partition system', 'Internal partition system', 'n/a', 'External partition system', 'Internal partition system', 'External partition system', 'Internal partition system', 'External partition system', 'Internal partition system', 'External partition system', 'Internal partition system', 'External partition system', 'Internal partition system']
      COBieSystemDescription=['External partition system', 'Internal partition system', 'External partition system', 'Internal partition system', 'External partition system', 'External partition system', 'Internal partition system', 'External partition system', 'Internal partition system', 'External partition system', 'External partition system', 'Internal partition system', 'External partition system', 'Internal partition system', 'n/a', 'External partition system', 'Internal partition system', 'External partition system', 'Internal partition system', 'External partition system', 'Internal partition system', 'External partition system', 'Internal partition system', 'External partition system', 'Internal partition system']
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.
   
   elif x=='Window':
      Description=['Lightdome', 'Fixed external window', 'Fixed internal window', 'Hung external window', 'Hung internal window', 'Opening as window', 'Revolving external window', 'Revolving internal window', 'Rolling shutter external window', 'Rolling shutter internal window', 'Skylight', 'Sliding external window', 'Sliding internal window']
      NEOM_Component_Description=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'Opening As Window', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      Ifc_Entity=['IfcWindow', 'IfcWindow', 'IfcWindow', 'IfcWindow', 'IfcWindow', 'IfcOpeningElement', 'IfcWindow', 'IfcWindow', 'IfcWindow', 'IfcWindow', 'IfcWindow', 'IfcWindow', 'IfcWindow']
      Ifc_Enumeration=['LIGHTDOME', 'WINDOW', 'WINDOW', 'WINDOW', 'WINDOW', 'OPENING', 'WINDOW', 'WINDOW', 'WINDOW', 'WINDOW', 'SKYLIGHT', 'WINDOW', 'WINDOW']
      COBieComponentDescription=['Lightdome', 'Fixed external window', 'Fixed internal window', 'Hung external window', 'Hung internal window', 'Opening as window', 'Revolving external window', 'Revolving internal window', 'Rolling shutter external window', 'Rolling shutter internal window', 'Skylight', 'Sliding external window', 'Sliding internal window']
      NEOM_Operations_Class=['Maintainable', 'Maintainable', 'Maintainable', 'Maintainable', 'Maintainable', 'Not operationally significant', 'Maintainable', 'Maintainable', 'Maintainable', 'Maintainable', 'Maintainable', 'Maintainable', 'Maintainable']
      IfcExportAs=['IfcWindow.LIGHTDOME', 'IfcWindow.WINDOW', 'IfcWindow.WINDOW', 'IfcWindow.WINDOW','IfcWindow.WINDOW','IfcOpeningElement.OPENING', 'IfcWindow.WINDOW', 'IfcWindow.WINDOW','IfcWindow.WINDOW','IfcWindow.WINDOW','IfcWindow.SKYLIGHT','IfcWindow.WINDOW','IfcWindow.WINDOW']
      NEOM_Clash_Test_Code=['ARC.07', 'ARC.07','ARC.07', 'ARC.07', 'ARC.07', 'n/a','ARC.07', 'ARC.07','ARC.07', 'ARC.07', 'ARC.07', 'ARC.07', 'ARC.07']
      COBieSystemName=['External roof system', 'External partition system', 'Internal partition system', 'External partition system', 'Internal partition system', 'n/a', 'External partition system', 'Internal partition system', 'External partition system', 'Internal partition system', 'External roof system', 'External partition system', 'Internal partition system']
      COBieSystemDescription=['External roof system', 'External partition system', 'Internal partition system', 'External partition system', 'Internal partition system', 'n/a', 'External partition system', 'Internal partition system', 'External partition system', 'Internal partition system', 'External roof system', 'External partition system', 'Internal partition system']
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.
   
   elif x=='Parking':
      Description=['Boom barrier door', 'Parking bumper', 'Protection crash cushion', 'Traffic calming device']
      NEOM_Component_Description=['n/a', 'Parking Bumper', 'Protection Crash Cushion', 'Traffic Calming Device']
      Ifc_Entity=['IfcDoor', 'IfcImpactProtectionDevice', 'IfcImpactProtectionDevice', 'IfcElementAssembly']
      Ifc_Enumeration=['BOOM_BARRIER', 'BUMPER', 'CRASHCUSHION', 'TRAFFIC_CALMING_DEVICE']
      COBieComponentDescription=['Boom barrier door', 'n/a', 'n/a', 'n/a']
      NEOM_Operations_Class=['Operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant']
      IfcExportAs=['IfcDoor.BOOM_BARRIER', 'IfcImpactProtectionDevice.BUMPER', 'IfcImpactProtectionDevice.CRASHCUSHION', 'IfcElementAssembly.TRAFFIC_CALMING_DEVICE']
      NEOM_Clash_Test_Code=['ARC.02', 'LAN.04', 'LAN.04', 'LAN.04']
      COBieSystemName=['External partition system', 'n/a', 'n/a', 'n/a']
      COBieSystemDescription=['External partition system', 'n/a', 'n/a', 'n/a']  
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.
   
   elif x=='Specialty Equipment':
      Description=['Advertising panel', 'Bldg element bin composting', 'Bldg element bin general', 'Bldg element bin recycling', 'Bldg element bollard', 'Bldg element cavity barrier', 'Bldg element fire / smoke curtain', 'Bldg element soap dispenser', 'Bldg element swimming pool', 'Bldg element toilet fixture', 'Chimney flue', 'Chimney pot', 'Conveyor baggage', 'Conveyor belt', 'Conveyor bucket', 'Conveyor chute', 'Conveyor escape chutes', 'Conveyor linen chutes', 'Conveyor refuse chutes', 'Conveyor screw', 'Craneway', 'Elec. cold room', 'Elec. cooker', 'Elec. dishwasher', 'Elec. freestanding electric heater', 'Elec. freestanding fan', 'Elec. ice making machine', 'Elec.freestanding water cooler', 'Elec.freestanding water heater', 'Elec.freezer', 'Elec.fridge freezer', 'Elec.hand dryer', 'Elec.kitchen machine', 'Elec.microwave', 'Elec.photocopier', 'Elec.refrigerator', 'Elec.tumble dryer machine', 'Elec.vending machine', 'Elec.washing machine', 'TV', 'Telephone', 'Elevator', 'Escalator', 'Gym equipment', 'Ladder', 'Medical equipment', 'Office equipment', 'Protection bumper', 'Protection crash cushion', 'Protection for column', 'Safety cage ladder', 'Security equipment', 'Solar panel', 'Specialty equipment', 'Travelator / Moving walkway', 'Window treatments (curtain, Blind, etc.)', 'Fall Arrest']
      NEOM_Component_Description=['Advertising Panel', 'Composting Bin', 'General Bin', 'Recycling Bin', 'Bollard', 'Cavity Barrier', 'Fire / Smoke Curtain', 'Soap Dispenser', 'Swimming Pool', 'Toilet Fixture', 'Chimney Flue', 'Chimney Pot', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'Gym Equipment', 'Ladder', 'Medical Equipment', 'Office Equipment', 'Protection Bumper', 'Protection Crash Cushion', 'Column Guards', 'Safety Cage Ladder', 'Security Equipment', 'n/a', 'Specialty Equipment', 'n/a', 'Window Treatments', 'Fall Arrest']
      Ifc_Entity=['IfcSign', 'IfcBuildingElementProxy', 'IfcBuildingElementProxy', 'IfcBuildingElementProxy', 'IfcBuildingElementProxy', 'IfcBuildingElementPart', 'IfcBuildingElementProxy', 'IfcBuildingElementProxy', 'IfcBuildingElementProxy', 'IfcBuildingElementProxy', 'IfcChimney', 'IfcChimney', 'IfcConveyorSegment', 'IfcConveyorSegment', 'IfcConveyorSegment', 'IfcConveyorSegment', 'IfcConveyorSegment', 'IfcConveyorSegment', 'IfcConveyorSegment', 'IfcConveyorSegment', 'IfcTransportElement', 'IfcElectricAppliance', 'IfcElectricAppliance', 'IfcElectricAppliance', 'IfcElectricAppliance', 'IfcElectricAppliance', 'IfcElectricAppliance', 'IfcElectricAppliance', 'IfcElectricAppliance', 'IfcElectricAppliance', 'IfcElectricAppliance', 'IfcElectricAppliance', 'IfcElectricAppliance', 'IfcElectricAppliance', 'IfcElectricAppliance', 'IfcElectricAppliance', 'IfcElectricAppliance', 'IfcElectricAppliance', 'IfcElectricAppliance', 'IfcElectricAppliance', 'IfcElectricAppliance', 'IfcTransportElement', 'IfcTransportElement', 'IfcFurniture', 'IfcTransportElement', 'IfcFurniture', 'IfcFurniture', 'IfcImpactProtectionDevice', 'IfcImpactProtectionDevice', 'IfcCovering', 'IfcBuildingElementPart', 'IfcFurniture', 'IfcSolarDevice', 'IfcBuildingElementProxy', 'IfcTransportElement', 'IfcBuildingElementProxy', 'IfcBuildingElementPart']
      Ifc_Enumeration=['USERDEFINED - Advertising panel', 'USERDEFINED - Composting bin', 'USERDEFINED - General bin', 'USERDEFINED - Recycling bin', 'USERDEFINED - Bollard', 'USERDEFINED - Cavity Barrier', 'USERDEFINED - Fire / Smoke curtain', 'USERDEFINED - Soap Dispenser', 'USERDEFINED - Swimming pool', 'USERDEFINED - Toilet fixture', 'USERDEFINED - Flue', 'USERDEFINED - Chimney pot', 'USERDEFINED - Baggage conveyor', 'BELTCONVEYOR', 'BUCKETCONVEYOR', 'CHUTECONVEYOR', 'USERDEFINED - Escape chutes conveyor', 'USERDEFINED - Linen chutes conveyor', 'USERDEFINED - Refuse chutes conveyor', 'SCREWCONVEYOR', 'CRANEWAY', 'USERDEFINED - Cold room', 'ELECTRICCOOKER', 'DISHWASHER', 'FREESTANDINGELECTRICHEATER', 'FREESTANDINGFAN', 'USERDEFINED - Ice making machine', 'FREESTANDINGWATERCOOLER', 'FREESTANDINGWATERHEATER', 'FREEZER', 'FRIDGE_FREEZER', 'HANDDRYER', 'KITCHENMACHINE', 'MICROWAVE', 'PHOTOCOPIER', 'REFRIGERATOR', 'TUMBLEDRYER', 'VENDINGMACHINE', 'WASHINGMACHINE', 'USERDEFINED - TV', 'USERDEFINED - Telephone', 'ELEVATOR', 'ESCALATOR', 'USERDEFINED - Gym equipment', 'LADDER', 'USERDEFINED - Medical equipment', 'USERDEFINED - Office equipment', 'BUMPER', 'CRASHCUSHION', 'USERDEFINED - Column guards', 'SAFETYCAGE', 'USERDEFINED - Security equipment', 'SOLARPANEL', 'USERDEFINED - Specialty equipment', 'MOVINGWALKWAY', 'USERDEFINED - Window treatments', 'USERDEFINED - Fall Arrest']
      COBieComponentDescription=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'Baggage conveyor', 'Belt conveyor', 'Bucket conveyor', 'Chute conveyor', 'Escape chutes conveyor', 'Linen chutes conveyor', 'Refuse chutes conveyor', 'Screw conveyor', 'Craneway', 'Cold room', 'Electric cooker', 'Dishwasher', 'Freestanding electric heater', 'Freestanding fan', 'Ice making machine', 'Freestanding water cooler', 'Freestanding water heater', 'Freezer', 'Fridge freezer', 'Hand dryer', 'Kitchen machine', 'Microwave', 'Photocopier', 'Refrigerator', 'Tumble dryer machine', 'Vending machine', 'Washing machine', 'Television', 'Telephone', 'Elevator', 'Escalator', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'Solar panel', 'n/a', 'Travelator / Moving walkway', 'n/a', 'Fall Arrest']
      NEOM_Operations_Class=['Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Maintainable', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Operationally significant', 'Maintainable', 'Maintainable', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Maintainable', 'Not operationally significant', 'Maintainable', 'Not operationally significant', 'Operationally significant']
      IfcExportAs=['IfcSign.USERDEFINED', 'IfcBuildingElementProxy.USERDEFINED', 'IfcBuildingElementProxy.USERDEFINED', 'IfcBuildingElementProxy.USERDEFINED', 'IfcBuildingElementProxy.USERDEFINED', 'IfcBuildingElementPart.USERDEFINED', 'IfcBuildingElementProxy.USERDEFINED', 'IfcBuildingElementProxy.USERDEFINED', 'IfcBuildingElementProxy.USERDEFINED', 'IfcBuildingElementProxy.USERDEFINED', 'IfcChimney.USERDEFINED - Flue', 'IfcChimney.USERDEFINED - Chimney pot', 'IfcConveyorSegment.USERDEFINED', 'IfcConveyorSegment.BELTCONVEYOR', 'IfcConveyorSegment.BUCKETCONVEYOR', 'IfcConveyorSegment.CHUTECONVEYOR', 'IfcConveyorSegment.USERDEFINED', 'IfcConveyorSegment.USERDEFINED', 'IfcConveyorSegment.USERDEFINED', 'IfcConveyorSegment.SCREWCONVEYOR', 'IfcTransportElement.CRANEWAY', 'IfcElectricAppliance.USERDEFINED', 'IfcElectricAppliance.ELECTRICCOOKER', 'IfcElectricAppliance.DISHWASHER', 'IfcElectricAppliance.FREESTANDINGELECTRICHEATER', 'IfcElectricAppliance.FREESTANDINGFAN', 'IfcElectricAppliance.USERDEFINED', 'IfcElectricAppliance.FREESTANDINGWATERCOOLER', 'IfcElectricAppliance.FREESTANDINGWATERHEATER', 'IfcElectricAppliance.FREEZER', 'IfcElectricAppliance.FRIDGE_FREEZER', 'IfcElectricAppliance.HANDDRYER', 'IfcElectricAppliance.KITCHENMACHINE', 'IfcElectricAppliance.MICROWAVE', 'IfcElectricAppliance.PHOTOCOPIER', 'IfcElectricAppliance.REFRIGERATOR', 'IfcElectricAppliance.TUMBLEDRYER', 'IfcElectricAppliance.VENDINGMACHINE', 'IfcElectricAppliance.WASHINGMACHINE', 'IfcConveyorSegment.USERDEFINED', 'IfcConveyorSegment.USERDEFINED', 'IfcTransportElement.ELEVATOR', 'IfcTransportElement.ESCALATOR', 'IfcFurniture.USERDEFINED', 'IfcTransportElement.LADDER', 'IfcFurniture.USERDEFINED', 'IfcFurniture.USERDEFINED', 'IfcImpactProtectionDevice.CRASHCUSHION', 'IfcImpactProtectionDevice.CRASHCUSHION', 'IfcCovering.USERDEFINED', 'IfcBuildingElementPart.SAFETYCAGE', 'IfcFurniture.USERDEFINED', 'IfcSolarDevice.SOLARPANEL', 'IfcBuildingElementProxy.USERDEFINED', 'IfcTransportElement.MOVINGWALKWAY', 'IfcFurniture.USERDEFINED', 'IfcBuildingElementPart.USERDEFINED']
      NEOM_Clash_Test_Code=['IDN.06', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.03', 'IDN.02', 'LAN.04', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'IDN.02', 'ARC.04']
      COBieSystemName=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'Conveying system', 'Conveying system', 'Conveying system', 'Conveying system', 'Conveying system', 'Conveying system', 'Conveying system', 'Conveying system', 'Conveying system', 'Electrical system', 'Electrical appliance system', 'Electrical appliance system', 'Electrical appliance system', 'Electrical appliance system', 'Equipment system', 'Electrical appliance system', 'Electrical appliance system', 'Electrical appliance system', 'Electrical appliance system', 'Electrical appliance system', 'Electrical appliance system', 'Electrical appliance system', 'Equipment system', 'Electrical appliance system', 'Electrical appliance system', 'Equipment system', 'Electrical appliance system', 'Electronic Device', 'Electronic Device', 'Conveying system', 'Conveying system', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'Sustainable system', 'n/a', 'Conveying system', 'n/a', 'Safety system']
      COBieSystemDescription=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'Conveying system', 'Conveying system', 'Conveying system', 'Conveying system', 'Conveying system', 'Conveying system', 'Conveying system', 'Conveying system', 'Conveying system', 'Electrical system', 'Electrical appliance system', 'Electrical appliance system', 'Electrical appliance system', 'Electrical appliance system', 'Equipment system', 'Electrical appliance system', 'Electrical appliance system', 'Electrical appliance system', 'Electrical appliance system', 'Electrical appliance system', 'Electrical appliance system', 'Electrical appliance system', 'Equipment system', 'Electrical appliance system', 'Electrical appliance system', 'Equipment system', 'Electrical appliance system', 'Electronic Device', 'Electronic Device', 'Conveying system', 'Conveying system', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'Sustainable system', 'n/a', 'Conveying system', 'n/a', 'Safety system']
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.
   
   elif x=='Planting':
      Description=['Bedding', 'Bush', 'External potted plant', 'Grasses', 'Green roof planting', 'Internal potted plant', 'Planted green wall', 'Planter', 'Shrub', 'Tree', 'Groundcover', 'Succulents']
      NEOM_Component_Description=['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
      Ifc_Entity=['IfcPlant', 'IfcPlant', 'IfcPlant', 'IfcPlant', 'IfcPlant', 'IfcPlant', 'IfcPlant', 'IfcPlant', 'IfcPlant', 'IfcPlant', 'IfcPlant', 'IfcPlant']
      Ifc_Enumeration=['USERDEFINED - Bedding', 'USERDEFINED - Bush', 'USERDEFINED - External potted plant', 'USERDEFINED - Grasses', 'USERDEFINED - Green roof planting', 'USERDEFINED - Internal potted plant', 'USERDEFINED - Planted green wall', 'USERDEFINED - Planter', 'USERDEFINED - Shrub', 'USERDEFINED - Tree', 'USERDEFINED - Groundcover', 'USERDEFINED - Succulents']
      COBieComponentDescription=['Bedding', 'Bush', 'External potted plant', 'Grasses', 'Green roof planting', 'Internal potted plant', 'Planted green wall', 'Planter', 'Shrub', 'Tree', 'Groundcover', 'Succulents']
      NEOM_Operations_Class=['Maintainable', 'Maintainable', 'Maintainable', 'Maintainable', 'Maintainable', 'Maintainable', 'Maintainable', 'Maintainable', 'Maintainable', 'Maintainable', 'Maintainable', 'Maintainable']
      IfcExportAs=['IfcPlant.USERDEFINED', 'IfcPlant.USERDEFINED', 'IfcPlant.USERDEFINED', 'IfcPlant.USERDEFINED', 'IfcPlant.USERDEFINED', 'IfcPlant.USERDEFINED', 'IfcPlant.USERDEFINED', 'IfcPlant.USERDEFINED', 'IfcPlant.USERDEFINED', 'IfcPlant.USERDEFINED', 'IfcPlant.USERDEFINED', 'IfcPlant.USERDEFINED']
      NEOM_Clash_Test_Code=['LAN.03', 'LAN.03', 'LAN.03', 'LAN.03', 'LAN.03', 'LAN.03', 'ARC.09', 'LAN.03', 'LAN.03', 'LAN.03', 'LAN.03', 'LAN.03']
      COBieSystemName=['Planting system', 'Planting system', 'Planting system', 'Planting system', 'Planting system', 'Planting system', 'Planting system', 'Planting system', 'Planting system', 'Planting system', 'Planting system', 'Planting system']
      COBieSystemDescription=['Planting system', 'Planting system', 'Planting system', 'Planting system', 'Planting system', 'Planting system', 'Planting system', 'Planting system', 'Planting system', 'Planting system', 'Planting system', 'Planting system'] 
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.
   
   elif x=='Structural Framing':
      Description=['Shading awning', 'Shading jalousie', 'Shading shutter', 'Standing Seam']
      NEOM_Component_Description=['Shading Awning', 'Shading Jalousie', 'Shading Shutter', 'Standing Seam']
      Ifc_Entity=['IfcShadingDevice', 'IfcShadingDevice', 'IfcShadingDevice', 'IfcMember']
      Ifc_Enumeration=['AWNING', 'JALOUSIE', 'SHUTTER', 'USERDEFINED-Standing Seam']
      COBieComponentDescription=['n/a', 'n/a', 'n/a', 'n/a']
      NEOM_Operations_Class=['Not operationally significant', 'Not operationally significant', 'Not operationally significant', 'Not operationally significant']
      IfcExportAs=['IfcShadingDevice.AWNING', 'IfcShadingDevice.JALOUSIE', 'IfcShadingDevice.SHUTTER', 'USERDEFINED-Standing Seam']
      NEOM_Clash_Test_Code=['ARC.10', 'ARC.10', 'ARC.10', 'ARC.10']
      COBieSystemName=['n/a', 'n/a', 'n/a', 'n/a']
      COBieSystemDescription=['n/a', 'n/a', 'n/a', 'n/a']
      c=[Description, NEOM_Component_Description, Ifc_Entity, Ifc_Enumeration, COBieComponentDescription, NEOM_Operations_Class, IfcExportAs, NEOM_Clash_Test_Code, COBieSystemName, COBieSystemDescription]
      c1=['Description', 'NEOM_Component_Description', 'Ifc_Entity', 'Ifc_Enumeration','COBie.Component.Description','NEOM_Operations_Class','IfcExportAs', 'NEOM_Clash_Test_Code','COBie.System.Name', 'COBie.System.Description']
#      print (len(Description),len(NEOM_Component_Description),len(Ifc_Entity),len(Ifc_Enumeration),len(NEOM_Operations_Class),len(IfcExportAs),len(NEOM_Clash_Test_Code))
      return c #returns a nested list of all the above lists.   

   else:
      print("work in progress to add more categories")


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
      script.get_output().update_progress(j1, len(c)-1)#Progress message.
      UpdateParameterValue(E1, z1, c1[j1]) #names should be converted to strings
      j1=j1+1

def UParam_1(x,instance):#This function filter the elements(type/instances), the parameter name and its value.

#   EI=instance#instance

   Description=GetLists(x)[0] #Description Categories

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

   j1=0

   while j1<len(c):#considering the list length will be same for all the parameters. the list contain parameter name
      z=c[j1] #Select the parameter name (which is a list) in nested list of parameters c.
      z1=z[0] # Selects the parameter value from the parameter name list
#      print(z1, c1[j1])
      script.get_output().update_progress(j1, len([c])-1)#Progress message.
      UpdateParameterValue(instance, z1, c1[j1]) #names should be converted to strings
      j1=j1+1

#Selecting Category
Category_Name = ['Wall','Curtain Wall','Curtain Panel','Curtain Mullion','Column','Floor','Railing', 'Ramp', 'Roof', 'Stair Run', 'Stair Landing', 'Stair','Door', 'Window', 'Parking','Specialty Equipment','Planting','Structural Framing', 'Exit']

Selected_Category = forms.CommandSwitchWindow.show(Category_Name, message='Select the category for filling iLOD parameters')

a=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsElementType()
b=FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType()

BWT=[]#Basic Wall Type
BWI=[]#Basic Wall Instance
BCWT=[]#Basic Curtain Wall Type
BCWI=[]#Basic Curtain Wall Instance

for i in a:#Family name can only be curtain wall/ basic wall and user can bring only these two types of name while making directshape.
   if str(i.FamilyName)!='Curtain Wall':
      BWT.append(i)
   elif str(i.FamilyName)=='Curtain Wall':
      BCWT.append(i)

for i in b:
   k=i.GetTypeId()
   j=doc.GetElement(k)
   if str(j.FamilyName)!='Curtain Wall':
      BWI.append(i)
   elif str(j.FamilyName)=='Curtain Wall':
      BCWI.append(i)


if Selected_Category == 'Wall':
   UParam('Wall',BWT,BWI)

elif Selected_Category == 'Curtain Wall':
   UParam('Curtain Wall',BCWT,BCWI)

elif Selected_Category == 'Curtain Panel':
   UParam_1('Curtain Panel',FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_CurtainWallPanels).WhereElementIsNotElementType())

elif Selected_Category == 'Curtain Mullion':
   UParam_1('Curtain Mullion',FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_CurtainWallMullions).WhereElementIsNotElementType())

elif Selected_Category == 'Column':
   UParam('Column',FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Columns).WhereElementIsElementType(),FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Columns).WhereElementIsNotElementType())

elif Selected_Category == 'Floor':
   UParam('Floor',FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsElementType(),FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsNotElementType())

elif Selected_Category == 'Railing':
   UParam('Railing',FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StairsRailing).WhereElementIsElementType(),FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StairsRailing).WhereElementIsNotElementType())

elif Selected_Category == 'Ramp':
   UParam('Ramp',FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Ramps).WhereElementIsElementType(),FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Ramps).WhereElementIsNotElementType())

elif Selected_Category == 'Roof':
   UParam('Roof',FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Roofs).WhereElementIsElementType(),FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Roofs).WhereElementIsNotElementType())

elif Selected_Category == 'Stair Run':
   UParam('Stair Run',FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StairsRuns).WhereElementIsElementType(),FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StairsRuns).WhereElementIsNotElementType())

elif Selected_Category == 'Stair Landing':
   UParam_1('Stair Landing',FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StairsLandings).WhereElementIsNotElementType())

elif Selected_Category == 'Stair':
   UParam('Stair',FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Stairs).WhereElementIsElementType(),FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Stairs).WhereElementIsNotElementType())

elif Selected_Category == 'Door':
   UParam('Door',FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsElementType(),FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType())

elif Selected_Category == 'Window':
   UParam('Window',FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).WhereElementIsElementType(),FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).WhereElementIsNotElementType())

elif Selected_Category == 'Parking':
   UParam('Parking',FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Parking).WhereElementIsElementType(),FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Parking).WhereElementIsNotElementType())

elif Selected_Category == 'Specialty Equipment':
   UParam('Specialty Equipment',FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_SpecialityEquipment).WhereElementIsElementType(),FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_SpecialityEquipment).WhereElementIsNotElementType())

elif Selected_Category == 'Planting':
   UParam('Planting',FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Planting).WhereElementIsElementType(),FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Planting).WhereElementIsNotElementType())

elif Selected_Category == 'Structural Framing':
   UParam('Structural Framing',FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsElementType(),FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType())

else:
   print('Parameters are not updated. Your selected option is Exit.')