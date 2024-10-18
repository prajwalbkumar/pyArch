# -*- coding: utf-8 -*-
'''Phaser'''
__title__ = "Phaser"
__author__ = "prajwalbkumar"


# Imports
from Autodesk.Revit.DB import *
from pyrevit import forms, script
from System.Collections.Generic import List

ui_doc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # Get the Active Document
app = __revit__.Application # Returns the Revit Application Object
output = script.get_output()

import time
from datetime import datetime
from Extract.RunData import get_run_data

start_time = time.time()
manual_time = 0
total_element_count = 0

try:
    # MAIN
    selection = ui_doc.Selection.GetElementIds()
    selected_elements = []
    unowned_elements = []
    elements_to_checkout = List[ElementId]()

    if len(selection) > 0:

        for elementid in selection:
            elements_to_checkout.Add(elementid)
        
        if doc.IsWorkshared:
            WorksharingUtils.CheckoutElements(doc, elements_to_checkout)

            for elementid in selection:    
                worksharingStatus = WorksharingUtils.GetCheckoutStatus(doc, elementid)
                if not worksharingStatus == CheckoutStatus.OwnedByOtherUser:
                    selected_elements.append(doc.GetElement(elementid))
                else:
                    unowned_elements.append(doc.GetElement(elementid))
        else:
            for elementid in selection:    
                selected_elements.append(doc.GetElement(elementid))

        
    else:
        forms.alert("Select few elements first!", title = "Script Exiting", warn_icon = True)
        script.exit()    


    phase_category = forms.alert("Select Phase action", title = "Open Excel File", warn_icon = False, options=["Phase Constructed", "Phase Demolished"])

    if not phase_category:
        script.exit()


    all_phases = FilteredElementCollector(doc).OfClass(Phase)

    target_phases = []
    for phase in all_phases:
        target_phases.append(phase.Name)

    if phase_category == "Phase Demolished":
        target_phases.append("None")

    user_phase = forms.SelectFromList.show(target_phases, title="Select Relevent Phase", width=300, height=300, button_name="Select Phase", multiselect=False)

    if not user_phase:
        script.exit()


    for phase in all_phases:
        if user_phase == phase.Name:
            user_phase_id = phase.Id
            break
        if user_phase == "None":
            user_phase_id = ElementId(-1)


    t = Transaction(doc, "Update Phase")
    t.Start()

    manual_time = manual_time + 150
    total_element_count = total_element_count + len(selected_elements) 

    for element in selected_elements:
        if not element.HasPhases():
            continue

        else:
            if not element.ArePhasesModifiable():
                continue
            
            else:
                    if phase_category == "Phase Constructed":
                        if(element.IsCreatedPhaseOrderValid(user_phase_id)):
                            element.CreatedPhaseId = user_phase_id
                    else:
                        if element.IsDemolishedPhaseOrderValid(user_phase_id):
                            element.DemolishedPhaseId = user_phase_id

    t.Commit()

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