# -*- coding: utf-8 -*-
'''STC Rating Check'''
__title__ = "STC Rating Check"
__author__ = "prajwalbkumar"


# Imports
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import Selection, ObjectType, ISelectionFilter
from pyrevit import forms, script
import csv 
import os
from System.Collections.Generic import List

import time
from datetime import datetime
from Extract.RunData import get_run_data

start_time = time.time()
manual_time = 0
total_element_count = 0

ui_doc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # Get the Active Document
output = script.get_output()

# Definition to Get all the Door Instances in the Document
def doors_in_document():
    doors = (
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Doors)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    return doors

# Define a selection filter class for doors
class DoorSelectionFilter(ISelectionFilter):
    def AllowElement(self, element):
        if element.Category.Id.IntegerValue == int(BuiltInCategory.OST_Doors):
            return True
        return False
    
    def AllowReference(self, ref, point):
        return False
    
    
# MAIN SCRIPT
try:
    door_collector = []

    selection = ui_doc.Selection.GetElementIds()
    if len(selection) > 0:
        for id in selection:
            element = doc.GetElement(id)
            try:
                if element.LookupParameter("Category").AsValueString() == "Doors":
                    door_collector.append(element)
            except:
                continue

    else:
        #Custom selection 
        selection_options = forms.alert("This tool checks and updates door STC Ratings.",
                                        title="STC Rating Check - Select Doors", 
                                        warn_icon=False, 
                                        options=["Check All Doors", "Choose Specific Doors"])

        if not selection_options:
            script.exit()

        elif selection_options == "Check All Doors":
            door_collector = doors_in_document()

        else:
            # Prompt user to select doors
            try:
                choices = ui_doc.Selection
                selected_elements = choices.PickObjects(ObjectType.Element, DoorSelectionFilter(), "Select doors only")
                
                for selected_element in selected_elements:
                    door = doc.GetElement(selected_element.ElementId)
                    door_collector.append(door)

            except:
                script.exit()

    if not door_collector:
        forms.alert("No doors found in the active document", title="Script Exiting", warn_icon=True)
        script.exit()

    unowned_elements = []
    if doc.IsWorkshared:
        move_door_ids = []
        elements_to_checkout = List[ElementId]()

        for element in door_collector:
            elements_to_checkout.Add(element.Id)

        checkedout_door_collector = []

        WorksharingUtils.CheckoutElements(doc, elements_to_checkout)
        for element in door_collector: 
            worksharingStatus = WorksharingUtils.GetCheckoutStatus(doc, element.Id)
            if not worksharingStatus == CheckoutStatus.OwnedByOtherUser:
                checkedout_door_collector.append(element)
            else:
                unowned_elements.append(element)

        door_collector = checkedout_door_collector

    try:
        if door_collector[0].LookupParameter("STC_Rating").AsString():
            pass
    except:
        forms.alert("No STC_Rating Parameter Found in Document\n\n"
                    "Add all DAR Shared Parameters first", title = "Script Exiting", warn_icon = True)
        script.exit()

    # Check if all Doors have STC Rating. If Not:
    failed_doors = []
    manual_time = manual_time + 150
    total_element_count = total_element_count + len(door_collector) 

    for door in door_collector:
        door_rating_param = door.LookupParameter("STC_Rating")
        # door_mark_param = door.LookupParameter("Mark").AsString()

        if door_rating_param:
            hosted_wall_rating = door.Host.LookupParameter("STC_Rating")
            if hosted_wall_rating:
                if hosted_wall_rating.HasValue:
                    if hosted_wall_rating.AsString() == "" or hosted_wall_rating.AsString() == "0":
                        continue
                    else:
                        if door_rating_param.AsString() == str(int(int(hosted_wall_rating.AsString()) - 15)):
                            continue
                        else:
                            failed_doors.append(door)


    if failed_doors:
        report = forms.alert("Door STC ratings require attentions", title="Door STC Rating Missing", warn_icon=True, options=["Show Report","Auto-Fill Values"]) 
        failed_data = []

        for door in failed_doors:
                hosted_wall_rating = door.Host.LookupParameter("STC_Rating")
                if door.LookupParameter("Mark"):
                    if not door.LookupParameter("Mark").HasValue or door.LookupParameter("Mark").AsString() == "": 
                        door_mark = "NONE"
                    else:
                        door_mark = door.LookupParameter("Mark").AsString().upper()
                else:
                    door_mark = "NONE"

                if door.LookupParameter("Level"):
                    door_level = door.LookupParameter("Level").AsValueString().upper()
                else:
                    door_level = "NONE"

                if door.LookupParameter("Room_Name"):
                    if not door.LookupParameter("Room_Name").HasValue or door.LookupParameter("Room_Name").AsString() == "": 
                        door_room_name = "NONE"
                    else:
                        door_room_name = door.LookupParameter("Room_Name").AsString().upper()
                else:
                    door_room_name = "NONE"
                    
                if door.LookupParameter("Room_Number"):
                    if not door.LookupParameter("Room_Number").HasValue or door.LookupParameter("Room_Number").AsString() == "": 
                        door_room_number = "NONE"
                    else:
                        door_room_number = door.LookupParameter("Room_Number").AsString().upper()
                else:
                    door_room_number = "NONE"

                failed_data.append([output.linkify(door.Id), door_mark, door_level, door_room_name, door_room_number, hosted_wall_rating.AsString(), door.LookupParameter("STC_Rating").AsString(), str(int(int(hosted_wall_rating.AsString()) - 15))])

        if report == "Show Report":
            output.print_md("##⚠️ {} Completed. Instances Need Attention ☹️" .format(__title__)) # Markdown Heading 2
            output.print_md("---") # Markdown Line Break
            output.print_md("❌ Some issues could not be resolved. Refer to the **Table Report** below for reference")  # Print a Line
            output.print_table(table_data=failed_data, columns=["ELEMENT ID","MARK", "LEVEL", "ROOM NAME", "ROOM NUMBER", "HOST WALL RATING", "CURRENT RATING", "CORRECT RATING"]) # Print a Table
            print("\n\n")
            output.print_md("---") # Markdown Line Break

        if report =="Auto-Fill Values":
            t = Transaction(doc, "Filling Door STC Ratings")
            t.Start()
            for door in failed_doors:
                try:
                    wall = door.Host
                    wall_stc_param = wall.LookupParameter("STC_Rating").AsString()
                    door.LookupParameter("STC_Rating").Set(str(int(int(wall_stc_param)- 15)))
                except:
                    pass
            t.Commit()
            
            success_message = "STC Rating of " + str(len(failed_doors)) + " doors have been filled"
            success = forms.alert(success_message, title="Parameters Updated", warn_icon=False, options=["Show Report", "Ok"])

            if success == "Show Report":
                output.print_md("##✅ {} Completed. 😊" .format(__title__)) # Markdown Heading 2
                output.print_md("---") # Markdown Line Break
                output.print_md("✅ Door ratings have been updated. Refer to the **Table Report** below for reference")  # Print a Line
                output.print_table(table_data=failed_data, columns=["ELEMENT ID","MARK", "LEVEL", "ROOM NAME", "ROOM NUMBER", "HOST WALL RATING", "PREVIOUS RATING", "UPDATED RATING"]) # Print a Table
                print("\n\n")
                output.print_md("---") # Markdown Line Break

    elif not unowned_elements:
        forms.alert("All door ratings correct", title="Door Rating Check", warn_icon=False) 

    if unowned_elements:
        unowned_element_data = []
        for element in unowned_elements:
            try:
                unowned_element_data.append([output.linkify(element.Id), element.Category.Name.upper(), "REQUEST OWNERSHIP", WorksharingUtils.GetWorksharingTooltipInfo(doc, element.Id).Owner])
            except:
                pass

        output.print_md("##⚠️ Elements Skipped ☹️") # Markdown Heading 2
        output.print_md("---") # Markdown Line Break
        output.print_md("❌ Make sure you have Ownership of the Elements - Request access. Refer to the **Table Report** below for reference")  # Print a Line
        output.print_table(table_data = unowned_element_data, columns=["ELEMENT ID", "CATEGORY", "TO-DO", "CURRENT OWNER"]) # Print a Table
        print("\n\n")
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

    forms.alert(
        "An error has occurred.\n"
        "Please reach out to the author.\n\n"
        "Author - {}.".format(__author__),
        title="{} - Script Terminated".format(__title__),
        warn_icon=True
    )