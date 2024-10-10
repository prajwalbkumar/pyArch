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

script_dir = os.path.dirname(__file__)
ui_doc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # Get the Active Document
app = __revit__.Application # Returns the Revit Application Object
rvt_year = int(app.VersionNumber)
output = script.get_output()

# MAIN
all_rooms = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()

if not all_rooms:
    forms.alert("No rooms in the document", title = "Script Exiting", warn_icon=False)
    script.exit()

not_placed_room_id = []
not_enclosed_room_id = []

for room in all_rooms:
    if room.Area == 0:
        if not room.Location:
            not_placed_room_id.append(room.Id)
        else:
            not_enclosed_room_id.append(room.Id)

unowned_elements = []
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


not_enclosed_rooms = []
elements_to_checkout = List[ElementId]()

for elementid in not_enclosed_room_id:
    elements_to_checkout.Add(elementid)

WorksharingUtils.CheckoutElements(doc, elements_to_checkout)
for elementid in not_enclosed_room_id:  
    worksharingStatus = WorksharingUtils.GetCheckoutStatus(doc, elementid)
    if not worksharingStatus == CheckoutStatus.OwnedByOtherUser:
        not_enclosed_rooms.append(doc.GetElement(elementid))
    else:
        unowned_elements.append(doc.GetElement(elementid))

input1 = ""
input2 = ""

print(not_placed_rooms)
print(not_enclosed_rooms)

if not_placed_rooms:
    input1 = forms.alert("There are NOT PLACED rooms in the model \n"
                        "Would you like to delete them?", title = "Delete Rooms", warn_icon = True, options = ["Ok", "No"])

if not_enclosed_rooms:
    input2 = forms.alert("There are NOT ENCLOSED rooms in the model \n"
                        "Would you like to delete them?", title = "Delete Rooms", warn_icon = True, options = ["Ok", "Show Report"])

if input2 == "Show Report":
    failed_data = []
    for room in not_enclosed_rooms:
        failed_data.append([output.linkify(room.Id),room.Level.Name.upper(),room.LookupParameter("Name").AsString().upper(),room.LookupParameter("Number").AsString().upper()])
        
    output.print_md("##⚠️ Not Enclosed Rooms Found ☹️") # Markdown Heading 2
    output.print_md("---") # Markdown Line Break
    output.print_md("❌ There are Issues in your Model.")  # Print a Line
    output.print_table(table_data=failed_data, columns=["ELEMENT ID","LEVEL", "ROOM NAME", "ROOM NUMBER"]) # Print a Table
    output.print_md("---") # Markdown Line Break

count = 0


if input1 == "Ok":
    t = Transaction(doc, "Delete Not Placed Rooms")
    t.Start()
    for room in not_placed_rooms:
        count += 1
        doc.Delete(room.Id)
    t.Commit()

if input2 == "Ok":
    t = Transaction(doc, "Delete Not Enclosed Rooms")
    t.Start()
    for room in not_enclosed_rooms:
        count += 1
        doc.Delete(room.Id)
    t.Commit()

print(count)
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