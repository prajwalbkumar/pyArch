from pyrevit import script
from pyrevit import forms
from Autodesk.Revit.DB import *
output = script.get_output()

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
        print("Error retrieving wall names: {}".format(e))
        return []

def get_floors_above(base_level_elevation, linked_doc):
    """Retrieve floors that are directly above the base level."""
    floors = FilteredElementCollector(linked_doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElements()
    slabs_above = []
    
    for floor in floors:
        floor_level_id = floor.get_Parameter(BuiltInParameter.LEVEL_PARAM).AsElementId()
        floor_level = linked_doc.GetElement(floor_level_id)
        slab_height_offset = floor.get_Parameter(BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM).AsDouble()
        slab_elevation = slab_height_offset + floor_level.Elevation
        
        if slab_elevation > base_level_elevation:  # Check if slab is above the base level
            floor_type = linked_doc.GetElement(floor.GetTypeId())
            slab_thickness = floor_type.GetCompoundStructure().GetWidth()
            slabs_above.append((slab_elevation, slab_thickness))
    
    return slabs_above

def get_beams(linked_doc):
    """Retrieve beams and their depths from the linked document."""
    beams = FilteredElementCollector(linked_doc).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().ToElements()
    beam_data = []
    
    for beam in beams:
        try:
            bbox = beam.get_BoundingBox(None)
            if bbox:
                # Calculate depth as the height of the bounding box
                beam_depth = bbox.Max.Z - bbox.Min.Z
                beam_bottom_elevation = bbox.Min.Z
                beam_data.append((beam_bottom_elevation, beam_depth, beam))
        except Exception as e:
            print("Error retrieving beam data: {}".format(e))
    
    return beam_data

def filter_concrete_levels(levels):
    concrete_levels = [level for level in levels if "CL" in level.LookupParameter("Name").AsString()]
    return concrete_levels

def find_next_concrete_level(base_level, concrete_levels):
    next_concrete_level = next((cl for cl in concrete_levels if cl.Elevation > base_level.Elevation), None)
    return next_concrete_level

def get_level_elevation(level_id):
    """Retrieve the elevation of a level given its ElementId."""
    level = doc.GetElement(level_id)
    if isinstance(level, Level):
        return level.Elevation
    return None

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# Prompt user to select a linked model
linked_files = FilteredElementCollector(doc).OfClass(RevitLinkInstance).ToElements()
linked_file_names = [link.Name for link in linked_files]
selected_link_name = forms.SelectFromList.show(linked_file_names, title='Select Linked Model', button_name='Select')

# Get the selected linked document
selected_link = None
for link in linked_files:
    if link.Name == selected_link_name:
        selected_link = link
        break

if not selected_link:
    forms.alert("No linked file selected or file not found.")
    script.exit()

linked_doc = selected_link.GetLinkDocument()

def align_walls(selected_wall_names):
    levels = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
    concrete_levels = filter_concrete_levels(levels)
    sorted_concrete_levels = sorted(concrete_levels, key=lambda lvl: lvl.Elevation)
    beams = get_beams(linked_doc)  # Retrieve beam data

    with Transaction(doc, "Align Wall Top Constraint and Set Offset") as t:
        t.Start()
        for wall in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements():
            if wall.Name in selected_wall_names:
                base_level_id = wall.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT).AsElementId()
                base_level = doc.GetElement(base_level_id)
                unc_height_param = wall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM)
                wall_type = doc.GetElement(wall.WallType.Id)

                if wall_type:
                    if wall_type.FamilyName == 'Curtain Wall':
                        print("Warning: Wall '{}' (ID: {}) is a curtain wall. Moving the wall might have changed the divisions of the panels.".format(wall.Name, output.linkify(wall.Id)))
                else:
                    forms.alert("Error: Wall type is None for wall Name {}".format(wall.Name))
                    continue

                if unc_height_param:
                    try:
                        unc_height_value = unc_height_param.AsDouble()
                        unc_height_mm = unc_height_value * 304.8  # Convert feet to millimeters
                        
                        if -1500 <= unc_height_mm <= 1500:
                            print("Wall Name: {} (ID: {}) has an unconnected height outside the range of -1500 mm to 1500 mm. Skipping top constraint change.".format(wall.Name, output.linkify(wall.Id)))
                            continue  # Skip to the next wall
                    except Exception as e:
                        forms.alert("Error processing unconnected height for wall Name {}: {}".format(wall.Name, e))
                        continue
                else:
                    forms.alert("Error: Unconnected height parameter is None for wall Name {}".format(wall.Name))
                    continue
                
                if base_level is None:
                    print("Base level not found for wall ID: {}".format(wall.Id.IntegerValue))
                    continue

                next_concrete_level = find_next_concrete_level(base_level, sorted_concrete_levels)

                if next_concrete_level:
                    wall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).Set(next_concrete_level.Id)
                    # Get the slabs above the base level
                    slabs_above = get_floors_above(base_level.Elevation, linked_doc)
                    
                    slab_thickness = 0
                    if slabs_above:
                        # Get the thickness of the slab closest to the wall
                        slab_thickness = min(slabs_above, key=lambda x: x[0] - base_level.Elevation)[1]
                        wall.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET).Set(-slab_thickness)
                    else:
                        #print("No slabs found above level: {}".format(next_concrete_level.LookupParameter("Name").AsString()))
                        pass  # Continue to adjust based on beams

                else:
                    print("No next concrete level found for wall ID: {}".format(wall.Id.IntegerValue))

                # Adjust wall top based on beams
                adjusted = False
                for beam_bottom_elevation, beam_depth, beam in beams:
                    if beam_bottom_elevation > base_level.Elevation:
                        new_top_offset = beam_bottom_elevation - base_level.Elevation
                        if beam_depth:
                            new_top_offset = beam_depth
                        current_offset = wall.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET).AsDouble()
                        
                        if slab_thickness and abs(current_offset - (-slab_thickness)) < 1e-3:
                            # The wall is already aligned with the slab bottom, adjust to beam
                            wall.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET).Set(-new_top_offset)
                            #print("Wall '{}' (ID: {}) adjusted to align with beam (ID: {}).".format(wall.Name, output.linkify(wall.Id), output.linkify(beam.Id)))
                            adjusted = True
                            break

                #if not adjusted:
                    # If no adjustment was made to align with beams, print message if needed
                    #print("No adjustment needed for wall '{}' (ID: {}).".format(wall.Name, output.linkify(wall.Id)))
        t.Commit()


def main():
    wall_names = get_wall_names()
    
    if not wall_names:
        forms.alert('No wall names found in the project.')
        return
    
    selected_wall_names = forms.SelectFromList.show(wall_names, multiselect=True, title='Select Wall Names', default=wall_names)
    
    if not selected_wall_names:
        forms.alert('No wall names selected. Exiting script.')
        return

    align_walls(selected_wall_names)
    
    forms.alert('Script complete!')

if __name__ == '__main__':
    main()
