import QbvMath
import os,sys
import copy

class QSys:
    def __init__(self,StreamList,PortList,StepSizeinNs,LongestCycleinMs,NoofQbvClass):
        self.StreamList = StreamList
        self.PortList= PortList
        self.StepSizeinNs = StepSizeinNs
        self.LongestCycle = LongestCycle
        self.NoofQvbClass = NoofQbvClass
        self.NoQbvClassOpenState = 2**(8-NoofQvbClass) - 1

class PathStop:
    def __init__(self,PortName,EndofFowarding,EndofQueueing,EndofTransmission):
        self.PortName = PortName
        self.EoF = EndofFowarding # end of fowarding, also start of Queueing. Start of Forwarding is noted as end of transmission of last stop
        self.EoQ = EndofQueueing # end of queueing, also start of transmission
        self.EoT = EndofTransmission #end of transmission
        self.Delay = 0

    def UpdateDelay(self):
        self.StopDelay = self.EoT - self.EoF


class Slot:
    def __init__(self,GateState,Span):
        self.GateState = GateState
        self.Span = Span


class Stream:
    def __init__(self,StreamName,StreamId,FrameSizeinByte,FrameSendIntervalinMs,RequiredDelayinMs,Path):
        self.StreamName = StreamName
        self.StreamId = StreamId
        self.PCP = 7 # PCP is set to 7 by default
        self.FrameSizeinByte = FrameSizeinByte #FrameSize in Bytes
        self.RemainingTransmitBitSize = self.FrameSizeinByte*8
        self.RemainingForwardTime = 0
        self.FrameSendIntervalinMs=FrameSendIntervalinMs    # FrameSendInterval in ms
        self.FrameSendIntervalStepSizeCount = 0
        self.RequiredDelayinMs = RequiredDelayinMs
        self.FrameTotalDelay = 0
        self.Path = Path
        self.InjectionCycleOffsetFractional = 0.1 # the fractional offset of the time of injecting a frame to a port versus to the absolut start of cycle.
        self.InjectionCycleOffsetStepSizeCount = 0
        self.InjectingPortIndex = 0
        self.WhereAmI = 0
        self.PathLog =[]
    
    def UpdateTotalDelay(self):
        self.InitialTimeStamp = self.PathLog[0].EoF
        self.FinalTimeStamp = self.PathLog[-1].EoT
        self.FrameTotalDelay = self.FinalTimeStamp - self.InitialTimeStamp
class EthPort:
    def __init__(self,PortName,TransmitSpeedinMbps):
        self.PortName = PortName
        self.TransmitSpeedinMbps = TransmitSpeedinMbps
        self.InBoundForwardDelayinUs = 200 # including check sum, arl table checking, vlan, etc., blabla, not including queue delay.
        self.IPGBitSize = 96
        self.ScheduleCycle = 0
        self.CarriedStream=[] #the stream that goes through this port
        self.SlotGateState = 0
        self.Schedule = [] #Schedule, DynamicArray  Slot{gatestate,stateduration}
        self.ScheduleRaw = []  #ScheduleRaw  Slot{gatestate}'''
        self.BeingForwarded=[]
        self.BeingTransmitted=[]        
        self.IPGRemainingBits = 0
        self.IPGSetpSizeCount=0
        self.State = 0 # 0 for IPG & idle, 1 for transmit
        self.QbvAlgorithmResult = 255
        self.GuardBandTimeinMs = 0
        self.MiniNoQbvSlotSizeinMs = 0
        self.TrafficClass0=[]
        self.TrafficClass1=[]
        self.TrafficClass2=[]
        self.TrafficClass3=[]
        self.TrafficClass4=[]
        self.TrafficClass5=[]
        self.TrafficClass6=[]
        self.TrafficClass7=[]
        self.EgressQueue=[]        
        self.EgressQueue.append(self.TrafficClass0)
        self.EgressQueue.append(self.TrafficClass1)
        self.EgressQueue.append(self.TrafficClass2)
        self.EgressQueue.append(self.TrafficClass3)
        self.EgressQueue.append(self.TrafficClass4)
        self.EgressQueue.append(self.TrafficClass5)
        self.EgressQueue.append(self.TrafficClass6)
        self.EgressQueue.append(self.TrafficClass7)
        self.OutBoundPropagationDelayinUs = 0
    '''
    def RecordScheduleTable(self,StepSizeinNs):
        LenofRecordedSchedule = len(self.Schedule)
        if LenofRecordedSchedule != 0:
            if self.Schedule[LenofRecordedSchedule-1][0] != self.SlotGateState:
                    #append new slot
                    self.Schedule.append([self.SlotGateState,StepSizeinNs])
            else:
                    #update the span
                    self.Schedule[LenofRecordedSchedule-1][1] = self.Schedule[LenofRecordedSchedule-1][1] + StepSizeinNs
        else:
            self.Schedule.append(copy.deepcopy([self.SlotGateState,StepSizeinNs]))
    '''
    
    def RecordScheduleTable(self,StepSizeinNs):
        LenofRecordedSchedule = len(self.Schedule)
        if LenofRecordedSchedule != 0:
            if self.Schedule[LenofRecordedSchedule-1].GateState != self.SlotGateState:
                    #append new slot
                    self.Schedule.append(Slot(self.SlotGateState,StepSizeinNs))
            else:
                    #update the span
                    self.Schedule[LenofRecordedSchedule-1].Span = self.Schedule[LenofRecordedSchedule-1].Span + StepSizeinNs
        else:
            self.Schedule.append(copy.deepcopy(Slot(self.SlotGateState,StepSizeinNs)))
    

