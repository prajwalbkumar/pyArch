# -*- coding: utf-8 -*-
'''Move Rooms from CL to FFL'''

__title__ = "Room Base"
__author__ = "prakritisrimal"

from pyrevit import revit, DB, forms, script
output = script.get_output()

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

def copy_room_properties(old_room, new_room):
    """Copy all parameters from the old room to the new room."""
    old_params = old_room.Parameters
    new_params = new_room.Parameters

    for old_param in old_params:
        if old_param.IsReadOnly:
            continue
        
        param_name = old_param.Definition.Name
        param_value = None
        
        if old_param.StorageType == DB.StorageType.String:
            param_value = old_param.AsString()
        elif old_param.StorageType == DB.StorageType.Double:
            param_value = old_param.AsDouble()
        elif old_param.StorageType == DB.StorageType.Integer:
            param_value = old_param.AsInteger()
        elif old_param.StorageType == DB.StorageType.ElementId:
            param_value = old_param.AsElementId()
        
        new_param = new_room.LookupParameter(param_name)
        if new_param and not new_param.IsReadOnly:
            try:
                if new_param.StorageType == DB.StorageType.String:
                    # Set the parameter as string if multiple targets match
                    if isinstance(param_value, str):
                        new_param.Set(param_value)
                    else:
                        # Convert to ElementId if not already a string
                        if isinstance(param_value, int):
                            param_value = DB.ElementId(param_value)
                        new_param.Set(param_value)
                elif new_param.StorageType == DB.StorageType.Double:
                    # Set the parameter as string if multiple targets match
                    if isinstance(param_value, str):
                        new_param.Set(param_value)
                    else:
                        # Convert to ElementId if not already a string
                        if isinstance(param_value, int):
                            param_value = DB.ElementId(param_value)
                        new_param.Set(param_value)
                elif new_param.StorageType == DB.StorageType.Integer:
                    # Set the parameter as string if multiple targets match
                    if isinstance(param_value, str):
                        new_param.Set(param_value)
                    else:
                        # Convert to ElementId if not already a string
                        if isinstance(param_value, int):
                            param_value = DB.ElementId(param_value)
                        new_param.Set(param_value)
                elif new_param.StorageType == DB.StorageType.ElementId:
                    # Set the parameter as string if multiple targets match
                    if isinstance(param_value, str):
                        new_param.Set(param_value)
                    else:
                        # Convert to ElementId if not already a string
                        if isinstance(param_value, int):
                            param_value = DB.ElementId(param_value)
                        new_param.Set(param_value)
            except Exception as e:
                output.print_md('Failed to set parameter {} on new room: {}'.format(param_name, e))



def move_rooms():
    doc = revit.doc
    rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()
    levels = DB.FilteredElementCollector(doc).OfClass(DB.Level).ToElements()
    active_view = doc.ActiveView
    
    if not rooms or not levels:
        forms.alert('No rooms or levels found in the project.')
        return

    cl_levels, ffl_levels = get_cl_and_ffl_levels(levels)
    level_pairs = create_level_pairs(cl_levels, ffl_levels)

    with revit.Transaction('Move Rooms to Next Level'):
        for room in rooms:
            room_level_id = room.LevelId
            
            if room_level_id in level_pairs:
                target_level_id = level_pairs[room_level_id]
                
                # Check if room has a valid location
                room_location = room.Location
                if not room_location:
                    output.print_md('Room {} does not have a valid location. Skipping...'.format(room.Id))
                    continue
                
                # Get the current room's location point and convert to 2D UV point
                room_location_point = room_location.Point
                if not room_location_point:
                    output.print_md('Room {} does not have a valid location point. Skipping...'.format(room.Id))
                    continue
                
                room_location_uv = DB.UV(room_location_point.X, room_location_point.Y)
                
                # Use NewRoom method to create a new room
                target_level = doc.GetElement(target_level_id)
                new_room = doc.Create.NewRoom(target_level, room_location_uv)
                
                # Copy parameters from the old room to the new room
                copy_room_properties(room, new_room)
                
                # Delete the old room
                doc.Delete(room.Id)

    forms.alert('Script complete!')

if __name__ == '__main__':
    move_rooms()


