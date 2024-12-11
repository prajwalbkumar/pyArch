# -*- coding: utf-8 -*-
'''Insert Worksets'''
__title__ = "Insert Worksets"
__author__ = "prakritisrimal"

from pyrevit import forms, revit, script
from Autodesk.Revit.DB import *
from Autodesk.Revit.Exceptions import InvalidOperationException
# Imports
import math
import os
import time
from datetime import datetime
from Extract.RunData import get_run_data
from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
from Autodesk.Revit.DB import WorksharingUtils
from System.Collections.Generic import List
from Autodesk.Revit.UI import TaskDialog, TaskDialogCommonButtons

# Record the start time
start_time = time.time()
manual_time = 10

script_dir = os.path.dirname(__file__)
ui_doc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document  # Get the Active Document
app = __revit__.Application  # Returns the Revit Application Object
rvt_year = int(app.VersionNumber)
output = script.get_output()

# Check if the document is workshared
worksharing_enabled = doc.IsWorkshared

if worksharing_enabled:
    a = forms.ask_for_string(default='Enter the name', 
                             prompt="To create a Workset as per DAR Standards, refer to the BIM Manual - N:\BIM-AUTOMATION\Documents\BIM Manual.pdf\n\n"
                                "To create a Workset for Architecture discipline, start with 'AR_' \n"
                                "To create a Workset for Interior discipline, start with 'AI_' \n"
                                "To create a Workset for Signage discipline, start with 'AG_' \n"
                                "To create a Workset for Links, start with 'Z_Link_'\n", title='Workset Name')

    if not a:
        #forms.alert('Enter a proper workset name', title='Invalid Workset Name')
        script.exit()
    else:
        Ws = FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset).ToWorksets()
        Exw = [i.Name for i in Ws]

        if a in Exw:
            forms.alert('Workset already exists', title='Duplicate Workset Name')
        else:
            t = Transaction(doc, "Create Workset")
            try:
                t.Start()
                Workset.Create(doc, a)
                t.Commit()
                # Record the end time
                end_time = time.time()
                runtime = end_time - start_time
                run_result = "Tool ran successfully"
                element_count = 1 if a else 0
                error_occured = "Nil"
                get_run_data(__title__, runtime, element_count, manual_time, run_result, error_occured)



                message = 'Workset "' + a + '" created successfully'
                forms.alert(message, title="Script Completed", warn_icon=False)

            except Exception as e:
                print ('Error moving elements to workset: {}'.format(e))
                # Record the end time and runtime
                end_time = time.time()
                runtime = end_time - start_time

                # Log the error details
                error_occured = "Error occurred: {}".format(str(e))
                run_result = "Error"
                element_count = 1

                # Function to log run data in case of error
                get_run_data(__title__, runtime, element_count, manual_time, run_result, error_occured)
                t.RollBack()
                message = "An unexpected error occurred: " + str(e)
                forms.alert(message, title="Error")
else:
    forms.alert("File not Workshared - Create a Workshared Model First!", title='Script Cancelled')
    script.exit()

