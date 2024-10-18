# -*- coding: utf-8 -*-
'''Move Doors from CL to FFL and adjust sill heights'''

__title__ = "Door Base"
__author__ = "prakritisrimal"

from pyrevit import script, forms, DB, revit
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import Selection, ObjectType, ISelectionFilter
from System.Collections.Generic import List
output = script.get_output()
doc = __revit__.ActiveUIDocument.Document
ui_doc = __revit__.ActiveUIDocument

def feet_to_mm(feet):
    """Convert feet to millimeters."""
    return feet * 304.8

def mm_to_feet(mm):
    """Convert millimeters to feet."""
    return mm / 304.8

def get_cl_and_ffl_levels(levels):
    """Identify Concrete Levels (CL) and Floor Finish Levels (FFL) from levels."""
    cl_levels = {}
    ffl_levels = {}
    
    for level in levels:
        level_name = level.Name
        if "CL" in level_name:
            cl_levels[level.Id] = level
        elif "FFL" in level_name:
            ffl_levels[level.Id] = level
    
    return cl_levels, ffl_levels

def create_level_pairs(cl_levels, ffl_levels):
    """Create pairs of CL and FFL levels."""
    level_pairs = {}
    
    cl_list = sorted(cl_levels.values(), key=lambda l: l.Elevation)
    ffl_list = sorted(ffl_levels.values(), key=lambda l: l.Elevation)
    
    for cl in cl_list:
        for ffl in ffl_list:
            if ffl.Elevation > cl.Elevation:
                level_pairs[cl.Id] = ffl.Id
                break
    
    return level_pairs

