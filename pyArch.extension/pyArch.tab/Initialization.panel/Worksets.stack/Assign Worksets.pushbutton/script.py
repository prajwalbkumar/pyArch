# -*- coding: utf-8 -*-
'''Assign elements to workset'''

__title__ = "Assign Worksets"
__author__ = "prakritisrimal"

from pyrevit import forms
from Autodesk.Revit.DB import *
doc = __revit__.ActiveUIDocument.Document

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
        excluded_categories = ['Areas', 'Curtain Panels', 'Curtain Systems', 'Curtain Wall Mullions', 'Mass', 
                                'Raster Images', 'HVAC Zones', 'Lines', 'Detail Items', 'Sun Path', 'Project Information', 'Cameras', 
                                'Sheets', 'Materials', 'Material Assets', 'Legend Components', 'Pipe Segments', 'Rooms']
        
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
        worksets = FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset).ToWorksets()
        
        def CheckExisting(workset_name):
            for workset in worksets:
                if workset.Name == workset_name:
                    return True
            return False

        def RevitValue(workset_name):
            for workset in worksets:
                if workset.Name == workset_name:
                    return workset

        if not CheckExisting(workset_name):
            print ('Workset "{}" not found.'.format(workset_name))
            return
        
        workset = RevitValue(workset_name)
        
        with Transaction(doc, 'Move Elements to Workset') as t:
            t.Start()
            moved_elements = 0
            for element in elements:
                workset_param = element.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
                if workset_param and not workset_param.IsReadOnly:
                    workset_param.Set(workset.Id.IntegerValue)
                    moved_elements += 1
            t.Commit()
            print('{} elements moved to workset "{}".'.format(moved_elements, workset_name))
    except Exception as e:
        print ('Error moving elements to workset: {}'.format(e))

