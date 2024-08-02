# -*- coding: utf-8 -*-
'''Door Detective'''
__title__ = "Door Detective"
__author__ = "prajwalbkumar"

# Imports
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import UIDocument
from pyrevit import revit, forms, script
import xlrd

ui_doc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # Get the Active Document
output = script.get_output()


# MAIN SCRIPT
# Door - Room_Type Checks
door_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()

# Check if the Room_Type Parameter is added in the Document or not!
try:
    if door_collector[0].LookupParameter("Room_Type").AsString():
        pass
except:
    forms.alert("No Room_Type Parameter Found in Document\n\n"
                "Run the Add Room Type Parameter First!", title = "Script Exiting", warn_icon = True)
    script.exit()

# Check if the Room_Type Parameters are filled according to the Excel File. 
options = forms.alert("Select the Door Design Database Excel File", title = "Open Excel File", warn_icon = False, options=["Select File"])
if options == "Select File":
    excel_path =  forms.pick_excel_file()
    if not excel_path:
        script.exit()
else:
    script.exit()

excel_workbook = xlrd.open_workbook(excel_path)
excel_worksheet = excel_workbook.sheet_by_index(1)
excel_room_types = []
for row in range(1, excel_worksheet.nrows):
    excel_room_types.append(excel_worksheet.cell_value(row,0).lower())

failed_doors_message = []
for door in door_collector:
    if not door.LookupParameter("Room_Type").HasValue:
        failed_doors_message.append("Door with Element ID - {} does not have any Room_Type Parameter" .format(output.linkify(door.Id)))

    elif door.LookupParameter("Room_Type").AsString() == "":
        failed_doors_message.append("Door with Element ID - {} does not have any Room_Type Parameter" .format(output.linkify(door.Id)))
    
    else:
        if door.LookupParameter("Room_Type").AsString().lower() in excel_room_types:
            continue
        else:
            failed_doors_message.append("Door with Element ID - {} contains an incorrect Room_Type Parameter" .format(output.linkify(door.Id)))

if failed_doors_message:
    report = forms.alert("Doors must have a valid Room_Type Parameter.\n\n"
                "Set the Parameter as per the Design Database.\n"
                "Or Transfer the Values from Rooms to Doors using the Copy Room Type Data Tool", title="Room_Type Error", warn_icon=True, options=["Show Report"])
    if report == "Show Report":
        for line in failed_doors_message:
            print(line)
        script.exit()
    else:
        script.exit()


checks = ["No. of Leaves", "Leaf Width", "Leaf Height", "Undercut", "Leaf Material","Leaf Elevation", "Leaf Face Finish", "Frame Material", "Frame Elevation", "Frame Finish"]
user_check = forms.SelectFromList.show(checks, title="Select Door Check", width=300, height=500, button_name="Select Code", multiselect=False)

if not user_check:
    script.exit()     

if user_check == checks[0]: 
    door_error_message = []
    for door in door_collector:
        door_room_type = door.LookupParameter("Room_Type").AsString().lower()
        door_leaf_number = door.Symbol.LookupParameter("Leaf_Number").AsValueString()
        for row in range(1, excel_worksheet.nrows):
            if door_room_type == excel_worksheet.cell_value(row,0).lower():
                if not door_leaf_number == str(int(excel_worksheet.cell_value(row,1))):
                    door_error_message.append("Door with Element ID {} has invalid Leaf Number - Refer the Door Design Database" .format(output.linkify(door.Id)))
                    break
                else:
                    break


if user_check == checks[1]: 
    door_error_message = []
    for door in door_collector:
        door_room_type = door.LookupParameter("Room_Type").AsString().lower()
        door_width = door.Symbol.LookupParameter("Width").AsValueString()
        for row in range(1, excel_worksheet.nrows):
            if door_room_type == excel_worksheet.cell_value(row,0).lower():
                if not door_width == str(int(excel_worksheet.cell_value(row,2))):
                    door_error_message.append("Door with Element ID {} has invalid Width - Refer the Door Design Database" .format(output.linkify(door.Id)))
                    break
                else:
                    break

if user_check == checks[2]: 
    door_error_message = []
    for door in door_collector:
        door_room_type = door.LookupParameter("Room_Type").AsString().lower()
        door_height = door.Symbol.LookupParameter("Height").AsValueString()
        for row in range(1, excel_worksheet.nrows):
            if door_room_type == excel_worksheet.cell_value(row,0).lower():
                if not door_height == str(int(excel_worksheet.cell_value(row,3))):
                    door_error_message.append("Door with Element ID {} has invalid Height - Refer the Door Design Database" .format(output.linkify(door.Id)))
                    break
                else:
                    break

