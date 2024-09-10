from typing import Tuple, Set, Iterable, List


class PipeFlowConfigurationType:
    Calculated = 0
    Preset = 1
    System = 2
    Demand = 3


class PipeFlowState:
    LaminarState = 0
    TransitionState = 1
    TurbulentState = 2
    MultiValues = -1


class PipeSystemType:
    UndefinedSystemType = 0
    SupplyHydronic = 7
    ReturnHydronic = 8
    Sanitary = 16
    Vent = 17
    DomesticHotWater = 19
    DomesticColdWater = 20
    OtherPipe = 22
    FireProtectWet = 23
    FireProtectDry = 24
    FireProtectPreaction = 25
    FireProtectOther = 26
    Fitting = 28
    Global = 29


class PipeLossMethodType:
    NotDefined = 0
    Table = 1
    SpecificLoss = 4
    Coefficient = 6


class FlexPipeType(MEPCurveType):


class FlexPipe(MEPCurve):
    @property
    def FlowState(self) -> PipeFlowState: ...
    @property
    def FlexPipeType(self) -> FlexPipeType: ...
    @FlexPipeType.setter
    def FlexPipeType(self, flexPipeType: FlexPipeType) -> None: ...
    @property
    def Points(self) -> List[XYZ]: ...
    @Points.setter
    def Points(self, points: List[XYZ]) -> None: ...
    @property
    def StartTangent(self) -> XYZ: ...
    @StartTangent.setter
    def StartTangent(self, tangent: XYZ) -> None: ...
    @property
    def EndTangent(self) -> XYZ: ...
    @EndTangent.setter
    def EndTangent(self, tangent: XYZ) -> None: ...
    @overload
    def Create(document: Document, systemTypeId: ElementId, pipeTypeId: ElementId, levelId: ElementId, startTangent: XYZ, endTangent: XYZ, points: List[XYZ]) -> FlexPipe: ...
    @overload
    def Create(document: Document, systemTypeId: ElementId, pipeTypeId: ElementId, levelId: ElementId, points: List[XYZ]) -> FlexPipe: ...
    def IsFlexPipeTypeId(document: Document, pipeTypeId: ElementId) -> bool: ...
    def IsPipingSystemTypeId(document: Document, systemTypeId: ElementId) -> bool: ...


class Pipe(MEPCurve):
    @property
    def FlowState(self) -> PipeFlowState: ...
    @property
    def PipeType(self) -> PipeType: ...
    @PipeType.setter
    def PipeType(self, pipeType: PipeType) -> None: ...
    @property
    def IsPlaceholder(self) -> bool: ...
    @property
    def PipeSegment(self) -> PipeSegment: ...
    @overload
    def Create(document: Document, pipeTypeId: ElementId, levelId: ElementId, startConnector: Connector, endConnector: Connector) -> Pipe: ...
    @overload
    def Create(document: Document, pipeTypeId: ElementId, levelId: ElementId, startConnector: Connector, endPoint: XYZ) -> Pipe: ...
    @overload
    def Create(document: Document, systemTypeId: ElementId, pipeTypeId: ElementId, levelId: ElementId, startPoint: XYZ, endPoint: XYZ) -> Pipe: ...
    def CreatePlaceholder(document: Document, systemTypeId: ElementId, pipeTypeId: ElementId, levelId: ElementId, startPoint: XYZ, endPoint: XYZ) -> Pipe: ...
    def SetSystemType(self, systemTypeId: ElementId) -> None: ...
    def IsPipeTypeId(document: Document, pipeTypeId: ElementId) -> bool: ...
    def IsPipingConnector(connector: Connector) -> bool: ...
    def IsPipingSystemTypeId(document: Document, systemTypeId: ElementId) -> bool: ...


class PipeType(MEPCurveType):


