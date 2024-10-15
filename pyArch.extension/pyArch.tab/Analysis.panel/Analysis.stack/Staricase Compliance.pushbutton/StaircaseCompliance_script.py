# -*- coding: utf-8 -*-
'''Staircase Compliance'''
__title__ = "Staircase Compliance"
__author__ = "prajwalbkumar"

# Imports
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Architecture import *
from pyrevit import forms, script
from System.Collections.Generic import List

import time
from datetime import datetime
from Extract.RunData import get_run_data

start_time = time.time()
manual_time = 0
total_element_count = 0


doc = __revit__.ActiveUIDocument.Document # Get the Active Document
output = script.get_output()


def get_inflated_bbox(element, headroom_clearance):
    bbox = element.get_BoundingBox(None)
    # print("Minimum: {}" .format(bbox.Min))
    # print("Maximum: {}" .format(bbox.Max))
    bbox.Max = XYZ(bbox.Max.X, bbox.Max.Y, (bbox.Max.Z + (headroom_clearance * 0.003)))
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

try:

    # Get all the Stairs in the Document. And Inflate their bounding boxes a over the top.
    stairs_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Stairs).WhereElementIsNotElementType().ToElements()

    if not stairs_collector:
        forms.alert("No staircase found in the active document \n\n"
                                "Run the tool after creating a staircase", title = "Script Exiting", warn_icon = True)
        script.exit()

    # Relevant Codes
    code = ["NFPA", "IBC", "SBC", "DCD"]

    # Prompt to choose a Code
    user_code = forms.SelectFromList.show(code, title="Select Relevent Code", width=300, height=300, button_name="Select Code", multiselect=False)

    if not user_code:
        script.exit()

    checks = ["TREAD", "RISER", "HEADROOM", "NOSING", "HANDRAIL HEIGHT", "HANDRAIL - WALL CLEARANCE", "HANDRAIL EXTENSION", "HANDRAIL COUNTS"]

    user_checks = forms.SelectFromList.show(checks, title="Select Checks", width=300, height=500, button_name="Select Check(s)", multiselect=True)

    if not user_checks:
        script.exit()

    if user_code == code[0]:
        tread_min = 280
        tread_max = 340
        riser_min = 100
        riser_max = 180
        headroom_clearance = 2030
        nosing = 25
        handrail_height_min = 865
        handrail_height_max = 965
        code_handrail_clearance = 57
        vertical_rise = 3660

    elif user_code == code[1]:
        tread_min = 279
        tread_max = 340
        riser_min = 102
        riser_max = 178
        headroom_clearance = 2032
        nosing = 32
        handrail_height_min = 864
        handrail_height_max = 965
        code_handrail_clearance = 38
        vertical_rise = 3658

    elif user_code == code[2]:
        tread_min = 280
        tread_max = 340
        riser_min = 100
        riser_max = 180
        headroom_clearance = 2100
        nosing = 30
        handrail_height_min = 860
        handrail_height_max = 960
        code_handrail_clearance = 38
        vertical_rise = 3700

    elif user_code == code[3]:
        tread_min = 280
        tread_max = 340
        riser_min = 100
        riser_max = 180
        headroom_clearance = 2032
        nosing = 25
        handrail_height_min = 865
        handrail_height_max = 965
        code_handrail_clearance = 57
        vertical_rise = 3660

    else:
        script.exit()

    if checks[0] in user_checks: # TREAD CHECK
        manual_time = manual_time + 180
        total_element_count = total_element_count + len(stairs_collector)        
        failed_data = []

        for stair in stairs_collector:
            try:
                stair_tread = int(stair.LookupParameter("Actual Tread Depth").AsDouble() * 304.8)
                if stair_tread < tread_min or stair_tread > tread_max:
                    if stair.LookupParameter("Base Level"):
                        base_level = stair.LookupParameter("Base Level").AsValueString()
                    else:
                        base_level = "NONE"

                    if stair.LookupParameter("Top Level"):
                        top_level = stair.LookupParameter("Top Level").AsValueString()
                    else:
                        top_level = "NONE"

                    if stair.LookupParameter("Actual Tread Depth"):
                        tread_depth = stair.LookupParameter("Actual Tread Depth").AsValueString()
                    else:
                        tread_depth = "NONE"
                    
                    failed_stair_data = [output.linkify(stair.Id),
                            base_level,
                            top_level,
                            tread_depth,
                            "{} - {}" .format(tread_min, tread_max),
                            "TREAD DEPTH ERROR"
                        ]
                    failed_data.append(failed_stair_data)
            
            except:
                if stair.LookupParameter("Base Level"):
                        base_level = stair.LookupParameter("Base Level").AsValueString()
                else:
                    base_level = "NONE"

                if stair.LookupParameter("Top Level"):
                    top_level = stair.LookupParameter("Top Level").AsValueString()
                else:
                    top_level = "NONE"

                if stair.LookupParameter("Actual Tread Depth"):
                    tread_depth = stair.LookupParameter("Actual Tread Depth").AsValueString()
                else:
                    tread_depth = "NONE"
                
                failed_stair_data = [output.linkify(stair.Id),
                        base_level,
                        top_level,
                        tread_depth,
                        "{} - {}" .format(tread_min, tread_max),
                        "STAIR SKIPPED"
                    ]
                failed_data.append(failed_stair_data)

        if failed_data:
            output.print_md("##⚠️ {} Checks Completed. Issues Found ☹️".format(checks[0]))
            output.print_md("---")
            output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")
            output.print_table(table_data=failed_data, columns=["ELEMENT ID", "BASE LEVEL", "TOP LEVEL", "CURRENT TREAD DEPTH", "CORRECT TREAD DEPTH RANGE", "ERROR CODE"])
            output.print_md("---")
            output.print_md("***✅ ERROR CODE REFERENCE***")
            output.print_md("---")
            output.print_md("**TREAD DEPTH ERROR** - The tread depth should be between {} mm - {} mm\n" .format(tread_min, tread_max))
            output.print_md("**STAIR SKIPPED** - The staircase has been skipped. Check Manually")
            output.print_md("---")

        if not failed_data:
            output.print_md("##✅ {} Checks Completed. No Issues Found 😃".format(checks[0]))
            output.print_md("---")

    if checks[1] in user_checks: # RISER CHECK
        manual_time = manual_time + 180
        total_element_count = total_element_count + len(stairs_collector)
        failed_data = []
        for stair in stairs_collector:
            try:
                stair_riser = int(stair.LookupParameter("Actual Riser Height").AsDouble() * 304.8)

                if stair_riser < riser_min or stair_riser > riser_max:
                    if stair.LookupParameter("Base Level"):
                            base_level = stair.LookupParameter("Base Level").AsValueString()
                    else:
                        base_level = "NONE"

                    if stair.LookupParameter("Top Level"):
                        top_level = stair.LookupParameter("Top Level").AsValueString()
                    else:
                        top_level = "NONE"

                    if stair.LookupParameter("Actual Riser Height"):
                        riser_height = stair.LookupParameter("Actual Riser Height").AsValueString()
                    else:
                        riser_height = "NONE"
                    
                    failed_stair_data = [output.linkify(stair.Id),
                            base_level,
                            top_level,
                            riser_height,
                            "{} - {}" .format(tread_min, tread_max),
                            "RISER HEIGHT ERROR"
                        ]
                    failed_data.append(failed_stair_data)                

            except:
                if stair.LookupParameter("Base Level"):
                        base_level = stair.LookupParameter("Base Level").AsValueString()
                else:
                    base_level = "NONE"

                if stair.LookupParameter("Top Level"):
                    top_level = stair.LookupParameter("Top Level").AsValueString()
                else:
                    top_level = "NONE"

                if stair.LookupParameter("Actual Riser Height"):
                    riser_height = stair.LookupParameter("Actual Riser Height").AsValueString()
                else:
                    riser_height = "NONE"
                
                failed_stair_data = [output.linkify(stair.Id),
                        base_level,
                        top_level,
                        riser_height,
                        "{} - {}" .format(tread_min, tread_max),
                        "STAIR SKIPPED"
                    ]
                failed_data.append(failed_stair_data)            

        if failed_data:
            output.print_md("##⚠️ {} Checks Completed. Issues Found ☹️".format(checks[1]))
            output.print_md("---")
            output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")
            output.print_table(table_data=failed_data, columns=["ELEMENT ID", "BASE LEVEL", "TOP LEVEL", "CURRENT RISER HEIGHT", "CORRECT RISER HEIGHT RANGE", "ERROR CODE"])
            output.print_md("---")
            output.print_md("***✅ ERROR CODE REFERENCE***")
            output.print_md("---")
            output.print_md("**RISER HEIGHT ERROR** - The riser height should be between {} mm - {} mm\n" .format(riser_min, riser_max))
            output.print_md("---")

        if not failed_data:
            output.print_md("##✅ {} Checks Completed. No Issues Found 😃".format(checks[1]))
            output.print_md("---")

    if checks[2] in user_checks: # HEADROOM CHECK
        manual_time = manual_time + 1500
        total_element_count = total_element_count + len(stairs_collector)  
        # Collect all linked instances
        linked_instance = FilteredElementCollector(doc).OfClass(RevitLinkInstance).ToElements()
        link_name = []
        target_instances_type = List[ElementId]()
        
        for link in linked_instance:
            link_name.append(link.Name)

        if link_name:
            target_instance_names = forms.SelectFromList.show(link_name, title = "Select Target File", width=600, height=600, button_name="Select File", multiselect=True)
            if not target_instance_names:
                script.exit()   

            for link in linked_instance:
                for name in target_instance_names:
                    if name != link.Name:
                        target_instances_type.Add(link.GetTypeId())
        
        t = Transaction(doc, "Clearance Check")
        t.Start()
        view_family_types = FilteredElementCollector(doc).OfClass(ViewFamilyType)

        for view_type in view_family_types:
            if view_type.ViewFamily == ViewFamily.ThreeDimensional:
                target_type = view_type
                break
            
        analytical_view = View3D.CreateIsometric(doc, target_type.Id)
        try:
            analytical_view.HideElements(target_instances_type)
        except:
            pass

        view_analytical = analytical_view.Duplicate(ViewDuplicateOption.Duplicate)
        view_analytical = doc.GetElement(view_analytical)

        options = Options()
        options.View = view_analytical
        options.IncludeNonVisibleObjects = True

        failed_data = []
        for stair in stairs_collector:
            try:
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
                        u_divisions = 2
                        v_divisions = 4
                        point_grid = pointgrid(face, u_divisions, v_divisions)
                        for point in point_grid:
                            all_points.append(point)


                if landing_faces:
                    for face in landing_faces:
                        # Define grid resolution
                        u_divisions = 6
                        v_divisions = 6
                        point_grid = pointgrid(face, u_divisions, v_divisions)
                        for point in point_grid:
                            all_points.append(point)
            
                direction = XYZ(0,0,1)
                for point in all_points:
                    intersector = ReferenceIntersector(view_analytical)
                    intersector.FindReferencesInRevitLinks = True
                    
                    result = intersector.FindNearest(XYZ(point.X, point.Y, (point.Z + 1)), direction)
                    if not result: 
                        continue
                    proximity = (result.Proximity + 1 ) * 304
                    if proximity < headroom_clearance:
                        failed_counter += 1
                        # # Visualize Rays
                        # plane = Plane.CreateByNormalAndOrigin(XYZ.BasisX, point)
                        # sketch_plane = SketchPlane.Create(doc, plane)
                        # model_line = doc.Create.NewModelCurve(Line.CreateBound(point, XYZ(point.X,point.Y,(point.Z + (result.Proximity + 1 )))), sketch_plane)
                
                if failed_counter:
                    if stair.LookupParameter("Base Level"):
                            base_level = stair.LookupParameter("Base Level").AsValueString()
                    else:
                        base_level = "NONE"

                    if stair.LookupParameter("Top Level"):
                        top_level = stair.LookupParameter("Top Level").AsValueString()
                    else:
                        top_level = "NONE" 

                    if stair.LookupParameter("Actual Riser Height"):
                        riser_height = stair.LookupParameter("Actual Riser Height").AsValueString()
                    else:
                        riser_height = "NONE" 

                    if stair.LookupParameter("Actual Number of Risers"):
                        riser_count = stair.LookupParameter("Actual Number of Risers").AsValueString()
                    else:
                        riser_count = "NONE"  

                    failed_stair_data = [
                        output.linkify(stair.Id),
                        base_level,
                        top_level,
                        riser_height,
                        riser_count,
                        "OVERHEAD NOT CLEAR"
                    ]
                    failed_data.append(failed_stair_data)
            except:
                if stair.LookupParameter("Base Level"):
                        base_level = stair.LookupParameter("Base Level").AsValueString()
                else:
                    base_level = "NONE"

                if stair.LookupParameter("Top Level"):
                    top_level = stair.LookupParameter("Top Level").AsValueString()
                else:
                    top_level = "NONE" 

                if stair.LookupParameter("Actual Riser Height"):
                    riser_height = stair.LookupParameter("Actual Riser Height").AsValueString()
                else:
                    riser_height = "NONE" 

                if stair.LookupParameter("Actual Number of Risers"):
                    riser_count = stair.LookupParameter("Actual Number of Risers").AsValueString()
                else:
                    riser_count = "NONE"  

                failed_stair_data = [
                    output.linkify(stair.Id),
                    base_level,
                    top_level,
                    riser_height,
                    riser_count,
                    "STAIR SKIPPED"
                ]
                failed_data.append(failed_stair_data)

        if failed_data:
            output.print_md("##⚠️ {} Checks Completed. Issues Found ☹️".format(checks[2]))
            output.print_md("---")
            output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")
            output.print_table(table_data=failed_data, columns=["ELEMENT ID", "BASE LEVEL", "TOP LEVEL", "RISER HEIGHT", "NO OF RISERS", "ERROR CODE"])
            output.print_md("---")
            output.print_md("***✅ ERROR CODE REFERENCE***")
            output.print_md("---")
            output.print_md("**OVERHEAD NOT CLEAR** - The headroom_clearance does not meet the minimum requriement of {} mm\n" .format(headroom_clearance))
            output.print_md("**STAIR SKIPPED** - Check the staircase manually")
            output.print_md("---")

        if not failed_data:
            output.print_md("##✅ {} Completed. No Issues Found 😃".format(checks[2]))
            output.print_md("---")

        t.RollBack()

    if checks[3] in user_checks: # NOSING CHECK
        manual_time = manual_time + 120
        total_element_count = total_element_count + len(stairs_collector)  
        failed_data = []
        for stair in stairs_collector:
            try:
                if (stair.LookupParameter("Family").AsValueString() == "Assembled Stair"):
                    counter = 0
                    for run in stair.GetStairsRuns():
                        run = doc.GetElement(run)
                        run_type = doc.GetElement(run.GetTypeId())
                        run_nosing   = int(run_type.LookupParameter("Nosing Profile").AsDouble() * 304.8)
                        if not run_nosing == nosing :
                            counter += 1
                    
                    if counter > 0:
                        if stair.LookupParameter("Base Level"):
                            base_level = stair.LookupParameter("Base Level").AsValueString()
                        else:
                            base_level = "NONE"

                        if stair.LookupParameter("Top Level"):
                            top_level = stair.LookupParameter("Top Level").AsValueString()
                        else:
                            top_level = "NONE"
                        
                        if stair.LookupParameter("Nosing Profile"):
                            run_nosing = int(run_type.LookupParameter("Nosing Profile").AsDouble() * 304.8)
                        else:
                            run_nosing = "NONE"

                        failed_stair_data = [output.linkify(stair.Id),
                        base_level,
                        top_level,
                        run_nosing,
                        nosing,
                        "NOSING LENGTH ERROR"
                        ]
                        failed_data.append(failed_stair_data)
            except:
                if stair.LookupParameter("Base Level"):
                    base_level = stair.LookupParameter("Base Level").AsValueString()
                else:
                    base_level = "NONE"

                if stair.LookupParameter("Top Level"):
                    top_level = stair.LookupParameter("Top Level").AsValueString()
                else:
                    top_level = "NONE"
                
                if stair.LookupParameter("Nosing Profile"):
                    run_nosing = int(run_type.LookupParameter("Nosing Profile").AsDouble() * 304.8)
                else:
                    run_nosing = "NONE"

                
                failed_stair_data = [output.linkify(stair.Id),
                base_level,
                top_level,
                run_nosing,
                nosing,
                "STAIR SKIPPED"
                ]
                failed_data.append(failed_stair_data)


        if failed_data:
            output.print_md("##⚠️ {} Checks Completed. Issues Found ☹️".format(checks[3]))
            output.print_md("---")
            output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")
            output.print_table(table_data=failed_data, columns=["ELEMENT ID", "BASE LEVEL", "TOP LEVEL", "CURRENT NOSING LENGTH", "CORRECT NOSING LENGTH", "ERROR CODE"])
            output.print_md("---")
            output.print_md("***✅ ERROR CODE REFERENCE***")
            output.print_md("---")
            output.print_md("**NOSING LENGTH ERROR** - The riser height should be {} mm \n" .format(nosing))
            output.print_md("---")

        if not failed_data:
            output.print_md("##✅ {} Checks Completed. No Issues Found 😃".format(checks[3]))
            output.print_md("---")

    if checks[4] in user_checks: # HANDRAIL HEIGHT CHECK
        manual_time = manual_time + 120
        total_element_count = total_element_count + len(stairs_collector)  
        failed_data = []
        for stair in stairs_collector:
            try:
                failed_counter = 0
                hand_rail_heights = []
                
                associated_railings = stair.GetAssociatedRailings()
                rail_counter = 0
                for railing in associated_railings:
                    railing = doc.GetElement(railing)
                    rail_counter += 1
                    railing_type = doc.GetElement(railing.GetTypeId())
                    rail_height = railing_type.PrimaryHandrailHeight * 304.8  
                    hand_rail_heights.append ("RAIL: " + str(rail_counter) + " HEIGHT: " + str(rail_height))     
                    if rail_height < handrail_height_min or rail_height > handrail_height_max:
                        failed_counter += 1
                
                if failed_counter > 0:
                    hand_rail_heights = "; ".join(hand_rail_heights)

                    if stair.LookupParameter("Base Level"):
                            base_level = stair.LookupParameter("Base Level").AsValueString()
                    else:
                        base_level = "NONE"

                    if stair.LookupParameter("Top Level"):
                        top_level = stair.LookupParameter("Top Level").AsValueString()
                    else:
                        top_level = "NONE"

                    failed_stair_data = [output.linkify(stair.Id),
                            base_level,
                            top_level,
                            hand_rail_heights,                    
                            "{} - {}" .format(handrail_height_min, handrail_height_max),
                            "HANDRAIL HEIGHT ERROR"
                        ]
                    failed_data.append(failed_stair_data)
            except:
                if stair.LookupParameter("Base Level"):
                        base_level = stair.LookupParameter("Base Level").AsValueString()
                else:
                    base_level = "NONE"

                if stair.LookupParameter("Top Level"):
                    top_level = stair.LookupParameter("Top Level").AsValueString()
                else:
                    top_level = "NONE"

                failed_stair_data = [output.linkify(stair.Id),
                        base_level,
                        top_level,
                        "NONE",                    
                        "{} - {}" .format(handrail_height_min, handrail_height_max),
                        "STAIR SKIPPED"
                    ]
                failed_data.append(failed_stair_data)


        if failed_data:
            output.print_md("##⚠️ {} Checks Completed. Issues Found ☹️".format(checks[4]))
            output.print_md("---")
            output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")
            output.print_table(table_data=failed_data, columns=["ELEMENT ID", "BASE LEVEL", "TOP LEVEL", "CURRENT RAILING HEIGHT", "CORRECT RAILING HEIGHT RANGE", "ERROR CODE"])
            output.print_md("---")
            output.print_md("***✅ ERROR CODE REFERENCE***")
            output.print_md("---")
            output.print_md("**HANDRAIL HEIGHT ERROR** - The handrail height should be between {} mm - {} mm\n" .format(handrail_height_min, handrail_height_max))
            output.print_md("---")

        if not failed_data:
            output.print_md("##✅ {} Checks Completed. No Issues Found 😃".format(checks[4]))
            output.print_md("---")

    if checks[5] in user_checks: # HANDRAIL - WALL CLEARANCE CHECK
        manual_time = manual_time + 120
        total_element_count = total_element_count + len(stairs_collector)  
        failed_data = []
        
        for stair in stairs_collector:
            try:
                failed_counter = 0
                hand_rail_clearance = []
                
                associated_railings = stair.GetAssociatedRailings()
                rail_counter = 0
                for railing in associated_railings:
                    railing = doc.GetElement(railing)
                    rail_counter += 1
                    railing_type = doc.GetElement(railing.GetTypeId())
                    
                    primary_handrail_type = doc.GetElement(railing_type.PrimaryHandrailType)

                    rail_clearance = primary_handrail_type.HandClearance * 304.8  

                    hand_rail_clearance.append ("RAIL: " + str(rail_counter) + " RAIL CLEARANCE: " + str(rail_clearance))     
                    if rail_clearance < handrail_height_min:
                        failed_counter += 1
                
                if failed_counter > 0:
                    hand_rail_clearance = "; ".join(hand_rail_clearance)

                    if stair.LookupParameter("Base Level"):
                        base_level = stair.LookupParameter("Base Level").AsValueString()
                    else:
                        base_level = "NONE"

                    if stair.LookupParameter("Top Level"):
                        top_level = stair.LookupParameter("Top Level").AsValueString()
                    else:
                        top_level = "NONE"

                    failed_stair_data = [output.linkify(stair.Id),
                            base_level,
                            top_level,
                            hand_rail_clearance,                    
                            code_handrail_clearance,
                            "HANDRAIL CLEARANCE ERROR"
                        ]
                    failed_data.append(failed_stair_data)
            except:
                if stair.LookupParameter("Base Level"):
                    base_level = stair.LookupParameter("Base Level").AsValueString()
                else:
                    base_level = "NONE"

                if stair.LookupParameter("Top Level"):
                    top_level = stair.LookupParameter("Top Level").AsValueString()
                else:
                    top_level = "NONE"

                failed_stair_data = [output.linkify(stair.Id),
                        base_level,
                        top_level,
                        "NONE",                    
                        code_handrail_clearance,
                        "STAIR SKIPPED"
                    ]
                failed_data.append(failed_stair_data)

        if failed_data:
            output.print_md("##⚠️ {} Checks Completed. Issues Found ☹️".format(checks[5]))
            output.print_md("---")
            output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")
            output.print_table(table_data=failed_data, columns=["ELEMENT ID", "BASE LEVEL", "TOP LEVEL", "CURRENT RAILING CLEARANCE", "CORRECT RAILING CLEARANCE", "ERROR CODE"])
            output.print_md("---")
            output.print_md("***✅ ERROR CODE REFERENCE***")
            output.print_md("---")
            output.print_md("**HANDRAIL CLEARANCE ERROR** - The handrail clearance should be between {} mm - {} mm\n" .format(handrail_height_min, handrail_height_max))
            output.print_md("---")

        if not failed_data:
            output.print_md("##✅ {} Checks Completed. No Issues Found 😃".format(checks[5]))
            output.print_md("---")

    if checks[6] in user_checks: # HANDRAIL EXTENSION CHECK
        manual_time = manual_time + 300
        total_element_count = total_element_count + len(stairs_collector)  
        failed_data = []
        for stair in stairs_collector:
            try:
                failed_counter = 0
                associated_railings = stair.GetAssociatedRailings()
                rail_counter = 0
                for railing in associated_railings:
                    railing = doc.GetElement(railing)
                    rail_counter += 1
                    railing_type = doc.GetElement(railing.GetTypeId())
                    
                    primary_handrail_type = doc.GetElement(railing_type.PrimaryHandrailType)

                    bottom_rail_extension = primary_handrail_type.StartOrBottomExtensionLength * 304.8
                    top_rail_extension = primary_handrail_type.EndOrTopExtensionLength * 304.8  
        
                    
                    stair_tread = int(stair.LookupParameter("Actual Tread Depth").AsDouble() * 304.8)

                    if bottom_rail_extension < stair_tread:
                        failed_counter += 1
                    elif top_rail_extension < 305:
                        failed_counter += 1
                
                if failed_counter > 0:
                    if stair.LookupParameter("Base Level"):
                        base_level = stair.LookupParameter("Base Level").AsValueString()
                    else:
                        base_level = "NONE"

                    if stair.LookupParameter("Top Level"):
                        top_level = stair.LookupParameter("Top Level").AsValueString()
                    else:
                        top_level = "NONE"

                    if stair.LookupParameter("Actual Tread Depth"):
                        stair_tread = int(stair.LookupParameter("Actual Tread Depth").AsDouble() * 304.8)
                    else:
                        stair_tread = "NONE"
                        
                    failed_stair_data = [output.linkify(stair.Id),
                            base_level,
                            top_level,                 
                            "{} / 305" .format(stair_tread),
                            "HANDRAIL EXTENSION ERROR"
                        ]
                    failed_data.append(failed_stair_data)
            except:
                if stair.LookupParameter("Base Level"):
                    base_level = stair.LookupParameter("Base Level").AsValueString()
                else:
                    base_level = "NONE"

                if stair.LookupParameter("Top Level"):
                    top_level = stair.LookupParameter("Top Level").AsValueString()
                else:
                    top_level = "NONE"

                if stair.LookupParameter("Actual Tread Depth"):
                    stair_tread = int(stair.LookupParameter("Actual Tread Depth").AsDouble() * 304.8)
                else:
                    stair_tread = "NONE"
                    
                failed_stair_data = [output.linkify(stair.Id),
                        base_level,
                        top_level,                 
                        "{} / 305" .format(stair_tread),
                        "STAIR SKIPPED"
                    ]
                failed_data.append(failed_stair_data)
                

        if failed_data:
            output.print_md("##⚠️ {} Checks Completed. Issues Found ☹️".format(checks[6]))
            output.print_md("---")
            output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")
            output.print_table(table_data=failed_data, columns=["ELEMENT ID", "BASE LEVEL", "TOP LEVEL", "CORRECT BOTTOM EXTENSION / TOP EXTENSION", "ERROR CODE"])
            output.print_md("---")
            output.print_md("***✅ ERROR CODE REFERENCE***")
            output.print_md("---")
            output.print_md("**HANDRAIL EXTENSION ERROR** - The handrail bottom extension should be {} mm and top extension should be {} mm\n" .format(stair_tread, 305))
            output.print_md("---")

        if not failed_data:
            output.print_md("##✅ {} Checks Completed. No Issues Found 😃".format(checks[6]))
            output.print_md("---")

    if checks[7] in user_checks: # HANDRAIL COUNTS
        manual_time = manual_time + 600
        total_element_count = total_element_count + len(stairs_collector)  

        failed_data = []

        options = Options()
        options.IncludeNonVisibleObjects = True

        for stair in stairs_collector:
            try:
            
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
            
                if run_faces:
                    longest_edge_length = []
                    for face in run_faces:
                        for edge_array in face.EdgeLoops:
                            for edge in edge_array:
                                longest_edge_length.append(edge.ApproximateLength)

                    longest_edge_length = sorted(longest_edge_length)
                    longest_edge_length = longest_edge_length[-1] * 304.8

                associated_railings = stair.GetAssociatedRailings()

                total_clearance = 0
                railing_counter = 0
                for railing in associated_railings:
                    railing_counter += 1
                    railing = doc.GetElement(railing)
                    railing_type = doc.GetElement(railing.GetTypeId())
                    primary_handrail_type = doc.GetElement(railing_type.PrimaryHandrailType)
                    
                    profile = doc.GetElement(primary_handrail_type.ProfileId)
                    
                    rail_diameter = profile.LookupParameter("Diameter").AsDouble() * 304.8
                    rail_clearance = primary_handrail_type.HandClearance * 304.8 
                    rail_offset = railing.LookupParameter("Offset from Path").AsDouble() * 304.8

                    total_clearance += (rail_diameter + rail_clearance + rail_offset)

                # Calculate clear width of the staircase
                stair_clear_width = longest_edge_length - total_clearance
                
                # Number of Mid Railing needed
                mid_rail_count = int(stair_clear_width / (760 * 2))

                total_rail_needed = mid_rail_count + 2

                if railing_counter != total_rail_needed:
                    if stair.LookupParameter("Base Level"):
                        base_level = stair.LookupParameter("Base Level").AsValueString()
                    else:
                        base_level = "NONE"

                    if stair.LookupParameter("Top Level"):
                        top_level = stair.LookupParameter("Top Level").AsValueString()
                    else:
                        top_level = "NONE"
                    failed_stair_data = [output.linkify(stair.Id),
                            base_level,
                            top_level,
                            int(stair_clear_width),
                            railing_counter,
                            total_rail_needed,
                            "HANDRAIL COUNT ERROR"
                        ]
                    failed_data.append(failed_stair_data)
            
            except:
                if stair.LookupParameter("Base Level"):
                    base_level = stair.LookupParameter("Base Level").AsValueString()
                else:
                    base_level = "NONE"

                if stair.LookupParameter("Top Level"):
                    top_level = stair.LookupParameter("Top Level").AsValueString()
                else:
                    top_level = "NONE"
                failed_stair_data = [output.linkify(stair.Id),
                        base_level,
                        top_level,
                        "NONE",
                        "NONE",
                        "NONE",
                        "STAIR SKIPPED"
                    ]
                failed_data.append(failed_stair_data)

        if failed_data:
            output.print_md("##⚠️ {} Checks Completed. Issues Found ☹️".format(checks[7]))
            output.print_md("---")
            output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")
            output.print_table(table_data=failed_data, columns=["ELEMENT ID", "BASE LEVEL", "TOP LEVEL", "MAX STAIR CLEAR WIDTH", "CURRENT RAILING COUNT", "CORRECT RAILING COUNT", "ERROR CODE"])
            output.print_md("---")
            output.print_md("***✅ ERROR CODE REFERENCE***")
            output.print_md("---")
            output.print_md("**HANDRAIL COUNT ERROR** - Check handrail counts associated to the staircase. Distribute the numbers evenly across the width")
            output.print_md("---")

        if not failed_data:
            output.print_md("##✅ {} Checks Completed. No Issues Found 😃".format(checks[7]))
            output.print_md("---")


    end_time = time.time()
    runtime = end_time - start_time
            
    run_result = "Tool ran successfully"
    if total_element_count:
        element_count = total_element_count
    else:
        element_count = 0

    error_occured ="Nil"

    get_run_data(__title__, runtime, element_count, manual_time, run_result, error_occured)

except Exception as e:
    
  
    end_time = time.time()
    runtime = end_time - start_time

    error_occured = "Error occurred: {}".format(str(e))
    run_result = "Error"
    element_count = 0
    
    get_run_data(__title__, runtime, element_count, manual_time, run_result, error_occured)