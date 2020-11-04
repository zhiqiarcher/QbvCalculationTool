import QbvSearchEngine
import QbvSystem
import os,sys


def Calculate(InputData):
    print('*********************************Start of Qbv Scheduel Calculation Process********************************************************')

    if getattr(sys, 'frozen', False):
        FP = os.path.dirname(sys.executable)
    elif __file__:
        FP = os.path.dirname(__file__)

    ScheduleTablePath = os.path.join(FP,"Accessory","ScheduleTable.txt")
    StreamPathLogPath = os.path.join(FP,"Accessory","StreamPathLog.txt")


    System = QbvSystem.Initialize(InputData)

    Result = QbvSearchEngine.Search(System)
    
    print('writing into file, wait......')

    f = open(ScheduleTablePath,'w')
    f.truncate()
    for port in Result[0]:
        f.write(port.PortName+'-Gate ')
        for slot in port.Schedule:
            f.write(str(slot.GateState)+' ')
        f.write('\n')
        f.write(port.PortName+'-Span ')
        for slot in port.Schedule:
            f.write(str(slot.Span)+' ')
        f.write('\n')
    f.close()

    
    f = open(StreamPathLogPath,'w')
    f.truncate()
    for Frame in Result[1]:
        f.write(Frame.StreamName + '-' + str(Frame.PCP) +'--P ')
        for step in Frame.PathLog:
            f.write(str(step.PortName) + ' ')
        f.write('\n')

        f.write(Frame.StreamName +'-Forw ')
        for step in Frame.PathLog:
            f.write(str(step.EoF) + ' ') # need conversion
        f.write('\n')

        f.write(Frame.StreamName +'-Queu ')
        for step in Frame.PathLog:
            f.write(str(step.EoQ) + ' ') # need conversion
        f.write('\n')

        f.write(Frame.StreamName +'-Tran ')
        for step in Frame.PathLog:
            f.write(str(step.EoT) + ' ') # need conversion
        f.write('\n')   

    f.close()

    print('files are written to ',os.path.dirname(__file__) ,'\\Accessory')
   
    print('*********************************End of Qbv Scheduel Calculation Process********************************************************')
    return Result #TBD currently the port and stream are returned, in the end the schedule table shall be returned


def WriteScheduleTable():
    pass

def WriteFramePath():
    pass


   
    
   

    



