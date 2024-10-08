# -*- coding: utf-8 -*-
'''DAR Startup'''
__title__ = "DAR Startup"
__author__ = "prajwalbkumar"

# Imports
from Autodesk.Revit.DB import *
from Autodesk.Revit.ApplicationServices import *
from Autodesk.Revit.UI import UIDocument
from pyrevit import revit, forms, script
import os

ui_doc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # Get the Active Document
output = script.get_output()
app = __revit__.Application # Returns the Revit Application Object
rvt_year = int(app.VersionNumber)

if rvt_year == 2023:
    template_path = r"K:\BIM\2023\Revit\Dar\Templates\AR_Template_Dar_R23.rte"

elif rvt_year == 2022:
    template_path = r"K:\BIM\2022\Revit\Dar\Templates\AR_Template_Dar_R22.rte"


# Creating a new Document
new_document = app.NewProjectDocument(template_path)

# Create a Workshared Model
new_document.EnableWorksharing("Shared Levels and Grids", "Z_Link_URS")

# Prompt user to select a destination folder

input = forms.alert("Select Location to Save File", title = "Select Folder", warn_icon=True, options= ["Browse Folder Location"])

if input:
    save_folder = forms.pick_folder(title="Select Destination Folder")

if not input:
    forms.alert("No folder selected. Exiting the script.", title = "File Not Created", warn_icon=True)
    script.exit()

if not save_folder:
    forms.alert("No folder selected. Exiting the script.", title = "File Not Created", warn_icon=True)
    script.exit()
    

# Prompt user to input the project file name
file_name = forms.ask_for_string(
    title="Enter Revit File Name",
    prompt="Refer to the BIM Manual - N:\BIM-AUTOMATION\Documents\BIM Manual.pdf\n\n"
    "Example Name: SH22XXX-01XXD-DAR-AL-AL-M3-AR-0001.rvt \n\n"
    "PRJ     - Project Number\n"
    "ORG     - Organization\n"
    "FUN     - Functional Breakdown\n"
    "SPA     - Spatial Breakdown\n"
    "FRM     - Form\n"
    "DSC     - Discipline\n"
    "NUM     - Number\n\n"
    "Revit File Name", 
    default="PRJ-ORG-FUN-SPA-FRM-DSC-NUM"
)

if not file_name:
    forms.alert("No project name entered. Exiting the script.", title = "File Not Created", warn_icon=True)
    script.exit()

# Set the save path for the new project file
save_path = os.path.join(save_folder, file_name + ".rvt")

# Save the newly created document
save_options = SaveAsOptions()
worksharing_save_option = WorksharingSaveAsOptions()
worksharing_save_option.SaveAsCentral = True

save_options.SetWorksharingOptions(worksharing_save_option)
save_options.OverwriteExistingFile = True  # If you want to allow overwriting an existing file

new_document.SaveAs(save_path, save_options)

# Open and activate the saved document
ui_doc.Application.OpenAndActivateDocument(save_path)

# Give final prompt
forms.alert("New Project File Created", title = "File Created", warn_icon=False)