class PipingSystem(MEPSystem):
    @property
    def SystemType(self) -> PipeSystemType: ...
    @property
    def BaseEquipmentConnector(self) -> Connector: ...
    @BaseEquipmentConnector.setter
    def BaseEquipmentConnector(self, baseEquipmentConnector: Connector) -> None: ...
    @property
    def PipingNetwork(self) -> ElementSet: ...
    @property
    def IsWellConnected(self) -> bool: ...
    def IsFlowServerMissing(self) -> bool: ...
    def IsPressureDropServerMissing(self) -> bool: ...
    @overload
    def Create(ADocument: Document, typeId: ElementId, name: str) -> PipingSystem: ...
    @overload
    def Create(ADocument: Document, typeId: ElementId) -> PipingSystem: ...
    def GetVolume(self) -> float: ...
    def GetFlow(self) -> float: ...
    def GetStaticPressure(self) -> float: ...
    def GetFixtureUnits(self) -> float: ...
    def GetPumpSets(self) -> ISet: ...
    def CreateHydraulicSeparation(document: Document, pipeElementIds: ISet) -> ISet: ...
    def DeleteHydraulicSeparation(document: Document, pipeElementIds: ISet) -> None: ...
    def IsHydraulicLoopBoundary(element: Element) -> bool: ...
    def CanBeHydraulicLoopBoundary(element: Element) -> bool: ...


class IPipeFittingAndAccessoryPressureDropServer:
    def Calculate(self, data: PipeFittingAndAccessoryPressureDropData) -> bool: ...
    def IsApplicable(self, data: PipeFittingAndAccessoryPressureDropData) -> bool: ...
    def GetDataSchema(self) -> Schema: ...


class PipeFittingAndAccessoryPressureDropItem:
    @property
    def BeginConnectorIndex(self) -> int: ...
    @property
    def EndConnectorIndex(self) -> int: ...
    @property
    def VelocityPressure(self) -> float: ...
    @property
    def Coefficient(self) -> float: ...
    @Coefficient.setter
    def Coefficient(self, coefficient: float) -> None: ...
    @property
    def IsValidObject(self) -> bool: ...
    def Dispose(self) -> None: ...


class PipeFittingAndAccessoryPressureDropData:
    @property
    def CalculationType(self) -> int: ...
    @property
    def IsCurrentEntityValid(self) -> bool: ...
    @IsCurrentEntityValid.setter
    def IsCurrentEntityValid(self, isCurrentEntityValid: bool) -> None: ...
    @property
    def IsValidObject(self) -> bool: ...
    def GetPipeFittingAndAccessoryData(self) -> PipeFittingAndAccessoryData: ...
    def GetPresureDropItems(self) -> List[PipeFittingAndAccessoryPressureDropItem]: ...
    def SetDefaultEntity(self, defaultEntity: Entity) -> None: ...
    def Dispose(self) -> None: ...


class IPipePlumbingFixtureFlowServer:
    def Calculate(self, data: PipePlumbingFixtureFlowData) -> None: ...
    def GetInformationLink(self) -> str: ...
    def GetHtmlDescription(self) -> str: ...


class PipingSystemType(MEPSystemType):
    @property
    def TwoLineRiseType(self) -> RiseDropSymbol: ...
    @TwoLineRiseType.setter
    def TwoLineRiseType(self, TwoLineRiseType: RiseDropSymbol) -> None: ...
    @property
    def TwoLineDropType(self) -> RiseDropSymbol: ...
    @TwoLineDropType.setter
    def TwoLineDropType(self, TwoLineDropType: RiseDropSymbol) -> None: ...
    @property
    def SingleLineBendRiseType(self) -> RiseDropSymbol: ...
    @SingleLineBendRiseType.setter
    def SingleLineBendRiseType(self, SingleLineBendRiseType: RiseDropSymbol) -> None: ...
    @property
    def SingleLineBendDropType(self) -> RiseDropSymbol: ...
    @SingleLineBendDropType.setter
    def SingleLineBendDropType(self, SingleLineBendDropType: RiseDropSymbol) -> None: ...
    @property
    def SingleLineJunctionRiseType(self) -> RiseDropSymbol: ...
    @SingleLineJunctionRiseType.setter
    def SingleLineJunctionRiseType(self, SingleLineJunctionRiseType: RiseDropSymbol) -> None: ...
    @property
    def SingleLineJunctionDropType(self) -> RiseDropSymbol: ...
    @SingleLineJunctionDropType.setter
    def SingleLineJunctionDropType(self, SingleLineJunctionDropType: RiseDropSymbol) -> None: ...
    @property
    def FluidTemperature(self) -> float: ...
    @FluidTemperature.setter
    def FluidTemperature(self, fluidTemperature: float) -> None: ...
    @property
    def FluidType(self) -> ElementId: ...
    @FluidType.setter
    def FluidType(self, fluidTypeId: ElementId) -> None: ...
    def Create(ADoc: Document, systemClassification: MEPSystemClassification, name: str) -> PipingSystemType: ...
    def ValidateRiseDropSymbolType(self, risedropType: RiseDropSymbol) -> bool: ...
    @property
    def FlowConversionMethod(self) -> FlowConversionMode: ...
    @FlowConversionMethod.setter
    def FlowConversionMethod(self, flowConversionMethod: FlowConversionMode) -> None: ...


