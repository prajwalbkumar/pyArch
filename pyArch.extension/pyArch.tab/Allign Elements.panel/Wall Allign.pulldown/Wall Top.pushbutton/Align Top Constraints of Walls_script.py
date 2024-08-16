from pyrevit import script
from pyrevit import forms
from Autodesk.Revit.DB import *

output = script.get_output()
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

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
    """Retrieve the thickness of floors above the base level and return slab bounding boxes."""
    floors = FilteredElementCollector(linked_doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElements()
    slabs_above = []

    for floor in floors:
        floor_level_id = floor.get_Parameter(BuiltInParameter.LEVEL_PARAM).AsElementId()
        floor_level = linked_doc.GetElement(floor_level_id)
        slab_height_offset = floor.get_Parameter(BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM).AsDouble()
        slab_elevation = slab_height_offset + floor_level.Elevation
        slab_id = floor.Id

        if slab_elevation > base_level_elevation:
            floor_type = linked_doc.GetElement(floor.GetTypeId())
            slab_thickness = floor_type.GetCompoundStructure().GetWidth()
            bbox = floor.get_BoundingBox(None)
            if bbox:
                slabs_above.append((slab_thickness, slab_height_offset, bbox, slab_id))
    
    return slabs_above

def get_beams(linked_doc):
    """Retrieve beams and their depths from the linked document."""
    beams = FilteredElementCollector(linked_doc).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().ToElements()
    beam_data = []
    
    for beam in beams:
        try:
            bbox = beam.get_BoundingBox(None)
            if bbox:
                beam_depth = bbox.Max.Z - bbox.Min.Z
                beam_bottom_elevation = bbox.Min.Z
                beam_data.append((beam_bottom_elevation, beam_depth, beam))
        except Exception as e:
            print("Error retrieving beam data: {}".format(e))
    
    return beam_data

def filter_concrete_levels(levels):
    """Filter levels to find those named with 'CL'."""
    return [level for level in levels if "CL" in level.LookupParameter("Name").AsString()]

def find_next_concrete_level(base_level, concrete_levels):
    """Find the next concrete level above the base level."""
    return next((cl for cl in concrete_levels if cl.Elevation > base_level.Elevation), None)

def print_bounding_box_details(bbox, label):
    """Print details of a bounding box."""
    print("{} - Min: ({:.2f}, {:.2f}, {:.2f}), Max: ({:.2f}, {:.2f}, {:.2f})".format(
        label,
        bbox.Min.X, bbox.Min.Y, bbox.Min.Z,
        bbox.Max.X, bbox.Max.Y, bbox.Max.Z
    ))

def adjust_wall_top_offset(wall, filtered_slabs_above):
    wall_bbox = wall.get_BoundingBox(None)
    if wall_bbox is None:
        print("Warning: Wall '{}' (ID: {}) has no bounding box.".format(wall.Name, output.linkify(wall.Id)))
        return

    wall_outline = Outline(wall_bbox.Min, wall_bbox.Max)

    for slab in filtered_slabs_above:
        slab_thickness, slab_height_offset, slab_bbox, slab_id = slab
        slab_bottom_elevation = slab_bbox.Min.Z
        slab_top_elevation = slab_bbox.Max.Z

        slab_outline = Outline(
            XYZ(slab_bbox.Min.X, slab_bbox.Min.Y, wall_bbox.Min.Z),
            XYZ(slab_bbox.Max.X, slab_bbox.Max.Y, wall_bbox.Max.Z)
        )

        # Debug information
        print("---")
        print("Slab thickness: {}, Slab height offset: {}, Slab ID: {}".format(slab_thickness, slab_height_offset, output.linkify(slab_id)))
        print("Wall Bounding Box - Min: ({:.2f}, {:.2f}, {:.2f}), Max: ({:.2f}, {:.2f}, {:.2f})".format(
            wall_bbox.Min.X, wall_bbox.Min.Y, wall_bbox.Min.Z,
            wall_bbox.Max.X, wall_bbox.Max.Y, wall_bbox.Max.Z
        ))
        print("Slab Bounding Box - Min: ({:.2f}, {:.2f}, {:.2f}), Max: ({:.2f}, {:.2f}, {:.2f})".format(
            slab_bbox.Min.X, slab_bbox.Min.Y, slab_bottom_elevation,
            slab_bbox.Max.X, slab_bbox.Max.Y, slab_top_elevation
        ))

        if wall_outline.Intersects(slab_outline, 1e-3):  # Increased tolerance to 1e-3
            wall_top_offset_param = slab_thickness + abs(slab_height_offset)
            current_offset = wall.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET).AsDouble()
            new_offset = -wall_top_offset_param if current_offset == 0 else min(current_offset, -wall_top_offset_param)
            wall.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET).Set(new_offset)
            print("Wall '{}' (ID: {}) adjusted to align with the intersecting slab (ID: {}) (thickness: {}).".format(
                wall.Name, output.linkify(wall.Id), output.linkify(slab_id), slab_thickness
            ))

def align_walls(selected_wall_names, linked_doc):
    levels = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
    concrete_levels = filter_concrete_levels(levels)
    sorted_concrete_levels = sorted(concrete_levels, key=lambda lvl: lvl.Elevation)
    beams = get_beams(linked_doc)  # Retrieve beam data

    adjusted_walls = []

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
                        
                        if (-1500 <= unc_height_mm <= 1500):
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
                        # Adjust wall top based on slabs
                        adjust_wall_top_offset(wall, slabs_above)
                        # Get the thickness of the slab closest to the wall
                        slab_thickness = min(slabs_above, key=lambda x: x[0] - base_level.Elevation)[1]
                        wall.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET).Set(-slab_thickness)
                        adjusted_walls.append(wall)  # Add to the list of adjusted walls

                # Adjust wall top based on beams
                for beam_bottom_elevation, beam_depth, beam in beams:
                    if beam_bottom_elevation > base_level.Elevation:
                        new_top_offset = beam_bottom_elevation - base_level.Elevation
                        if beam_depth:
                            new_top_offset = beam_depth
                        current_offset = wall.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET).AsDouble()
                        
                        if not slab_thickness or abs(current_offset + slab_thickness) < 1e-3:
                            # Adjust wall to beam bottom
                            wall.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET).Set(-new_top_offset)
                            adjusted_walls.append(wall)  # Add to the list of adjusted walls
                            break  # Exit loop after adjustment

        t.Commit()

    return adjusted_walls

def main():
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
        forms.alert("No linked model selected.")
        return
    
    linked_doc = selected_link.GetLinkDocument()

    wall_names = get_wall_names()
    selected_wall_names = forms.SelectFromList.show(wall_names, multiselect=True, title='Select Walls to Align')

    if selected_wall_names:
        adjusted_walls = align_walls(selected_wall_names, linked_doc)
        
        # Call adjust_wall_top_offset for further adjustments based on slabs
        if adjusted_walls:
            with Transaction(doc, "Adjust Wall Top Offset Based on Slabs") as t:
                t.Start()
                for wall in adjusted_walls:
                    slabs_above = get_floors_above(doc.GetElement(wall.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT).AsElementId()).Elevation, linked_doc)
                    adjust_wall_top_offset(wall, slabs_above)
                t.Commit()
    else:
        forms.alert("No walls selected for alignment.")

if __name__ == "__main__":
    main()
