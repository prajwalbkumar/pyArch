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

def get_faces(solid):
    faces = []
    all_faces = solid.Faces
    for face in all_faces:
        faces.append(face)
    return faces

def get_upper_faces(wall, wall_geometry):
    upper_faces = []
    for component in wall_geometry:
        for geometry in component:
            if (geometry.ToString() == "Autodesk.Revit.DB.Solid"):
                # print(geometry.Volume) ## This is a solid as well
                faces = get_faces(geometry)
                if faces:
                    for face in faces:
                        vector_z = int(face.FaceNormal.Z)
                        if vector_z == 1:
                            upper_faces.append(face)
    return upper_faces


def get_face_centroid(face):
    
    # Get the edges that define the face boundary
    edges = face.EdgeLoops
    points = []

    # Extract all points from the edges
    for edge_loop in edges:
        for edge in edge_loop:
            points.append(edge.AsCurve().GetEndPoint(0))
            points.append(edge.AsCurve().GetEndPoint(1))

    # Calculate the average of all points to find the centroid
    if points:
        sum_x = sum(pt.X for pt in points)
        sum_y = sum(pt.Y for pt in points)
        sum_z = sum(pt.Z for pt in points)
        count = len(points)
        centroid = XYZ(sum_x / count, sum_y / count, sum_z / count)
        return centroid

    return None


def pointgrid(face, u_divisions, v_divisions):

    u_min = face.GetBoundingBox().Min.U
    u_max = face.GetBoundingBox().Max.U
    v_min = face.GetBoundingBox().Min.V
    v_max = face.GetBoundingBox().Max.V

    # Calculate divisions size in UV space
    u_step = (u_max - u_min) / u_divisions
    v_step = (v_max - v_min) / v_divisions
    face_point_grid = []
    for i in range(1, u_divisions):
        for j in range(1,v_divisions):
            u = u_min + i * u_step
            v = v_min + j * v_step
            uv_point = UV(u, v)
            xyz_point = face.Evaluate(uv_point)  # Evaluate the 3D point on the face
            if face.IsInside(uv_point):
                face_point_grid.append(xyz_point)
    
    return face_point_grid

