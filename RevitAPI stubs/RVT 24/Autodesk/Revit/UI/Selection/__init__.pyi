from typing import Tuple, Set, Iterable, List


class ISelectionFilter:
    def AllowElement(self, elem: Element) -> bool: ...
    def AllowReference(self, reference: Reference, position: XYZ) -> bool: ...


class PickedBox:
    @property
    def Min(self) -> XYZ: ...
    @Min.setter
    def Min(self, __set_formal: XYZ) -> None: ...
    @property
    def Max(self) -> XYZ: ...
    @Max.setter
    def Max(self, __set_formal: XYZ) -> None: ...


class Selection:
    @overload
    def PickObject(self, objectType: ObjectType, selectionFilter: ISelectionFilter, statusPrompt: str) -> Reference: ...
    @overload
    def PickObject(self, objectType: ObjectType, selectionFilter: ISelectionFilter) -> Reference: ...
    @overload
    def PickObject(self, objectType: ObjectType, statusPrompt: str) -> Reference: ...
    @overload
    def PickObject(self, objectType: ObjectType) -> Reference: ...
    @overload
    def PickObjects(self, objectType: ObjectType, selectionFilter: ISelectionFilter, statusPrompt: str, pPreSelected: List[Reference]) -> List[Reference]: ...
    @overload
    def PickObjects(self, objectType: ObjectType, selectionFilter: ISelectionFilter, statusPrompt: str) -> List[Reference]: ...
    @overload
    def PickObjects(self, objectType: ObjectType, selectionFilter: ISelectionFilter) -> List[Reference]: ...
    @overload
    def PickObjects(self, objectType: ObjectType, statusPrompt: str) -> List[Reference]: ...
    @overload
    def PickObjects(self, objectType: ObjectType) -> List[Reference]: ...
    @overload
    def PickPoint(self, snapSettings: ObjectSnapTypes, statusPrompt: str) -> XYZ: ...
    @overload
    def PickPoint(self, statusPrompt: str) -> XYZ: ...
    @overload
    def PickPoint(self, snapSettings: ObjectSnapTypes) -> XYZ: ...
    @overload
    def PickPoint(self) -> XYZ: ...
    @overload
    def PickBox(self, style: PickBoxStyle, statusPrompt: str) -> PickedBox: ...
    @overload
    def PickBox(self, style: PickBoxStyle) -> PickedBox: ...
    @overload
    def PickElementsByRectangle(self, selectionFilter: ISelectionFilter, statusPrompt: str) -> List[Element]: ...
    @overload
    def PickElementsByRectangle(self, selectionFilter: ISelectionFilter) -> List[Element]: ...
    @overload
    def PickElementsByRectangle(self, statusPrompt: str) -> List[Element]: ...
    @overload
    def PickElementsByRectangle(self) -> List[Element]: ...
    @property
    def IsValidObject(self) -> bool: ...
    def SetElementIds(self, elementIds: ICollection) -> None: ...
    def GetElementIds(self) -> ICollection: ...
    def GetReferences(self) -> List[Reference]: ...
    def SetReferences(self, references: List[Reference]) -> None: ...
    def Dispose(self) -> None: ...


class ObjectType:
    Nothing = 0
    Element = 1
    PointOnElement = 2
    Edge = 3
    Face = 4
    LinkedElement = 5
    Subelement = 6


class ObjectSnapTypes:
    #None = 0
    Endpoints = 1
    Midpoints = 2
    Nearest = 4
    WorkPlaneGrid = 8
    Intersections = 16
    Centers = 32
    Perpendicular = 64
    Tangents = 128
    Quadrants = 256
    Points = 512
    Remote = 1024
    CoordinationModelPoints = 2048


class PickBoxStyle:
    Crossing = 0
    Enclosing = 1
    Directional = 2


class SelectableInViewFilter(ElementSlowFilter):
    @overload
    def __init__(self, document: Document, viewId: ElementId, inverted: bool): ...
    @overload
    def __init__(self, document: Document, viewId: ElementId): ...