def move_doors_and_adjust_sill_heights():
    doc = revit.doc


     # Define a selection filter class for walls
    class DoorSelectionFilter(ISelectionFilter):
        def AllowElement(self, element):
            if element.Category.Id.IntegerValue == int(BuiltInCategory.OST_Doors):
                return True
            return False
        
        def AllowReference(self, ref, point):
            return False

    target_doors = []


    #Pre-Selected Doors
    selection = ui_doc.Selection.GetElementIds()
    if len(selection)>0:
        for id in selection:
            element = doc.GetElement(id)
            try:
                if element.Category.Id.IntegerValue == int(BuiltInCategory.OST_Doors):
                    target_doors.append(element)
            except:
                continue

    else:
        #Custom selection 
        selection_options = forms.alert("This Tool Aligns Door Base.",
                                        title="Align Door Base - Select Doors", 
                                        warn_icon=False, 
                                        options=["Select All Doors", "Select Specific Doors"])
        if not selection_options:
            script.exit()

        elif selection_options == "Select All Doors":

            unique_door_names = set()
            door_type_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType()

            for door_type in door_type_collector:
                door_name = door_type.Name
                if door_name:
                    unique_door_names.add(door_name)

            if not unique_door_names:
                #forms.alert("No doors found in the model. Exiting script.")
                script.exit()

            sorted_door_names = sorted(unique_door_names)
            
            door_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()
            
            selected_door_names = forms.SelectFromList.show(sorted_door_names, multiselect=True, title='Select Doors to Align')
            if not selected_door_names:
                script.exit()

            for door in door_collector:
                if door.Name in selected_door_names:
                    target_doors.append(door)

        else:
            # Prompt user to select doors
            try:
                choices = ui_doc.Selection
                selected_elements = choices.PickObjects(ObjectType.Element, DoorSelectionFilter(), "Select doors only")
                
                for selected_element in selected_elements:
                    door = doc.GetElement(selected_element.ElementId)
                    target_doors.append(door)

            except:
                script.exit()



    # Filter out not owned element
    collected_elements = target_doors  #List of Elements that the Tool Targets
    owned_elements = []
    unowned_elements = []
    elements_to_checkout = List[ElementId]()

    for element in collected_elements:
        elements_to_checkout.Add(element.Id)

    WorksharingUtils.CheckoutElements(doc, elements_to_checkout)

    for element in collected_elements:    
        worksharingStatus = WorksharingUtils.GetCheckoutStatus(doc, element.Id)
        if not worksharingStatus == CheckoutStatus.OwnedByOtherUser:
            owned_elements.append(element)
        else:
            unowned_elements.append(element)

    checkedout_target_doors = owned_elements


    
    skipped_data  =  []
    failed_data   =  []

    levels = DB.FilteredElementCollector(doc).OfClass(DB.Level).ToElements()
    
    if not checkedout_target_doors or not levels:
        forms.alert('No doors or levels found in the project.')
        return

    tolerance = 100  # Tolerance range in millimeters

    cl_levels, ffl_levels = get_cl_and_ffl_levels(levels)
    level_pairs = create_level_pairs(cl_levels, ffl_levels)

    with revit.Transaction('Move Doors to Next Level'):
        for door in target_doors:
            door_level_id = door.LevelId
            door_name = door.Name
            type_id = door.GetTypeId()
            door_type = doc.GetElement(type_id)
            door_description_param = door_type.LookupParameter("Door_Type")

            if door_description_param:
                door_description = door_description_param.AsString()
            else:
                door_description = ''
            
            if door_level_id in ffl_levels:
                # Perform access panel door adjustments
                level_param = door.get_Parameter(DB.BuiltInParameter.FAMILY_LEVEL_PARAM)
                sill_height_param = door.get_Parameter(DB.BuiltInParameter.INSTANCE_SILL_HEIGHT_PARAM)
                
                if level_param and sill_height_param:
                    current_sill_height_mm = feet_to_mm(sill_height_param.AsDouble())

                    if 'AP' in door.Symbol.Family.Name or 'Access Panel' in door_description:
                        if current_sill_height_mm >= 0 and current_sill_height_mm < 150:
                            sill_height_param.Set(mm_to_feet(150))
                            print('Access panel door (door ID {}) Sill height adjusted to 150mm.'.format(output.linkify(door.Id)))
                        else:
                            door_data = [ output.linkify(door.Id),
                                         door.Name,door.LookupParameter("Sill Height").AsValueString(),door.get_Parameter(DB.BuiltInParameter.SCHEDULE_LEVEL_PARAM).AsValueString(), 
                                         "INSUFFICIENT SILL HEIGHT" ]
                            skipped_data.append(door_data)

                        continue  # Skip further processing for this door

            else:
                # Process doors not at FFL level
                if door_level_id in level_pairs:
                    target_level_id = level_pairs[door_level_id]
                    level_param = door.get_Parameter(DB.BuiltInParameter.FAMILY_LEVEL_PARAM)
                    sill_height_param = door.get_Parameter(DB.BuiltInParameter.INSTANCE_SILL_HEIGHT_PARAM)
                    
                    if level_param and sill_height_param:
                        current_level = doc.GetElement(door_level_id)
                        target_level = doc.GetElement(target_level_id)
                        
                        current_level_elevation_mm = feet_to_mm(current_level.Elevation)
                        target_level_elevation_mm = feet_to_mm(target_level.Elevation)
                        level_difference_mm = target_level_elevation_mm - current_level_elevation_mm
                        current_sill_height_mm = feet_to_mm(sill_height_param.AsDouble())
                        
                        if 'AP' in door.Symbol.Family.Name or 'Access Panel' in door_description:
                            if current_sill_height_mm >= 0 and current_sill_height_mm < 150:
                                sill_height_param.Set(mm_to_feet(150))
                                level_param.Set(target_level_id)
   
                            else:
                                door_data = [ output.linkify(door.Id),
                                         door.Name,door.LookupParameter("Sill Height").AsValueString(),door.get_Parameter(DB.BuiltInParameter.SCHEDULE_LEVEL_PARAM).AsValueString(), 
                                         "INSUFFICIENT SILL HEIGHT" ]
                                skipped_data.append(door_data)
                            continue

                        if current_sill_height_mm < 0:
                            door_data = [ output.linkify(door.Id),
                                         door.Name,door.LookupParameter("Sill Height").AsValueString(),door.get_Parameter(DB.BuiltInParameter.SCHEDULE_LEVEL_PARAM).AsValueString(), 
                                         "INSUFFICIENT SILL HEIGHT" ]
                            skipped_data.append(door_data)
                            continue

                        if current_sill_height_mm >= 101:
                            door_data = [ output.linkify(door.Id),
                                        door.Name,door.LookupParameter("Sill Height").AsValueString(),door.get_Parameter(DB.BuiltInParameter.SCHEDULE_LEVEL_PARAM).AsValueString(), 
                                        "INSUFFICIENT SILL HEIGHT" ]
                            skipped_data.append(door_data)
                            continue

                        if abs(current_sill_height_mm - level_difference_mm) <= tolerance:
                            sill_height_param.Set(mm_to_feet(0))

                        elif current_sill_height_mm > level_difference_mm:
                            new_sill_height_mm = current_sill_height_mm - level_difference_mm
                            sill_height_param.Set(mm_to_feet(new_sill_height_mm))

                        else:
                            door_data = [ output.linkify(door.Id),
                                        door.Name,door.LookupParameter("Sill Height").AsValueString(),door.get_Parameter(DB.BuiltInParameter.SCHEDULE_LEVEL_PARAM).AsValueString(), 
                                        "EXCESSIVE LEVEL DIFFERENCE" ]
                            skipped_data.append(door_data)
                            continue

                        level_param.Set(target_level_id)
                    else:
                        door_data = [ output.linkify(door.Id),
                                     door.Name,door.LookupParameter("Sill Height").AsValueString(), door.get_Parameter(DB.BuiltInParameter.SCHEDULE_LEVEL_PARAM).AsValueString(), 
                                    "INSUFFICIENT PARAMETERS" ]
                        failed_data.append(door_data)
                        forms.alert('Door ID {} does not have the required parameters.'.format(output.linkify(door.Id)))

    if skipped_data:
        output.print_md("##⚠️ {} Completed. Some Doors were Skipped ☹️".format(__title__))
        output.print_md("---")
        output.print_md("❌ Some Doors were Skipped. Refer to the **Table Report** below for reference")
        output.print_table(table_data=skipped_data, columns=["ELEMENT ID", "DOOR NAME", "SILL HEIGHT", "LEVEL", "ERROR CODE"])
        output.print_md("---")
        output.print_md("***✅ ERROR CODE REFERENCE***")
        output.print_md("---")
        output.print_md("**INSUFFICIENT SILL HEIGHT**      - sill height not in the range of 0 to 100 \n")
        output.print_md("**EXCESSIVE LEVEL DIFFERENCE**    - Excessive Level Difference between CL and FFL \n")
        output.print_md("---")

    if failed_data:
        output.print_md("##⚠️ {} Completed. Issues Found ☹️".format(__title__))
        output.print_md("---")
        output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")
        output.print_table(table_data=failed_data, columns=["ELEMENT ID", "DOOR NAME", "SILL HEIGHT", "LEVEL", "ERROR CODE"])
        output.print_md("---")
        output.print_md("***✅ ERROR CODE REFERENCE***")
        output.print_md("---")
        output.print_md("**INSUFFICIENT PARAMETERS** - Door does not have the required parameters \n")
        output.print_md("---")

    if unowned_elements:
        unowned_element_data = []
        for element in unowned_elements:
            try:
                unowned_element_data.append([output.linkify(element.Id), element.Category.Name.upper(), "REQUEST OWNERSHIP", WorksharingUtils.GetWorksharingTooltipInfo(doc, element.Id).Owner])
            except:
                pass

        output.print_md("##⚠️ Elements Skipped ☹️") # Markdown Heading 2
        output.print_md("---") # Markdown Line Break
        output.print_md("❌ Make sure you have Ownership of the Elements - Request access. Refer to the **Table Report** below for reference")  # Print a Line
        output.print_table(table_data = unowned_element_data, columns=["ELEMENT ID", "CATEGORY", "TO-DO", "CURRENT OWNER"]) # Print a Table
        print("\n\n")
        output.print_md("---") # Markdown Line Break


    if not skipped_data and not failed_data and not unowned_element_data:
        output.print_md("##✅ {} Completed. No Issues Found 😃".format(__title__))
        output.print_md("---")





if __name__ == '__main__':
    move_doors_and_adjust_sill_heights()
