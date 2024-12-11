# -*- coding: utf-8 -*-
'''Assign elements to workset'''

__title__ = "Assign Worksets"
__author__ = "prakritisrimal"

# Imports
import math
import os
import time
from datetime import datetime
from Extract.RunData import get_run_data
from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
from Autodesk.Revit.DB import WorksharingUtils
from System.Collections.Generic import List
from Autodesk.Revit.UI import TaskDialog, TaskDialogCommonButtons

# Record the start time
start_time = time.time()
manual_time = 30

script_dir = os.path.dirname(__file__)
ui_doc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document  # Get the Active Document
app = __revit__.Application  # Returns the Revit Application Object
rvt_year = int(app.VersionNumber)
output = script.get_output()


report_data = []
moved_data = []
unowned_element_data = []
workset_errors = []
elements_count = []

def get_model_category_names():
    """Retrieve a list of model categories that have elements in the model."""
    try:
        collector = FilteredElementCollector(doc).WhereElementIsNotElementType()
        unique_category_names = set()

        for element in collector:
            category = element.Category
            if category and category.Name and category.CategoryType == CategoryType.Model:
                # Skip subcategories by checking if the category has a parent
                if category.Parent is None and category.Name not in excluded_categories:
                    unique_category_names.add(category.Name)
        return list(unique_category_names)
    except Exception as e:
        forms.alert('Error retrieving model category names: {}'.format(e))
        return []

def get_combined_category_names():
    try:
        collector = FilteredElementCollector(doc).WhereElementIsNotElementType()
        unique_category_names = set()

        # List of annotation category names to include
        annotation_categories = ['Grids', 'Levels', 'Scope Boxes', 'Matchlines']
        # List of category names to exclude
        excluded_categories = ['Areas', 'Curtain Panels', 'Analysis Display Style', 'Curtain Systems', 'Curtain Wall Mullions', 'Mass', 
                                'Raster Images', 'HVAC Zones', 'Lines', 'Detail Items', 'Sun Path', 'Project Information', 'Cameras', 
                                'Sheets', 'Materials', 'Material Assets', 'Legend Components', 'Pipe Segments', 'Rooms', 'Exit Sign.dwg']
        
        # Include model categories
        for element in collector:
            category = element.Category
            if category and category.Name:
                if category.CategoryType == CategoryType.Model or (category.CategoryType == CategoryType.Annotation and category.Name in annotation_categories):
                    if category.Parent is None and category.Name not in excluded_categories:
                        unique_category_names.add(category.Name)
        
        return list(unique_category_names)
    except Exception as e:
        forms.alert('Error retrieving category names: {}'.format(e))
        return []

def get_workset_names():
    """Retrieve a list of wall names available in the model."""
    try:
        collector = FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset).ToWorksets()
        unique_workset_names = set()
        for ws in collector:
            ws_name = ws.Name
            if ws_name:
                if 'Z_' or 'Shared' or 'Scope' or 'Workset' in ws_name:
                    continue
                else:
                    unique_workset_names.add(ws_name)
        return list(unique_workset_names)
    except Exception as e:
        print("Error retrieving wall names: {}".format(e))
        return []
    
def move_elements_to_workset(elements, workset_name):  
    """Move elements to a specified workset."""
    
    try:
        elements_new = []
        standard_worksets = (
            "Workset1, "
            "AG_Signage, "
            "AI_Casework, "
            "AI_Ceiling, "
            "AI_EL, "
            "AI_Floor Finish, "
            "AI_Furniture, "
            "AI_Group, "
            "AI_Internal, "
            "AI_ME, "
            "AI_Specialty Equipment, "
            "AI_Wall Base, "
            "AI_Wall Finishes, "
            "AIX_Casework, "
            "AIX_Ceiling, "
            "AIX_EL, "
            "AIX_Floor Finish, "
            "AIX_Furniture, "
            "AIX_Group, "
            "AIX_Internal, "
            "AIX_ME, "
            "AIX_Specialty Equipment, "
            "AIX_Wall Base, "
            "AIX_Wall Finishes, "
            "AR_Ceiling, "
            "AR_EL, "
            "AR_External, "
            "AR_Floor, "
            "AR_FLS, "
            "AR_Furniture, "
            "AR_Group, "
            "AR_Internal, "
            "AR_ME, "
            "AR_Room Separator, "
            "AR_Skin, "
            "AR_ST, "
            "ARC_Ceiling, "
            "ARC_Columns, "
            "ARC_External, "
            "ARC_Furniture, "
            "ARC_Groups, "
            "ARC_Internal, "
            "ARC_LifeSafety, "
            "ARC_Rendering, "
            "ARC_Skin, "
            "ARX_Ceiling, "
            "ARX_EL, "
            "ARX_External, "
            "ARX_Floor, "
            "ARX_FLS, "
            "ARX_Furniture, "
            "ARX_Group, "
            "ARX_Internal, "
            "ARX_ME, "
            "ARX_Room Separator, "
            "ARX_ST, "
            "ASG_Signage, "
            "ASK_Skin, "
            "ELE_Lighting, "
            "MEC_HVAC, "
            "PLD_Plumbing, "
            "Scope Box, "
            "Scope Boxes, "
            "SGN_Signage, "
            "Shared Levels and Grids, "
            "STR_Concrete, "
            "STR_Steel, "
            "Z_Link_AI, "
            "Z_Link_AR, "
            "Z_Link_ARC, "
            "Z_Link_CAD, "
            "Z_Link_EL, "
            "Z_Link_ELE, "
            "Z_Link_ELV, "
            "Z_Link_FPR, "
            "Z_Link_ME, "
            "Z_Link_MEC, "
            "Z_Link_MF, "
            "Z_Link_MH, "
            "Z_Link_MP, "
            "Z_Link_PLD, "
            "Z_Link_ST, "
            "Z_Link_STR, "
            "Z_Link_URS"
        )

        # Filter out not owned elements
        collected_elements = elements  # List of elements that the tool targets
        owned_elements = []
        unowned_elements = []
        elements_to_checkout = List[ElementId]()

        for element in collected_elements:
            elements_to_checkout.Add(element.Id)

        WorksharingUtils.CheckoutElements(doc, elements_to_checkout)

        for element in collected_elements:    
            worksharingStatus = WorksharingUtils.GetCheckoutStatus(doc, element.Id)
            if worksharingStatus != CheckoutStatus.OwnedByOtherUser:
                owned_elements.append(element)
            else:
                unowned_elements.append(element)

        # Process owned elements
        for element in owned_elements:  
            original_workset = element.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM).AsValueString()

            # Collect elements that need to be moved to the target workset
            if original_workset.lower() in standard_worksets.lower() and original_workset.lower() != workset_name.lower():
                elements_new.append((element, original_workset))  # Store element with its original workset

        worksets = FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset).ToWorksets()

        def CheckExisting(workset_name):
            lower_workset_name = workset_name.lower()
            for workset in worksets:
                if workset.Name.lower() == lower_workset_name:
                    return True
            return False

        def RevitValue(workset_name):
            lower_workset_name = workset_name.lower()
            for workset in worksets:
                if workset.Name.lower() == lower_workset_name:
                    return workset





        if not CheckExisting(workset_name):
            workset_errors.append('⚠️ Workset "{}" not found. ☹️'.format(workset_name))
        else:
            target_workset = RevitValue(workset_name)

            # Loop over all elements and move them to the new workset
            for element, original_workset in elements_new:
                workset_param = element.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
                if workset_param and not workset_param.IsReadOnly:
                    workset_param.Set(target_workset.Id.IntegerValue)
                    moved_elements = 1
                    # Collect report data for the entire set of elements
                    report_data.append((output.linkify(element.Id), original_workset, workset_name))  # Store element details
                    moved_data.append(moved_elements)



                    

        # Collect data for unowned elements
        for element in unowned_elements:
            try:
                unowned_element_data.append([
                    output.linkify(element.Id), 
                    element.Category.Name.upper(), 
                    "REQUEST OWNERSHIP", 
                    WorksharingUtils.GetWorksharingTooltipInfo(doc, element.Id).Owner
                ])
            except Exception as e:
                pass

    except Exception as e:
        # Handle exceptions and log error details
        print('Error moving elements to workset: {}'.format(e))


