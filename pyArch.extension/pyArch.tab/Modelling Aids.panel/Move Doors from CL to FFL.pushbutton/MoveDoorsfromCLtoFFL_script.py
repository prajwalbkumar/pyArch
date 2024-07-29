from pyrevit import revit, DB, forms

def highlight_element(element_id):
    """Highlight the specified element."""
    uidoc = revit.uidoc
    uidoc.Selection.SetElementIds(DB.ElementId(element_id))
    uidoc.ShowElements(element_id)

def feet_to_mm(feet):
    """Convert feet to millimeters."""
    return feet * 304.8

def mm_to_feet(mm):
    """Convert millimeters to feet."""
    return mm / 304.8

def move_doors_and_adjust_sill_heights():
    doc = revit.doc
    doors = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()
    levels = DB.FilteredElementCollector(doc).OfClass(DB.Level).ToElements()
    
    if not doors or not levels:
        forms.alert('No doors or levels found in the project.')
        return

    # Sort levels by elevation
    levels = sorted(levels, key=lambda x: x.Elevation)

    # Create a dictionary to pair CL and FFL levels
    level_pairs = {}
    for i in range(0, len(levels) - 1, 2):
        level_pairs[levels[i].Id] = levels[i + 1].Id

    tolerance = 100  # Tolerance in millimeters

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


                    if current_sill_height_mm >= 101:
                        print("Sill height for door ID {} is greater than 101 mm. Skipping level change and sill height adjustment.".format(door.Id))
                        continue  # Skip this door

                    # If we are here, the sill height is 101 mm or less
                    if abs(current_sill_height_mm - level_difference_mm) <= tolerance:
                        sill_height_param.Set(mm_to_feet(0))  # Convert back to feet
                        #print("Sill height set to 0 for door ID: {}".format(door.Id))
                    elif current_sill_height_mm > level_difference_mm:
                        new_sill_height_mm = current_sill_height_mm - level_difference_mm
                        sill_height_param.Set(mm_to_feet(new_sill_height_mm))  # Convert back to feet
                        #print("Sill height reduced by level difference for door ID: {}".format(door.Id))
                    else:
                        #print("Sill height difference exceeds tolerance for door ID: {}".format(door.Id))
                        highlight_element(door.Id)

                    # Move door to target level
                    level_param.Set(target_level_id)
                else:
                    forms.alert('Door ID ' + str(door.Id) + ' does not have the required parameters.')

if __name__ == '__main__':
    move_doors_and_adjust_sill_heights()
