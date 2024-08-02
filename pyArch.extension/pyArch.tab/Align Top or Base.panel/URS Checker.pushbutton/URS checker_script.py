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
                grids.append({
                    'name': name,
                    'curve': curve,
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
        
        easting_match = "Match" if abs(easting_urs - easting_main) < 1e-6 else "Mismatch"
        northing_match = "Match" if abs(northing_urs - northing_main) < 1e-6 else "Mismatch"
        elevation_match = "Match" if abs(elevation_urs - elevation_main) < 1e-6 else "Mismatch"
        
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
    level_names_urs = set(levels_urs.keys())
    level_names_main = set(levels_main.keys())
    
    missing_in_urs = level_names_main - level_names_urs
    missing_in_main = level_names_urs - level_names_main
    
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
            elevation_match = "Match" if abs(elevation_urs - elevation_main) < 1e-6 else "Mismatch"
            report_data.append(["Level", level, "{:.2f}".format(elevation_urs), "{:.2f}".format(elevation_main), elevation_match])
        except ValueError:
            report_data.append(["Level", level, "Invalid", "Invalid", "Error in Data"])

    # Check grids by name first
    grid_names_urs = [grid['name'] for grid in grids_urs]
    grid_names_main = [grid['name'] for grid in grids_main]
    
    missing_in_urs = set(grid_names_main) - set(grid_names_urs)
    missing_in_main = set(grid_names_urs) - set(grid_names_main)
    
    if missing_in_urs or missing_in_main:
        if missing_in_urs:
            for grid in missing_in_urs:
                report_data.append(["Grid", grid, "Not in URS", "N/A", "Error: Missing"])
        if missing_in_main:
            for grid in missing_in_main:
                report_data.append(["Grid", grid, "N/A", "Not in Main", "Error: Missing"])
    
    grid_comparison = {name: (grids_urs[i]['curve'], grids_main[i]['curve']) for i, name in enumerate(grid_names_urs)}
    
    for grid, (curve_urs, curve_main) in grid_comparison.items():
        try:
            start_urs = curve_urs.GetEndPoint(0)
            end_urs = curve_urs.GetEndPoint(1)
            start_main = curve_main.GetEndPoint(0)
            end_main = curve_main.GetEndPoint(1)
            
            # Comparing start points
            start_match = "Match" if abs(start_urs.X - start_main.X) < 1e-6 and abs(start_urs.Y - start_main.Y) < 1e-6 else "Mismatch"
            
            # Comparing end points
            end_match = "Match" if abs(end_urs.X - end_main.X) < 1e-6 and abs(end_urs.Y - end_main.Y) < 1e-6 else "Mismatch"
            
            report_data.append([
                "Grid",
                "{} (Start)".format(grid),
                "{:.2f}, {:.2f}".format(start_urs.X, start_urs.Y),
                "{:.2f}, {:.2f}".format(start_main.X, start_main.Y),
                start_match
            ])
            report_data.append([
                "",
                "{} (End)".format(grid),
                "{:.2f}, {:.2f}".format(end_urs.X, end_urs.Y),
                "{:.2f}, {:.2f}".format(end_main.X, end_main.Y),
                end_match
            ])
        except Exception as e:
            report_data.append([
                "Grid",
                grid,
                "Error",
                "Error",
                "Error: {}".format(e)
            ])
    
    # Compare project base points
    report_data.extend(compare_base_points(p_bp_urs, p_bp_main))
    
    return report_data


def main():
    """Main function to run the comparison."""
        # Get the output object
    output = script.get_output()

    # Prompt user to select the URS and Main files
    forms.alert("Please select the URS and Main Revit files for comparison.", title="File Selection")
    
    urs_file = forms.pick_file(file_ext='rvt', title="Select the URS file")
    if not urs_file:
        forms.alert("No URS file selected. Exiting.", exit_code=1)

    main_file = forms.pick_file(file_ext='rvt', title="Select the Main file")
    if not main_file:
        forms.alert("No Main file selected. Exiting.", exit_code=1)
    
    doc_urs = open_revit_document(urs_file)
    doc_main = open_revit_document(main_file)
    
    # Perform comparison
    report_data = compare_files(doc_urs, doc_main)
    
    # Print results
    output = script.get_output()
    output.print_table(report_data, ["Type", "Name", "URS File Value", "Main File Value", "Match Status"])

if __name__ == "__main__":
    main()
