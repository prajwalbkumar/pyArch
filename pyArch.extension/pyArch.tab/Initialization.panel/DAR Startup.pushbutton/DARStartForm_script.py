# -*- coding: utf-8 -*-
'''Create a new file'''
__Title__ = "Create a new file"
__author__ = "prajwalbkumar, romaramnani"

import clr
import os
import System
import time

clr.AddReference("RevitAPI")
from Autodesk.Revit.DB import *
import Autodesk.Revit.DB as DB
from Autodesk.Revit.DB  import WorksharingUtils, RelinquishOptions
from datetime           import datetime
from Extract.RunData    import get_run_data
from pyrevit            import forms, script

# XAML WPF
clr.AddReference('PresentationFramework')
clr.AddReference('PresentationCore')
clr.AddReference('WindowsBase')
clr.AddReference("System.Windows.Forms")
clr.AddReference('System.Windows')
from System.Windows.Forms import FolderBrowserDialog, DialogResult

PATH_SCRIPT = os.path.dirname(__file__)
app = __revit__.Application
ui_doc = __revit__.ActiveUIDocument
other_doc= ui_doc.Document
other_file_path = other_doc.PathName

class NewModel:
    def __init__(self):
        self.TextBoxList = ['PRJNUM', 'ORG', 'FUN', 'SPA', 'FOR', 'DIS', 'NUM']

        # Path to the XAML file
        path_xaml_file = os.path.join(PATH_SCRIPT, 'DARStartup.xaml')

        # Load the XAML window
        self.window = forms.WPFWindow(path_xaml_file)
        
        # Access the TextBox from the XAML file
        self.FolderPath = self.window.FindName('FolderPath')

        # Access the BrowseButton from the XAML file and bind the click event
        browse_button = self.window.FindName('BrowseButton')
        browse_button.Click += self.browse_folder_click

        self.window.DataContext = self

        # Populate text boxes with initial values
        self.populate_textboxes()

        # Access the SubmitButton and bind the click event
        submit_button = self.window.FindName('CreateButton')
        submit_button.Click += self.submit_button_click

        #hyperlink = self.window.FindName("Hyperlink")
        #hyperlink.RequestNavigate += self.hyperlink_request_navigate

        # Show the form
        self.window.ShowDialog()

    def browse_for_folder(self):
        dialog = FolderBrowserDialog()
        dialog.SelectedPath = "P:\\"  # Set the initial directory to P:\
        if dialog.ShowDialog() == DialogResult.OK:
            return dialog.SelectedPath
        return None

    def browse_folder_click(self, sender, e):
        folder_path = self.browse_for_folder()
        if folder_path:
            self.FolderPath.Text = folder_path

    def get_textbox_values(self):
        values = []
        wrap_panel = self.window.FindName('WrapPanelTextBoxes')
        if wrap_panel:
            for i in range(7):
                text_box = wrap_panel.FindName('TextBox{}'.format(i))
                if text_box:
                    #print("TextBox[{}]: {}".format(i, text_box.Text))
                    values.append(text_box.Text)
                else:
                    print("TextBox[{}] not found".format(i))
        else:
            print("WrapPanelTextBoxes not found")
        return values

    def populate_textboxes(self):
        wrap_panel = self.window.FindName('WrapPanelTextBoxes')
        if wrap_panel:
            for i in range(7):
                textbox = wrap_panel.FindName('TextBox{}'.format(i))
                if textbox:
                    textbox.TextChanged += self.on_textbox_text_changed
                else:
                    print("TextBox {} not found during populate.".format(i))

    def folderpath_text_changed(self, sender, event):
        project_name = self.window.FindName("ProjectName")
        if project_name:
            project_name.Visibility = System.Windows.Visibility.Visible if sender.Text else System.Windows.Visibility.Collapsed

    def on_textbox_text_changed(self, sender, e):
        wrap_panel = self.window.FindName('WrapPanelTextBoxes')
        if wrap_panel:
            for i in range(7):
                textbox = wrap_panel.FindName('TextBox{}'.format(i))
                if textbox and textbox == sender:
                    self.TextBoxList[i] = textbox.Text
                    #print("Updated TextBoxList[{}] to: {}".format(i, textbox.Text))
                    break

    def submit_button_click(self, sender, e):
        self.textbox_values = self.get_textbox_values()
        self.project_name = self.window.FindName('P_Name')
        self.project_address = self.window.FindName('P_Address')
        self.client_name = self.window.FindName('C_Name')  
        self.building_name = self.window.FindName('B_Name') 
        self.window.Close()
        #print('Retrieved values:', self.textbox_values)
    
    #def on_closing(self, sender, e):
    #    sys.exit(0)

output = script.get_output()
rvt_year = int(app.VersionNumber)

if rvt_year == 2023:
    template_path = r"K:\BIM\2023\Revit\Dar\Templates\AR_Template_Dar_R23.rte"

elif rvt_year == 2022:
    template_path = r"K:\BIM\2022\Revit\Dar\Templates\AR_Template_Dar_R22.rte"

# Run the UI
UI = NewModel()
project_data = UI.window.DataContext

# Record the start time
start_time = time.time()
manual_time = 500 
if UI.FolderPath.Text == 'P:\\':
    forms.alert('Project folder path not entered.')
    script.exit()