class PipePlumbingFixtureFlowData:
    @property
    def Flow(self) -> float: ...
    @Flow.setter
    def Flow(self, flow: float) -> None: ...
    @property
    def FlowConfiguration(self) -> PipeFlowConfigurationType: ...
    @property
    def FixtureUnits(self) -> float: ...
    @property
    def FlowConversionMode(self) -> FlowConversionMode: ...
    @property
    def DimensionFlow(self) -> float: ...
    @property
    def IsValidObject(self) -> bool: ...
    def Dispose(self) -> None: ...


class IPipePressureDropServer:
    def Calculate(self, data: PipePressureDropData) -> None: ...
    def GetInformationLink(self) -> str: ...
    def GetHtmlDescription(self) -> str: ...


class PipePressureDropData:
    @property
    def RelativeRoughness(self) -> float: ...
    @RelativeRoughness.setter
    def RelativeRoughness(self, relativeRoughness: float) -> None: ...
    @property
    def ReynoldsNumber(self) -> float: ...
    @ReynoldsNumber.setter
    def ReynoldsNumber(self, reynoldsNumber: float) -> None: ...
    @property
    def FlowState(self) -> PipeFlowState: ...
    @FlowState.setter
    def FlowState(self, flowState: PipeFlowState) -> None: ...
    @property
    def Friction(self) -> float: ...
    @Friction.setter
    def Friction(self, friction: float) -> None: ...
    @property
    def FrictionFactor(self) -> float: ...
    @FrictionFactor.setter
    def FrictionFactor(self, frictionFactor: float) -> None: ...
    @property
    def Velocity(self) -> float: ...
    @Velocity.setter
    def Velocity(self, velocity: float) -> None: ...
    @property
    def VelocityPressure(self) -> float: ...
    @VelocityPressure.setter
    def VelocityPressure(self, velocityPressure: float) -> None: ...
    @property
    def Coefficient(self) -> float: ...
    @Coefficient.setter
    def Coefficient(self, coefficient: float) -> None: ...
    @property
    def PressureDrop(self) -> float: ...
    @PressureDrop.setter
    def PressureDrop(self, pressureDrop: float) -> None: ...
    @property
    def Roughness(self) -> float: ...
    @property
    def Length(self) -> float: ...
    @property
    def Flow(self) -> float: ...
    @property
    def InsideDiameter(self) -> float: ...
    @property
    def OutsideDiameter(self) -> float: ...
    @property
    def NominalDiameter(self) -> float: ...
    @property
    def Density(self) -> float: ...
    @property
    def Viscosity(self) -> float: ...
    @property
    def CategoryId(self) -> ElementId: ...
    @property
    def KLevel(self) -> SystemCalculationLevel: ...
    @property
    def IsValidObject(self) -> bool: ...
    def Dispose(self) -> None: ...


class FlowConversionMode:
    Valves = 0
    Tanks = 1
    Invalid = -1


class PipeFittingAndAccessoryConnectorData:
    @property
    def Width(self) -> float: ...
    @property
    def Height(self) -> float: ...
    @property
    def Diameter(self) -> float: ...
    @property
    def Angle(self) -> float: ...
    @property
    def Index(self) -> int: ...
    @property
    def LinkIndex(self) -> int: ...
    @property
    def FlowDirection(self) -> FlowDirectionType: ...
    @property
    def Flow(self) -> float: ...
    @property
    def VelocityPressure(self) -> float: ...
    @property
    def Profile(self) -> ConnectorProfileType: ...
    @property
    def IsValidObject(self) -> bool: ...
    def GetCoordination(self) -> Transform: ...
    def Dispose(self) -> None: ...