def process (selected_category_names, selected_option, workset_name, doc):
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
            trade_ops = ['Architecture', 'Interior', 'Signage']
            selected_trade_option = forms.SelectFromList.show (
            trade_ops,
            multiselect=False, width=300, height=300,
            title='Select the discipline for which the worksets have to be assigned',
            default=trade_ops[0])  # Optionally, set a default selection  

            if selected_trade_option == trade_ops[0]:
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
                            floor_type = floor.FloorType
                            if floor_type:
                                compound_structure = floor_type.GetCompoundStructure()
                                if compound_structure:
                                    for layer in compound_structure.GetLayers():
                                        material_id = layer.MaterialId
                                        if material_id and material_id != ElementId.InvalidElementId:
                                            material = doc.GetElement(material_id)
                                            if material:
                                                if any(keyword in material.Name for keyword in ['Concrete', 'Steel', 'ST']):
                                                    move_elements_to_workset([floor], 'AR_ST')
                                                    break
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
                    if signage:
                        move_elements_to_workset(signage, 'AG_Signage')

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
                            wall_type = wall.WallType
                            if wall_type:
                                compound_structure = wall_type.GetCompoundStructure()
                                if compound_structure:
                                    for layer in compound_structure.GetLayers():
                                        material_id = layer.MaterialId
                                        if material_id and material_id != ElementId.InvalidElementId:
                                            material = doc.GetElement(material_id)
                                            if material:
                                                if any(keyword in material.Name for keyword in ['Concrete', 'Steel', 'ST']):
                                                    move_elements_to_workset([wall], 'AR_ST')
                                                    break
                                                elif 'Ext' in wall.Name:
                                                    move_elements_to_workset([wall], 'AR_External')
                                                elif 'Int' in wall.Name:
                                                    move_elements_to_workset([wall], 'AR_Internal')
                                                elif 'WS_Ext' in wall.Name:
                                                    move_elements_to_workset([wall], 'AR_Skin')
                            if 'CW' in wall.Name:
                                move_elements_to_workset([wall], 'AR_Internal')
                                continue 

                if 'Windows' in selected_category_names:
                    windows = get_elements(BuiltInCategory.OST_Windows)
                    if windows:
                        move_elements_to_workset(windows, 'AR_External')
            
            if selected_trade_option == trade_ops[1]:
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

            if selected_trade_option == trade_ops[2]:
                elements = FilteredElementCollector(doc).WhereElementIsNotElementType().ToElements()
                for element in elements: 
                    element_name = element.Name
                    if 'Grids' in element_name:
                        grids = get_elements(BuiltInCategory.OST_Grids)
                        if grids:
                            move_elements_to_workset (grids, 'Shared Levels and Grids')

                    if 'Levels' in element_name:
                        levels = get_elements(BuiltInCategory.OST_Levels)
                        if levels:
                            move_elements_to_workset (levels, 'Shared Levels and Grids')
                    
                    if 'Scope Boxes' in element_name:
                        scope_boxes = get_elements(BuiltInCategory.OST_VolumeOfInterest)
                        if scope_boxes:
                            move_elements_to_workset (scope_boxes, 'Scope Box')
                    
                    if 'Matchline' in element_name:
                        matchline = get_elements (BuiltInCategory.OST_Matchline)
                        if matchline:
                            move_elements_to_workset (matchline, 'Scope Box')

                    if 'RVT Links' in element_name:
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
                        move_elements_to_workset (element, 'AG_Signage')

        if selected_option == 'DAEP':
            trade_ops = ['Architecture', 'Interior', 'Signage']
            selected_trade_option = forms.SelectFromList.show (
            trade_ops,
            multiselect=False, width=300, height=300,
            title='Select the discipline for which the worksets have to be assigned',
            default=trade_ops[0])  # Optionally, set a default selection  

            if selected_trade_option == trade_ops[0]:
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
                            floor_type = floor.FloorType
                            if floor_type:
                                compound_structure = floor_type.GetCompoundStructure()
                                if compound_structure:
                                    for layer in compound_structure.GetLayers():
                                        material_id = layer.MaterialId
                                        if material_id and material_id != ElementId.InvalidElementId:
                                            material = doc.GetElement(material_id)
                                            if material:
                                                if any(keyword in material.Name for keyword in ['Concrete', 'Steel', 'ST']):
                                                    move_elements_to_workset([floor], 'ARX_ST')
                                                    break
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
                            wall_type = wall.WallType
                            if wall_type:
                                compound_structure = wall_type.GetCompoundStructure()
                                if compound_structure:
                                    for layer in compound_structure.GetLayers():
                                        material_id = layer.MaterialId
                                        if material_id and material_id != ElementId.InvalidElementId:
                                            material = doc.GetElement(material_id)
                                            if material:
                                                if any(keyword in material.Name for keyword in ['Concrete', 'Steel', 'ST']):
                                                    move_elements_to_workset([wall], 'ARX_ST')
                                                    break
                                                elif 'Ext' in wall.Name:
                                                    move_elements_to_workset([wall], 'ARX_External')
                                                elif 'Int' in wall.Name:
                                                    move_elements_to_workset([wall], 'ARX_Internal')
                                                elif 'WS_Ext' in wall.Name:
                                                    move_elements_to_workset([wall], 'ASK_Skin')
                            if 'CW' in wall.Name:
                                move_elements_to_workset([wall], 'ARX_Internal')
                                continue 

                if 'Windows' in selected_category_names:
                    windows = get_elements(BuiltInCategory.OST_Windows)
                    if windows:
                        move_elements_to_workset(windows, 'ARX_External')
            
            if selected_trade_option == trade_ops[1]:
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

            if selected_trade_option == trade_ops[2]:
                elements = FilteredElementCollector(doc).WhereElementIsNotElementType().ToElements()
                for element in elements: 
                    element_name = element.Name
                    if 'Grids' in element_name:
                        grids = get_elements(BuiltInCategory.OST_Grids)
                        if grids:
                            move_elements_to_workset (grids, 'Shared Levels and Grids')

                    if 'Levels' in element_name:
                        levels = get_elements(BuiltInCategory.OST_Levels)
                        if levels:
                            move_elements_to_workset (levels, 'Shared Levels and Grids')
                    
                    if 'Scope Boxes' in element_name:
                        scope_boxes = get_elements(BuiltInCategory.OST_VolumeOfInterest)
                        if scope_boxes:
                            move_elements_to_workset (scope_boxes, 'Scope Box')
                    
                    if 'Matchline' in element_name:
                        matchline = get_elements (BuiltInCategory.OST_Matchline)
                        if matchline:
                            move_elements_to_workset (matchline, 'Scope Box')

                    if 'RVT Links' in element_name:
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
                    move_elements_to_workset([column], 'ARC_Columns')
                strl_columns = get_elements(BuiltInCategory.OST_StructuralColumns)
                if strl_columns:
                    for strl_column in strl_columns:
                        strl_column_type = strl_column.ColumnType
                        if strl_column_type:
                            strl_compound_structure = strl_column_type.GetCompoundStructure()
                            if strl_compound_structure:
                                for layer in strl_compound_structure.GetLayers():
                                    material_id = layer.MaterialId
                                    if material_id and material_id != ElementId.InvalidElementId:
                                        material = doc.GetElement(material_id)
                                        if material:
                                            if any(keyword in material.Name for keyword in ['Concrete']):
                                                move_elements_to_workset([strl_column], 'STR_Concrete')
                                                break
                                            if any (keyword in material.Name for keyword in ['Steel', 'ST', 'Metal', 'Alumnium']):
                                                move_elements_to_workset([strl_column], 'STR_Steel')
                                                break
                                            else:
                                                move_elements_to_workset([strl_column], 'ARC_Columns')


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
                        wall_type = wall.WallType
                        if wall_type:
                            compound_structure = wall_type.GetCompoundStructure()
                            if compound_structure:
                                for layer in compound_structure.GetLayers():
                                    material_id = layer.MaterialId
                                    if material_id and material_id != ElementId.InvalidElementId:
                                        material = doc.GetElement(material_id)
                                        if material:
                                            if any(keyword in material.Name for keyword in 'Concrete'):
                                                move_elements_to_workset([wall], 'STR_Concrete')
                                                break
                                            if any(keyword in material.Name for keyword in 'Steel'):
                                                move_elements_to_workset([wall], 'STR_Steel')
                                                break
                                            elif 'Ext' in wall.Name:
                                                move_elements_to_workset([wall], 'ARC_External')
                                            elif 'IDN' in wall.Name:
                                                move_elements_to_workset([wall], 'ARC_Internal')
                        if 'CW' in wall.Name:
                            move_elements_to_workset([wall], 'ARC_Internal')
                            continue 

            if 'Windows' in selected_category_names:
                windows = get_elements(BuiltInCategory.OST_Windows)
                if windows:
                    move_elements_to_workset(windows, 'ARC_External')

        

    except Exception as e:
        forms.alert("An error occurred: {}".format(e))