def align_walls(selected_wall_names, linked_doc, adjustment_type):
    levels = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
    concrete_levels = filter_concrete_levels(levels)
    sorted_concrete_levels = sorted(concrete_levels, key=lambda lvl: lvl.Elevation)
    walls_updated = 0    
    adjusted_walls = []
    beams = get_beams(linked_doc) 
    wall_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()

    target_walls = []

    for wall in wall_collector:
        if wall.Name in selected_wall_names:
            target_walls.append(wall)
        
    with Transaction(doc, "Align Wall Top Constraint and Set Offset") as t:
        t.Start()
        view_family_types = FilteredElementCollector(doc).OfClass(ViewFamilyType)
        for view_type in view_family_types:
            if view_type.ViewFamily == ViewFamily.ThreeDimensional:
                target_type = view_type
                break

        analytical_view = View3D.CreateIsometric(doc, target_type.Id)
        view_analytical = analytical_view.Duplicate(ViewDuplicateOption.Duplicate)
        view_analytical = doc.GetElement(view_analytical)
        options = Options()
        options.View = view_analytical
        options.IncludeNonVisibleObjects = True
        reset_walls = []
        for wall in target_walls:   
            # print ("Wall Name: {}; Wall ID:{}".format(wall.Name, output.linkify(wall.Id)))
            base_level_id = wall.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT).AsElementId()
            base_level = doc.GetElement(base_level_id)
            next_concrete_level = find_next_concrete_level(base_level, sorted_concrete_levels)
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
            base_offset_param = wall.LookupParameter("Base Offset").AsDouble()
            wall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).Set(ElementId.InvalidElementId)
            unc_height_param_value = (1800/304.8) - base_offset_param
            unc_height_param.Set(unc_height_param_value)
            # print ("Unconnected height set to {} for wall {}".format(unc_height_param, output.linkify(wall.Id)))
            reset_walls.append(wall)

    
        for wall in reset_walls:
            print ("Wall Name: {}; Wall ID:{}".format(wall.Name, output.linkify(wall.Id)))
            base_level_id = wall.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT).AsElementId()
            base_level = doc.GetElement(base_level_id)
            next_concrete_level = find_next_concrete_level(base_level, sorted_concrete_levels)
            unc_height_param = wall.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM)
            wall_type = doc.GetElement(wall.WallType.Id)
            

            wall_geometry = wall.get_Geometry(options)
            # print ("Wall geometry found for wall{} ID:{}; {}".format(wall.Name, output.linkify(wall.Id), wall_geometry))
            #if not wall_geometry:
                #print ("Wall geometry not found for wall{} ID:{}".format(wall.Name, output.linkify(wall.Id)))
            wall_upper_faces = get_upper_faces(wall, [wall_geometry])

            if not wall_upper_faces:
                continue  # Skip walls with no upper faces

            all_points = []
            for face in wall_upper_faces:
                u_divisions = 100
                v_divisions = 2
                point_grid = pointgrid(face, u_divisions, v_divisions)
                all_points.extend(point_grid)
            
            direction = XYZ(0, 0, 1)

            element_above = None
            for point in all_points:
                intersector = ReferenceIntersector(view_analytical)
                intersector.FindReferencesInRevitLinks = True  
                result = intersector.FindNearest(XYZ(point.X, point.Y, point.Z + 1), direction)
                if result is not None:
                    reference = result.GetReference()

                    if adjustment_type == 'Architecture':
                        linked_element = linked_doc.GetElement(reference.LinkedElementId)
                        if linked_element:
                            element_above = linked_element
                            break

                    if adjustment_type == 'Interior':
                        element = doc.GetElement(reference.ElementId)
                        if element:
                            if element.Category.Name == "Ceilings":
                                element_above = element 
                            elif element.Category.Name == "RVT Links":
                                linked_element = linked_doc.GetElement(reference.LinkedElementId)
                                if linked_element:
                                    element_above = linked_element
                            break
                        # else:
                        #     element_above = linked_doc.GetElement(reference.LinkedElementId)   

            if element_above:
                print("Found element above: {} (ID: {})".format(element_above.Name, output.linkify(element_above.Id)))
            else:
                print("No element found above wall {} (ID: {})".format(wall.Name, output.linkify(wall.Id)))    
                
            if element_above is not None:    
                if element_above.Category.Name == "Floors":
                    floor_type = linked_doc.GetElement(linked_element.GetTypeId())
                    slab_thickness = floor_type.GetCompoundStructure().GetWidth()
                    height_offset_from_level = linked_element.get_Parameter(BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM).AsDouble()
                    param = wall.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET)
                    if next_concrete_level:
                        wall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).Set(next_concrete_level.Id)                     
                    if param.IsReadOnly:
                        continue
                    param.Set(-(abs(height_offset_from_level)+slab_thickness))
                    walls_updated += 1
                    adjusted_walls.append(wall)
                    print("Nearest object for wall {} is a Floor". format (output.linkify (wall.Id)))
                    print ("Wall top offset{} is set for wall {}". format (-slab_thickness, wall.Id))

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
                                if param.IsReadOnly:
                                    continue
                                    
                                param.Set(-new_top_offset)
                                adjusted_walls.append(wall) 
                                walls_updated += 1 # Add to the list of adjusted walls
                                break   # Exit loop after adjustment

                        if not next_concrete_level:
                            continue                         
                        
                elif element_above.Category.Name == "Ceilings":
                    ceilings = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Ceilings).WhereElementIsNotElementType().ToElements()
                    if next_concrete_level:
                        wall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).Set(next_concrete_level.Id)
                    for ceiling in ceilings:
                        ceiling_bbox = ceiling.get_BoundingBox(None)
                        if ceiling_bbox is None:
                            continue
                        ceiling_top_elevation = ceiling_bbox.Max.Z
                        new_offset = next_concrete_level.Elevation - ceiling_top_elevation
                        param = wall.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET)
                        if param.IsReadOnly:
                            continue
                        param.Set(-new_offset + (150/304.8))
                        adjusted_walls.append(wall) 
                        walls_updated += 1 # Add to the list of adjusted walls
                        print("Nearest object for wall {} is a Ceiling". format (output.linkify (wall.Id)))
                        print ("Wall top offset{} is set for wall {}". format (-slab_thickness, wall.Id))
                        break

        t.Commit()
        print("Number of walls successfully updated: {}".format(walls_updated))

    return adjusted_walls


def main():
    # Step 1: Prompt the user to select between 'Architecture' or 'Interior' adjustment types
    adjustment_type = forms.SelectFromList.show(
        ["Architecture", "Interior"],
        title='Select Adjustment Type',
        button_name='Select',
        multiselect=False
    )

    if not adjustment_type:
        forms.alert("No adjustment type selected. Exiting script.")
        return

    # Step 2: Prompt user to select a linked model file
    linked_files = FilteredElementCollector(doc).OfClass(RevitLinkInstance).ToElements()
    if not linked_files:
        forms.alert("No linked files available. Exiting script.")
        return
    
    linked_file_names = [link.Name for link in linked_files]
    selected_link_name = forms.SelectFromList.show(linked_file_names, title='Select Linked Model', button_name='Select')

    if not selected_link_name:
        return

    selected_link = next((link for link in linked_files if link.Name == selected_link_name), None)

    if not selected_link:
        forms.alert("Error: Could not find the selected linked model. Exiting script.")
        return

    linked_doc = selected_link.GetLinkDocument()

    # Step 3: Prompt user to select walls for alignment
    wall_names = get_wall_names()
    if not wall_names:
        forms.alert("No walls found in the model. Exiting script.")
        return

    selected_wall_names = forms.SelectFromList.show(
        wall_names,
        multiselect=True,
        title='Select Walls to Align'
    )

    if not selected_wall_names:
        return
    if selected_wall_names:
     # Step 4: Call the align_walls function for wall alignment based on the selected walls and linked document
        adjusted_walls = align_walls(selected_wall_names, linked_doc, adjustment_type)
        if adjustment_type == 'Interior':
            with Transaction(doc, "Adjust Wall Top Offset Based on Slabs") as transaction:
                transaction.Start()

                for wall in adjusted_walls:
                    wall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).Set(ElementId.InvalidElementId)
                        
                transaction.Commit()
                #print("Successfully adjusted wall tops based on slabs.")
if __name__ == "__main__":
    main()

