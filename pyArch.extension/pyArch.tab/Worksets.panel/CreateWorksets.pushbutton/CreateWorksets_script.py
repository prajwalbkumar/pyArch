# Import Libraries
from Autodesk.Revit import DB
from pyrevit import revit
from pyrevit import forms, script
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
        if DB.WorksetTable.IsWorksetNameUnique(doc, name):
            workset = DB.Workset.Create(doc, name)
            counter = counter + 1
    return counter
            

# Main Function 
doc =__revit__.ActiveUIDocument.Document
if not doc.IsWorkshared:
    try:
        with revit.Transaction("Create Workshared Model"):
            doc.EnableWorksharing("Shared Grids and Levels", "Workset1")
    except:
        forms.alert("File not Workshared - Create a Workshared Model First!", title='Script Cancelled')
        script.exit()

    with revit.Transaction("Create Workset"):
        workset_names = readfile() # Import Worksets as a List from Excel in the Future
        create_worksets(doc, workset_names)
    
else:
    with revit.Transaction("Create Workset"):
        workset_names = readfile() # Import Worksets as a List from Excel in the Future
        count = create_worksets(doc, workset_names)


message = str(count) + " out of " + str(len(workset_names)) + " Worksets Created :)"
forms.alert(message, title = "Script Completed", warn_icon = False)

