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

        if slab_elevation > base_level_elevation:
            print ("---")
            print("Floor level elevation: {}".format(floor_level.Elevation))
            print("Floor height offset from level: {}".format(slab_height_offset))
            floor_type = linked_doc.GetElement(floor.GetTypeId())
            print("Floor type: {}".format(floor_type.LookupParameter("Type Name").AsString()))
            slab_thickness = floor_type.GetCompoundStructure().GetWidth()
            print("Floor thickness: {}".format(slab_thickness))

            bbox = floor.get_BoundingBox(None)
            if bbox:
                slabs_above.append((slab_thickness, bbox))
    
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

def create_bounding_box_between_slabs(slab1_bbox, slab2_bbox):
    """Create a bounding box that covers the space between two slabs."""
    min_x = min(slab1_bbox.Min.X, slab2_bbox.Min.X)
    min_y = min(slab1_bbox.Min.Y, slab2_bbox.Min.Y)
    max_x = max(slab1_bbox.Max.X, slab2_bbox.Max.X)
    max_y = max(slab1_bbox.Max.Y, slab2_bbox.Max.Y)
    min_z = slab1_bbox.Max.Z  # Bottom of the first slab
    max_z = slab2_bbox.Min.Z  # Top of the second slab
    
    bbox = BoundingBoxXYZ()
    bbox.Min = XYZ(min_x, min_y, min_z)
    bbox.Max = XYZ(max_x, max_y, max_z)
    
    return bbox

from Autodesk.Revit.DB import Outline

def draw_bounding_box(bbox, color, doc):
    """Draw the bounding box as a series of lines in Revit."""
    # Create a new Transaction for drawing
    with Transaction(doc, "Draw Bounding Box") as t:
        t.Start()
        
        # Define the line creation API
        def create_line(start, end):
            return Line.CreateBound(start, end)
        
        # Define the bounding box coordinates
        lines = []
        min_pt = bbox.Min
        max_pt = bbox.Max
        
        # Create lines for each edge of the bounding box
        lines.append(create_line(XYZ(min_pt.X, min_pt.Y, min_pt.Z), XYZ(max_pt.X, min_pt.Y, min_pt.Z)))
        lines.append(create_line(XYZ(max_pt.X, min_pt.Y, min_pt.Z), XYZ(max_pt.X, max_pt.Y, min_pt.Z)))
        lines.append(create_line(XYZ(max_pt.X, max_pt.Y, min_pt.Z), XYZ(min_pt.X, max_pt.Y, min_pt.Z)))
        lines.append(create_line(XYZ(min_pt.X, min_pt.Y, min_pt.Z), XYZ(min_pt.X, min_pt.Y, max_pt.Z)))
        lines.append(create_line(XYZ(max_pt.X, min_pt.Y, min_pt.Z), XYZ(max_pt.X, min_pt.Y, max_pt.Z)))
        lines.append(create_line(XYZ(max_pt.X, max_pt.Y, min_pt.Z), XYZ(max_pt.X, max_pt.Y, max_pt.Z)))
        lines.append(create_line(XYZ(min_pt.X, max_pt.Y, min_pt.Z), XYZ(min_pt.X, max_pt.Y, max_pt.Z)))
        lines.append(create_line(XYZ(min_pt.X, min_pt.Y, max_pt.Z), XYZ(max_pt.X, min_pt.Y, max_pt.Z)))
        lines.append(create_line(XYZ(min_pt.X, min_pt.Y, max_pt.Z), XYZ(min_pt.X, max_pt.Y, max_pt.Z)))
        lines.append(create_line(XYZ(max_pt.X, min_pt.Y, max_pt.Z), XYZ(max_pt.X, max_pt.Y, max_pt.Z)))
        lines.append(create_line(XYZ(min_pt.X, max_pt.Y, max_pt.Z), XYZ(max_pt.X, max_pt.Y, max_pt.Z)))
        
        # Create the lines in the document
        for line in lines:
            doc.Create.NewModelCurve(line, doc.ActiveView.SketchPlane)
        
        t.Commit()

