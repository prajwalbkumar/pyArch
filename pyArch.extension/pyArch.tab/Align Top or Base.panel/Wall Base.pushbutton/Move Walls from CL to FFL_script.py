from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Level, BuiltInParameter, UnitUtils, DisplayUnitType
from pyrevit import revit, forms

doc = revit.doc

def get_wall_names():
    """Retrieve a list of wall names available in the model."""
    try:
        # Create a collector to get all walls in the project
        collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType()

        # Initialize a set to store unique wall names
        unique_wall_names = set()

        # Iterate over all wall elements and get their names
        for wall in collector:
            wall_name = wall.Name
            unique_wall_names.add(wall_name)
        
        return list(unique_wall_names)  # Return as a list
    except Exception as e:
        forms.alert('Error retrieving wall names: {}'.format(e))
        return []

def move_walls_based_on_direction(movement_direction, selected_wall_names):
    walls = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
    levels = FilteredElementCollector(doc).OfClass(Level).ToElements()

    if not walls:
        forms.alert('No walls found in the project.')
        return
    if not levels:
        forms.alert('No levels found in the project.')
        return

    # Filter walls based on selected wall names
    walls = [wall for wall in walls if wall.Name in selected_wall_names]

    # Sort levels by elevationoffset
    levels = sorted(levels, key=lambda x: x.Elevation)

    # Create a dictionary to pair CL and FFL levels
    level_pairs = {}
    for i in range(0, len(levels) - 1, 2):
        level_pairs[levels[i].Id] = levels[i + 1].Id

    with revit.Transaction('Move Walls Based on Direction'):
        for wall in walls:
            wall_level_id = wall.LevelId
            wall_name = wall.Name if wall.Name else "Unknown Name"
            wall_level = doc.GetElement(wall_level_id)

            # Check base offset parameter
            base_offset_param = wall.get_Parameter(BuiltInParameter.WALL_BASE_OFFSET)
            if base_offset_param:
                base_offset_mm = UnitUtils.ConvertFromInternalUnits(base_offset_param.AsDouble(), DisplayUnitType.DUT_MILLIMETERS)
                
                if base_offset_mm > 100:
                    print("Wall ID {} (Name: {}) has a base offset greater than 100 mm. Skipping level change and adjustment.".format(wall.Id, wall_name))
                    continue  # Skip this wall
                
                if base_offset_mm <= 100:
                    base_offset_param.Set(UnitUtils.ConvertToInternalUnits(0, DisplayUnitType.DUT_MILLIMETERS))
            
            if movement_direction == 'CL to FFL':
                if "CL" in wall_level.Name:
                    if wall_level_id in level_pairs.keys():
                        target_level_id = level_pairs[wall_level_id]
                        level_param = wall.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT)
                        if level_param:
                            level_param.Set(target_level_id)
                        else:
                            forms.alert("Wall ID {} (Name: {}) does not have a 'Base Constraint' parameter.".format(wall.Id, wall_name))
            elif movement_direction == 'FFL to CL':
                if "FFL" in wall_level.Name:
                    if wall_level_id in level_pairs.values():
                        for cl_id, ffl_id in level_pairs.items():
                            if ffl_id == wall_level_id:
                                level_param = wall.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT)
                                if level_param:
                                    level_param.Set(cl_id)
                                else:
                                    forms.alert("Wall ID {} (Name: {}) does not have a 'Base Constraint' parameter.".format(wall.Id, wall_name))
                                break

def main():
    # Get wall names
    wall_names = get_wall_names()
    
    if not wall_names:
        forms.alert('No wall names found in the project.')
        return

    # Get user choice for wall movement
    movement_direction = forms.SelectFromList.show(
        ['Move Walls from CL to FFL', 'Move Walls from FFL to CL'],
        multiselect=False,
        title='Choose the direction to move walls'
    )
    
    if not movement_direction:
        forms.alert('No direction selected. Exiting script.')
        return
    
    # Map user choice to direction
    movement_direction = 'CL to FFL' if 'CL to FFL' in movement_direction else 'FFL to CL'
    
    # Let user select wall names
    selected_wall_names = forms.SelectFromList.show(wall_names, multiselect=True, title='Select Wall Names', default=wall_names)
    
    if not selected_wall_names:
        forms.alert('No wall names selected. Exiting script.')
        return

    # Call the function to move the walls based on user input
    move_walls_based_on_direction(movement_direction, selected_wall_names)
    
    forms.alert('Script complete!')

if __name__ == '__main__':
    main()
