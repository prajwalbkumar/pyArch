# -*- coding: utf-8 -*-
'''FLS Doors Validator'''
__title__ = "Fire Rating Checks"
__author__ = "prajwalbkumar"


# Imports
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import UIDocument
from pyrevit import revit, forms, script

script_dir = os.path.dirname(__file__)
ui_doc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # Get the Active Document

# MAIN SCRIPT

# Option to Select Fire or Acosutic