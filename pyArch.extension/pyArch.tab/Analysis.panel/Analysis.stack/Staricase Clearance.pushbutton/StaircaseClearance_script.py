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
    target_floor_collection = (FilteredElementCollector(st_doc).OfCategory(BuiltInCategory.OST_Floors).WherePasses(intersect_filter).WhereElementIsNotElementType().ToElementIds()) 
    target_framing_collection = (FilteredElementCollector(st_doc).OfCategory(BuiltInCategory.OST_StructuralFraming).WherePasses(intersect_filter).WhereElementIsNotElementType().ToElementIds()) 
    
    for element_id in target_floor_collection:
        target_link_element_id.append(element_id)

    for element_id in target_framing_collection:
        target_link_element_id.append(element_id)

# Get all model elements in the active document
wall_element_ids = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElementIds()
floor_element_ids = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElementIds()
ceiling_element_ids = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Ceilings).WhereElementIsNotElementType().ToElementIds()
ramp_element_ids = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Ramps).WhereElementIsNotElementType().ToElementIds()
roof_element_ids = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Roofs).WhereElementIsNotElementType().ToElementIds()

target_host_element_id = []
for element in wall_element_ids:
    target_host_element_id.append(element_id)

for element in floor_element_ids:
    target_host_element_id.append(element_id)

for element in ceiling_element_ids:
    target_host_element_id.append(element_id)

for element in ramp_element_ids:
    target_host_element_id.append(element_id)

for element in roof_element_ids:
    target_host_element_id.append(element_id)

for element in stairs_collector:
    target_host_element_id.append(element.Id)

for stair in stairs_collector:
    # Isolate Stair - Landing & Run Geometries
    stair_run_ids = stair.GetStairsRuns()
    stair_geom = []
    for run_id in stair_run_ids:
        run = doc.GetElement(run_id)
        stair_geom.append(run.get_Geometry(Options()))

    stair_ladning_ids = stair.GetStairsLandings()
    for landing_id in stair_ladning_ids:
        landing = doc.GetElement(landing_id)
        stair_geom.append(landing.get_Geometry(Options()))
    