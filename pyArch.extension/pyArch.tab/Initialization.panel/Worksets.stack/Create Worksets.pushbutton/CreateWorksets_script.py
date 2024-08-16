# -*- coding: utf-8 -*-
'''Create Worksets'''
__title__ = "Create Worksets"
__author__ = "prajwalbkumar - prakritisrimal"


# Import Libraries
from Autodesk.Revit.DB import *
from Autodesk.Revit.ApplicationServices import *
from Autodesk.Revit.UI import UIDocument
from pyrevit import revit, forms, script
import csv

# Read all the Rows from the CSV Files as Lists
def readfile():
    source_file = forms.pick_file(file_ext ='csv')
    with open(source_file) as csvfile: 
        reader = csv.DictReader(csvfile) 
        workset_names = []

        for row in reader:
            print (row["Worksets"])
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
ops = ['ARCHITECTURE', 'INTERIOR', 'SIGNAGE', 'EXIT']
selected_option = forms.SelectFromList.show(
    ops,
    multiselect=False,
    title='Select the trade for which the worksets should be created',
    default=ops[0]  # Optionally, set a default selection
)

if not selected_option:
    print("Worksets are not created")
elif selected_option == 'EXIT':
    print("Worksets are not created")
else:
    # Read the appropriate CSV file based on the selected trade
    workset_names = readfile()

    if not workset_names:
        forms.alert("No worksets found for " + selected_option + ".", title="Script Cancelled")
        script.exit()

    # Create worksets within a transaction
    with revit.Transaction("Create Workset"):
        count = create_worksets(doc, workset_names)

    # Display a message with the results
    message = str(count) + " out of " + str(len(workset_names)) + " Worksets Created for " + selected_option
    forms.alert(message, title="Script Completed", warn_icon=False)
