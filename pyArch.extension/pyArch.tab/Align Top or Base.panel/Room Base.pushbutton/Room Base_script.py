import pyrevit
from pyrevit import revit, DB

# Get the active document
doc = revit.doc

try:
    # Start a transaction to commit changes to the Revit database
    t = DB.Transaction(doc, "Move rooms to FFL")
    t.Start()

    # Get all rooms in the document
    rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).ToElements()

    # Get all levels in the document
    levels = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Levels).ToElements()

    # Create a dictionary to map level names to level elements
    level_map = {level.Name: level for level in levels}

    print("Found {} rooms and {} levels in the document".format(len(rooms), len(levels)))

    # Find the levels for CL and FFL
    cl_level = level_map.get("CL")
    ffl_level = level_map.get("FFL")

    if not cl_level:
        print("No level named 'CL' found")
    if not ffl_level:
        print("No level named 'FFL' found")

    # Loop through each room
    for room in rooms:
        print("Processing room {}".format(room.Number))  # Use room.Number for identification

        # Get the level of the room
        current_level = room.Level
        if current_level and current_level.Id == cl_level.Id:
            print("Room is on CL level")

            # Find the corresponding room on FFL level
            # Note: this assumes there is a one-to-one correspondence between rooms on different levels
            ffl_room = next((r for r in rooms if r.Level.Id == ffl_level.Id and r.Number == room.Number), None)
            if ffl_room:
                print("Found corresponding room on FFL level")
                # Change the level of the room
                room.Level = ffl_level
                print("Moved room {} from CL to FFL".format(room.Number))
            else:
                print("No corresponding room found on FFL level for room {}".format(room.Number))
        else:
            print("Room is not on CL level")

    # Commit the transaction to persist the changes
    t.Commit()
    print("Transaction committed")

finally:
    # Ensure the transaction is always closed
    if t.HasStarted():
        t.RollBack()
        print("Transaction rolled back")
