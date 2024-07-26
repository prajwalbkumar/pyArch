from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory
from pyrevit import revit, forms

doc = revit.doc

def highlight_element(element_id):
    #Highlight the specified element
    uidoc = revit.uidoc
    uidoc.Selection.SetElementIds([DB.ElementId(element_id)])
    uidoc.ShowElements([DB.ElementId(element_id)])

def feet_to_mm(feet):
    #Convert feet to millimeters.
    return feet * 304.8

def mm_to_feet(mm):
    #Convert millimeters to feet.
    return mm / 304.8

def get_wall_materials(wall):
  #Retrieve the wall's material from its type's compound structure.
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

def get_wall_types():
    #Retrieve a list of wall types available in the model
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
        forms.alert('Error retrieving wall types: {}'.format(e))
        return []

def main():
    # Get wall types
    wall_type_families = get_wall_types()
    
    if not wall_type_families:
        forms.alert('No wall types found in the project.')
        return
    
    # Remove duplicates (already handled by get_wall_types) and map families to ids
    unique_wall_type_families = wall_type_families
    family_to_id_map = {family: [] for family in unique_wall_type_families}
    
    # Get user choice for wall movement
    movement_direction = forms.CommandSwitchWindow.show([
        'Move Walls from CL to FFL',
        'Move Walls from FFL to CL'
    ], message='Choose the direction to move walls:')
    
    if not movement_direction:
        forms.alert('No direction selected. Exiting script.')
        return
    
    # Map user choice to direction
    movement_direction = 'CL to FFL' if 'CL to FFL' in movement_direction else 'FFL to CL'
    
    # Let user select wall families
    selected_wall_type_families = forms.SelectFromList.show(unique_wall_type_families, multiselect=True, title='Select Wall Families', default=unique_wall_type_families)
    
    if not selected_wall_type_families:
        forms.alert('No wall families selected. Exiting script.')
        return
    
    forms.alert('Script complete!')

if __name__ == '__main__':
    main()