def process (selected_option, selected_trade_option, selected_category_names, workset_name, doc):
    """Process selected categories and move elements to appropriate worksets."""
    try:
        def get_elements(category):
            elements = FilteredElementCollector(doc).OfCategory(category).WhereElementIsNotElementType().ToElements()
            return list(elements) if elements is not None else []
        
        def get_import_instances():
            """Get all ImportInstance elements."""
            import_instances = FilteredElementCollector(doc).OfClass(ImportInstance).WhereElementIsNotElementType().ToElements()
            return list(import_instances) if import_instances else []
        
        if selected_option == 'DAR':
            if selected_trade_option == 'Architecture':
                if 'Grids' in selected_category_names:
                    grids = get_elements(BuiltInCategory.OST_Grids)
                    if grids:
                        move_elements_to_workset (grids, 'Shared Levels and Grids')

                if 'Levels' in selected_category_names:
                    levels = get_elements(BuiltInCategory.OST_Levels)
                    if levels:
                        move_elements_to_workset (levels, 'Shared Levels and Grids')
                
                if 'Scope Boxes' in selected_category_names:
                    scope_boxes = get_elements(BuiltInCategory.OST_VolumeOfInterest)
                    if scope_boxes:
                        move_elements_to_workset (scope_boxes, 'Scope Box')
                
                if 'Matchline' in selected_category_names:
                    matchline = get_elements (BuiltInCategory.OST_Matchline)
                    if matchline:
                        move_elements_to_workset (matchline, 'Scope Box')

                if 'Ceilings' in selected_category_names:
                    ceilings = get_elements(BuiltInCategory.OST_Ceilings)
                    if ceilings:
                        move_elements_to_workset(ceilings, 'AR_Ceiling')

                if 'Casework' in selected_category_names:
                    casework =  get_elements(BuiltInCategory.OST_Casework)
                    if casework:
                        move_elements_to_workset (casework, 'AR_Furniture')

                if 'Doors' in selected_category_names:
                    doors = get_elements(BuiltInCategory.OST_Doors)
                    if doors:
                        external_doors = [d for d in doors if 'Ext' in d.Symbol.Family.Name]
                        internal_doors = [d for d in doors if 'Int' in d.Symbol.Family.Name]
                        move_elements_to_workset(external_doors, 'AR_External')
                        move_elements_to_workset(internal_doors, 'AR_Internal')

                if 'Columns' in selected_category_names:
                    columns = get_elements(BuiltInCategory.OST_Columns)
                    if columns:
                        for column in columns:
                            if 'SC' in column.Name or 'SS'in column.Name: 
                                move_elements_to_workset(columns, 'AR_ST')
                            else:
                                move_elements_to_workset(columns, 'AR_External')
                    strl_columns = get_elements(BuiltInCategory.OST_StructuralColumns)
                    if strl_columns:
                        move_elements_to_workset(strl_columns, 'AR_ST')

                if 'Electrical Equipment' in selected_category_names or 'Electrical Fixtures' in selected_category_names or 'Lighting Fixtures' in selected_category_names:
                    equip = get_elements(BuiltInCategory.OST_ElectricalEquipment)
                    fixtures = get_elements(BuiltInCategory.OST_ElectricalFixtures)
                    light_fixtures = get_elements(BuiltInCategory.OST_LightingFixtures)
                    if equip:
                        move_elements_to_workset(equip, 'AR_EL')
                    if fixtures:
                        move_elements_to_workset(fixtures, 'AR_EL')
                    if light_fixtures:
                        move_elements_to_workset(light_fixtures, 'AR_EL')

                if 'Entourage' in selected_category_names:
                    entourage = get_elements(BuiltInCategory.OST_Entourage)
                    if entourage:
                        move_elements_to_workset(entourage, 'AR_External')

                if 'Floors' in selected_category_names:
                    floors = get_elements(BuiltInCategory.OST_Floors)
                    if floors:
                        for floor in floors:
                            if 'SC' in floor.Name or 'SS' in floor.Name:
                                move_elements_to_workset([floor], 'AR_ST')
                            else:
                                move_elements_to_workset([floor], 'AR_Floor')
                           

                if 'Fire Protection' in selected_category_names:
                    fps = get_elements(BuiltInCategory.OST_FireProtection)
                    if fps:
                        move_elements_to_workset(fps, 'AR_FLS')

                if 'Food Service Equipment' in selected_category_names or 'Furniture' in selected_category_names or 'Furniture Systems' in selected_category_names:
                    fse = get_elements(BuiltInCategory.OST_FoodServiceEquipment)
                    furniture = get_elements(BuiltInCategory.OST_Furniture)
                    furniture_systems = get_elements(BuiltInCategory.OST_FurnitureSystems)
                    if fse:
                        move_elements_to_workset(fse, 'AR_Furniture')
                    if furniture:
                        move_elements_to_workset(furniture, 'AR_Furniture')
                    if furniture_systems:
                        move_elements_to_workset(furniture_systems, 'AR_Furniture')
                
                if 'Generic Models' in selected_category_names:
                    generic_models = get_elements(BuiltInCategory.OST_GenericModel)
                    if generic_models:
                        move_elements_to_workset(generic_models, 'AR_Internal')

                if 'Hardscape' in selected_category_names:
                    hardscape = get_elements(BuiltInCategory.OST_Hardscape)
                    if hardscape:
                        move_elements_to_workset(hardscape, 'AR_External')
                
                if 'Mechanical Control Devices' in selected_category_names or 'Mechanical Equipment' in selected_category_names:
                    mcd = get_elements(BuiltInCategory.OST_MechanicalControlDevices)
                    mech_equipments = get_elements(BuiltInCategory.OST_MechanicalEquipment)
                    if mcd:
                        move_elements_to_workset(mcd, 'AR_ME')
                    if mech_equipments:
                        move_elements_to_workset(mech_equipments, 'AR_ME')
                
                if 'Model Group' in selected_category_names:
                    groups = get_elements(BuiltInCategory.OST_IOSModelGroups)
                    if groups:
                        move_elements_to_workset(groups, 'AR_Group')

                if 'Medical Equipment' in selected_category_names:
                    medical_equipment = get_elements(BuiltInCategory.OST_MedicalEquipment)
                    if medical_equipment:
                        move_elements_to_workset(medical_equipment, 'AR_Furniture')

                if 'Parking' in selected_category_names:
                    parking = get_elements(BuiltInCategory.OST_Parking)
                    if parking:
                        move_elements_to_workset(parking, 'AR_Internal')

                if 'Planting' in selected_category_names:
                    planting = get_elements(BuiltInCategory.OST_Planting)
                    if planting:
                        move_elements_to_workset(planting, 'AR_External')

                if 'Plumbing Equipment' in selected_category_names or 'Plumbing Fixtures' in selected_category_names:
                    plumb_equip = get_elements(BuiltInCategory.OST_PlumbingEquipment)
                    plumb_fixt = get_elements(BuiltInCategory.OST_PlumbingFixtures)
                    if plumb_equip:
                        move_elements_to_workset(plumb_equip, 'AR_ME')
                    if plumb_fixt:
                        move_elements_to_workset(plumb_fixt, 'AR_ME')

                if 'Railings' in selected_category_names:
                    railings = get_elements(BuiltInCategory.OST_Railings)
                    if railings:
                        move_elements_to_workset(railings, 'AR_Internal')

                if 'Ramps' in selected_category_names:
                    ramps = get_elements(BuiltInCategory.OST_Ramps)
                    if ramps:
                        move_elements_to_workset(ramps, 'AR_ST')

                if 'RVT Links' in selected_category_names:
                    links = get_elements(BuiltInCategory.OST_RvtLinks)
                    if links:
                        for link in links:
                            link_name = link.LookupParameter("File Name")
                            if link_name:
                                link_name = link_name.AsString()
                                if "AR" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_AR')
                                elif "AI" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_AI')
                                elif "SC" in link_name or "ST" in link_name or "SS" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_ST')
                                elif "EL" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_EL')
                                elif "MF" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_MF')
                                elif "MH" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_MH')
                                elif "URS" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_URS')

                if any('dwg' in name.lower() for name in selected_category_names):
                    dwg_collector = get_import_instances()
                    if dwg_collector:
                        move_elements_to_workset(dwg_collector, 'Z_Link_CAD')

                if 'Roads' in selected_category_names or 'Roofs' in selected_category_names:
                    roads = get_elements(BuiltInCategory.OST_Roads)
                    roofs = get_elements(BuiltInCategory.OST_Roofs)
                    if roads:
                        move_elements_to_workset(roads, 'AR_External')
                    if roofs:
                        move_elements_to_workset(roofs, 'AR_External')

                if 'Shaft Openings' in selected_category_names:
                    shaft_opening = get_elements(BuiltInCategory.OST_ShaftOpening)
                    if shaft_opening:
                        move_elements_to_workset(shaft_opening, 'AR_Internal')

                if 'Signage' in selected_category_names: 
                    signage = get_elements(BuiltInCategory.OST_Signage)

                    # Define the names of the worksets
                    signage_power_workset_name = 'AG_Signage_Power'
                    signage_power_plus_data_workset_name = 'AG_Signage_Power + Data'
                    signage_workset_name = 'AG_Signage'
                    hidden_workset_name = 'AG_Hidden'  # Name of the hidden workset



                    # Lists to categorize signage elements
                    signage_power_elements = []
                    signage_power_plus_data_elements = []
                    no_value_signage = []

                    # Iterate through each signage element
                    if signage:
                        for element in signage:
                            workset_param = element.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM).AsValueString()

                            # If the element is in AG_Hidden, skip it
                            if workset_param.lower()  == hidden_workset_name.lower():
                                print("Skipping element ID: {} because it's in the AG_Hidden workset.".format(element.Id))
                                continue  # Skip elements in the AG_Hidden workset


                            # If the element is in AG_Hidden, skip it
                            if workset_param.lower()  == signage_power_workset_name.lower():
                                print("Skipping element ID: {} because it's in the AG_Signage_Power workset.".format(element.Id))
                                continue  # Skip elements in the AG_Signage_Power workset


                            # If the element is in AG_Hidden, skip it
                            if workset_param.lower()  == signage_power_plus_data_workset_name.lower():
                                print("Skipping element ID: {} because it's in the AG_Signage_Power + Data workset.".format(element.Id))
                                continue  # Skip elements in the AG_Signage_Power + Data workset

                            # Get the custom parameter "Signage Requirement" by name
                            signage_requirement_param = element.LookupParameter("Sign_Requirement")  # Use the correct parameter name
                            
                            # Check the value of the Signage Requirement parameter
                            signage_requirement_value = signage_requirement_param.AsString() if signage_requirement_param else None



                            # Categorize elements based on the Signage Requirement value
                            if signage_requirement_value is None or signage_requirement_value == "":
                                # Move elements with no signage requirement to AG_Signage
                                no_value_signage.append(element)
                            elif signage_requirement_value == 'AG Signage Power':
                                signage_power_elements.append(element)
                            elif signage_requirement_value == 'AG Signage Power + Data':
                                signage_power_plus_data_elements.append(element)

                    # Move elements based on their categories
                    if no_value_signage:
                        move_elements_to_workset(no_value_signage, signage_workset_name)

                    if signage_power_elements:
                        move_elements_to_workset(signage_power_elements, signage_power_workset_name)

                    if signage_power_plus_data_elements:
                        move_elements_to_workset(signage_power_plus_data_elements, signage_power_plus_data_workset_name)



                if 'Specialty Equipment' in selected_category_names:
                    spec_equip = get_elements(BuiltInCategory.OST_SpecialityEquipment)
                    if spec_equip:
                        move_elements_to_workset(spec_equip, 'AR_Internal')

                if 'Structural Foundations' in selected_category_names:
                    foundations = get_elements(BuiltInCategory.OST_StructuralFoundation)
                    if foundations:
                        move_elements_to_workset(foundations, 'AR_ST')

                if 'Structural Framing' in selected_category_names:
                    framing = get_elements(BuiltInCategory.OST_StructuralFraming)
                    if framing:
                        move_elements_to_workset(framing, 'AR_ST')

                if 'Walls' in selected_category_names:
                    walls = get_elements(BuiltInCategory.OST_Walls)
                    if walls:
                        for wall in walls:
                                if 'SC' in wall.Name or 'SS' in wall.Name:
                                    move_elements_to_workset([wall], 'AR_ST')
                                elif 'Ext' in wall.Name:
                                    move_elements_to_workset([wall], 'AR_External')
                                elif 'Int' in wall.Name:
                                    move_elements_to_workset([wall], 'AR_Internal')
                                elif 'WS_Ext' in wall.Name:
                                    move_elements_to_workset([wall], 'AR_Skin')
                                    continue 

                if 'Windows' in selected_category_names:
                    windows = get_elements(BuiltInCategory.OST_Windows)
                    if windows:
                        move_elements_to_workset(windows, 'AR_External')
            
            if selected_trade_option == 'Interior':
                if 'Grids' in selected_category_names:
                    grids = get_elements(BuiltInCategory.OST_Grids)
                    if grids:
                        move_elements_to_workset (grids, 'Shared Levels and Grids')

                if 'Levels' in selected_category_names:
                    levels = get_elements(BuiltInCategory.OST_Levels)
                    if levels:
                        move_elements_to_workset (levels, 'Shared Levels and Grids')
                
                if 'Scope Boxes' in selected_category_names:
                    scope_boxes = get_elements(BuiltInCategory.OST_VolumeOfInterest)
                    if scope_boxes:
                        move_elements_to_workset (scope_boxes, 'Scope Box')
                
                if 'Matchline' in selected_category_names:
                    matchline = get_elements (BuiltInCategory.OST_Matchline)
                    if matchline:
                        move_elements_to_workset (matchline, 'Scope Box')

                if 'Audio Visual Devices' in selected_category_names:
                    avd = get_elements(BuiltInCategory.OST_AudioVisualDevices)
                    if avd:
                        move_elements_to_workset(avd, 'AI_Internal')

                if 'Ceilings' in selected_category_names:
                    ceiling = get_elements(BuiltInCategory.OST_Ceilings)
                    if ceiling:
                        move_elements_to_workset(ceiling, 'AI_Ceiling')

                if 'Casework' in selected_category_names:
                    casework =  get_elements(BuiltInCategory.OST_Casework)
                    if casework:
                        move_elements_to_workset (casework, 'AI_Furniture')

                if 'Doors' in selected_category_names:
                    doors = get_elements(BuiltInCategory.OST_Doors)
                    if doors:
                        move_elements_to_workset(doors, 'AI_Internal')

                if 'Columns' in selected_category_names:
                    columns = get_elements(BuiltInCategory.OST_Columns)
                    if columns:
                        move_elements_to_workset(columns, 'AI_Internal')

                if any(cat in selected_category_names for cat in ['Electrical Equipment', 'Electrical Fixtures', 'Lighting Fixtures']):
                    equip = get_elements(BuiltInCategory.OST_ElectricalEquipment)
                    fixtures = get_elements(BuiltInCategory.OST_ElectricalFixtures)
                    light_fixtures = get_elements(BuiltInCategory.OST_LightingFixtures)
                    if equip:
                        move_elements_to_workset(equip, 'AI_EL')
                    if fixtures:
                        move_elements_to_workset(fixtures, 'AI_EL')
                    if light_fixtures:
                        move_elements_to_workset(light_fixtures, 'AI_EL')

                if 'Entourage' in selected_category_names:
                    entourage = get_elements(BuiltInCategory.OST_Entourage)
                    if entourage:
                        move_elements_to_workset(entourage, 'AI_Internal')

                if 'Floors' in selected_category_names:
                    floors = get_elements(BuiltInCategory.OST_Floors)
                    if floors:
                        move_elements_to_workset(floors, 'AI_Floor Finish')

                if any(cat in selected_category_names for cat in ['Food Service Equipment', 'Furniture', 'Furniture Systems']):
                    fse = get_elements(BuiltInCategory.OST_FoodServiceEquipment)
                    furniture = get_elements(BuiltInCategory.OST_Furniture)
                    furniture_systems = get_elements(BuiltInCategory.OST_FurnitureSystems)
                    if fse:
                        move_elements_to_workset(fse, 'AI_Furniture')
                    if furniture:
                        move_elements_to_workset(furniture, 'AI_Furniture')
                    if furniture_systems:
                        move_elements_to_workset(furniture_systems, 'AI_Furniture')

                if 'Generic Models' in selected_category_names:
                    generic_models = get_elements(BuiltInCategory.OST_GenericModel)
                    if generic_models:
                        move_elements_to_workset(generic_models, 'AI_Internal')

                if 'Hardscape' in selected_category_names:
                    hardscape = get_elements(BuiltInCategory.OST_Hardscape)
                    if hardscape:
                        move_elements_to_workset(hardscape, 'AI_Internal')

                if any(cat in selected_category_names for cat in ['Mechanical Control Devices', 'Mechanical Equipment']):
                    mcd = get_elements(BuiltInCategory.OST_MechanicalControlDevices)
                    mech_equipments = get_elements(BuiltInCategory.OST_MechanicalEquipment)
                    if mcd:
                        move_elements_to_workset(mcd, 'AI_ME')
                    if mech_equipments:
                        move_elements_to_workset(mech_equipments, 'AI_ME')

                if 'Model Group' in selected_category_names:
                    groups = get_elements(BuiltInCategory.OST_IOSModelGroups)
                    if groups:
                        move_elements_to_workset(groups, 'AI_Group')

                if 'Medical Equipment' in selected_category_names:
                    medical_equipment = get_elements(BuiltInCategory.OST_MedicalEquipment)
                    if medical_equipment:
                        move_elements_to_workset(medical_equipment, 'AI_Furniture')

                if 'Parking' in selected_category_names:
                    parking = get_elements(BuiltInCategory.OST_Parking)
                    if parking:
                        move_elements_to_workset(parking, 'AI_Internal')

                if 'Planting' in selected_category_names:
                    planting = get_elements(BuiltInCategory.OST_Planting)
                    if planting:
                        move_elements_to_workset(planting, 'AI_Internal')

                if any(cat in selected_category_names for cat in ['Plumbing Equipment', 'Plumbing Fixtures']):
                    plumb_equip = get_elements(BuiltInCategory.OST_PlumbingEquipment)
                    plumb_fixt = get_elements(BuiltInCategory.OST_PlumbingFixtures)
                    if plumb_equip:
                        move_elements_to_workset(plumb_equip, 'AI_ME')
                    if plumb_fixt:
                        move_elements_to_workset(plumb_fixt, 'AI_ME')

                if 'Railings' in selected_category_names:
                    railings = get_elements(BuiltInCategory.OST_Railings)
                    if railings:
                        move_elements_to_workset(railings, 'AI_Internal')

                if 'Ramps' in selected_category_names:
                    ramps = get_elements(BuiltInCategory.OST_Ramps)
                    if ramps:
                        move_elements_to_workset(ramps, 'AI_Internal')

                if 'RVT Links' in selected_category_names:
                    links = get_elements(BuiltInCategory.OST_RvtLinks)
                    if links:
                        for link in links:
                            link_name = link.LookupParameter("File Name")
                            if link_name:
                                link_name = link_name.AsString()
                                if "AR" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_AR')
                                elif "AI" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_AI')
                                elif "SC" in link_name or "ST" in link_name or "SS" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_ST')
                                elif "EL" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_EL')
                                elif "MF" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_MF')
                                elif "MH" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_MH')
                                elif "URS" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_URS')

                if any('dwg' in name.lower() for name in selected_category_names):
                    dwg_collector = get_import_instances()
                    if dwg_collector:
                        move_elements_to_workset(dwg_collector, 'Z_Link_CAD')

                if 'Shaft Openings' in selected_category_names:
                    shaft_opening = get_elements(BuiltInCategory.OST_ShaftOpening)
                    if shaft_opening:
                        move_elements_to_workset(shaft_opening, 'AI_Internal')

                if 'Signage' in selected_category_names:
                    signage = get_elements(BuiltInCategory.OST_Signage)
                    if signage:
                        move_elements_to_workset(signage, 'AG_Signage')

                if 'Specialty Equipment' in selected_category_names:
                    spec_equip = get_elements(BuiltInCategory.OST_SpecialityEquipment)
                    if spec_equip:
                        move_elements_to_workset(spec_equip, 'AI_Internal')

                if 'Stairs' in selected_category_names:
                    stairs = get_elements(BuiltInCategory.OST_Stairs)
                    if stairs:
                        move_elements_to_workset(stairs, 'AI_Internal')

                if 'Topography' in selected_category_names:
                    topography = get_elements(BuiltInCategory.OST_Topography)
                    if topography:
                        move_elements_to_workset(topography, 'AI_Topography')

                if 'Walls' in selected_category_names:
                    walls = get_elements(BuiltInCategory.OST_Walls)
                    if walls:
                        for wall in walls:
                            if 'WF' in wall.Name:
                                move_elements_to_workset([wall], 'AI_Wall Finishes')
                            elif 'BS' in wall.Name:
                                move_elements_to_workset([wall], 'AI_Wall Base')
                            else:
                                move_elements_to_workset([wall], 'AI_Internal')

                if 'Windows' in selected_category_names:
                    windows = get_elements(BuiltInCategory.OST_Windows)
                    if windows:
                        move_elements_to_workset(windows, 'AI_Internal')

            if selected_trade_option == 'Signage':

                    if 'Grids' in selected_category_names:
                        grids = get_elements(BuiltInCategory.OST_Grids)
                        if grids:
                            move_elements_to_workset (grids, 'Shared Levels and Grids')

                    if 'Levels' in selected_category_names:
                        levels = get_elements(BuiltInCategory.OST_Levels)
                        if levels:
                            move_elements_to_workset (levels, 'Shared Levels and Grids')
                    
                    if 'Scope Boxes' in selected_category_names:
                        scope_boxes = get_elements(BuiltInCategory.OST_VolumeOfInterest)
                        if scope_boxes:
                            move_elements_to_workset (scope_boxes, 'Scope Box')
                    
                    if 'Matchline' in selected_category_names:
                        matchline = get_elements (BuiltInCategory.OST_Matchline)
                        if matchline:
                            move_elements_to_workset (matchline, 'Scope Box')

                    if 'RVT Links' in selected_category_names:
                        links = get_elements(BuiltInCategory.OST_RvtLinks)
                        if links:
                            for link in links:
                                link_name = link.LookupParameter("File Name")
                                if link_name:
                                    link_name = link_name.AsString()
                                if "AR" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_AR')
                                elif "AI" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_AI')
                                elif "SC" in link_name or "ST" in link_name or "SS" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_ST')
                                elif "EL" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_EL')
                                elif "MF" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_MF')
                                elif "MH" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_MH')
                                elif "URS" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_URS')

                    if 'Signage' in selected_category_names: 
                        signage = get_elements(BuiltInCategory.OST_Signage)

                        # Define the names of the worksets
                        signage_power_workset_name = 'AG_Signage_Power'
                        signage_power_plus_data_workset_name = 'AG_Signage_Power + Data'
                        signage_workset_name = 'AG_Signage'
                        hidden_workset_name = 'AG_Hidden'  # Name of the hidden workset

                        # Lists to categorize signage elements
                        signage_power_elements = []
                        signage_power_plus_data_elements = []
                        no_value_signage = []

                        # Iterate through each signage element
                        if signage:
                            for element in signage:
                                workset_param = element.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM).AsValueString()



                                # If the element is in AG_Hidden, skip it
                                if workset_param.lower()  == hidden_workset_name.lower():
                                    print("Skipping element ID: {} because it's in the AG_Hidden workset.".format(element.Id))
                                    continue  # Skip elements in the AG_Hidden workset


                                # If the element is in AG_Hidden, skip it
                                if workset_param.lower()  == signage_power_workset_name.lower():
                                    print("Skipping element ID: {} because it's in the AG_Signage_Power workset.".format(element.Id))
                                    continue  # Skip elements in the AG_Signage_Power workset


                                # If the element is in AG_Hidden, skip it
                                if workset_param.lower()  == signage_power_plus_data_workset_name.lower():
                                    print("Skipping element ID: {} because it's in the AG_Signage_Power + Data workset.".format(element.Id))
                                    continue  # Skip elements in the AG_Signage_Power + Data workset

                                # Get the custom parameter "Signage Requirement" by name
                                signage_requirement_param = element.LookupParameter("Sign_Requirement")  # Use the correct parameter name
                                
                                # Check the value of the Signage Requirement parameter
                                signage_requirement_value = signage_requirement_param.AsString() if signage_requirement_param else None



                                # Categorize elements based on the Signage Requirement value
                                if signage_requirement_value is None or signage_requirement_value == "":
                                    # Move elements with no signage requirement to AG_Signage
                                    no_value_signage.append(element)
                                elif signage_requirement_value == 'AG Signage Power':
                                    signage_power_elements.append(element)
                                elif signage_requirement_value == 'AG Signage Power + Data':
                                    signage_power_plus_data_elements.append(element)

                        # Move elements based on their categories
                        if no_value_signage:
                            move_elements_to_workset(no_value_signage, signage_workset_name)

                        if signage_power_elements:
                            move_elements_to_workset(signage_power_elements, signage_power_workset_name)

                        if signage_power_plus_data_elements:
                            move_elements_to_workset(signage_power_plus_data_elements, signage_power_plus_data_workset_name)


        if selected_option == 'DAEP':

            if selected_trade_option == 'Architecture':
                if 'Grids' in selected_category_names:
                    grids = get_elements(BuiltInCategory.OST_Grids)
                    if grids:
                        move_elements_to_workset (grids, 'Shared Levels and Grids')

                if 'Levels' in selected_category_names:
                    levels = get_elements(BuiltInCategory.OST_Levels)
                    if levels:
                        move_elements_to_workset (levels, 'Shared Levels and Grids')
                
                if 'Scope Boxes' in selected_category_names:
                    scope_boxes = get_elements(BuiltInCategory.OST_VolumeOfInterest)
                    if scope_boxes:
                        move_elements_to_workset (scope_boxes, 'Scope Box')
                
                if 'Matchline' in selected_category_names:
                    matchline = get_elements (BuiltInCategory.OST_Matchline)
                    if matchline:
                        move_elements_to_workset (matchline, 'Scope Box')

                if 'Ceilings' in selected_category_names:
                    ceilings = get_elements(BuiltInCategory.OST_Ceilings)
                    if ceilings:
                        move_elements_to_workset(ceilings, 'ARX_Ceiling')

                if 'Casework' in selected_category_names:
                    casework =  get_elements(BuiltInCategory.OST_Casework)
                    if casework:
                        move_elements_to_workset (casework, 'ARX_Furniture')

                if 'Doors' in selected_category_names:
                    doors = get_elements(BuiltInCategory.OST_Doors)
                    if doors:
                        external_doors = [d for d in doors if 'Ext' in d.Symbol.Family.Name]
                        internal_doors = [d for d in doors if 'Int' in d.Symbol.Family.Name]
                        move_elements_to_workset(external_doors, 'ARX_External')
                        move_elements_to_workset(internal_doors, 'ARX_Internal')

                if 'Columns' in selected_category_names:
                    columns = get_elements(BuiltInCategory.OST_Columns)
                    if columns:
                        move_elements_to_workset(columns, 'ARX_External')
                    strl_columns = get_elements(BuiltInCategory.OST_StructuralColumns)
                    if strl_columns:
                        move_elements_to_workset(strl_columns, 'ARX_ST')

                if 'Electrical Equipment' in selected_category_names or 'Electrical Fixtures' in selected_category_names or 'Lighting Fixtures' in selected_category_names:
                    equip = get_elements(BuiltInCategory.OST_ElectricalEquipment)
                    fixtures = get_elements(BuiltInCategory.OST_ElectricalFixtures)
                    light_fixtures = get_elements(BuiltInCategory.OST_LightingFixtures)
                    if equip:
                        move_elements_to_workset(equip, 'ARX_EL')
                    if fixtures:
                        move_elements_to_workset(fixtures, 'ARX_EL')
                    if light_fixtures:
                        move_elements_to_workset(light_fixtures, 'ARX_EL')

                if 'Entourage' in selected_category_names:
                    entourage = get_elements(BuiltInCategory.OST_Entourage)
                    if entourage:
                        move_elements_to_workset(entourage, 'ARX_External')

                if 'Floors' in selected_category_names:
                    floors = get_elements(BuiltInCategory.OST_Floors)
                    if floors:
                        for floor in floors:
                            if 'SC' in floor.Name or 'SS'in floor.Name:
                                move_elements_to_workset([floor], 'ARX_ST')
                            else:
                              move_elements_to_workset([floor], 'ARX_Floor')
                              

                if 'Fire Protection' in selected_category_names:
                    fps = get_elements(BuiltInCategory.OST_FireProtection)
                    if fps:
                        move_elements_to_workset(fps, 'ARX_FLS')

                if 'Food Service Equipment' in selected_category_names or 'Furniture' in selected_category_names or 'Furniture Systems' in selected_category_names:
                    fse = get_elements(BuiltInCategory.OST_FoodServiceEquipment)
                    furniture = get_elements(BuiltInCategory.OST_Furniture)
                    furniture_systems = get_elements(BuiltInCategory.OST_FurnitureSystems)
                    if fse:
                        move_elements_to_workset(fse, 'ARX_Furniture')
                    if furniture:
                        move_elements_to_workset(furniture, 'ARX_Furniture')
                    if furniture_systems:
                        move_elements_to_workset(furniture_systems, 'ARX_Furniture')
                
                if 'Generic Models' in selected_category_names:
                    generic_models = get_elements(BuiltInCategory.OST_GenericModel)
                    if generic_models:
                        move_elements_to_workset(generic_models, 'ARX_Internal')

                if 'Hardscape' in selected_category_names:
                    hardscape = get_elements(BuiltInCategory.OST_Hardscape)
                    if hardscape:
                        move_elements_to_workset(hardscape, 'ARX_External')
                
                if 'Mechanical Control Devices' in selected_category_names or 'Mechanical Equipment' in selected_category_names:
                    mcd = get_elements(BuiltInCategory.OST_MechanicalControlDevices)
                    mech_equipments = get_elements(BuiltInCategory.OST_MechanicalEquipment)
                    if mcd:
                        move_elements_to_workset(mcd, 'ARX_ME')
                    if mech_equipments:
                        move_elements_to_workset(mech_equipments, 'ARX_ME')
                
                if 'Model Group' in selected_category_names:
                    groups = get_elements(BuiltInCategory.OST_IOSModelGroups)
                    if groups:
                        move_elements_to_workset(groups, 'ARX_Group')

                if 'Medical Equipment' in selected_category_names:
                    medical_equipment = get_elements(BuiltInCategory.OST_MedicalEquipment)
                    if medical_equipment:
                        move_elements_to_workset(medical_equipment, 'ARX_Furniture')

                if 'Parking' in selected_category_names:
                    parking = get_elements(BuiltInCategory.OST_Parking)
                    if parking:
                        move_elements_to_workset(parking, 'ARX_Internal')

                if 'Planting' in selected_category_names:
                    planting = get_elements(BuiltInCategory.OST_Planting)
                    if planting:
                        move_elements_to_workset(planting, 'ARX_External')

                if 'Plumbing Equipment' in selected_category_names or 'Plumbing Fixtures' in selected_category_names:
                    plumb_equip = get_elements(BuiltInCategory.OST_PlumbingEquipment)
                    plumb_fixt = get_elements(BuiltInCategory.OST_PlumbingFixtures)
                    if plumb_equip:
                        move_elements_to_workset(plumb_equip, 'ARX_ME')
                    if plumb_fixt:
                        move_elements_to_workset(plumb_fixt, 'ARX_ME')

                if 'Railings' in selected_category_names:
                    railings = get_elements(BuiltInCategory.OST_Railings)
                    if railings:
                        move_elements_to_workset(railings, 'ARX_Internal')

                if 'Ramps' in selected_category_names:
                    ramps = get_elements(BuiltInCategory.OST_Ramps)
                    if ramps:
                        move_elements_to_workset(ramps, 'ARX_ST')

                if 'RVT Links' in selected_category_names:
                    links = get_elements(BuiltInCategory.OST_RvtLinks)
                    if links:
                        for link in links:
                            link_name = link.LookupParameter("File Name")
                            if link_name:
                                link_name = link_name.AsString()
                                if "AR" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_AR')
                                elif "AI" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_AI')
                                elif "SC" in link_name or "ST" in link_name or "SS" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_ST')
                                elif "EL" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_EL')
                                elif "MF" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_MF')
                                elif "MH" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_MH')
                                elif "URS" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_URS')

                if any('dwg' in name.lower() for name in selected_category_names):
                    dwg_collector = get_import_instances()
                    if dwg_collector:
                        move_elements_to_workset(dwg_collector, 'Z_Link_CAD')

                if 'Roads' in selected_category_names or 'Roofs' in selected_category_names:
                    roads = get_elements(BuiltInCategory.OST_Roads)
                    roofs = get_elements(BuiltInCategory.OST_Roofs)
                    if roads:
                        move_elements_to_workset(roads, 'ARX_External')
                    if roofs:
                        move_elements_to_workset(roofs, 'ARX_External')

                if 'Shaft Openings' in selected_category_names:
                    shaft_opening = get_elements(BuiltInCategory.OST_ShaftOpening)
                    if shaft_opening:
                        move_elements_to_workset(shaft_opening, 'ARX_Internal')

                if 'Signage' in selected_category_names:
                    signage = get_elements(BuiltInCategory.OST_Signage)
                    if signage:
                        move_elements_to_workset(signage, 'ASG_Signage')

                if 'Specialty Equipment' in selected_category_names:
                    spec_equip = get_elements(BuiltInCategory.OST_SpecialityEquipment)
                    if spec_equip:
                        move_elements_to_workset(spec_equip, 'ARX_Internal')

                if 'Structural Foundations' in selected_category_names:
                    foundations = get_elements(BuiltInCategory.OST_StructuralFoundation)
                    if foundations:
                        move_elements_to_workset(foundations, 'ARX_ST')

                if 'Structural Framing' in selected_category_names:
                    framing = get_elements(BuiltInCategory.OST_StructuralFraming)
                    if framing:
                        move_elements_to_workset(framing, 'ARX_ST')

                if 'Walls' in selected_category_names:
                    walls = get_elements(BuiltInCategory.OST_Walls)
                    if walls:
                        for wall in walls:
                            if 'SC' in wall.Name or 'SS' in wall.Name:
                                move_elements_to_workset([wall], 'ARX_ST')
                            elif 'Ext' in wall.Name:
                                move_elements_to_workset([wall], 'ARX_External')
                            elif 'Int' in wall.Name:
                                move_elements_to_workset([wall], 'ARX_Internal')
                            elif 'WS_Ext' in wall.Name:
                                move_elements_to_workset([wall], 'ASX_Skin')


                if 'Windows' in selected_category_names:
                    windows = get_elements(BuiltInCategory.OST_Windows)
                    if windows:
                        move_elements_to_workset(windows, 'ARX_External')
            
            if selected_trade_option == 'Interior':
                if 'Grids' in selected_category_names:
                    grids = get_elements(BuiltInCategory.OST_Grids)
                    if grids:
                        move_elements_to_workset (grids, 'Shared Levels and Grids')

                if 'Levels' in selected_category_names:
                    levels = get_elements(BuiltInCategory.OST_Levels)
                    if levels:
                        move_elements_to_workset (levels, 'Shared Levels and Grids')
                
                if 'Scope Boxes' in selected_category_names:
                    scope_boxes = get_elements(BuiltInCategory.OST_VolumeOfInterest)
                    if scope_boxes:
                        move_elements_to_workset (scope_boxes, 'Scope Box')
                
                if 'Matchline' in selected_category_names:
                    matchline = get_elements (BuiltInCategory.OST_Matchline)
                    if matchline:
                        move_elements_to_workset (matchline, 'Scope Box')

                if 'Audio Visual Devices' in selected_category_names:
                    avd = get_elements(BuiltInCategory.OST_AudioVisualDevices)
                    if avd:
                        move_elements_to_workset(avd, 'AIX_Internal')

                if 'Ceilings' in selected_category_names:
                    ceiling = get_elements(BuiltInCategory.OST_Ceilings)
                    if ceiling:
                        move_elements_to_workset(ceiling, 'AIX_Ceiling')

                if 'Casework' in selected_category_names:
                    casework =  get_elements(BuiltInCategory.OST_Casework)
                    if casework:
                        move_elements_to_workset (casework, 'AIX_Furniture')

                if 'Doors' in selected_category_names:
                    doors = get_elements(BuiltInCategory.OST_Doors)
                    if doors:
                        move_elements_to_workset(doors, 'AIX_Internal')

                if 'Columns' in selected_category_names:
                    columns = get_elements(BuiltInCategory.OST_Columns)
                    if columns:
                        move_elements_to_workset(columns, 'AIX_Internal')

                if any(cat in selected_category_names for cat in ['Electrical Equipment', 'Electrical Fixtures', 'Lighting Fixtures']):
                    equip = get_elements(BuiltInCategory.OST_ElectricalEquipment)
                    fixtures = get_elements(BuiltInCategory.OST_ElectricalFixtures)
                    light_fixtures = get_elements(BuiltInCategory.OST_LightingFixtures)
                    if equip:
                        move_elements_to_workset(equip, 'AIX_EL')
                    if fixtures:
                        move_elements_to_workset(fixtures, 'AIX_EL')
                    if light_fixtures:
                        move_elements_to_workset(light_fixtures, 'AIX_EL')

                if 'Entourage' in selected_category_names:
                    entourage = get_elements(BuiltInCategory.OST_Entourage)
                    if entourage:
                        move_elements_to_workset(entourage, 'AIX_Internal')

                if 'Floors' in selected_category_names:
                    floors = get_elements(BuiltInCategory.OST_Floors)
                    if floors:
                        move_elements_to_workset(floors, 'AIX_Floor Finish')

                if any(cat in selected_category_names for cat in ['Food Service Equipment', 'Furniture', 'Furniture Systems']):
                    fse = get_elements(BuiltInCategory.OST_FoodServiceEquipment)
                    furniture = get_elements(BuiltInCategory.OST_Furniture)
                    furniture_systems = get_elements(BuiltInCategory.OST_FurnitureSystems)
                    if fse:
                        move_elements_to_workset(fse, 'AIX_Furniture')
                    if furniture:
                        move_elements_to_workset(furniture, 'AIX_Furniture')
                    if furniture_systems:
                        move_elements_to_workset(furniture_systems, 'AIX_Furniture')

                if 'Generic Models' in selected_category_names:
                    generic_models = get_elements(BuiltInCategory.OST_GenericModel)
                    if generic_models:
                        move_elements_to_workset(generic_models, 'AIX_Internal')

                if 'Hardscape' in selected_category_names:
                    hardscape = get_elements(BuiltInCategory.OST_Hardscape)
                    if hardscape:
                        move_elements_to_workset(hardscape, 'AIX_Internal')

                if any(cat in selected_category_names for cat in ['Mechanical Control Devices', 'Mechanical Equipment']):
                    mcd = get_elements(BuiltInCategory.OST_MechanicalControlDevices)
                    mech_equipments = get_elements(BuiltInCategory.OST_MechanicalEquipment)
                    if mcd:
                        move_elements_to_workset(mcd, 'AIX_ME')
                    if mech_equipments:
                        move_elements_to_workset(mech_equipments, 'AIX_ME')

                if 'Model Group' in selected_category_names:
                    groups = get_elements(BuiltInCategory.OST_IOSModelGroups)
                    if groups:
                        move_elements_to_workset(groups, 'AIX_Group')

                if 'Medical Equipment' in selected_category_names:
                    medical_equipment = get_elements(BuiltInCategory.OST_MedicalEquipment)
                    if medical_equipment:
                        move_elements_to_workset(medical_equipment, 'AIX_Furniture')

                if 'Parking' in selected_category_names:
                    parking = get_elements(BuiltInCategory.OST_Parking)
                    if parking:
                        move_elements_to_workset(parking, 'AIX_Internal')

                if 'Planting' in selected_category_names:
                    planting = get_elements(BuiltInCategory.OST_Planting)
                    if planting:
                        move_elements_to_workset(planting, 'AIX_Internal')

                if any(cat in selected_category_names for cat in ['Plumbing Equipment', 'Plumbing Fixtures']):
                    plumb_equip = get_elements(BuiltInCategory.OST_PlumbingEquipment)
                    plumb_fixt = get_elements(BuiltInCategory.OST_PlumbingFixtures)
                    if plumb_equip:
                        move_elements_to_workset(plumb_equip, 'AIX_ME')
                    if plumb_fixt:
                        move_elements_to_workset(plumb_fixt, 'AIX_ME')

                if 'Railings' in selected_category_names:
                    railings = get_elements(BuiltInCategory.OST_Railings)
                    if railings:
                        move_elements_to_workset(railings, 'AIX_Internal')

                if 'Ramps' in selected_category_names:
                    ramps = get_elements(BuiltInCategory.OST_Ramps)
                    if ramps:
                        move_elements_to_workset(ramps, 'AIX_Internal')

                if 'RVT Links' in selected_category_names:
                    links = get_elements(BuiltInCategory.OST_RvtLinks)
                    if links:
                        for link in links:
                            link_name = link.LookupParameter("File Name")
                            if link_name:
                                link_name = link_name.AsString()
                                if "AR" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_AR')
                                elif "AI" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_AI')
                                elif "SC" in link_name or "ST" in link_name or "SS" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_ST')
                                elif "EL" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_EL')
                                elif "MF" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_MF')
                                elif "MH" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_MH')
                                elif "URS" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_URS')

                if any('dwg' in name.lower() for name in selected_category_names):
                    dwg_collector = get_import_instances()
                    if dwg_collector:
                        move_elements_to_workset(dwg_collector, 'Z_Link_CAD')

                if 'Shaft Openings' in selected_category_names:
                    shaft_opening = get_elements(BuiltInCategory.OST_ShaftOpening)
                    if shaft_opening:
                        move_elements_to_workset(shaft_opening, 'AIX_Internal')

                if 'Signage' in selected_category_names:
                    signage = get_elements(BuiltInCategory.OST_Signage)
                    if signage:
                        move_elements_to_workset(signage, 'ASG_Signage')

                if 'Specialty Equipment' in selected_category_names:
                    spec_equip = get_elements(BuiltInCategory.OST_SpecialityEquipment)
                    if spec_equip:
                        move_elements_to_workset(spec_equip, 'AIX_Internal')

                if 'Stairs' in selected_category_names:
                    stairs = get_elements(BuiltInCategory.OST_Stairs)
                    if stairs:
                        move_elements_to_workset(stairs, 'AIX_Internal')

                if 'Topography' in selected_category_names:
                    topography = get_elements(BuiltInCategory.OST_Topography)
                    if topography:
                        move_elements_to_workset(topography, 'AIX_Topography')

                if 'Walls' in selected_category_names:
                    walls = get_elements(BuiltInCategory.OST_Walls)
                    if walls:
                        for wall in walls:
                            if 'WF' in wall.Name:
                                move_elements_to_workset([wall], 'AIX_Wall Finishes')
                            elif 'BS' in wall.Name:
                                move_elements_to_workset([wall], 'AIX_Wall Base')
                            else:
                                move_elements_to_workset([wall], 'AIX_Internal')

                if 'Windows' in selected_category_names:
                    windows = get_elements(BuiltInCategory.OST_Windows)
                    if windows:
                        move_elements_to_workset(windows, 'AIX_Internal')

            if selected_trade_option == 'Signage':

                    if 'Grids' in selected_category_names:
                        grids = get_elements(BuiltInCategory.OST_Grids)
                        if grids:
                            move_elements_to_workset (grids, 'Shared Levels and Grids')

                    if 'Levels' in selected_category_names:
                        levels = get_elements(BuiltInCategory.OST_Levels)
                        if levels:
                            move_elements_to_workset (levels, 'Shared Levels and Grids')
                    
                    if 'Scope Boxes' in selected_category_names:
                        scope_boxes = get_elements(BuiltInCategory.OST_VolumeOfInterest)
                        if scope_boxes:
                            move_elements_to_workset (scope_boxes, 'Scope Box')
                    
                    if 'Matchline' in selected_category_names:
                        matchline = get_elements (BuiltInCategory.OST_Matchline)
                        if matchline:
                            move_elements_to_workset (matchline, 'Scope Box')

                    if 'RVT Links' in selected_category_names:
                        links = get_elements(BuiltInCategory.OST_RvtLinks)
                        if links:
                            for link in links:
                                link_name = link.LookupParameter("File Name")
                                if link_name:
                                    link_name = link_name.AsString()
                                if "AR" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_AR')
                                elif "AI" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_AI')
                                elif "SC" in link_name or "ST" in link_name or "SS" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_ST')
                                elif "EL" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_EL')
                                elif "MF" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_MF')
                                elif "MH" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_MH')
                                elif "URS" in link_name:
                                    move_elements_to_workset([link], 'Z_Link_URS')
                    else:
                        move_elements_to_workset (element, 'ASG_Signage')

        if selected_option == 'NEOM':
            if 'Grids' in selected_category_names:
                grids = get_elements(BuiltInCategory.OST_Grids)
                if grids:
                    move_elements_to_workset (grids, 'Shared Levels and Grids')

            if 'Levels' in selected_category_names:
                levels = get_elements(BuiltInCategory.OST_Levels)
                if levels:
                    move_elements_to_workset (levels, 'Shared Levels and Grids')
            
            if 'Scope Boxes' in selected_category_names:
                scope_boxes = get_elements(BuiltInCategory.OST_VolumeOfInterest)
                if scope_boxes:
                    move_elements_to_workset (scope_boxes, 'Scope Box')
            
            if 'Matchline' in selected_category_names:
                matchline = get_elements (BuiltInCategory.OST_Matchline)
                if matchline:
                    move_elements_to_workset (matchline, 'Scope Box')

            if 'Ceilings' in selected_category_names:
                ceilings = get_elements(BuiltInCategory.OST_Ceilings)
                if ceilings:
                    move_elements_to_workset(ceilings, 'ARC_Ceiling')

            if 'Casework' in selected_category_names:
                casework =  get_elements(BuiltInCategory.OST_Casework)
                if casework:
                    move_elements_to_workset (casework, 'ARC_Furniture')

            if 'Doors' in selected_category_names:
                doors = get_elements(BuiltInCategory.OST_Doors)
                if doors:
                    external_doors = [d for d in doors if 'ext' in d.Symbol.Family.Name]
                    internal_doors = [d for d in doors if 'int' in d.Symbol.Family.Name]
                    move_elements_to_workset(external_doors, 'ARC_External')
                    move_elements_to_workset(internal_doors, 'ARC_Internal')

            if 'Columns' in selected_category_names:
                columns = get_elements(BuiltInCategory.OST_Columns)
                if columns:
                    for column in columns:
                        if 'SC' in column.Name:
                            move_elements_to_workset([column], 'STR_Concrete')
                        elif 'SS' in column.Name:
                            move_elements_to_workset([column], 'STR_Steel')
                        else:
                            move_elements_to_workset([column], 'ARC_columns')

                strl_columns = get_elements(BuiltInCategory.OST_StructuralColumns)
                if strl_columns:
                    for strl_column in strl_columns:
                        if 'SC' in strl_column.Name:
                            move_elements_to_workset([strl_column], 'STR_Concrete')
                        elif 'SS' in strl_column.Name:
                            move_elements_to_workset([strl_column], 'STR_Steel')
                        else:
                            move_elements_to_workset([strl_column], 'ARC_columns')
                                        


            if 'Electrical Equipment' in selected_category_names or 'Electrical Fixtures' in selected_category_names or 'Lighting Fixtures' in selected_category_names:
                equip = get_elements(BuiltInCategory.OST_ElectricalEquipment)
                fixtures = get_elements(BuiltInCategory.OST_ElectricalFixtures)
                light_fixtures = get_elements(BuiltInCategory.OST_LightingFixtures)
                if equip:
                    move_elements_to_workset(equip, 'ELE_Lighting')
                if fixtures:
                    move_elements_to_workset(fixtures, 'ELE_Lighting')
                if light_fixtures:
                    move_elements_to_workset(light_fixtures, 'ELE_Lighting')

            if 'Entourage' in selected_category_names:
                entourage = get_elements(BuiltInCategory.OST_Entourage)
                if entourage:
                    move_elements_to_workset(entourage, 'ARC_External')

            if 'Floors' in selected_category_names:
                floors = get_elements(BuiltInCategory.OST_Floors)
                if floors:
                    for floor in floors:
                        floor_name = floor.Name
                        if 'Concrete' in floor.Name:
                            move_elements_to_workset ([floor], 'STR_Concrete')
                        if 'Steel' in floor.Name:
                            move_elements_to_workset ([floor], 'STR_Steel')
                        if 'IDN' in floor.Name:
                            move_elements_to_workset ([floor], 'ARC_Internal')
        
            if 'Fire Protection' in selected_category_names:
                fps = get_elements(BuiltInCategory.OST_FireProtection)
                if fps:
                    move_elements_to_workset(fps, 'ARC_LifeSafety')

            if 'Food Service Equipment' in selected_category_names or 'Furniture' in selected_category_names or 'Furniture Systems' in selected_category_names:
                fse = get_elements(BuiltInCategory.OST_FoodServiceEquipment)
                furniture = get_elements(BuiltInCategory.OST_Furniture)
                furniture_systems = get_elements(BuiltInCategory.OST_FurnitureSystems)
                if fse:
                    move_elements_to_workset(fse, 'ARC_Furniture')
                if furniture:
                    move_elements_to_workset(furniture, 'ARC_Furniture')
                if furniture_systems:
                    move_elements_to_workset(furniture_systems, 'ARC_Furniture')
            
            if 'Generic Models' in selected_category_names:
                generic_models = get_elements(BuiltInCategory.OST_GenericModel)
                if generic_models:
                    move_elements_to_workset(generic_models, 'ARC_Internal')

            if 'Hardscape' in selected_category_names:
                hardscape = get_elements(BuiltInCategory.OST_Hardscape)
                if hardscape:
                    move_elements_to_workset(hardscape, 'ARC_External')
            
            if 'Mechanical Control Devices' in selected_category_names or 'Mechanical Equipment' in selected_category_names:
                mcd = get_elements(BuiltInCategory.OST_MechanicalControlDevices)
                mech_equipments = get_elements(BuiltInCategory.OST_MechanicalEquipment)
                if mcd:
                    move_elements_to_workset(mcd, 'MEC_HVAC')
                if mech_equipments:
                    move_elements_to_workset(mech_equipments, 'MEC_HVAC')
            
            if 'Model Group' in selected_category_names:
                groups = get_elements(BuiltInCategory.OST_IOSModelGroups)
                if groups:
                    move_elements_to_workset(groups, 'ARC_Groups')

            if 'Medical Equipment' in selected_category_names:
                medical_equipment = get_elements(BuiltInCategory.OST_MedicalEquipment)
                if medical_equipment:
                    move_elements_to_workset(medical_equipment, 'ARC_Furniture')

            if 'Parking' in selected_category_names:
                parking = get_elements(BuiltInCategory.OST_Parking)
                if parking:
                    move_elements_to_workset(parking, 'ARC_Internal')

            if 'Planting' in selected_category_names:
                planting = get_elements(BuiltInCategory.OST_Planting)
                if planting:
                    move_elements_to_workset(planting, 'ARC_External')

            if 'Plumbing Equipment' in selected_category_names or 'Plumbing Fixtures' in selected_category_names:
                plumb_equip = get_elements(BuiltInCategory.OST_PlumbingEquipment)
                plumb_fixt = get_elements(BuiltInCategory.OST_PlumbingFixtures)
                if plumb_equip:
                    move_elements_to_workset(plumb_equip, 'PLD_Plumbing')
                if plumb_fixt:
                    move_elements_to_workset(plumb_fixt, 'PLD_Plumbing')

            if 'Railings' in selected_category_names:
                railings = get_elements(BuiltInCategory.OST_Railings)
                if railings:
                    move_elements_to_workset(railings, 'ARC_Internal')

            if 'Ramps' in selected_category_names:
                ramps = get_elements(BuiltInCategory.OST_Ramps)
                if ramps:
                    move_elements_to_workset(ramps, 'ARC_ST')

            if 'RVT Links' in selected_category_names:
                links = get_elements(BuiltInCategory.OST_RvtLinks)
                if links:
                    for link in links:
                        link_name = link.LookupParameter("File Name")
                        if link_name:
                            link_name = link_name.AsString()
                            if "ARC" in link_name:
                                move_elements_to_workset([link], 'Z_Link_ARC')
                            elif "SLT" in link_name or "STR" in link_name:
                                move_elements_to_workset([link], 'Z_Link_STR')
                            elif "ELE" in link_name:
                                move_elements_to_workset([link], 'Z_Link_ELE')
                            elif "ELV" in link_name:
                                move_elements_to_workset([link], 'Z_Link_ELV')
                            elif "FLS" in link_name:
                                move_elements_to_workset([link], 'Z_Link_FPR')
                            elif "MEC" in link_name:
                                move_elements_to_workset([link], 'Z_Link_MEC')
                            elif "PLD" in link_name:
                                move_elements_to_workset([link], 'Z_Link_PLD')
                            elif "URS" in link_name:
                                move_elements_to_workset([link], 'Z_Link_URS')

            if any('dwg' in name.lower() for name in selected_category_names):
                dwg_collector = get_import_instances()
                if dwg_collector:
                    move_elements_to_workset(dwg_collector, 'Z_Link_CAD')

            if 'Roads' in selected_category_names or 'Roofs' in selected_category_names:
                roads = get_elements(BuiltInCategory.OST_Roads)
                roofs = get_elements(BuiltInCategory.OST_Roofs)
                if roads:
                    move_elements_to_workset(roads, 'ARC_External')
                if roofs:
                    move_elements_to_workset(roofs, 'ARC_External')

            if 'Shaft Openings' in selected_category_names:
                shaft_opening = get_elements(BuiltInCategory.OST_ShaftOpening)
                if shaft_opening:
                    move_elements_to_workset(shaft_opening, 'ARC_Internal')

            if 'Signage' in selected_category_names:
                signage = get_elements(BuiltInCategory.OST_Signage)
                if signage:
                    move_elements_to_workset(signage, 'SGN_Signage')

            if 'Specialty Equipment' in selected_category_names:
                spec_equip = get_elements(BuiltInCategory.OST_SpecialityEquipment)
                if spec_equip:
                    move_elements_to_workset(spec_equip, 'ARC_Internal')

            if 'Structural Foundations' in selected_category_names:
                foundations = get_elements(BuiltInCategory.OST_StructuralFoundation)
                if foundations:
                    for foundation in foundations:
                        material = doc.GetElement(foundation.Symbol.LookupParameter("Structural Material").AsElementId())
                        if material.MaterialCategory == "Concrete":
                            move_elements_to_workset([foundation], 'STR_Concrete')
                            break
                        else:
                            move_elements_to_workset([foundation], 'STR_Steel')
                            break

            if 'Structural Framing' in selected_category_names:
                framings = get_elements(BuiltInCategory.OST_StructuralFraming)
                if framings:
                    for framing in framings:
                        material = doc.GetElement(framing.Parameter.LookupParameter("Structural Material").AsElementId())
                        if material.MaterialCategory == "Concrete":
                            move_elements_to_workset([foundation], 'STR_Concrete')
                            break
                        else:
                            move_elements_to_workset([foundation], 'STR_Steel')
                            break

            if 'Walls' in selected_category_names:
                walls = get_elements(BuiltInCategory.OST_Walls)
                if walls:
                    for wall in walls:
                        if 'SC' in wall.Name:
                            move_elements_to_workset([strl_column], 'STR_Concrete')
                        elif 'SS' in wall.Name:
                            move_elements_to_workset([strl_column], 'STR_Steel')
                        elif 'Ext' in wall.Name:
                            move_elements_to_workset([wall], 'ARC_External')
                        elif 'IDN' in wall.Name:
                            move_elements_to_workset([wall], 'ARC_Internal')
                            continue


            if 'Windows' in selected_category_names:
                windows = get_elements(BuiltInCategory.OST_Windows)
                if windows:
                    move_elements_to_workset(windows, 'ARC_External')

        

    except Exception as e:
        forms.alert("An error occurred: {}".format(e))

        #Record the end time and runtime
        end_time = time.time()
        runtime = end_time - start_time

        # Log the error details
        error_occured = "Error occurred: {}".format(str(e))
        run_result = "Error"
        element_count = 10

        # Function to log run data in case of error
        get_run_data(__title__, runtime, element_count, manual_time, run_result, error_occured)

