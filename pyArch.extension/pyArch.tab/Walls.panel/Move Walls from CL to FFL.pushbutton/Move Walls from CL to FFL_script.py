from pyrevit import revit, DB, forms

doc = revit.doc

def highlight_element(element_id):
    """Highlight the specified element."""
    uidoc = revit.uidoc
    uidoc.Selection.SetElementIds([DB.ElementId(element_id)])
    uidoc.ShowElements([DB.ElementId(element_id)])

def feet_to_mm(feet):
    """Convert feet to millimeters."""
    return feet * 304.8

def mm_to_feet(mm):
    """Convert millimeters to feet."""
    return mm / 304.8

def get_wall_materials(wall):
    """Retrieve the wall's material from its type's compound structure."""
    wall_type = wall.WallType
    compound_structure = wall_type.GetCompoundStructure()
    if compound_structure:
        layers = compound_structure.GetLayers()
        for layer in layers:
            material_id = layer.MaterialId
            if material_id != DB.ElementId.InvalidElementId:
                material = doc.GetElement(material_id)
                if material:
                    return material.Name
    return None

def move_walls_based_on_material():
    walls = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
    levels = DB.FilteredElementCollector(doc).OfClass(DB.Level).ToElements()

    if not walls:
        forms.alert('No walls found in the project.')
        return
    if not levels:
        forms.alert('No levels found in the project.')
        return

    # Sort levels by elevation
    levels = sorted(levels, key=lambda x: x.Elevation)

    # Create a dictionary to pair CL and FFL levels
    level_pairs = {}
    for i in range(0, len(levels) - 1, 2):
        level_pairs[levels[i].Id] = levels[i + 1].Id

    with revit.Transaction('Move Walls Based on Material'):
        for wall in walls:
            wall_level_id = wall.LevelId
            wall_name = wall.Name if wall.Name else "Unknown Name"
            wall_level = doc.GetElement(wall_level_id)
            wall_material = get_wall_materials(wall)

            if wall_material:
                if 'hollow' in wall_material.lower() or 'solid' in wall_material.lower():
                    if "FFL" in wall_level.Name:
                        if wall_level_id in level_pairs.values():
                            for cl_id, ffl_id in level_pairs.items():
                                if ffl_id == wall_level_id:
                                    # Use Level ID parameter to set the new level
                                    level_param = wall.LookupParameter("Base Constraint")
                                    if level_param:
                                        level_param.Set(cl_id)
                                    else:
                                        forms.alert("Wall ID {} (Name: {}) does not have a 'Base Constraint' parameter.".format(wall.Id, wall_name))
                                    break
                else:
                    if "CL" in wall_level.Name:
                        if wall_level_id in level_pairs.keys():
                            target_level_id = level_pairs[wall_level_id]
                            # Use Level ID parameter to set the new level
                            level_param = wall.LookupParameter("Base Constraint")
                            if level_param:
                                level_param.Set(target_level_id)
                            else:
                                forms.alert("Wall ID {} (Name: {}) does not have a 'Base Constraint' parameter.".format(wall.Id, wall_name))
            else:
                forms.alert('Material type for wall ID {} (Name: {}) could not be determined.'.format(wall.Id, wall_name))

if __name__ == '__main__':
    move_walls_based_on_material()
    forms.alert('Script complete!')