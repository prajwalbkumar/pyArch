# -*- coding: utf-8 -*-
'''Create Worksets'''
__title__ = "Create Worksets"
__author__ = "prajwalbkumar - prakritisrimal"


# Import Libraries
from Autodesk.Revit.DB import *
from Autodesk.Revit.ApplicationServices import *
from Autodesk.Revit.UI import UIDocument, TaskDialog, TaskDialogCommonButtons
from pyrevit import revit, forms, script
import csv
import os
import math
import time
from datetime import datetime
from Extract.RunData import get_run_data
from Autodesk.Revit.DB import WorksharingUtils
from System.Collections.Generic import List


# Record the start time
start_time = time.time()
manual_time = 300

script_dir = os.path.dirname(__file__)
ui_doc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document  # Get the Active Document
app = __revit__.Application  # Returns the Revit Application Object
rvt_year = int(app.VersionNumber)
output = script.get_output()


# Read all the Rows from the CSV Files as Lists
def readfile(selected_option):

    if selected_option == 'DAR':
        trade_ops = ['Architecture', 'Interior', 'Signage']
        selected_trade_option = forms.SelectFromList.show (
        trade_ops,
        multiselect=False, width=300, height=300,
        title='Select the discipline for which the worksets have to be created',
        default=trade_ops[0])  # Optionally, set a default selection  

        if selected_trade_option == trade_ops[0]:
            csv_filename = "WorksetLists_ARCHITECTURE.csv"
            source_file = os.path.join(script_dir, csv_filename)
        
        elif selected_trade_option == trade_ops[1]:
            csv_filename = "WorksetLists_INTERIOR.csv"
            source_file = os.path.join(script_dir, csv_filename)

        elif selected_trade_option == trade_ops[2]:
            csv_filename = "WorksetLists_SIGNAGE.csv"
            source_file = os.path.join(script_dir, csv_filename)

        if not selected_trade_option:
            script.exit()
    
    elif selected_option == "NEOM":
        csv_filename = "WorksetLists_NEOM.csv"
        source_file = os.path.join(script_dir, csv_filename)

    elif selected_option == "DAEP":
        trade_ops = ['Architecture', 'Interior', 'Signage']
        selected_trade_option = forms.SelectFromList.show (
        trade_ops,
        multiselect=False, width=300, height=300,
        title='Select the discipline for which the worksets have to be created',
        default=trade_ops[0])  # Optionally, set a default selection  

        if selected_trade_option == trade_ops[0]:
            csv_filename = "WorksetLists_ARCHITECTURE_DAEP.csv"
            source_file = os.path.join(script_dir, csv_filename)
        
        elif selected_trade_option == trade_ops[1]:
            csv_filename = "WorksetLists_INTERIOR_DAEP.csv"
            source_file = os.path.join(script_dir, csv_filename)

        elif selected_trade_option == trade_ops[2]:
            csv_filename = "WorksetLists_SIGNAGE_DAEP.csv"
            source_file = os.path.join(script_dir, csv_filename)

        if not selected_trade_option:
            script.exit()         

    with open(source_file) as csvfile: 
        reader = csv.DictReader(csvfile) 
        workset_names = []

        for row in reader:
            workset_names.append(row["Worksets"])
    return workset_names

# Create Worksets from the List
def create_worksets(doc, workset_names):
    counter = 0
    for name in workset_names:
        if WorksetTable.IsWorksetNameUnique(doc, name):
            Workset.Create(doc, name)
            counter += 1
    return counter


# Main Function
doc = __revit__.ActiveUIDocument.Document

if not doc.IsWorkshared:
    try:
        doc.EnableWorksharing("Shared Levels and Grids", "Scope Boxes")
    except:
        forms.alert("File not Workshared - Create a Workshared Model First!", title='Script Cancelled')
        script.exit()


# Prompt user for trade selection
ops = ['DAR', 'DAEP', 'NEOM']
selected_option = forms.SelectFromList.show(
    ops,
    multiselect=False, width=300, height=300,
    title='Select the standards as per which worksets should be created',
    default=ops[0]  # Optionally, set a default selection
)
if not selected_option:
    script.exit()


else:
    # Read the appropriate CSV file based on the selected trade
    workset_names = readfile(selected_option)

    if not workset_names:
        forms.alert("No worksets found for " + selected_option + ".", title="Script Cancelled")
        script.exit()

    # Create worksets within a transaction
    try:
        with Transaction(doc, 'Create Workset') as t:
            t.Start()
            count = create_worksets(doc, workset_names)
            t.Commit()

            # Record the end time
            end_time = time.time()
            runtime = end_time - start_time
            run_result = "Tool ran successfully"
            element_count = count
            error_occured = "Nil"
            get_run_data(__title__, runtime, element_count, manual_time, run_result, error_occured)

    except Exception as e:
        print ('Error moving elements to workset: {}'.format(e))
        # Record the end time and runtime
        end_time = time.time()
        runtime = end_time - start_time

        # Log the error details
        error_occured = "Error occurred: {}".format(str(e))
        run_result = "Error"
        element_count = count

        # Function to log run data in case of error
        get_run_data(__title__, runtime, element_count, manual_time, run_result, error_occured)

    # Display a message with the results
    message = str(count) + " Worksets Created for " + selected_option
    forms.alert(message, title="Script Completed", warn_icon=False)
