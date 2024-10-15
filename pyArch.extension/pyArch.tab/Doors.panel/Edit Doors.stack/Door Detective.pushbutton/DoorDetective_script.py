# -*- coding: utf-8 -*-
'''Door Detective'''
__title__ = "Door Detective"
__author__ = "prajwalbkumar"

# Imports
from Autodesk.Revit.DB import *
from pyrevit import forms, script
import xlrd
import os

import time
from datetime import datetime
from Extract.RunData import get_run_data

start_time = time.time()
manual_time = 0
total_element_count = 0

doc = __revit__.ActiveUIDocument.Document # Get the Active Document
output = script.get_output()

script_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(script_dir, "..", ".."))
excel_filename = "Door Design Database.xlsx"
excel_path = os.path.join(parent_dir, excel_filename)

try:
    # MAIN SCRIPT
    # Door - Room_Type Checks
    door_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()

    if not door_collector:
        forms.alert("No doors found in the active document\n"
                                "Run the tool after creating a door", title = "Script Exiting", warn_icon = True)
        script.exit()


    try:
        if door_collector[0].LookupParameter("Room_Type").AsString():
            pass
    except:
        forms.alert("No Room_Type Parameter Found in Document\n"
                    "Run the Add Room Type Parameter First!", title = "Script Exiting", warn_icon = True)
        script.exit()

    # Check if the Room_Type Parameters are filled according to the Excel File. 
    # options = forms.alert("Select the Door Design Database Excel File", title = "Open Excel File", warn_icon = False, options=["Select File"])
    # if options == "Select File":
    #     excel_path =  forms.pick_excel_file()
    #     if not excel_path:
    #         script.exit()
    # else:
    #     script.exit()

    excel_workbook = xlrd.open_workbook(excel_path)
    excel_worksheet = excel_workbook.sheet_by_index(1)
    excel_room_types = []
    for row in range(1, excel_worksheet.nrows):
        excel_room_types.append(excel_worksheet.cell_value(row,0).lower())

    # Check for Room_Type Value
    failed_data = []

    manual_time = manual_time + 60
    total_element_count = total_element_count + len(door_collector)   

    for door in door_collector:
        failed_door_data = []
        if not door.LookupParameter("Room_Type").HasValue:
            failed_door_data.append(output.linkify(door.Id))
            if door.LookupParameter("Mark").HasValue:
                failed_door_data.append(door.LookupParameter("Mark").AsString().upper())
            else:
                failed_door_data.append("NONE")
            if door.LookupParameter("Level"):
                failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
            else:
                failed_door_data.append("NONE")
            failed_door_data.append("ROOM_TYPE VALUE MISSING")
            failed_data.append(failed_door_data)
            continue

        elif door.LookupParameter("Room_Type").AsString() == "":
            failed_door_data.append(output.linkify(door.Id))
            if door.LookupParameter("Mark").HasValue:
                failed_door_data.append(door.LookupParameter("Mark").AsString().upper())
            else:
                failed_door_data.append("NONE")
            if door.LookupParameter("Level"):
                failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
            else:
                failed_door_data.append("NONE")
            failed_door_data.append("ROOM_TYPE VALUE MISSING")
            failed_data.append(failed_door_data)
            continue
        
        else:
            if door.LookupParameter("Room_Type").AsString().lower() in excel_room_types:
                continue
            else:
                failed_door_data.append(output.linkify(door.Id))
                if door.LookupParameter("Mark").HasValue:
                    failed_door_data.append(door.LookupParameter("Mark").AsString().upper())
                else:
                    failed_door_data.append("NONE")
            if door.LookupParameter("Level"):
                failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
            else:
                failed_door_data.append("NONE")
                failed_door_data.append("ROOM_TYPE VALUE MISMATCH")
                failed_data.append(failed_door_data)

    if failed_data:
        output.print_md("##⚠️ {} Completed. Issues Found ☹️" .format(__title__)) # Markdown Heading 2
        output.print_md("---") # Markdown Line Break
        output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")  # Print a Line
        output.print_table(table_data=failed_data, columns=["ELEMENT ID", "MARK","LEVEL", "ROOM TYPE", "ERROR CODE", "CURRENT VALUE", "EXPECTED VALUE"]) # Print a Table
        print("\n\n")
        output.print_md("---") # Markdown Line Break
        output.print_md("***✅ ERROR CODE REFERENCE***")  # Print a Line
        output.print_md("---") # Markdown Line Break
        output.print_md("**ROOM_TYPE VALUE MISSING**  - Empty Room Type Parameter. Run the Copy Room Type Tool.") # Print a Quote
        output.print_md("**ROOM_TYPE VALUE MISMATCH** - Incorrect Room Rype Value. Refer to the Design Database for Values.") # Print a Quote
        output.print_md("---") # Markdown Line Break

        end_time = time.time()
        runtime = end_time - start_time
                
        run_result = "Tool ran successfully"
        if total_element_count:
            element_count = total_element_count
        else:
            element_count = 0

        error_occured ="Nil"

        get_run_data(__title__, runtime, element_count, manual_time, run_result, error_occured)
        
        script.exit()


    checks = ["No. of Leaves Check", "Leaf Width Check", "Leaf Height Check", "Undercut Check", "Leaf Material Check","Leaf Elevation Check", "Leaf Face Finish Check", "Frame Material Check", "Frame Elevation Check", "Frame Finish Check"]
    select_check = forms.SelectFromList.show(checks, title="Select Door Check", width=300, height=500, button_name="Select Code", multiselect=True)

    if not select_check:
        script.exit()     

    for user_check in select_check:
        if user_check == checks[0]: 
            manual_time = manual_time + 180
            total_element_count = total_element_count + len(door_collector)   
            failed_data = []
            for door in door_collector:
                failed_door_data = []
                door_room_type = door.LookupParameter("Room_Type").AsString().lower()
                try:
                    if not door.Symbol.LookupParameter("Leaf_Number").HasValue or door.Symbol.LookupParameter("Leaf_Number") == "":
                        failed_door_data.append(output.linkify(door.Id))
                        failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                        if door.LookupParameter("Level"):
                            failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                        else:
                            failed_door_data.append("NONE")
                        failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                        failed_door_data.append("LEAF NUMBER PARAMETER EMPTY")
                        failed_door_data.append("NONE")
                        failed_door_data.append(str(int(excel_worksheet.cell_value(row,1))).upper())
                        failed_data.append(failed_door_data)
                        continue   
                except:
                    failed_door_data.append(output.linkify(door.Id))
                    failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                    if door.LookupParameter("Level"):
                        failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                    else:
                        failed_door_data.append("NONE")
                    failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                    failed_door_data.append("NO LEAF NUMBER PARAMETER FOUND")
                    failed_door_data.append("NONE")
                    failed_door_data.append(str(int(excel_worksheet.cell_value(row,1))).upper())
                    failed_data.append(failed_door_data)
                    continue   


                door_leaf_number = door.Symbol.LookupParameter("Leaf_Number").AsValueString()
                for row in range(1, excel_worksheet.nrows):
                    if door_room_type == excel_worksheet.cell_value(row,0).lower():
                        if not door_leaf_number == str(int(excel_worksheet.cell_value(row,1))):
                            failed_door_data.append(output.linkify(door.Id))
                            failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                            if door.LookupParameter("Level"):
                                failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                            else:
                                failed_door_data.append("NONE")
                            failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                            failed_door_data.append("INVALID LEAF NUMBER")
                            failed_door_data.append(door_leaf_number.upper())
                            failed_door_data.append(str(int(excel_worksheet.cell_value(row,1))).upper())
                            failed_data.append(failed_door_data)
                            break
                            
            # Print Reports
            if failed_data:
                output.print_md("##⚠️ {} Completed. Issues Found ☹️" .format(user_check)) # Markdown Heading 2
                output.print_md("---") # Markdown Line Break
                output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")  # Print a Line
                output.print_table(table_data=failed_data, columns=["ELEMENT ID", "MARK","LEVEL", "ROOM TYPE", "ERROR CODE", "CURRENT VALUE", "EXPECTED VALUE"]) # Print a Table
                print("\n\n")
                output.print_md("---") # Markdown Line Break
            else:
                output.print_md("##✅ {} Completed. No Issues Found 😃" .format(user_check)) # Markdown Heading 2
                output.print_md("---") # Markdown Line Break

        if user_check == checks[1]: 
            manual_time = manual_time + 180
            total_element_count = total_element_count + len(door_collector)
            failed_data = []
            for door in door_collector:
                failed_door_data = []
                door_room_type = door.LookupParameter("Room_Type").AsString().lower()
                try:
                    if not door.Symbol.LookupParameter("Width").HasValue or door.Symbol.LookupParameter("Width") == "":
                        failed_door_data.append(output.linkify(door.Id))
                        failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                        if door.LookupParameter("Level"):
                            failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                        else:
                            failed_door_data.append("NONE")
                        failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                        failed_door_data.append("INVALID LEAF WIDTH")
                        failed_door_data.append("NONE")
                        failed_door_data.append(str(int(excel_worksheet.cell_value(row,2))).upper())
                        failed_data.append(failed_door_data)
                        continue   
                except:
                    failed_door_data.append(output.linkify(door.Id))
                    failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                    if door.LookupParameter("Level"):
                        failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                    else:
                        failed_door_data.append("NONE")
                    failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                    failed_door_data.append("INVALID LEAF WIDTH")
                    failed_door_data.append("NONE")
                    failed_door_data.append(str(int(excel_worksheet.cell_value(row,2))).upper())
                    failed_data.append(failed_door_data)
                    continue   


                door_width = door.Symbol.LookupParameter("Width").AsValueString()
                for row in range(1, excel_worksheet.nrows):
                    if door_room_type == excel_worksheet.cell_value(row,0).lower():
                        if not door_width == str(int(excel_worksheet.cell_value(row,2))):
                            failed_door_data.append(output.linkify(door.Id))
                            failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                            if door.LookupParameter("Level"):
                                failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                            else:
                                failed_door_data.append("NONE")
                            failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                            failed_door_data.append("INVALID LEAF WIDTH")
                            failed_door_data.append(door_width.upper())
                            failed_door_data.append(str(int(excel_worksheet.cell_value(row,2))).upper())
                            failed_data.append(failed_door_data)
                            break

            # Print Reports
            if failed_data:
                output.print_md("##⚠️ {} Completed. Issues Found ☹️" .format(user_check)) # Markdown Heading 2
                output.print_md("---") # Markdown Line Break
                output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")  # Print a Line
                output.print_table(table_data=failed_data, columns=["ELEMENT ID", "MARK","LEVEL", "ROOM TYPE", "ERROR CODE", "CURRENT VALUE", "EXPECTED VALUE"]) # Print a Table
                print("\n\n")
                output.print_md("---") # Markdown Line Break
            else:
                output.print_md("##✅ {} Completed. No Issues Found 😃" .format(user_check)) # Markdown Heading 2
                output.print_md("---") # Markdown Line Break

        if user_check == checks[2]: 
            manual_time = manual_time + 180
            total_element_count = total_element_count + len(door_collector)
            failed_data = []
            for door in door_collector:
                failed_door_data = []
                door_room_type = door.LookupParameter("Room_Type").AsString().lower()
                try:
                    if not door.Symbol.LookupParameter("Height").HasValue or door.Symbol.LookupParameter("Heigth") == "":
                        failed_door_data.append(output.linkify(door.Id))
                        failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                        if door.LookupParameter("Level"):
                            failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                        else:
                            failed_door_data.append("NONE")
                        failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                        failed_door_data.append("INVALID LEAF HEIGHT")
                        failed_door_data.append("NONE")
                        failed_door_data.append(str(int(excel_worksheet.cell_value(row,3))).upper())
                        failed_data.append(failed_door_data)
                        continue   
                except:
                    failed_door_data.append(output.linkify(door.Id))
                    failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                    if door.LookupParameter("Level"):
                        failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                    else:
                        failed_door_data.append("NONE")
                    failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                    failed_door_data.append("INVALID LEAF HEIGHT")
                    failed_door_data.append("NONE")
                    failed_door_data.append(str(int(excel_worksheet.cell_value(row,3))).upper())
                    failed_data.append(failed_door_data)
                    continue   

                door_height = door.Symbol.LookupParameter("Height").AsValueString()
                for row in range(1, excel_worksheet.nrows):
                    if door_room_type == excel_worksheet.cell_value(row,0).lower():
                        if not door_height == str(int(excel_worksheet.cell_value(row,3))):
                            failed_door_data.append(output.linkify(door.Id))
                            failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                            if door.LookupParameter("Level"):
                                failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                            else:
                                failed_door_data.append("NONE")
                            failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                            failed_door_data.append("INVALID LEAF HEIGHT")
                            failed_door_data.append(door_height.upper())
                            failed_door_data.append(str(int(excel_worksheet.cell_value(row,3))).upper())
                            failed_data.append(failed_door_data)
                            break

            # Print Reports
            if failed_data:
                output.print_md("##⚠️ {} Completed. Issues Found ☹️" .format(user_check)) # Markdown Heading 2
                output.print_md("---") # Markdown Line Break
                output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")  # Print a Line
                output.print_table(table_data=failed_data, columns=["ELEMENT ID", "MARK","LEVEL", "ROOM TYPE", "ERROR CODE", "CURRENT VALUE", "EXPECTED VALUE"]) # Print a Table
                print("\n\n")
                output.print_md("---") # Markdown Line Break
            else:
                output.print_md("##✅ {} Completed. No Issues Found 😃" .format(user_check)) # Markdown Heading 2
                output.print_md("---") # Markdown Line Break

        if user_check == checks[3]: 
            manual_time = manual_time + 180
            total_element_count = total_element_count + len(door_collector)
            failed_data = []
            for door in door_collector:
                failed_door_data = []
                door_room_type = door.LookupParameter("Room_Type").AsString().lower()
                try:
                    if not door.Symbol.LookupParameter("Undercut").HasValue or door.Symbol.LookupParameter("Undercut") == "":
                        failed_door_data.append(output.linkify(door.Id))
                        failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                        if door.LookupParameter("Level"):
                            failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                        else:
                            failed_door_data.append("NONE")
                        failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                        failed_door_data.append("INVALID UNDERCUT")
                        failed_door_data.append("NONE")
                        failed_door_data.append(str(int(excel_worksheet.cell_value(row,4))).upper())
                        failed_data.append(failed_door_data)
                        continue  
                except:
                    failed_door_data.append(output.linkify(door.Id))
                    failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                    if door.LookupParameter("Level"):
                        failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                    else:
                        failed_door_data.append("NONE")
                    failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                    failed_door_data.append("INVALID UNDERCUT")
                    failed_door_data.append("NONE")
                    failed_door_data.append(str(int(excel_worksheet.cell_value(row,4))).upper())
                    failed_data.append(failed_door_data)
                    continue  

                door_undercut = door.Symbol.LookupParameter("Undercut").AsValueString()
                for row in range(1, excel_worksheet.nrows):
                    if door_room_type == excel_worksheet.cell_value(row,0).lower():
                        if not door_undercut == str(int(excel_worksheet.cell_value(row,4))):
                            failed_door_data.append(output.linkify(door.Id))
                            failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                            if door.LookupParameter("Level"):
                                failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                            else:
                                failed_door_data.append("NONE")
                            failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                            failed_door_data.append("INVALID UNDERCUT")
                            failed_door_data.append(door_undercut.upper())
                            failed_door_data.append(str(int(excel_worksheet.cell_value(row,4))).upper())
                            failed_data.append(failed_door_data)
                            break

            # Print Reports
            if failed_data:
                output.print_md("##⚠️ {} Completed. Issues Found ☹️" .format(user_check)) # Markdown Heading 2
                output.print_md("---") # Markdown Line Break
                output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")  # Print a Line
                output.print_table(table_data=failed_data, columns=["ELEMENT ID", "MARK","LEVEL", "ROOM TYPE", "ERROR CODE", "CURRENT VALUE", "EXPECTED VALUE"]) # Print a Table
                print("\n\n")
                output.print_md("---") # Markdown Line Break
            else:
                output.print_md("##✅ {} Completed. No Issues Found 😃" .format(user_check)) # Markdown Heading 2
                output.print_md("---") # Markdown Line Break

        if user_check == checks[4]: 
            manual_time = manual_time + 180
            total_element_count = total_element_count + len(door_collector)
            failed_data = []
            for door in door_collector:
                failed_door_data = []
                door_room_type = door.LookupParameter("Room_Type").AsString().lower()
                try:
                    if not door.Symbol.LookupParameter("Leaf_Material").HasValue or door.Symbol.LookupParameter("Leaf_Material") == "":
                        failed_door_data.append(output.linkify(door.Id))
                        failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                        if door.LookupParameter("Level"):
                            failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                        else:
                            failed_door_data.append("NONE")
                        failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                        failed_door_data.append("INVALID LEAF MATERIAL")
                        failed_door_data.append("NONE")
                        failed_door_data.append(str(excel_worksheet.cell_value(row,5).lower()).upper())
                        failed_data.append(failed_door_data)
                        continue   
                except:
                        failed_door_data.append(output.linkify(door.Id))
                        failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                        if door.LookupParameter("Level"):
                            failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                        else:
                            failed_door_data.append("NONE")
                        failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                        failed_door_data.append("INVALID LEAF MATERIAL")
                        failed_door_data.append("NONE")
                        failed_door_data.append(str(excel_worksheet.cell_value(row,5).lower()).upper())
                        failed_data.append(failed_door_data)
                        continue

                door_leaf_material = door.Symbol.LookupParameter("Leaf_Material").AsValueString().lower()
                for row in range(1, excel_worksheet.nrows):
                    if door_room_type == excel_worksheet.cell_value(row,0).lower():
                        if not door_leaf_material == str(excel_worksheet.cell_value(row,5).lower()):
                            failed_door_data.append(output.linkify(door.Id))
                            failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                            if door.LookupParameter("Level"):
                                failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                            else:
                                failed_door_data.append("NONE")
                            failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                            failed_door_data.append("INVALID LEAF MATERIAL")
                            failed_door_data.append(door_leaf_material.upper())
                            failed_door_data.append(str(excel_worksheet.cell_value(row,5).lower()).upper())
                            failed_data.append(failed_door_data)
                            break

            # Print Reports
            if failed_data:
                output.print_md("##⚠️ {} Completed. Issues Found ☹️" .format(user_check)) # Markdown Heading 2
                output.print_md("---") # Markdown Line Break
                output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")  # Print a Line
                output.print_table(table_data=failed_data, columns=["ELEMENT ID", "MARK","LEVEL", "ROOM TYPE", "ERROR CODE", "CURRENT VALUE", "EXPECTED VALUE"]) # Print a Table
                output.print_md("---") # Markdown Line Break
            else:
                output.print_md("##✅ {} Completed. No Issues Found 😃" .format(user_check)) # Markdown Heading 2
                output.print_md("---") # Markdown Line Break

        if user_check == checks[5]: 
            manual_time = manual_time + 180
            total_element_count = total_element_count + len(door_collector)
            failed_data = []
            for door in door_collector:
                failed_door_data = []
                door_room_type = door.LookupParameter("Room_Type").AsString().lower()
                try:
                    if not door.Symbol.LookupParameter("Leaf_Elevation").HasValue or door.Symbol.LookupParameter("Leaf_Elevation") == "":
                        failed_door_data.append(output.linkify(door.Id))
                        failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                        if door.LookupParameter("Level"):
                            failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                        else:
                            failed_door_data.append("NONE")
                        failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                        failed_door_data.append("INVALID LEAF ELEVATION")
                        failed_door_data.append("NONE")
                        failed_door_data.append(str(excel_worksheet.cell_value(row,6).lower()).upper())
                        failed_data.append(failed_door_data)
                        continue  
                except:
                    failed_door_data.append(output.linkify(door.Id))
                    failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                    if door.LookupParameter("Level"):
                        failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                    else:
                        failed_door_data.append("NONE")
                    failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                    failed_door_data.append("INVALID LEAF ELEVATION")
                    failed_door_data.append("NONE")
                    failed_door_data.append(str(excel_worksheet.cell_value(row,6).lower()).upper())
                    failed_data.append(failed_door_data)
                    continue

                door_leaf_elevation = door.Symbol.LookupParameter("Leaf_Elevation").AsValueString().lower()
                for row in range(1, excel_worksheet.nrows):
                    if door_room_type == excel_worksheet.cell_value(row,0).lower():
                        if not door_leaf_elevation == str(excel_worksheet.cell_value(row,6).lower()):
                            failed_door_data.append(output.linkify(door.Id))
                            failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                            if door.LookupParameter("Level"):
                                failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                            else:
                                failed_door_data.append("NONE")
                            failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                            failed_door_data.append("INVALID LEAF ELEVATION")
                            failed_door_data.append(door_leaf_elevation.upper())
                            failed_door_data.append(str(excel_worksheet.cell_value(row,6).lower()).upper())
                            failed_data.append(failed_door_data)
                            break

            # Print Reports
            if failed_data:
                output.print_md("##⚠️ {} Completed. Issues Found ☹️" .format(user_check)) # Markdown Heading 2
                output.print_md("---") # Markdown Line Break
                output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")  # Print a Line
                output.print_table(table_data=failed_data, columns=["ELEMENT ID", "MARK","LEVEL", "ROOM TYPE", "ERROR CODE", "CURRENT VALUE", "EXPECTED VALUE"]) # Print a Table
                print("\n\n")
                output.print_md("---") # Markdown Line Break
            else:
                output.print_md("##✅ {} Completed. No Issues Found 😃" .format(user_check)) # Markdown Heading 2
                output.print_md("---") # Markdown Line Break

        if user_check == checks[6]: 
            manual_time = manual_time + 180
            total_element_count = total_element_count + len(door_collector)
            failed_data = []
            for door in door_collector:
                failed_door_data = []
                door_room_type = door.LookupParameter("Room_Type").AsString().lower()
                try:
                    if not door.Symbol.LookupParameter("Leaf_Face_Finish").HasValue or door.Symbol.LookupParameter("Leaf_Face_Finish") == "":
                        failed_door_data.append(output.linkify(door.Id))
                        failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                        if door.LookupParameter("Level"):
                            failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                        else:
                            failed_door_data.append("NONE")
                        failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                        failed_door_data.append("INVALID LEAF FACE FINISH")
                        failed_door_data.append("NONE")
                        failed_door_data.append(str(excel_worksheet.cell_value(row,7).lower()).upper())
                        failed_data.append(failed_door_data)
                        continue  
                except:
                    failed_door_data.append(output.linkify(door.Id))
                    failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                    if door.LookupParameter("Level"):
                        failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                    else:
                        failed_door_data.append("NONE")
                    failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                    failed_door_data.append("INVALID LEAF FACE FINISH")
                    failed_door_data.append("NONE")
                    failed_door_data.append(str(excel_worksheet.cell_value(row,7).lower()).upper())
                    failed_data.append(failed_door_data)
                    continue 

                door_leaf_face_finish = door.Symbol.LookupParameter("Leaf_Face_Finish").AsValueString().lower()
                for row in range(1, excel_worksheet.nrows):
                    if door_room_type == excel_worksheet.cell_value(row,0).lower():
                        if not door_leaf_face_finish == str(excel_worksheet.cell_value(row,7).lower()):
                            failed_door_data.append(output.linkify(door.Id))
                            failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                            if door.LookupParameter("Level"):
                                failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                            else:
                                failed_door_data.append("NONE")
                            failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                            failed_door_data.append("INVALID LEAF FACE FINISH")
                            failed_door_data.append(door_leaf_face_finish.upper())
                            failed_door_data.append(str(excel_worksheet.cell_value(row,7).lower()).upper())
                            failed_data.append(failed_door_data)
                            break

            # Print Reports
            if failed_data:
                output.print_md("##⚠️ {} Completed. Issues Found ☹️" .format(user_check)) # Markdown Heading 2
                output.print_md("---") # Markdown Line Break
                output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")  # Print a Line
                output.print_table(table_data=failed_data, columns=["ELEMENT ID", "MARK","LEVEL", "ROOM TYPE", "ERROR CODE", "CURRENT VALUE", "EXPECTED VALUE"]) # Print a Table
                print("\n\n")            
                output.print_md("---") # Markdown Line Break
            else:
                output.print_md("##✅ {} Completed. No Issues Found 😃" .format(user_check)) # Markdown Heading 2
                output.print_md("---") # Markdown Line Break

        if user_check == checks[7]: 
            manual_time = manual_time + 180
            total_element_count = total_element_count + len(door_collector)
            failed_data = []
            for door in door_collector:
                failed_door_data = []
                door_room_type = door.LookupParameter("Room_Type").AsString().lower()
                try:
                    if not door.Symbol.LookupParameter("Frame_Material").HasValue or door.Symbol.LookupParameter("Frame_Material") == "":
                        failed_door_data.append(output.linkify(door.Id))
                        failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                        if door.LookupParameter("Level"):
                            failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                        else:
                            failed_door_data.append("NONE")
                        failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                        failed_door_data.append("INVALID FRAME MATERIAL")
                        failed_door_data.append("NONE")
                        failed_door_data.append(str(excel_worksheet.cell_value(row,8).lower()).upper())
                        failed_data.append(failed_door_data)
                        continue  
                except:
                    failed_door_data.append(output.linkify(door.Id))
                    failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                    if door.LookupParameter("Level"):
                        failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                    else:
                        failed_door_data.append("NONE")
                    failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                    failed_door_data.append("INVALID FRAME MATERIAL")
                    failed_door_data.append("NONE")
                    failed_door_data.append(str(excel_worksheet.cell_value(row,8).lower()).upper())
                    failed_data.append(failed_door_data)
                    continue  
                    
                door_frame_material = door.Symbol.LookupParameter("Frame_Material").AsValueString().lower()
                for row in range(1, excel_worksheet.nrows):
                    if door_room_type == excel_worksheet.cell_value(row,0).lower():
                        if not door_frame_material == str(excel_worksheet.cell_value(row,8).lower()):
                            failed_door_data.append(output.linkify(door.Id))
                            failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                            if door.LookupParameter("Level"):
                                failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                            else:
                                failed_door_data.append("NONE")
                            failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                            failed_door_data.append("INVALID FRAME MATERIAL")
                            failed_door_data.append(door_frame_material.upper())
                            failed_door_data.append(str(excel_worksheet.cell_value(row,8).lower()).upper())
                            failed_data.append(failed_door_data)
                            break

            # Print Reports
            if failed_data:
                output.print_md("##⚠️ {} Completed. Issues Found ☹️" .format(user_check)) # Markdown Heading 2
                output.print_md("---") # Markdown Line Break
                output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")  # Print a Line
                output.print_table(table_data=failed_data, columns=["ELEMENT ID", "MARK","LEVEL", "ROOM TYPE", "ERROR CODE", "CURRENT VALUE", "EXPECTED VALUE"]) # Print a Table
                print("\n\n")            
                output.print_md("---") # Markdown Line Break
            else:
                output.print_md("##✅ {} Completed. No Issues Found 😃" .format(user_check)) # Markdown Heading 2
                output.print_md("---") # Markdown Line Break

        if user_check == checks[8]: 
            manual_time = manual_time + 180
            total_element_count = total_element_count + len(door_collector)
            failed_data = []
            for door in door_collector:
                failed_door_data = []
                door_room_type = door.LookupParameter("Room_Type").AsString().lower()
                try:
                    if not door.Symbol.LookupParameter("Frame_Elevation").HasValue or door.Symbol.LookupParameter("Frame_Elevation") == "":
                        failed_door_data.append(output.linkify(door.Id))
                        failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                        if door.LookupParameter("Level"):
                            failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                        else:
                            failed_door_data.append("NONE")
                        failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                        failed_door_data.append("INVALID FRAME ELEVATION")
                        failed_door_data.append("NONE")
                        failed_door_data.append(str(excel_worksheet.cell_value(row,9).lower()).upper())
                        failed_data.append(failed_door_data)
                        continue  
                except:
                    failed_door_data.append(output.linkify(door.Id))
                    failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                    if door.LookupParameter("Level"):
                        failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                    else:
                        failed_door_data.append("NONE")
                    failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                    failed_door_data.append("INVALID FRAME ELEVATION")
                    failed_door_data.append("NONE")
                    failed_door_data.append(str(excel_worksheet.cell_value(row,9).lower()).upper())
                    failed_data.append(failed_door_data)
                    continue  

                door_frame_elevation = door.Symbol.LookupParameter("Frame_Elevation").AsValueString().lower()
                for row in range(1, excel_worksheet.nrows):
                    if door_room_type == excel_worksheet.cell_value(row,0).lower():
                        if not door_frame_elevation == str(excel_worksheet.cell_value(row,9).lower()):
                            failed_door_data.append(output.linkify(door.Id))
                            failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                            if door.LookupParameter("Level"):
                                failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                            else:
                                failed_door_data.append("NONE")
                            failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                            failed_door_data.append("INVALID FRAME ELEVATION")
                            failed_door_data.append(door_frame_elevation.upper())
                            failed_door_data.append(str(excel_worksheet.cell_value(row,9).lower()).upper())
                            failed_data.append(failed_door_data)
                            break

            # Print Reports
            if failed_data:
                output.print_md("##⚠️ {} Completed. Issues Found ☹️" .format(user_check)) # Markdown Heading 2
                output.print_md("---") # Markdown Line Break
                output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")  # Print a Line
                output.print_table(table_data=failed_data, columns=["ELEMENT ID", "MARK","LEVEL", "ROOM TYPE", "ERROR CODE", "CURRENT VALUE", "EXPECTED VALUE"]) # Print a Table
                print("\n\n")            
                output.print_md("---") # Markdown Line Break
            else:
                output.print_md("##✅ {} Completed. No Issues Found 😃" .format(user_check)) # Markdown Heading 2
                output.print_md("---") # Markdown Line Break

        if user_check == checks[9]: 
            manual_time = manual_time + 180
            total_element_count = total_element_count + len(door_collector)
            failed_data = []
            for door in door_collector:
                failed_door_data = []
                door_room_type = door.LookupParameter("Room_Type").AsString().lower()
                try:
                    if not door.Symbol.LookupParameter("Frame_Face_Finish").HasValue or door.Symbol.LookupParameter("Frame_Face_Finish") == "":
                        failed_door_data.append(output.linkify(door.Id))
                        failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                        if door.LookupParameter("Level"):
                            failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                        else:
                            failed_door_data.append("NONE")
                        failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                        failed_door_data.append("INVALID FRAME FINISH")
                        failed_door_data.append("NONE")
                        failed_door_data.append(str(excel_worksheet.cell_value(row,10).lower()).upper())
                        failed_data.append(failed_door_data)
                        continue  
                except:
                    failed_door_data.append(output.linkify(door.Id))
                    failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                    if door.LookupParameter("Level"):
                        failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                    else:
                        failed_door_data.append("NONE")
                    failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                    failed_door_data.append("INVALID FRAME FINISH")
                    failed_door_data.append("NONE")
                    failed_door_data.append(str(excel_worksheet.cell_value(row,10).lower()).upper())
                    failed_data.append(failed_door_data)
                    continue  
                door_frame_finish = door.Symbol.LookupParameter("Frame_Face_Finish").AsValueString().lower()
                for row in range(1, excel_worksheet.nrows):
                    if door_room_type == excel_worksheet.cell_value(row,0).lower():
                        if not door_frame_finish == str(excel_worksheet.cell_value(row,10).lower()):
                            failed_door_data.append(output.linkify(door.Id))
                            failed_door_data.append(door.LookupParameter("Mark").AsValueString().upper())
                            if door.LookupParameter("Level"):
                                failed_door_data.append(door.LookupParameter("Level").AsValueString().upper())
                            else:
                                failed_door_data.append("NONE")
                            failed_door_data.append(door.LookupParameter("Room_Type").AsString().upper())
                            failed_door_data.append("INVALID FRAME FINISH")
                            failed_door_data.append(door_frame_finish.upper())
                            failed_door_data.append(str(excel_worksheet.cell_value(row,10).lower()).upper())
                            failed_data.append(failed_door_data)
                            break

            # Print Reports
            if failed_data:
                output.print_md("##⚠️ {} Completed. Issues Found ☹️" .format(user_check)) # Markdown Heading 2
                output.print_md("---") # Markdown Line Break
                output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")  # Print a Line
                output.print_table(table_data=failed_data, columns=["ELEMENT ID", "MARK","LEVEL", "ROOM TYPE", "ERROR CODE", "CURRENT VALUE", "EXPECTED VALUE"]) # Print a Table
                print("\n\n")            
                output.print_md("---") # Markdown Line Break
            else:
                output.print_md("##✅ {} Completed. No Issues Found 😃" .format(user_check)) # Markdown Heading 2
                output.print_md("---") # Markdown Line Break


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