class PipeFittingAndAccessoryData:
    @property
    def ServerGUID(self) -> Guid: ...
    @property
    def PartType(self) -> PartType: ...
    @property
    def BehaviorType(self) -> int: ...
    @property
    def SystemClassification(self) -> MEPSystemClassification: ...
    @property
    def Origin(self) -> XYZ: ...
    @property
    def FluidViscosity(self) -> float: ...
    @property
    def FluidDensity(self) -> float: ...
    @property
    def IsValidObject(self) -> bool: ...
    def GetEntity(self) -> Entity: ...
    def GetAllConnectorData(self) -> List[PipeFittingAndAccessoryConnectorData]: ...
    def GetFamilyInstanceId(self) -> ElementId: ...
    def Dispose(self) -> None: ...


class PipeSegment(Segment):
    @property
    def ScheduleTypeId(self) -> ElementId: ...
    def Create(ADocument: Document, MaterialId: ElementId, ScheduleId: ElementId, sizeSet: ICollection) -> PipeSegment: ...


class PlumbingUtils:
    def ConvertPipePlaceholders(document: Document, placeholderIds: ICollection) -> ICollection: ...
    @overload
    def ConnectPipePlaceholdersAtElbow(document: Document, connector1: Connector, connector2: Connector) -> bool: ...
    @overload
    def ConnectPipePlaceholdersAtElbow(document: Document, placeholder1Id: ElementId, placeholder2Id: ElementId) -> bool: ...
    @overload
    def ConnectPipePlaceholdersAtTee(document: Document, connector1: Connector, connector2: Connector, connector3: Connector) -> bool: ...
    @overload
    def ConnectPipePlaceholdersAtTee(document: Document, placeholder1Id: ElementId, placeholder2Id: ElementId) -> bool: ...
    @overload
    def ConnectPipePlaceholdersAtCross(document: Document, connector1: Connector, connector2: Connector, connector3: Connector, connector4: Connector) -> bool: ...
    @overload
    def ConnectPipePlaceholdersAtCross(document: Document, placeholder1Id: ElementId, placeholder2Id: ElementId, placeholder3Id: ElementId) -> bool: ...
    @overload
    def ConnectPipePlaceholdersAtCross(document: Document, placeholder1Id: ElementId, placeholder2Id: ElementId) -> bool: ...
    def PlaceCapOnOpenEnds(document: Document, elemId: ElementId, typeId: ElementId) -> None: ...
    def HasOpenConnector(document: Document, elemId: ElementId) -> bool: ...
    def BreakCurve(document: Document, pipeId: ElementId, ptBreak: XYZ) -> ElementId: ...


class FluidTemperatureSetIterator:
    @property
    def IsValidObject(self) -> bool: ...
    def MoveNext(self) -> bool: ...
    def IsDone(self) -> bool: ...
    def Reset(self) -> None: ...
    def GetCurrent(self) -> FluidTemperature: ...
    @property
    def Current(self) -> FluidTemperature: ...
    def Dispose(self) -> None: ...


class FluidTemperature:
    def __init__(self, temperature: float, viscosity: float, density: float): ...
    @property
    def Temperature(self) -> float: ...
    @Temperature.setter
    def Temperature(self, temperature: float) -> None: ...
    @property
    def Viscosity(self) -> float: ...
    @Viscosity.setter
    def Viscosity(self, viscosity: float) -> None: ...
    @property
    def Density(self) -> float: ...
    @Density.setter
    def Density(self, density: float) -> None: ...
    @property
    def IsValidObject(self) -> bool: ...
    def Dispose(self) -> None: ...


class FluidType(ElementType):
    def GetFluidTemperatureSetIterator(self) -> FluidTemperatureSetIterator: ...
    @overload
    def Create(document: Document, fluidTypeName: str, basedOnFluidType: FluidType) -> FluidType: ...
    @overload
    def Create(document: Document, fluidTypeName: str) -> FluidType: ...
    def GetFluidType(document: Document, fluidTypeName: str) -> FluidType: ...
    def IsFluidInUse(document: Document, fluidId: ElementId) -> bool: ...
    def ClearAllTemperatures(self) -> None: ...
    def GetTemperature(self, temperature: float) -> FluidTemperature: ...
    def AddTemperature(self, fluidTemperature: FluidTemperature) -> None: ...
    def RemoveTemperature(self, temperature: float) -> None: ...
    def GetEnumerator(self) -> IEnumerator: ...