if not UI.textbox_values[0]:
    forms.alert('Project number not entered.')
    script.exit()

if not UI.textbox_values[2]:
    forms.alert('Building code not entered.')
    script.exit()

if not UI.textbox_values[5]:
    forms.alert('Discipline code not entered.')
    script.exit()

if not UI.FolderPath and not UI.FolderPath.Text:
    forms.alert('No folder selected.')
    script.exit()

file_name = '-'.join(UI.textbox_values) + ".rvt"
if not file_name:
    forms.alert("No project name entered. Exiting the script.", title = "File Not Created", warn_icon=True)
    script.exit()

def show_yes_no_dialog():
    result = forms.alert(
        msg="The file already exists. Do you want to replace it?",
        title="File Exists",
        yes=True,
        no=True
    )
    return result

def check_and_handle_file(folder_path, file_name):
        save_path = os.path.join(folder_path, file_name)
        if os.path.isfile(save_path):
            result = forms.alert(msg="The file already exists. Do you want to replace it?",
                                title="File Exists",
                                yes=True,
                                no=True)
            if result:
                return save_path  # Replace the file
            else:
                new_file_name = forms.ask_for_string(title="Enter Revit File Name", default="PRJ-ORG-FUN-SPA-FRM-DSC-NUM") + ".rvt"
                if new_file_name:
                    return os.path.join(folder_path, new_file_name)
                else:
                    return None  # User cancelled the operation
        else:
            return save_path
        
if UI.FolderPath and file_name:
    save_path = check_and_handle_file(UI.FolderPath.Text, file_name)
    #print("Save path:", save_path)
else:
    print("Invalid folder path or file name")
    script.exit()

# Creating a new Document
new_document = app.NewProjectDocument(template_path)

# Create a Workshared Model
new_document.EnableWorksharing("Shared Levels and Grids", "Scope Boxes")

# Save the newly created document
save_options = SaveAsOptions()
worksharing_save_option = WorksharingSaveAsOptions()
worksharing_save_option.SaveAsCentral = True

save_options.SetWorksharingOptions(worksharing_save_option)
save_options.OverwriteExistingFile = True  # If you want to allow overwriting an existing file

new_document.SaveAs(save_path, save_options)

# Open and activate the saved document
ui_doc.Application.OpenAndActivateDocument(save_path)

def update_landing_parameter():
    try:
        ui_doc1 = __revit__.ActiveUIDocument
        doc = ui_doc1.Document  

        t = Transaction(doc, "Fill Project Info")
        t.Start()
        
        project_info = doc.ProjectInformation
        param1 = project_info.get_Parameter(BuiltInParameter.PROJECT_NAME)
        if param1:
            if UI.project_name.Text:
                param1.Set(UI.project_name.Text)
            else:
                pass
        param2 = project_info.get_Parameter(BuiltInParameter.PROJECT_NUMBER)
        if param2:
            param2.Set(UI.textbox_values[0])
        param3 = project_info.get_Parameter(BuiltInParameter.PROJECT_ADDRESS)
        if param3:
            if UI.project_address.Text:
                param3.Set(UI.project_address.Text)
            else:
                pass
            
        param4 = project_info.get_Parameter(BuiltInParameter.CLIENT_NAME)
        if param4:
            if UI.client_name.Text:
                param4.Set(UI.client_name.Text)
            else:
                pass

        sheet_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
        if sheet_collector:
            for sheet in sheet_collector:
                param5 = sheet.LookupParameter("Building_Code")
                if param5:
                    param5.Set(UI.textbox_values[2])
                param6 = sheet.LookupParameter("Building_Name")
                if param6:
                    if UI.building_name.Text:
                        param6.Set(UI.building_name.Text)
                    else: 
                        pass
                param7 = sheet.LookupParameter("Discipline")
                if param7:
                    param7.Set(UI.textbox_values[5])

        t.Commit()
        
        options = RelinquishOptions(True)
        transact_options = TransactWithCentralOptions()

        WorksharingUtils.RelinquishOwnership(doc, options, transact_options)
        doc.Save()

        ui_doc.Application.OpenAndActivateDocument(other_file_path)
        doc.Close(saveModified=True)

        #DB.Document.Save(doc)
        #DB.Document.Close(doc)
        ui_doc.Application.OpenAndActivateDocument(save_path)

        # Give final prompt
        forms.alert("New Project File Created", title = "File Created", warn_icon=False)

        # Record the end time
        end_time = time.time()
        runtime = end_time - start_time
                
        run_result = "Tool ran successfully"
    
        element_count = 1

        error_occured ="Nil"

        get_run_data(__Title__, runtime, element_count, manual_time, run_result, error_occured)
        raise ValueError("Simulated error for testing purposes.")

    except Exception as e:
       
        t.RollBack()

        print("Error occurred: {}".format(str(e)))
        
        # Record the end time
        end_time = time.time()
        runtime = end_time - start_time

        error_occured = ("Error occurred: ", str(e))    
        run_result = "Error"
        element_count = 0
        
        get_run_data(__Title__, runtime, element_count, manual_time, run_result, error_occured)

update_landing_parameter()