def Initialize(InputData):
   
    #Start of Manually assign value for all obojects, stream, port, ect., 

    PortDataList = InputData[0]
    StreamDataList = InputData[1]
    PortList = []
    StreamList = []
    GuardBandSizeinBits = InputData[3]
    MiniNoQbvSlotSizeinBits = InputData[4]
    for Port in PortDataList:
        PortList.append(EthPort(Port[0],Port[1]))

    for Each in StreamDataList:
        StreamPath=[]
        for stops in Each[5]:
            StreamPath.append(PortList[stops])
        StreamList.append(Stream(Each[0],Each[1],Each[2],Each[3],Each[4],StreamPath))
    
    InitializedSystem = Preprocess(StreamList,PortList,GuardBandSizeinBits,MiniNoQbvSlotSizeinBits)
    InitializedSystem.append(InputData[2])
    InitializedSystem.append(InputData[3])
    
    
    return(InitializedSystem)

def bindStreamPort(StreamList,PortList):
    for Port in PortList:
        for stream in StreamList:
            for CarryingPort in stream.Path:
                if Port.PortName == CarryingPort.PortName:
                    Port.CarriedStream.append(stream)

    return [StreamList,PortList]

def Preprocess(StreamList,PortList,GuardBandSizeinBits,MiniNoQbvSlotSizeinBits):

    PortList = bindStreamPort(StreamList,PortList)[1]

    #CalculateStepSize
    StepSizeinNs = getStepSize(PortList)    
    print('calculation step size is',StepSizeinNs,'ns')
    print('')

    #Calculate schedule Cycle for each Port
    LongestCycle = 0     
    for Port in PortList:
        if len(Port.CarriedStream) >0:
            Port.ScheduleCycle=getPortScheduleCycle(Port.CarriedStream)
            for stream in Port.CarriedStream:
                print('Port ', Port.PortName,' carries stream ',stream.StreamName,', with cycle ',stream.FrameSendIntervalinMs, 'ms')
            if Port.ScheduleCycle > LongestCycle:
                LongestCycle = Port.ScheduleCycle
            print('Determined schedule cycle for this port is ', Port.ScheduleCycle)
            print('')
        else:
            print(Port.PortName,'transmitts no stream, no schedule cycle is needed')
            print('')
        Port.GuardBandTimeinMs = GuardBandSizeinBits / (1000*Port.TransmitSpeedinMbps)
        Port.MiniNoQbvSlotSizeinMs = MiniNoQbvSlotSizeinBits / (1000*Port.TransmitSpeedinMbps)

    if (LongestCycle * 1000000) % StepSizeinNs != 0:
        print('Cycle vs stepsize error, initialization aborted')
        sys.exit()

    StreamList= UpdateInjectionOffset(StreamList,StepSizeinNs)

    #Caculate average delay per hop of each stream and sort accordingly ,Sort the order of streams.
    #This is not implemented yet.   

    return [StreamList,PortList,StepSizeinNs,LongestCycle]

def UpdateInjectionOffset(StreamList,StepSizeinNs):
    for stream in StreamList:
        stream.InjectionCycleOffsetStepSizeCount = int(1000000*stream.InjectionCycleOffsetFractional*stream.FrameSendIntervalinMs/StepSizeinNs)
        stream.FrameSendIntervalStepSizeCount = int(1000000*stream.FrameSendIntervalinMs/StepSizeinNs)
    return StreamList

    
def getStepSize(PortList):
    MaxPortSpeed = PortList[0].TransmitSpeedinMbps  

    for Port in PortList:
        if Port.TransmitSpeedinMbps>MaxPortSpeed:
            MaxPortSpeed=Port.TransmitSpeedinMbps

    SmallestByteTimeinNs = 1000/MaxPortSpeed

    return SmallestByteTimeinNs

def getPortScheduleCycle(StreamList):
    # which is, in fact, the least common digit of all send cycle

    ReducedStreamList=[]
    for stream in StreamList:
        if stream.FrameSendIntervalinMs in ReducedStreamList:
            pass
        else:
            ReducedStreamList.append(stream.FrameSendIntervalinMs)
      
    LCM = QbvMath.getLcm(ReducedStreamList)

    return LCM