if user_check == checks[3]: 
    door_error_message = []
    for door in door_collector:
        door_room_type = door.LookupParameter("Room_Type").AsString().lower()
        door_undercut = door.Symbol.LookupParameter("Undercut").AsValueString()
        for row in range(1, excel_worksheet.nrows):
            if door_room_type == excel_worksheet.cell_value(row,0).lower():
                if not door_undercut == str(int(excel_worksheet.cell_value(row,4))):
                    door_error_message.append("Door with Element ID {} has invalid Undercut - Refer the Door Design Database" .format(output.linkify(door.Id)))
                    break
                else:
                    break

if user_check == checks[4]: 
    door_error_message = []
    for door in door_collector:
        door_room_type = door.LookupParameter("Room_Type").AsString().lower()
        door_leaf_material = door.Symbol.LookupParameter("Leaf_Material").AsValueString().lower()
        for row in range(1, excel_worksheet.nrows):
            if door_room_type == excel_worksheet.cell_value(row,0).lower():
                if not door_leaf_material == str(excel_worksheet.cell_value(row,5).lower()):
                    door_error_message.append("Door with Element ID {} has invalid Leaf Material - Refer the Door Design Database" .format(output.linkify(door.Id)))
                    break
                else:
                    break

if user_check == checks[5]: 
    door_error_message = []
    for door in door_collector:
        door_room_type = door.LookupParameter("Room_Type").AsString().lower()
        door_leaf_elevation = door.Symbol.LookupParameter("Leaf_Elevation").AsValueString().lower()
        for row in range(1, excel_worksheet.nrows):
            if door_room_type == excel_worksheet.cell_value(row,0).lower():
                if not door_leaf_elevation == str(excel_worksheet.cell_value(row,6).lower()):
                    door_error_message.append("Door with Element ID {} has invalid Leaf Elevation - Refer the Door Design Database" .format(output.linkify(door.Id)))
                    break
                else:
                    break

if user_check == checks[6]: 
    door_error_message = []
    for door in door_collector:
        door_room_type = door.LookupParameter("Room_Type").AsString().lower()
        door_leaf_face_finish = door.Symbol.LookupParameter("Leaf_Face_Finish").AsValueString().lower()
        for row in range(1, excel_worksheet.nrows):
            if door_room_type == excel_worksheet.cell_value(row,0).lower():
                if not door_leaf_face_finish == str(excel_worksheet.cell_value(row,7).lower()):
                    door_error_message.append("Door with Element ID {} has invalid Leaf Face Finish - Refer the Door Design Database" .format(output.linkify(door.Id)))
                    break
                else:
                    break

if user_check == checks[7]: 
    door_error_message = []
    for door in door_collector:
        door_room_type = door.LookupParameter("Room_Type").AsString().lower()
        door_frame_material = door.Symbol.LookupParameter("Frame_Material").AsValueString().lower()
        for row in range(1, excel_worksheet.nrows):
            if door_room_type == excel_worksheet.cell_value(row,0).lower():
                if not door_frame_material == str(excel_worksheet.cell_value(row,8).lower()):
                    door_error_message.append("Door with Element ID {} has invalid Leaf Frame Material - Refer the Door Design Database" .format(output.linkify(door.Id)))
                    break
                else:
                    break

if user_check == checks[8]: 
    door_error_message = []
    for door in door_collector:
        door_room_type = door.LookupParameter("Room_Type").AsString().lower()
        door_frame_elevation = door.Symbol.LookupParameter("Frame_Elevation").AsValueString().lower()
        for row in range(1, excel_worksheet.nrows):
            if door_room_type == excel_worksheet.cell_value(row,0).lower():
                if not door_frame_elevation == str(excel_worksheet.cell_value(row,9).lower()):
                    door_error_message.append("Door with Element ID {} has invalid Leaf Frame Elevation - Refer the Door Design Database" .format(output.linkify(door.Id)))
                    break
                else:
                    break

if user_check == checks[9]: 
    door_error_message = []
    for door in door_collector:
        door_room_type = door.LookupParameter("Room_Type").AsString().lower()
        door_frame_finish = door.Symbol.LookupParameter("Frame_Face_Finish").AsValueString().lower()
        for row in range(1, excel_worksheet.nrows):
            if door_room_type == excel_worksheet.cell_value(row,0).lower():
                if not door_frame_finish == str(excel_worksheet.cell_value(row,10).lower()):
                    door_error_message.append("Door with Element ID {} has invalid Leaf Frame Elevation - Refer the Door Design Database" .format(output.linkify(door.Id)))
                    break
                else:
                    break

if door_error_message:
    for line in door_error_message:
        print(line)