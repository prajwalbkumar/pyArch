# -*- coding: utf-8 -*-
'''Dimension Grid'''
__title__ = "Dimension Grid"
__author__ = "prajwalbkumar"


# Imports
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import UIDocument
from pyrevit import revit, forms, script
import os

script_dir = os.path.dirname(__file__)
ui_doc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # Get the Active Document
app = __revit__.Application # Returns the Revit Application Object
rvt_year = int(app.VersionNumber)
output = script.get_output()
view = doc.ActiveView


# MAIN
grids_collector = FilteredElementCollector(doc, view.Id).OfCategory(BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()
scope_boxes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_VolumeOfInterest).ToElements()

scope_box_names = []
for box in scope_boxes:
    scope_box_names.append(box.Name)

selected_scope_box = forms.SelectFromList.show(scope_box_names,multiselect=False, width=300, height=300,title='Select View ScopeBox')  # Optionally, set a default selection

if not selected_scope_box:
    script.exit()

else:
    for box in scope_boxes:
        if box.Name == selected_scope_box:
            scope_box = box
            break

bbox = scope_box.get_BoundingBox(view)

corner1 = XYZ(bbox.Min.X, bbox.Min.Y, bbox.Min.Z)
corner2 = XYZ(bbox.Max.X, bbox.Min.Y, bbox.Min.Z)
corner3 = XYZ(bbox.Max.X, bbox.Max.Y, bbox.Min.Z)
corner4 = XYZ(bbox.Min.X, bbox.Max.Y, bbox.Min.Z)

# Create lines representing the bounding box edges
line1 = Line.CreateBound(corner1, corner2)
line2 = Line.CreateBound(corner2, corner3)
line3 = Line.CreateBound(corner3, corner4)
line4 = Line.CreateBound(corner4, corner1)

# Create model curves in the active view
bbox_curves = [line1, line2, line3, line4]

t = Transaction(doc, "Allign Grids")
t.Start()

all_directions = []
for grid in grids_collector:
    curves = grid.GetCurvesInView(DatumExtentType.ViewSpecific, view)
    for curve in curves:
        grids_view_curve = curve

    all_directions.append(grids_view_curve.


# Convert all Grids to ViewSpecific Grids
for grid in grids_collector:
    grid.SetDatumExtentType(DatumEnds.End0, view, DatumExtentType.ViewSpecific)
    grid.SetDatumExtentType(DatumEnds.End1, view, DatumExtentType.ViewSpecific)

    # Get the curves of the grids
    curves = grid.GetCurvesInView(DatumExtentType.ViewSpecific, view)
    for curve in curves:
        grids_view_curve = curve
        # point = curve.GetEndPoint(0)
        # plane = Plane.CreateByNormalAndOrigin(XYZ.BasisZ, point)
        # sketch_plane = SketchPlane.Create(doc, plane)
        # model_line = doc.Create.NewModelCurve(Line.CreateBound(point, curve.GetEndPoint(1)), sketch_plane)
    
    start_point = grids_view_curve.GetEndPoint(0)
    end_point = grids_view_curve.GetEndPoint(1)
    direction = (end_point - start_point).Normalize()

    def new_point(exisiting_point, direction, bbox_curves, start_point = None):

        projected_points = []
        for curve in bbox_curves:
            project = curve.Project(exisiting_point).XYZPoint
            projected_points.append(XYZ(project.X, project.Y, 0))

    
        possible_points = []

        exisiting_point = XYZ(exisiting_point.X, exisiting_point.Y, 0)

        for point in projected_points:
            if (exisiting_point - point).Normalize().IsAlmostEqualTo(direction) or (exisiting_point - point).Normalize().IsAlmostEqualTo(direction.Negate()):
                possible_points.append(point)

        if start_point:
            if start_point.IsAlmostEqualTo(possible_points[0]):
                    new_point = possible_points[1]
            else:
                new_point = possible_points[0]

        else:
            if point.DistanceTo(possible_points[0]) > point.DistanceTo(possible_points[1]):
                new_point = possible_points[0]
                
            else:
                new_point = possible_points[1]
    
        return new_point
    
    
    new_start_point = new_point(start_point, direction, bbox_curves)
    new_end_point = new_point(end_point, direction, bbox_curves, new_start_point)

    new_start_point = XYZ(new_start_point.X, new_start_point.Y, start_point.Z)
    new_end_point = XYZ(new_end_point.X, new_end_point.Y, end_point.Z)
    new_grid_line = Line.CreateBound(new_start_point, new_end_point)

    grid.SetCurveInView(DatumExtentType.ViewSpecific, view, new_grid_line)

    # plane = Plane.CreateByNormalAndOrigin(XYZ.BasisZ, new_start_point)
    # sketch_plane = SketchPlane.Create(doc, plane)
    # model_line = doc.Create.NewModelCurve(new_grid_line, sketch_plane)
    
t.Commit()