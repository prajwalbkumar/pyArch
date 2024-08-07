# -*- coding: utf-8 -*-
'''URS Checker'''
__title__ = "URS Checker"
__author__ = "prakritisrimal"

import clr
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from pyrevit import forms
from pyrevit import script

clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

def open_revit_document(file_path):
    """Open a Revit document from the given file path."""
    app = __revit__.Application
    return app.OpenDocumentFile(file_path)

def feet_to_meters(feet, inches):
    """Convert feet and inches to meters."""
    return (feet * 0.3048) + (inches * 0.0254)

def get_levels(doc):
    """Retrieve levels from the Revit document."""
    levels = {}
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
    for level in collector:
        name = level.Name
        elevation = level.Elevation
        # Convert feet to meters
        elevation_meters = feet_to_meters(elevation // 1, (elevation % 1) * 12)
        levels[name] = elevation_meters
    return levels

def get_grids(doc):
    """Retrieve grid lines from the Revit document."""
    grids = []
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()
    for grid in collector:
        name = grid.Name
        curve = grid.Curve
        if curve:
            # Determine grid orientation
            if isinstance(curve, Line):
                direction = curve.Direction
                orientation = "Vertical" if abs(direction.X) < 1e-6 else "Horizontal"
                midpoint = (curve.GetEndPoint(0) + curve.GetEndPoint(1)) / 2
                grids.append({
                    'name': name,
                    'midpoint': midpoint,
                    'orientation': orientation
                })
    return grids

def get_project_base_point(doc):
    """Retrieve project base point from the Revit document."""
    base_points = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_ProjectBasePoint).WhereElementIsNotElementType().ToElements()
    if base_points:
        return base_points[0]
    return None

def compare_base_points(bp_urs, bp_main):
    """Compare the location of two project base points."""
    if not bp_urs or not bp_main:
        return [["Project Base Point", "", "", "Project Base Point information missing in one or both files."]]
    
    loc_urs = bp_urs.Location
    loc_main = bp_main.Location
    
    if loc_urs is None or loc_main is None:
        return [["Project Base Point", "", "", "Project Base Point location missing in one or both base points."]]
    
    if isinstance(loc_urs, LocationPoint) and isinstance(loc_main, LocationPoint):
        point_urs = loc_urs.Point
        point_main = loc_main.Point
        
        easting_urs = point_urs.X
        northing_urs = point_urs.Y
        elevation_urs = point_urs.Z
        
        easting_main = point_main.X
        northing_main = point_main.Y
        elevation_main = point_main.Z
        
        easting_match = "Match" if abs(easting_urs - easting_main) < 1e-8 else "Mismatch"
        northing_match = "Match" if abs(northing_urs - northing_main) < 1e-8 else "Mismatch"
        elevation_match = "Match" if abs(elevation_urs - elevation_main) < 1e-8 else "Mismatch"
        
        return [
            ["Project Base Point", "Easting", "{:.3f}".format(easting_urs), "{:.3f}".format(easting_main), easting_match],
            ["", "Northing", "{:.3f}".format(northing_urs), "{:.3f}".format(northing_main), northing_match],
            ["", "Elevation", "{:.3f}".format(elevation_urs), "{:.3f}".format(elevation_main), elevation_match]
        ]
    else:
        # Print the values even if there's a type mismatch
        if isinstance(loc_urs, LocationPoint):
            point_urs = loc_urs.Point
            easting_urs = point_urs.X
            northing_urs = point_urs.Y
            elevation_urs = point_urs.Z
        else:
            easting_urs = northing_urs = elevation_urs = "N/A"
        
        if isinstance(loc_main, LocationPoint):
            point_main = loc_main.Point
            easting_main = point_main.X
            northing_main = point_main.Y
            elevation_main = point_main.Z
        else:
            easting_main = northing_main = elevation_main = "N/A"
        
        return [
            ["Project Base Point", "Easting", "{}".format(easting_urs), "{}".format(easting_main), "Mismatch"],
            ["", "Northing", "{}".format(northing_urs), "{}".format(northing_main), "Mismatch"],
            ["", "Elevation", "{}".format(elevation_urs), "{}".format(elevation_main), "Mismatch"]
        ]

