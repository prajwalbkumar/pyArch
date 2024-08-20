# -*- coding: utf-8 -*-
'''Move Doors from CL to FFL and adjust sill heights'''

__title__ = "Door Base"
__author__ = "prakritisrimal"

from pyrevit import revit, DB, forms, script
output = script.get_output()

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
    doors = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()
    levels = DB.FilteredElementCollector(doc).OfClass(DB.Level).ToElements()
    
    if not doors or not levels:
        forms.alert('No doors or levels found in the project.')
        return

    # Fixed tolerance value in millimeters
    tolerance = 100  # Set tolerance range between -100 and +100 as needed

    cl_levels, ffl_levels = get_cl_and_ffl_levels(levels)
    level_pairs = create_level_pairs(cl_levels, ffl_levels)

    with revit.Transaction('Move Doors to Next Level'):
        for door in doors:
            door_level_id = door.LevelId
            
            if door_level_id in level_pairs:
                target_level_id = level_pairs[door_level_id]
                level_param = door.get_Parameter(DB.BuiltInParameter.FAMILY_LEVEL_PARAM)
                sill_height_param = door.get_Parameter(DB.BuiltInParameter.INSTANCE_SILL_HEIGHT_PARAM)
                
                if level_param and sill_height_param:
                    current_level = doc.GetElement(door_level_id)
                    target_level = doc.GetElement(target_level_id)
                    
                    # Convert elevations from feet to millimeters
                    current_level_elevation_mm = feet_to_mm(current_level.Elevation)
                    target_level_elevation_mm = feet_to_mm(target_level.Elevation)
                    level_difference_mm = target_level_elevation_mm - current_level_elevation_mm

                    current_sill_height_mm = feet_to_mm(sill_height_param.AsDouble())

                    if current_sill_height_mm < 0:
                        print('Sill height for door ID {} is negative. Skipping level change and sill height adjustment.'.format(output.linkify(door.Id)))
                        continue  # Skip this door

                    if current_sill_height_mm >= 101:
                        print("Sill height for door ID {} is greater than 101 mm. Skipping level change and sill height adjustment.".format(output.linkify(door.Id)))
                        continue  # Skip this door

                    # If we are here, the sill height is 101 mm or less
                    if abs(current_sill_height_mm - level_difference_mm) <= tolerance:
                        sill_height_param.Set(mm_to_feet(0))  # Convert back to feet
                        print("Sill height set to 0 for door ID: {}".format(output.linkify(door.Id)))
                    elif current_sill_height_mm > level_difference_mm:
                        new_sill_height_mm = current_sill_height_mm - level_difference_mm
                        sill_height_param.Set(mm_to_feet(new_sill_height_mm))  # Convert back to feet
                        print("Sill height reduced by level difference for door ID: {}".format(output.linkify(door.Id)))
                    else:
                        print("Sill height difference exceeds tolerance for door ID: {}".format(output.linkify(door.Id)))
                        continue

                    # Move door to target level
                    level_param.Set(target_level_id)
                else:
                    forms.alert('Door ID ' + str(door.Id) + ' does not have the required parameters.')
    forms.alert('Script complete!')
if __name__ == '__main__':
    move_doors_and_adjust_sill_heights()
