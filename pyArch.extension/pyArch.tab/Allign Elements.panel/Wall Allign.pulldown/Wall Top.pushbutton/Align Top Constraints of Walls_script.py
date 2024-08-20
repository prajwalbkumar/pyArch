# -*- coding: utf-8 -*-
'''Align wall top to slab/beam bottom'''

__title__ = "Wall Top"
__author__ = "prakritisrimal"

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
        try:
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
        except Exception as e:
            print("Error processing floor: {}".format(e))

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

def get_ceilings():
    """Retrieve all ceiling elements in the model."""
    ceilings = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Ceilings).WhereElementIsNotElementType().ToElements()
    return ceilings

def filter_concrete_levels(levels):
    """Filter levels to find those named with 'CL'."""
    return [level for level in levels if "CL" in level.LookupParameter("Name").AsString()]

def find_next_concrete_level(base_level, concrete_levels):
    """Find the next concrete level above the base level."""
    return next((cl for cl in concrete_levels if cl.Elevation > base_level.Elevation), None)

def adjust_wall_top_offset(wall, filtered_slabs_above):
    """Adjust the wall top offset based on slabs above."""
    wall_bbox = wall.get_BoundingBox(None)
    if wall_bbox is None:
        print("Warning: Wall '{}' (ID: {}) has no bounding box.".format(wall.Name, output.linkify(wall.Id)))
        return

    wall_outline = Outline(wall_bbox.Min, wall_bbox.Max)
    adjusted = False  # Track if any adjustments were made

    for slab in filtered_slabs_above:
        slab_thickness, slab_height_offset, slab_bbox, slab_id = slab
        slab_bottom_elevation = slab_bbox.Min.Z
        slab_top_elevation = slab_bbox.Max.Z

        slab_outline = Outline(slab_bbox.Min, slab_bbox.Max)
        if wall_outline.Intersects(slab_outline, 1e-3):
            if wall_bbox.Min.Z < slab_bbox.Max.Z and wall_bbox.Max.Z > slab_bbox.Min.Z:
                wall_top_offset_param = slab_thickness + abs(slab_height_offset)
                param = wall.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET)
                current_offset = param.AsDouble()
                new_offset = -wall_top_offset_param if current_offset == 0 else min(current_offset, -wall_top_offset_param)
                param.Set(new_offset)
                adjusted = True
                #print("Wall '{}' (ID: {}) adjusted to align with the intersecting slab (ID: {}) (thickness: {}).".format(
                    #wall.Name, output.linkify(wall.Id), output.linkify(slab_id), slab_thickness))

    if not adjusted:
        #print("No adjustments made for wall '{}' (ID: {})".format(wall.Name, output.linkify(wall.Id)))

def adjust_wall_to_ceiling(wall, ceilings, next_concrete_level):
    """Adjust the wall top to align with the ceiling."""
    wall_bbox = wall.get_BoundingBox(None)
    if wall_bbox is None:
        print("Warning: Wall '{}' (ID: {}) has no bounding box.".format(wall.Name, output.linkify(wall.Id)))
        return

    wall_outline = Outline(wall_bbox.Min, wall_bbox.Max)
    ceiling_found = False

    for ceiling in ceilings:
        ceiling_bbox = ceiling.get_BoundingBox(None)
        if ceiling_bbox is None:
            continue

        ceiling_outline = Outline(ceiling_bbox.Min, ceiling_bbox.Max)
        if wall_outline.Intersects(ceiling_outline, 1e-3):
            ceiling_top_elevation = ceiling_bbox.Max.Z
            new_offset = next_concrete_level.Elevation - ceiling_top_elevation
            param = wall.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET)
            param.Set(-new_offset + 0.49212598)
            ceiling_found = True
            #print("Wall '{}' (ID: {}) adjusted to align with ceiling (ID: {}).".format(
                #wall.Name, output.linkify(wall.Id), output.linkify(ceiling.Id)))
            break

    if not ceiling_found:
        #print("No ceiling found for wall '{}' (ID: {}). Using existing alignment logic.".format(
            #wall.Name, output.linkify(wall.Id)))
        # No ceiling found, use existing alignment logic
        slabs_above = get_floors_above(wall_bbox.Min.Z, doc)
        adjust_wall_top_offset(wall, slabs_above)

def check_unconnected_height(wall):
    """Check the unconnected height of a wall and generate a warning if greater than 10,000 mm."""
    unc_height_param = wall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM)
    if unc_height_param:
        unc_height_value = unc_height_param.AsDouble()
        unc_height_mm = unc_height_value * 304.8  # Convert feet to millimeters
        if unc_height_mm > 10000:
            print("Warning: Wall '{}' (ID: {}) has an unconnected height greater than 10,000 mm.".format(
                wall.Name, output.linkify(wall.Id)))

def align_walls(selected_wall_names, linked_doc, adjustment_type):
    """Align walls to the slab or ceiling based on the selected adjustment type."""
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
                        param = wall.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET)   
                        param.Set(-slab_thickness)
                        adjusted_walls.append(wall)   # Add to the list of adjusted walls

                # Adjust wall top based on beams
                for beam_bottom_elevation, beam_depth, beam in beams:
                    if beam_bottom_elevation > base_level.Elevation:
                        new_top_offset = beam_bottom_elevation - base_level.Elevation
                        if beam_depth:
                            new_top_offset = beam_depth
                        current_offset = wall.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET).AsDouble()
                        
                        if not slab_thickness or abs(current_offset + slab_thickness) < 1e-3:
                            # Adjust wall to beam bottom
                            param = wall.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET)
                            param.Set(-new_top_offset)
                            adjusted_walls.append(wall)  # Add to the list of adjusted walls
                            break   # Exit loop after adjustment

                if not next_concrete_level:
                    continue

                if adjustment_type == "Interior":
                    ceilings = get_ceilings()
                    if ceilings:
                        adjust_wall_to_ceiling(wall, ceilings, next_concrete_level)
                        adjusted_walls.append(wall)

                # Check the unconnected height and issue a warning if necessary
                check_unconnected_height(wall)
        t.Commit()
    return adjusted_walls

def main():
    # Prompt user to select between 'Architecture' or 'Interior' adjustments
    adjustment_type = forms.SelectFromList.show(
        ["Architecture", "Interior"],
        title='Select Adjustment Type',
        button_name='Select',
        multiselect=False
    )

    if not adjustment_type:
        forms.alert("No adjustment type selected.")
        return

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
        adjusted_walls = align_walls(selected_wall_names, linked_doc, adjustment_type)
        
        # Call adjust_wall_top_offset for further adjustments based on slabs
        if adjusted_walls:
            try:
                # Start a transaction to adjust wall top offsets based on slabs
                transaction = Transaction(doc, "Adjust Wall Top Offset Based on Slabs")
                transaction.Start()

                for wall in adjusted_walls:
                    slabs_above = get_floors_above(doc.GetElement(wall.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT).AsElementId()).Elevation, linked_doc)
                    adjust_wall_top_offset(wall, slabs_above)

                    # If 'Interior' is selected, reset the wall's top constraint to 'Unconnected'
                    if adjustment_type == 'Interior':
                        wall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).Set(ElementId.InvalidElementId)
                    
                # Commit the transaction
                transaction.Commit()
            except Exception as e:
                print("Error in slab adjustment transaction: {}".format(e))
                transaction.RollBack()
    else:
        forms.alert("No walls selected for alignment.")

if __name__ == "__main__":
    main()