def main(): 
    if not doc.IsWorkshared:
        forms.alert("File not Workshared - Create a Workshared Model First!", title='Script Cancelled')
        return
    
    # Prompt user for standards selection
    ops = ['DAR', 'DAEP', 'NEOM']
    selected_option = forms.SelectFromList.show(
        ops,
        multiselect=False, width=300, height=300,
        title='Select the standards as per which worksets should be created',
        default=ops[0]  # Optionally, set a default selection
    )
    if not selected_option:
        script.exit()

    if selected_option:
        workset_names = get_workset_names()
        # Fetch both model and annotation categories
        category_names = get_combined_category_names()
        if not category_names:
            forms.alert('No categories found in the project.')
            return
        
        # If 'NEOM' is selected, skip trade selection and go to categories
        if selected_option == 'NEOM':
            selected_category_names = forms.SelectFromList.show(category_names, multiselect=True, title='Select Categories', default=category_names)

            if selected_category_names:
                process(selected_option, None, selected_category_names, workset_names, doc)
            else:
                forms.alert('No categories selected. Exiting script.')
                return

        else:  # For 'DAR' and 'DAEP', ask for trade selection
            trade_ops = ['Architecture', 'Interior', 'Signage']
            selected_trade_option = forms.SelectFromList.show(trade_ops, multiselect=False, title='Select trade', default=trade_ops[0])

            if not selected_trade_option:
                forms.alert('No trades selected. Exiting script.')
                return

            selected_category_names = forms.SelectFromList.show(category_names, multiselect=True, title='Select Categories', default=category_names)

            if selected_category_names:

                # Start a single transaction for all elements
                with Transaction(doc, 'Move Elements to Workset') as t:
                    t.Start()

                    process(selected_option, selected_trade_option, selected_category_names, workset_names, doc)

                    
                    t.Commit()  # Commit the transaction once, after processing all elements
                    total_moved_elements = sum(moved_data)



                    # Record the end time
                    end_time = time.time()
                    runtime = end_time - start_time

                    run_result = "Tool ran successfully"
                    element_count = total_moved_elements
                    error_occured = "Nil"
                    get_run_data(__title__, runtime, element_count, manual_time, run_result, error_occured)




                    # 1. Display Workset Errors 
                    if workset_errors:
                        output.print_md("## ⚠️ Workset Errors")  # Markdown Heading 2
                        output.print_md("---")  # Markdown Line Break
                        for error in workset_errors:
                            output.print_md(error)

                    # 2. Display Moved Elements 
                    if report_data:
                        output.print_md("## ⚠️ WORKSETS UPDATED")  # Markdown Heading 2
                        output.print_md("---")  # Markdown Line Break
                        output.print_table(table_data=report_data, columns=["ELEMENT ID", "BEFORE", "AFTER"])

                    # 3. Display Unowned Elements 
                    if unowned_element_data:
                        output.print_md("## ⚠️ Elements Skipped ☹️")  # Markdown Heading 2
                        output.print_md("---")  # Markdown Line Break
                        output.print_md("❌ Make sure you have Ownership of the Elements - Request access. Refer to the **Table Report** below for reference")
                        output.print_table(table_data=unowned_element_data, columns=["ELEMENT ID", "CATEGORY", "TO-DO", "CURRENT OWNER"])


            else:
                forms.alert('No categories selected. Exiting script.')
                return
            
            



if __name__ == '__main__':
    main()