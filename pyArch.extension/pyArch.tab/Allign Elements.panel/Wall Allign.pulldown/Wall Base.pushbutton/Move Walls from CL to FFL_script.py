# -*- coding: utf-8 -*-
'''Move Walls from CL to FFL/ from FFL to CL'''

__title__ = "Wall Base"
__author__ = "prakritisrimal"

from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
output = script.get_output()

doc = revit.doc

def get_wall_names():
    """Retrieve a list of wall names available in the model."""
    try:
        collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType()
        unique_wall_names = set()
        for wall in collector:
            wall_name = wall.Name
            if wall_name:
                unique_wall_names.add(wall_name)
        return list(unique_wall_names)
    except Exception as e:
        forms.alert('Error retrieving wall names: {}'.format(e))
        return []

def extract_walls_from_groups(elements):
    """Extract walls from groups if they are part of a group."""
    walls = []
    for elem in elements:
        if isinstance(elem, Group):
            for group_elem in elem.GroupMembers:
                if isinstance(group_elem, Wall):
                    walls.append(group_elem)
        else:
            if isinstance(elem, Wall):
                walls.append(elem)
    return walls

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

def update_base_offset(walls):
    """Update the base offset parameter of walls, setting it to 0 based on specified conditions."""
    with Transaction(doc, "Update Wall Base Offset") as t:
        try:
            t.Start()
            for wall in walls:
                base_offset_param = wall.LookupParameter("Base Offset")
                
                if base_offset_param:
                    try:
                        base_offset_value = base_offset_param.AsDouble()
                        base_offset_mm = base_offset_value * 304.8  # Convert feet to millimeters
                        
                        if -100 <= base_offset_mm <= 100:
                            if base_offset_mm > 0:
                                print("Wall Name: {} (ID: {}) base offset set to 0 from {} mm and wall moved to CL/FFL as per user selection.".format(wall.Name, output.linkify(wall.Id), base_offset_mm))
                            base_offset_param.Set(0)  # Set to 0, assuming input in feet
                        else:
                            print("Wall Name: {} (ID: {}) has a base offset outside the range of -100 mm to 100 mm. Skipping level change and adjustment.".format(wall.Name, output.linkify(wall.Id)))
                        
                    except Exception as e:
                        forms.alert("Error processing base offset for wall Name {}: {}".format(wall.Name, e))
                        continue
                else:
                    forms.alert("Error: Base offset parameter is None for wall Name {}".format(wall.Name))
                    continue
            t.Commit()
        except Exception as e:
            t.RollBack()
            forms.alert('Error during base offset update: {}'.format(e))

def move_walls_based_on_direction(movement_direction, selected_wall_names):
    walls = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
    walls = extract_walls_from_groups(walls)  # Extract walls from groups
    levels = FilteredElementCollector(doc).OfClass(Level).ToElements()

    if not walls:
        forms.alert('No walls found in the project.')
        return
    if not levels:
        forms.alert('No levels found in the project.')
        return

    walls = [wall for wall in walls if wall.Name in selected_wall_names]
    
    cl_levels, ffl_levels = get_cl_and_ffl_levels(levels)
    level_pairs = create_level_pairs(cl_levels, ffl_levels)

    update_base_offset(walls)
    walls_not_moved = []

    with Transaction(doc, 'Move Walls Based on Direction') as txn:
        try:
            txn.Start()
            for wall in walls:
                wall_level_id = wall.LevelId
                wall_name = wall.Name
                wall_level = doc.GetElement(wall_level_id)
                wall_type = doc.GetElement(wall.WallType.Id)

                if wall_type and wall_type.FamilyName == 'Curtain Wall':
                    print("Warning: Wall {} (ID: {}) is a curtain wall. Moving the wall might have changed the divisions of the panels.".format(wall_name, output.linkify(wall.Id)))
                    
                if wall_level:
                    wall_level_name = wall_level.Name if wall_level.Name else "Unknown Level"
                    
                    if movement_direction == 'CL to FFL':
                        if "CL" in wall_level_name:
                            if wall_level_id in level_pairs:
                                target_ffl_id = level_pairs[wall_level_id]
                                level_param = wall.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT)
                                if level_param:
                                    level_param.Set(target_ffl_id)
                                else:
                                    walls_not_moved.append((wall_name, wall.Id))
                    elif movement_direction == 'FFL to CL':
                        if "FFL" in wall_level_name:
                            if wall_level_id in level_pairs.values():
                                for cl_id, ffl_id in level_pairs.items():
                                    if ffl_id == wall_level_id:
                                        level_param = wall.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT)
                                        if level_param:
                                            level_param.Set(cl_id)
                                        else:
                                            walls_not_moved.append((wall_name, wall.Id))
                                        break
                else:
                    walls_not_moved.append((wall_name, wall.Id))
            txn.Commit()
        except Exception as e:
            txn.RollBack()
            forms.alert('Error during wall movement: {}'.format(e))
    
    if walls_not_moved:
        print("The following walls were not moved:")
        for wall_name, wall_id in walls_not_moved:
            print("Wall Name {} (ID: {}) was not moved.".format(wall_name, output.linkify(wall_id)))

def main():
    wall_names = get_wall_names()
    
    if not wall_names:
        forms.alert('No wall names found in the project.')
        return

    movement_direction = forms.SelectFromList.show(
        ['Move Walls from CL to FFL', 'Move Walls from FFL to CL'],
        multiselect=False,
        title='Choose the direction to move walls'
    )
    
    if not movement_direction:
        forms.alert('No direction selected. Exiting script.')
        return
    
    movement_direction = 'CL to FFL' if 'CL to FFL' in movement_direction else 'FFL to CL'
    
    selected_wall_names = forms.SelectFromList.show(wall_names, multiselect=True, title='Select Wall Names', default=wall_names)
    
    if not selected_wall_names:
        forms.alert('No wall names selected. Exiting script.')
        return

    move_walls_based_on_direction(movement_direction, selected_wall_names)
    
    forms.alert('Script complete!')

if __name__ == '__main__':
    main()
