

from pyrevit import script
from pyrevit import forms
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, BuiltInParameter, Wall, Level, Transaction, RevitLinkInstance, ElementId

def get_floor_thickness_from_linked_file(linked_doc, level):
    floors = FilteredElementCollector(linked_doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElements()
    for floor in floors:
        floor_level_id = floor.get_Parameter(BuiltInParameter.LEVEL_PARAM).AsElementId()
        floor_level = linked_doc.GetElement(floor_level_id)
        #print("Floor level elevation: {}".format(floor_level.Elevation))
        #print("Level elevation: {}".format(level.Elevation))
        if floor_level.Elevation == level.Elevation:
            floor_type = linked_doc.GetElement(floor.GetTypeId())
            #print("Floor type: {}".format(floor_type.LookupParameter("Type Name").AsString()))
            thickness = floor_type.GetCompoundStructure().GetWidth()
            #print("Floor thickness: {}".format(thickness))
            return thickness
    #print("No matching floor thickness found")
    return None

def filter_concrete_levels(levels):
    concrete_levels = [level for level in levels if "CL" in level.LookupParameter("Name").AsString()]
    return concrete_levels

def find_next_concrete_level(base_level, concrete_levels):
    next_concrete_level = next((cl for cl in concrete_levels if cl.Elevation > base_level.Elevation), None)
    return next_concrete_level

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

walls = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()

# Prompt user to select a linked model
linked_files = FilteredElementCollector(doc).OfClass(RevitLinkInstance).ToElements()
linked_file_names = [link.Name for link in linked_files]
selected_link_name = forms.SelectFromList.show(linked_file_names, title='Select Linked Model', button_name='Select')


# Get the selected linked document
selected_link = None
for link in linked_files:
    if link.Name == selected_link_name:
        selected_link = link
        break

if not selected_link:
    forms.alert("No linked file selected or file not found.")
    script.exit()

linked_doc = selected_link.GetLinkDocument()

levels = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
concrete_levels = filter_concrete_levels(levels)
sorted_concrete_levels = sorted(concrete_levels, key=lambda lvl: lvl.Elevation)

with Transaction(doc, "Align Wall Top Constraint and Set Offset") as t:
    t.Start()
    for wall in walls:
        base_level_id = wall.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT).AsElementId()
        base_level = doc.GetElement(base_level_id)

        if not base_level:
            print("Base level not found for wall ID: {}".format(wall.Id.IntegerValue))
            continue

        next_concrete_level = find_next_concrete_level(base_level, sorted_concrete_levels)

        if next_concrete_level:
            wall.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).Set(next_concrete_level.Id)

            floor_thickness = get_floor_thickness_from_linked_file(linked_doc, next_concrete_level)
            if floor_thickness:
                wall.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET).Set(-floor_thickness)
            else:
                print("No floor thickness found for level: {}".format(next_concrete_level.LookupParameter("Name").AsString()))
        else:
            print("No next concrete level found for wall ID: {}".format(wall.Id.IntegerValue))

    t.Commit()
forms.alert("Script complete!")