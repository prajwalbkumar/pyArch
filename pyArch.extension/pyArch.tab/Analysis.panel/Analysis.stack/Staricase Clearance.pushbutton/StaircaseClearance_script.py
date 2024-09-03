# -*- coding: utf-8 -*-
'''Staircase Clearance'''
__title__ = "Staircase Clearance"
__author__ = "prajwalbkumar"

# Imports
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Architecture import *
from Autodesk.Revit.UI import UIDocument
from pyrevit import revit, forms, script
import os

script_dir = os.path.dirname(__file__)
ui_doc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # Get the Active Document
app = __revit__.Application # Returns the Revit Application Object
output = script.get_output()


def get_inflated_bbox(element, clearance):
    bbox = element.get_BoundingBox(None)
    # print("Minimum: {}" .format(bbox.Min))
    # print("Maximum: {}" .format(bbox.Max))
    bbox.Max = XYZ(bbox.Max.X, bbox.Max.Y, (bbox.Max.Z + (clearance * 0.003)))
    # print("New Maximum: {}" .format(bbox.Max))
    return bbox

def get_faces(solid):
    faces = []
    all_faces = solid.Faces
    for face in all_faces:
        faces.append(face)
    return faces

def get_upper_faces(stair, stair_geometry):
    upper_faces = []
    if (stair.LookupParameter("Family").AsValueString() == "Assembled Stair"):
        for components in stair_geometry:
            for geometry in components:
                if (geometry.ToString() == "Autodesk.Revit.DB.GeometryInstance"):
                    geometry_instance = geometry.GetInstanceGeometry()
                    for solid in geometry_instance:
                        faces = get_faces(solid)
                        if faces:
                            for face in faces:
                                vector_z = int(face.FaceNormal.Z)
                                if vector_z == 1:
                                    upper_faces.append(face)
        return upper_faces

    else:
        for component in stair_geometry:
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

    # Calculate step size in UV space
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



view = doc.ActiveView
type = str(type(view))

if not type == "<type 'View3D'>":
    forms.alert("Active View must be a 3D View \n\n"
                        "Make sure that the 3D View contains all Model Elements", title = "Script Exiting", warn_icon = True)

    script.exit()

# Relevant Codes
code = ["NFPA", "IBC", "SBC", "DCD"]

# Prompt to choose a Code
user_code = forms.SelectFromList.show(code, title="Select Relevent Code", width=300, height=300, button_name="Select Code", multiselect=False)

if user_code == code[0]:
    clearance = 2030

elif user_code == code[1]:
    clearance = 2032

elif user_code == code[2]:
    clearance = 2100

elif user_code == code[3]:
    clearance = 2030

else:
    script.exit()

# # Collect all linked instances
# linked_instance = FilteredElementCollector(doc).OfClass(RevitLinkInstance).ToElements()

# link_name = []
# for link in linked_instance:
#     link_name.append(link.Name)

# st_instance_name = forms.SelectFromList.show(link_name, title = "Select ST File", width=600, height=600, button_name="Select File", multiselect=False)

# if not st_instance_name:
#     script.exit()

# for link in linked_instance:
#     if st_instance_name == link.Name:
#         st_instance = link
#         break

# # Get the transformation matrix of the link
# transform = st_instance.GetTransform()



# # Get all target elements from the ST Link. 
# st_doc = st_instance.GetLinkDocument()
# target_link_element_id = []
# for stair in stairs_collector:
#     bbox = get_inflated_bbox(stair, clearance)

#     bbox.Min = transform.Inverse.OfPoint(bbox.Min)
#     bbox.Max = transform.Inverse.OfPoint(bbox.Max)

#     outline = Outline(bbox.Min, bbox.Max)

#     intersect_filter = BoundingBoxIntersectsFilter(outline)
#     target_floor_collection = (FilteredElementCollector(st_doc).OfCategory(BuiltInCategory.OST_Floors).WherePasses(intersect_filter).WhereElementIsNotElementType().ToElements()) 
#     target_framing_collection = (FilteredElementCollector(st_doc).OfCategory(BuiltInCategory.OST_StructuralFraming).WherePasses(intersect_filter).WhereElementIsNotElementType().ToElements()) 
    
#     for element in target_floor_collection:
#         target_link_element_id.append(element.Id)

#     for element in target_framing_collection:
#         target_link_element_id.append(element.Id)

# # Get all model elements in the active document
# wall_element_ids = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElementIds()
# floor_element_ids = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElementIds()
# ceiling_element_ids = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Ceilings).WhereElementIsNotElementType().ToElementIds()
# ramp_element_ids = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Ramps).WhereElementIsNotElementType().ToElementIds()
# roof_element_ids = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Roofs).WhereElementIsNotElementType().ToElementIds()

# target_host_element_id = []
# for element_id in wall_element_ids:
#     target_host_element_id.append(element_id)

# for element_id in floor_element_ids:
#     target_host_element_id.append(element_id)

# for element_id in ceiling_element_ids:
#     target_host_element_id.append(element_id)

# for element_id in ramp_element_ids:
#     target_host_element_id.append(element_id)

# for element_id in roof_element_ids:
#     target_host_element_id.append(element_id)

# for element_id in stairs_collector:
#     target_host_element_id.append(element_id)