def main():
    if not doc.IsWorkshared:
        forms.alert("File not Workshared - Create a Workshared Model First!", title='Script Cancelled')
        return
    
    # Prompt user for trade selection
    ops = ['DAR', 'DAEP', 'NEOM']
    selected_option = forms.SelectFromList.show(
        ops,
        multiselect=False, width=300, height=300,
        title='Select the standards as per which worksets should be created',
        default=ops[0]  # Optionally, set a default selection
    )
    if not selected_option:
        script.exit()

    workset_names = get_workset_names()
    # Fetch both model and annotation categories
    category_names = get_combined_category_names()
    if not category_names:
        forms.alert('No categories found in the project.')
        return
    
    selected_category_names = forms.SelectFromList.show(category_names, multiselect=True, title='Select Categories', default=category_names)

    if selected_category_names:
        process(selected_category_names, selected_option, workset_names, doc)
        
    if not selected_category_names:
        forms.alert('No categories selected. Exiting script.')
        return

    # if selected_option == 'Architecture':
    #     process_architecture(selected_category_names)

    # elif selected_option == 'Interior':
    #     process_interior(selected_category_names)

    # elif selected_option == 'Signage':
    #     process_signage(doc)

    # elif selected_option == 'Exit':
    #     print("Worksets are not created")
    #     return  # Ensuring script ends after 'Exit' selection

if __name__ == '__main__':
    main()


