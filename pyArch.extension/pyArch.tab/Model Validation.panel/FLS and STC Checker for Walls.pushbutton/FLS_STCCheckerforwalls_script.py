# -*- coding: utf-8 -*-
'''FLS and STC Wall Type Checker'''
__title__ = "FLS and STC Checker for Walls"
__author__ = "prakritisrimal"

from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
output = script.get_output()

doc = revit.doc

def check_fls_stc_for_walls():
    walls =  DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
    if walls:
        for wall in walls:
            wall_name = wall.Name
            wall_type = wall.WallType
            if wall_type:
                compound_structure = wall_type.GetCompoundStructure()
                if compound_structure:
                    for layer in compound_structure.GetLayers():
                        material_id = layer.MaterialId
                        if material_id and material_id != ElementId.InvalidElementId:
                            material = doc.GetElement(material_id)
                            if material:
                                if any(keyword in material.Name for keyword in ['Concrete', 'Steel', 'ST']):






    
    