# Get all the Stairs in the Document. And Inflate their bounding boxes a over the top.
stairs_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Stairs).WhereElementIsNotElementType().ToElements()
if not stairs_collector:
    forms.alert("No staircase found in the active document \n\n"
                            "Run the tool after creating a staircase", title = "Script Exiting", warn_icon = True)
    script.exit()

options = Options()
options.View = doc.ActiveView
options.IncludeNonVisibleObjects = True

t = Transaction(doc, "Test")
t.Start()

failed_data = []
for stair in stairs_collector:
    failed_counter = 0
    stair_tread_count = 0
    stair_geometry = []
    run_faces = []
    stair_run_ids = stair.GetStairsRuns()

    # Calculate Upper Faces for Run
    run_index_upper_faces = []
    for run_id in stair_run_ids:
        run = doc.GetElement(run_id)
        stair_tread_count += run.LookupParameter("Actual Number of Treads").AsInteger()
        stair_geometry.append(run.get_Geometry(options))
        run_index_upper_faces.append(get_upper_faces(stair, stair_geometry))

# TODO: Research why the code block above gives duplicate top faces when returning the faces for the second run

    all_faces = []
    for run in run_index_upper_faces:
        for face in run:
            all_faces.append(face)

    all_centroids_z = []
    for face in all_faces:
        all_centroids_z.append(int(get_face_centroid(face).Z * 304.8))

    # Remove Duplicate Faces
    run_upper_faces = []
    seen = set()  # This will contain only unique occurrences

    for i, ele in enumerate(all_centroids_z):
        if ele not in seen:  # This checks if the item is not already in the seen list
            run_upper_faces.append(i)
        seen.add(ele)  # Ensure the element is added after processing
    
    run_unique_upper_faces = []
    for index in run_upper_faces:
        run_unique_upper_faces.append(all_faces[index])
        
    face_areas = []
    for face in run_unique_upper_faces:
        face_areas.append(face.Area)

    # Create a list of (index, area) pairs
    indexed_areas = []
    for index, area in enumerate(face_areas):
        indexed_areas.append((index, area))

    # Sort the list based on the area values
    sorted_indexed_areas = sorted(indexed_areas, key=lambda x: x[1])

    # Extract the sorted indices
    sorted_indices = []
    for item in sorted_indexed_areas:
        sorted_indices.append(item[0])

    # The sorted_indices list now contains the indices in the order of the sorted areas
    sorted_faces = []
    for index in sorted_indices:
        sorted_faces.append(run_unique_upper_faces[index])

    sorted_faces.reverse()
    for index in range(stair_tread_count):
        run_faces.append(sorted_faces[index])

    # Extract Landing Faces
    stair_geometry = []
    stair_landing_ids = stair.GetStairsLandings()
    landing_faces = []
    for landing_id in stair_landing_ids:
        landing = doc.GetElement(landing_id)
        stair_geometry.append(landing.get_Geometry(options))
        landing_faces = get_upper_faces(stair, stair_geometry)

            
    all_points = []
    if run_faces:
        for face in run_faces:
            # Define grid resolution
            u_divisions = 6
            v_divisions = 10
            point_grid = pointgrid(face, u_divisions, v_divisions)
            for point in point_grid:
                all_points.append(point)


    if landing_faces:
        for face in landing_faces:
            # Define grid resolution
            u_divisions = 20
            v_divisions = 20
            point_grid = pointgrid(face, u_divisions, v_divisions)
            for point in point_grid:
                all_points.append(point)
   
    direction = XYZ(0,0,1)
    for point in all_points:
        intersector = ReferenceIntersector(view)
        intersector.FindReferencesInRevitLinks = True
        
        result = intersector.FindNearest(XYZ(point.X, point.Y, (point.Z + 1)), direction)
        if not result: 
            continue
        proximity = (result.Proximity + 1 ) * 304
        if proximity < clearance:
            failed_counter += 1
            # Visualize Rays
            plane = Plane.CreateByNormalAndOrigin(XYZ.BasisX, point)
            sketch_plane = SketchPlane.Create(doc, plane)
            model_line = doc.Create.NewModelCurve(Line.CreateBound(point, XYZ(point.X,point.Y,(point.Z + (result.Proximity + 1 )))), sketch_plane)
    

    # TODO : FIRE UP THE VISUALIZATION SEQUENCE

    if failed_counter:
        failed_stair_data = [
            output.linkify(stair.Id),
            stair.LookupParameter("Base Level").AsValueString(),
            stair.LookupParameter("Top Level").AsValueString(),
            stair.LookupParameter("Actual Riser Height").AsValueString(),
            stair.LookupParameter("Actual Number of Risers").AsValueString(),
            "OVERHEAD NOT CLEAR"
        ]
        failed_data.append(failed_stair_data)


if failed_data:
    output.print_md("##⚠️ {} Completed. Issues Found ☹️".format(__title__))
    output.print_md("---")
    output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")
    output.print_table(table_data=failed_data, columns=["ELEMENT ID", "BASE LEVEL", "TOP LEVEL", "RISER HEIGHT", "NO OF RISERS", "ERROR CODE"])
    output.print_md("---")
    output.print_md("***✅ ERROR CODE REFERENCE***")
    output.print_md("---")
    output.print_md("**OVERHEAD NOT CLEAR** - The clearance does not meet the minimum requriement of {}mm\n" .format(clearance))
    output.print_md("---")
else:
    output.print_md("##✅ {} Completed. No Issues Found 😃".format(__title__))
    output.print_md("---")

t.Commit()