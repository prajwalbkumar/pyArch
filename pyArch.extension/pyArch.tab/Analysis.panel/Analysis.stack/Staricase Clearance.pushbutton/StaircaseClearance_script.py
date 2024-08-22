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
rvt_year = int(app.VersionNumber)
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
    

# Relevant Codes
code = ["NFPA", "FRENCH", "IBC", "BS-EN", "SBC", "NBC", "DCD"]

# Prompt to choose a Code
user_code = forms.SelectFromList.show(code, title="Select Relevent Code", width=300, height=300, button_name="Select Code", multiselect=False)

if user_code == code[0]:
    clearance = 2800

elif user_code == code[1]:
    clearance = 2800

elif user_code == code[2]:
    clearance = 2800

elif user_code == code[3]:
    clearance = 2800

elif user_code == code[4]:
    clearance = 2800

elif user_code == code[5]:
    clearance = 2800

elif user_code == code[6]:
    clearance = 2800

else:
    script.exit()

# Collect all linked instances
linked_instance = FilteredElementCollector(doc).OfClass(RevitLinkInstance).ToElements()

link_name = []
for link in linked_instance:
    link_name.append(link.Name)

st_instance_name = forms.SelectFromList.show(link_name, title = "Select URS File", width=600, height=600, button_name="Select File", multiselect=False)

if not st_instance_name:
    script.exit()

for link in linked_instance:
    if st_instance_name == link.Name:
        st_instance = link
        break

# Get the transformation matrix of the link
transform = st_instance.GetTransform()

# Get all the Stairs in the Document. And Inflate their bounding boxes a over the top.
stairs_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Stairs).WhereElementIsNotElementType().ToElements()

# Get all target elements from the ST Link. 
st_doc = st_instance.GetLinkDocument()
target_link_element_id = []
for stair in stairs_collector:
    bbox = get_inflated_bbox(stair, clearance)

    bbox.Min = transform.Inverse.OfPoint(bbox.Min)
    bbox.Max = transform.Inverse.OfPoint(bbox.Max)

    outline = Outline(bbox.Min, bbox.Max)

    intersect_filter = BoundingBoxIntersectsFilter(outline)
    target_floor_collection = (FilteredElementCollector(st_doc).OfCategory(BuiltInCategory.OST_Floors).WherePasses(intersect_filter).WhereElementIsNotElementType().ToElements()) 
    target_framing_collection = (FilteredElementCollector(st_doc).OfCategory(BuiltInCategory.OST_StructuralFraming).WherePasses(intersect_filter).WhereElementIsNotElementType().ToElements()) 
    
    for element in target_floor_collection:
        target_link_element_id.append(element.Id)

    for element in target_framing_collection:
        target_link_element_id.append(element.Id)

# Get all model elements in the active document
wall_element_ids = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElementIds()
floor_element_ids = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElementIds()
ceiling_element_ids = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Ceilings).WhereElementIsNotElementType().ToElementIds()
ramp_element_ids = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Ramps).WhereElementIsNotElementType().ToElementIds()
roof_element_ids = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Roofs).WhereElementIsNotElementType().ToElementIds()

target_host_element_id = []
for element_id in wall_element_ids:
    target_host_element_id.append(element_id)

for element_id in floor_element_ids:
    target_host_element_id.append(element_id)

for element_id in ceiling_element_ids:
    target_host_element_id.append(element_id)

for element_id in ramp_element_ids:
    target_host_element_id.append(element_id)

for element_id in roof_element_ids:
    target_host_element_id.append(element_id)

for element_id in stairs_collector:
    target_host_element_id.append(element_id)

options = Options()
options.View = doc.ActiveView
options.IncludeNonVisibleObjects = True

for stair in stairs_collector:

    # Calculate Run Faces
    all_upper_faces = []

    # Isolate Stair - Landing & Run Geometries
    stair_run_ids = stair.GetStairsRuns()
    stair_geometry = []

    # Calculate Upper Faces for Run
    treads = 0
    for run_id in stair_run_ids:
        run = doc.GetElement(run_id)
        stair_geometry.append(run.get_Geometry(options))
        treads += run.LookupParameter("Actual Number of Treads").AsInteger()

        run_upper_faces = get_upper_faces(stair, stair_geometry)
        face_areas = []
        for face in run_upper_faces:
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
            sorted_faces.append(run_upper_faces[index])

        sorted_faces.reverse()
        run_faces = []
        for index in range(run.LookupParameter("Actual Number of Treads").AsInteger()):
            run_faces.append(sorted_faces[index])        


    stair_ladning_ids = stair.GetStairsLandings()
    for landing_id in stair_ladning_ids:
        landing = doc.GetElement(landing_id)
        stair_geometry.append(landing.get_Geometry(options))
        landing_faces = get_upper_faces(stair, stair_geometry)

    test_faces = run_faces + landing_faces  
    
    