def print_bounding_box_details(bbox, label):
    """Print details of a bounding box and draw it."""
    print("{} - Min: ({:.2f}, {:.2f}, {:.2f}), Max: ({:.2f}, {:.2f}, {:.2f})".format(
        label,
        bbox.Min.X, bbox.Min.Y, bbox.Min.Z,
        bbox.Max.X, bbox.Max.Y, bbox.Max.Z
    ))
    draw_bounding_box(bbox, "blue", doc)

def align_walls(selected_wall_names, linked_doc):
    """Align walls based on their top constraints and slab thickness."""
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

                if wall_type and wall_type.FamilyName == 'Curtain Wall':
                    print("Warning: Wall '{}' (ID: {}) is a curtain wall. Moving the wall might have changed the divisions of the panels.".format(wall.Name, output.linkify(wall.Id)))

                if unc_height_param:
                    try:
                        unc_height_value = unc_height_param.AsDouble()
                        unc_height_mm = unc_height_value * 304.8  # Convert feet to millimeters
                        
                        if -1500 <= unc_height_mm <= 1500:
                            print("Wall Name: {} (ID: {}) has an unconnected height in the range of -1500 mm to 1500 mm. Skipping top constraint change.".format(wall.Name, output.linkify(wall.Id)))
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
                    slabs_above = get_floors_above(base_level.Elevation, linked_doc)

                    if len(slabs_above) > 0:
                        # Check the first slab
                        first_slab_thickness, first_slab_bbox = slabs_above[0]
                        slab_bottom_elevation = first_slab_bbox.Min.Z
                        slab_top_elevation = first_slab_bbox.Max.Z

                        # Get the bounding box of the wall
                        wall_bbox = wall.get_BoundingBox(None)
                        if wall_bbox:
                            # Create outline for wall and slab
                            wall_outline = Outline(wall_bbox.Min, wall_bbox.Max)
                            slab_outline = Outline(
                                XYZ(first_slab_bbox.Min.X, first_slab_bbox.Min.Y, slab_bottom_elevation),
                                XYZ(first_slab_bbox.Max.X, first_slab_bbox.Max.Y, slab_top_elevation)
                            )

                            # Print debug information for wall and slab outlines
                            print("Wall Outline:")
                            print_bounding_box_details(wall_bbox, "Wall")
                            print("Slab Outline:")
                            print_bounding_box_details(first_slab_bbox, "Slab")

                            # Check if the wall outline intersects with the slab outline
                            if wall_outline.Intersects(slab_outline, 0.00001):
                                slab_thickness = first_slab_thickness
                                print("Wall '{}' (ID: {}) intersects with the first slab. Slab thickness: {:.2f} mm.".format(wall.Name, output.linkify(wall.Id), slab_thickness))
                                wall_top_offset_param = wall.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET)
                                if wall_top_offset_param:
                                    wall_top_offset_param.Set(0)
                                    print("Wall '{}' (ID: {}) adjusted to align with the first slab (thickness: {}).".format(wall.Name, output.linkify(wall.Id), slab_thickness))
                            else:
                                print("Wall '{}' (ID: {}) does not intersect with the first slab bounding box.".format(wall.Name, output.linkify(wall.Id)))

                    for beam_bottom_elevation, beam_depth, beam in beams:
                        if beam_bottom_elevation > base_level.Elevation:
                            new_top_offset = beam_bottom_elevation - base_level.Elevation
                            if beam_depth:
                                new_top_offset = beam_depth
                            wall.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET).Set(-new_top_offset)
                            #print("Wall '{}' (ID: {}) adjusted to align with beam (ID: {}).".format(wall.Name, output.linkify(wall.Id), output.linkify(beam.Id)))
                            break

        t.Commit()



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
        forms.alert("No linked file selected or file not found.")
        script.exit()

    linked_doc = selected_link.GetLinkDocument()

    # Retrieve wall names and prompt user to select walls
    wall_names = get_wall_names()
    
    if not wall_names:
        forms.alert('No wall names found in the project.')
        return
    
    selected_wall_names = forms.SelectFromList.show(wall_names, multiselect=True, title='Select Wall Names', default=wall_names)
    
    if not selected_wall_names:
        forms.alert('No wall names selected. Exiting script.')
        return

    align_walls(selected_wall_names, linked_doc)
    
    forms.alert('Script complete!')



if __name__ == '__main__':
    main()
