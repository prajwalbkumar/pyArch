# -*- coding: utf-8 -*-
'''Delete Rooms'''
__title__ = "Delete Rooms"
__author__ = "prajwalbkumar"

# Imports
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import UIDocument
from pyrevit import revit, forms, script
import os
from System.Collections.Generic import List

import time
from datetime import datetime
from Extract.RunData import get_run_data

start_time = time.time()
manual_time = 0
total_element_count = 0

script_dir = os.path.dirname(__file__)
ui_doc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # Get the Active Document
app = __revit__.Application # Returns the Revit Application Object
rvt_year = int(app.VersionNumber)
output = script.get_output()

try:
    # MAIN
    all_rooms = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()

    if not all_rooms:
        forms.alert("No rooms in the document", title = "Script Exiting", warn_icon=False)
        script.exit()

    not_placed_room_id = []

    manual_time = manual_time + 600
    total_element_count = total_element_count + len(all_rooms) 

    for room in all_rooms:
        if room.Area == 0:
            if not room.Location:
                not_placed_room_id.append(room.Id)

    unowned_elements = []

    if doc.IsWorkshared:
        not_placed_rooms = []
        elements_to_checkout = List[ElementId]()

        for elementid in not_placed_room_id:
            elements_to_checkout.Add(elementid)

        WorksharingUtils.CheckoutElements(doc, elements_to_checkout)
        for elementid in not_placed_room_id: 
            worksharingStatus = WorksharingUtils.GetCheckoutStatus(doc, elementid)
            if not worksharingStatus == CheckoutStatus.OwnedByOtherUser:
                not_placed_rooms.append(doc.GetElement(elementid))
            else:
                unowned_elements.append(doc.GetElement(elementid))

    else:
        not_placed_rooms = []
        for elementid in not_placed_room_id: 
            not_placed_rooms.append(doc.GetElement(elementid))
            
    count = 0
    if not_placed_rooms:
        t = Transaction(doc, "Delete Not Placed Rooms")
        t.Start()
        for room in not_placed_rooms:
            count += 1
            doc.Delete(room.Id)
        t.Commit()

    if count:
        forms.alert("{} Room(s) have been deleted" .format(count), title = "Rooms Deleted", warn_icon = False)
    if not count:
        forms.alert("No Rooms Deleted", title = "Run Successful", warn_icon = False)

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