class PipeInsulation(InsulationLiningBase):
    def Create(document: Document, pipeOrContentElementId: ElementId, pipeInsulationTypeId: ElementId, Thickness: float) -> PipeInsulation: ...


class PipeInsulationType(ElementType):


class PipeScheduleType(ElementType):
    def Create(doc: Document, name: str) -> PipeScheduleType: ...
    def GetPipeScheduleId(doc: Document, name: str) -> ElementId: ...


class PipeSettings(Element):
    @property
    def FlatOnTop(self) -> str: ...
    @FlatOnTop.setter
    def FlatOnTop(self, flatOnTop: str) -> None: ...
    @property
    def FlatOnBottom(self) -> str: ...
    @FlatOnBottom.setter
    def FlatOnBottom(self, flatOnBottom: str) -> None: ...
    @property
    def SetUp(self) -> str: ...
    @SetUp.setter
    def SetUp(self, setUp: str) -> None: ...
    @property
    def SetDown(self) -> str: ...
    @SetDown.setter
    def SetDown(self, setDown: str) -> None: ...
    @property
    def SetUpFromBottom(self) -> str: ...
    @SetUpFromBottom.setter
    def SetUpFromBottom(self, setUpFromBottom: str) -> None: ...
    @property
    def SetDownFromBottom(self) -> str: ...
    @SetDownFromBottom.setter
    def SetDownFromBottom(self, setDownFromBottom: str) -> None: ...
    @property
    def Centerline(self) -> str: ...
    @Centerline.setter
    def Centerline(self, centerline: str) -> None: ...
    @property
    def FittingAngleUsage(self) -> FittingAngleUsage: ...
    @FittingAngleUsage.setter
    def FittingAngleUsage(self, fittingAngleUsage: FittingAngleUsage) -> None: ...
    @property
    def SizeSuffix(self) -> str: ...
    @SizeSuffix.setter
    def SizeSuffix(self, str: str) -> None: ...
    @property
    def SizePrefix(self) -> str: ...
    @SizePrefix.setter
    def SizePrefix(self, str: str) -> None: ...
    @property
    def ConnectorSeparator(self) -> str: ...
    @ConnectorSeparator.setter
    def ConnectorSeparator(self, str: str) -> None: ...
    @property
    def ConnectorTolerance(self) -> float: ...
    @ConnectorTolerance.setter
    def ConnectorTolerance(self, dValue: float) -> None: ...
    @property
    def FittingAnnotationSize(self) -> float: ...
    @FittingAnnotationSize.setter
    def FittingAnnotationSize(self, dValue: float) -> None: ...
    @property
    def UseAnnotationScaleForSingleLineFittings(self) -> bool: ...
    @UseAnnotationScaleForSingleLineFittings.setter
    def UseAnnotationScaleForSingleLineFittings(self, value: bool) -> None: ...
    @property
    def AnalysisForClosedLoopHydronicPipingNetworks(self) -> bool: ...
    @AnalysisForClosedLoopHydronicPipingNetworks.setter
    def AnalysisForClosedLoopHydronicPipingNetworks(self, value: bool) -> None: ...
    def GetPipeSettings(document: Document) -> PipeSettings: ...
    def GetPipeSlopes(self) -> List[float]: ...
    def SetPipeSlopes(self, slopes: List[float]) -> None: ...
    def AddPipeSlope(self, slope: float) -> None: ...
    def GetSpecificFittingAngles(self) -> List[float]: ...
    def SetSpecificFittingAngleStatus(self, angle: float, bStatus: bool) -> None: ...
    def GetSpecificFittingAngleStatus(self, angle: float) -> bool: ...
    def IsAnalysisForClosedLoopHydronicPipingNetworksEnabled(ccda: Document) -> bool: ...
    def IsValidSpecificFittingAngle(self, angle: float) -> bool: ...
    def GetFlowConvertionServerInfo(self) -> MEPCalculationServerInfo: ...
    def SetFlowConvertionServerInfo(self, serverInfo: MEPCalculationServerInfo) -> None: ...