def compare_files(doc_urs, doc_main):
    """Compare levels, grids, and project base points between two Revit documents."""
    levels_urs = get_levels(doc_urs)
    levels_main = get_levels(doc_main)
    
    grids_urs = get_grids(doc_urs)
    grids_main = get_grids(doc_main)
    
    p_bp_urs = get_project_base_point(doc_urs)
    p_bp_main = get_project_base_point(doc_main)
    
    report_data = []

    # Check levels by name first
    level_names_urs = sorted(levels_urs.keys())
    level_names_main = sorted(levels_main.keys())
    
    missing_in_urs = set(level_names_main) - set(level_names_urs)
    missing_in_main = set(level_names_urs) - set(level_names_main)
    
    if missing_in_urs or missing_in_main:
        if missing_in_urs:
            for level in missing_in_urs:
                report_data.append(["Level", level, "Not in URS", "N/A", "Error: Missing"])
        if missing_in_main:
            for level in missing_in_main:
                report_data.append(["Level", level, "N/A", "Not in Main", "Error: Missing"])
    
    level_comparison = {level: (levels_urs.get(level), levels_main.get(level)) for level in level_names_urs}
    
    for level, (elevation_urs, elevation_main) in level_comparison.items():
        try:
            elevation_urs = float(elevation_urs)
            elevation_main = float(elevation_main)
            elevation_match = "Match" if abs(elevation_urs - elevation_main) < 1e-10 else "Mismatch"
            report_data.append(["Level", level, "{:.2f}".format(elevation_urs), "{:.2f}".format(elevation_main), elevation_match])
        except ValueError:
            report_data.append(["Level", level, "Invalid", "Invalid", "Error in Data"])

    # Check grids by name first
    grid_names_urs = sorted([grid['name'] for grid in grids_urs])
    grid_names_main = sorted([grid['name'] for grid in grids_main])
    
    missing_in_urs = set(grid_names_main) - set(grid_names_urs)
    missing_in_main = set(grid_names_urs) - set(grid_names_main)
    
    if missing_in_urs or missing_in_main:
        if missing_in_urs:
            for grid in missing_in_urs:
                report_data.append(["Grid", grid, "Not in URS", "N/A", "Error: Missing"])
        if missing_in_main:
            for grid in missing_in_main:
                report_data.append(["Grid", grid, "N/A", "Not in Main", "Error: Missing"])
    
    # Create a map of grid names to their midpoints and orientations
    grid_map_urs = {grid['name']: (grid['midpoint'], grid['orientation']) for grid in grids_urs}
    grid_map_main = {grid['name']: (grid['midpoint'], grid['orientation']) for grid in grids_main}
    
    for grid_name in grid_map_urs:
        if grid_name in grid_map_main:
            midpoint_urs, orientation_urs = grid_map_urs[grid_name]
            midpoint_main, orientation_main = grid_map_main[grid_name]
            
            if orientation_urs == orientation_main:
                if orientation_urs == "Vertical":
                    # Compare only X values for vertical grids
                    start_match = "Match" if abs(midpoint_urs.X - midpoint_main.X) < 1e-10 else "Mismatch"
                    report_data.append([
                        "Grid",
                        "{} (Midpoint)".format(grid_name),
                        "{:.10f}".format(midpoint_urs.X),
                        "{:.10f}".format(midpoint_main.X),
                        start_match
                    ])
                elif orientation_urs == "Horizontal":
                    # Compare only Y values for horizontal grids
                    start_match = "Match" if abs(midpoint_urs.Y - midpoint_main.Y) < 1e-10 else "Mismatch"
                    report_data.append([
                        "Grid",
                        "{} (Midpoint)".format(grid_name),
                        "{:.10f}".format(midpoint_urs.Y),
                        "{:.10f}".format(midpoint_main.Y),
                        start_match
                    ])
            else:
                # Orientation mismatch
                report_data.append([
                    "Grid",
                    grid_name,
                    "Mismatch in orientation",
                    "Mismatch in orientation",
                    "Error: Orientation mismatch"
                ])
        else:
            # Grid missing in main
            report_data.append([
                "Grid",
                grid_name,
                "Not in URS",
                "N/A",
                "Error: Missing"
            ])
    
    # Compare project base points
    report_data.extend(compare_base_points(p_bp_urs, p_bp_main))
    
    return report_data

def main():
    """Main function to run the comparison."""
    # Get the output object
    output = script.get_output()

    # Prompt user to select the URS and Main files
    forms.alert("Please select the URS Revit file for comparison.", title="File Selection")
    
    urs_file = forms.pick_file(file_ext='rvt', title="Select the URS file")
    if not urs_file:
        forms.alert("No URS file selected. Exiting.", exit_code=1)
    
    forms.alert("Please select the Main Revit file for comparison with the URS file.", title="File Selection")
    main_file = forms.pick_file(file_ext='rvt', title="Select the Main file")
    if not main_file:
        forms.alert("No Main file selected. Exiting.", exit_code=1)
    
    doc_urs = open_revit_document(urs_file)
    doc_main = open_revit_document(main_file)
    
    # Perform comparison
    report_data = compare_files(doc_urs, doc_main)
    
    # Metadata for the report
    report_metadata = {
        'Title': 'URS Comparison Report',
        'URS File': urs_file,
        'Main File': main_file,

    }
    
    # Print results
    output.print_md('# {}'.format(report_metadata['Title']))
    output.print_md('**URS File:** {}'.format(report_metadata['URS File']))
    output.print_md('**Main File:** {}'.format(report_metadata['Main File']))
    output.print_table(report_data, ["Type", "Name", "URS File Value", "Main File Value", "Match Status"])

if __name__ == "__main__":
    main()