import QbvMath,QbvSystem,copy,TransmissionSelectionAlgorithm

# IPG is not taken into consideration yet.

def Networking(System):
        StreamList = System[0]
        PortList= System[1]
        StepSizeinNs = System[2]
        LongestCycle = System[3]
        NoofQvbClass = System[4]
        
        Sink=[]
        SentFrame = 0
        NoQbvClassOpenState = 2**(8-NoofQvbClass) - 1

        #Bind the stream with the index of the injecting/initial sending port in the PortList
        r = len(PortList)
        for stream in StreamList:
            for i in range(0,r-1):
                if stream.Path[0].PortName == PortList[i].PortName:
                    stream.InjectingPortIndex = i

        M= int (1000000*LongestCycle/StepSizeinNs)       
        #Start of the Major for cycle
        print('start calculating, wait......')
        onepercent = 0.01*M
        
        for i in range(M):
            if i % onepercent == 0:
                print(i/onepercent,'%')
            
            #This for cycle servers as the clocking source of this alorithm
            #Each cycle means the elapsing of a single stepsize
            
            #Status of all streams/ports shall be updated once in one cycle.

            #Injecting stream/frame into ports
            for Frame in StreamList:
                if i % Frame.FrameSendIntervalStepSizeCount == Frame.InjectionCycleOffsetStepSizeCount:                    

                    ####
                    PortList[Frame.InjectingPortIndex].EgressQueue[Frame.PCP].append(copy.deepcopy(Frame))
                    ####
                    #
                    PortList[Frame.InjectingPortIndex].EgressQueue[Frame.PCP][-1].PathLog.append(QbvSystem.PathStop(PortList[Frame.InjectingPortIndex].PortName,i,0,0))
                    #
                    SentFrame = SentFrame + 1
                    print()
        
            #Operating all ports
            #SlotGateState = 0
            for Port in PortList:
                
                # Simulate Port Action Stage 1 : Forwarding a frame inside a switch.
                # simulating the time consumed by ARL checking, checksum, memory copy, VLAN checking etc
                # the forwarding action is simulated by runing out a timer
                LenofBeingForward = len(Port.BeingForwarded)
                if LenofBeingForward > 0:
                    for frame in Port.BeingForwarded:                
                        frame.RemainingForwardTime = frame.RemainingForwardTime - StepSizeinNs # timer counting down
                    if Port.BeingForwarded[0].RemainingForwardTime<1:
                        Port.BeingForwarded[0].PathLog.append(QbvSystem.PathStop(Port.PortName,i,i,i))
                        Port.EgressQueue[frame.PCP].append(Port.BeingForwarded[0])
                        del Port.BeingForwarded[0]
                
                #Simulating FQTSS
                if Port.State == 0:
                    #idle state
                    if Port.IPGRemainingBits >=1:
                        # IPG state
                        Port.IPGRemainingBits = Port.IPGRemainingBits - StepSizeinNs * Port.TransmitSpeedinMbps /1000
                    else:
                        #idle State
                        # TSA
                        #SlotGateState = 0 # crucial
                        SelectedQueue = TransmissionSelectionAlgorithm.TSA(Port)
                        if SelectedQueue <= 7 and SelectedQueue >0:
                            #move frame for transmission
                            if len(Port.EgressQueue[SelectedQueue])>0 and len(Port.BeingTransmitted)<1:
                                Port.EgressQueue[SelectedQueue][0].PathLog[Port.EgressQueue[SelectedQueue][0].WhereAmI].EoQ=i
                                Port.BeingTransmitted.append(Port.EgressQueue[SelectedQueue][0])
                                del Port.EgressQueue[SelectedQueue][0]
                                Port.State = 1
                        else:
                            Port.SlotGateState = 0 # crucial                        
                else:       
                    #transmitting
                    #finish transmitting
                    #Simulate Port Action Stage 3: transmit the stream/frame in the 'being transmitted buffer'
                    #There is no such specific buffer in actual switch. It is emulated to ease coding.
                    if len(Port.BeingTransmitted)>0:
                        Port.SlotGateState = copy.copy(2**Port.BeingTransmitted[0].PCP)                    
                        Port.BeingTransmitted[0].RemainingTransmitBitSize = Port.BeingTransmitted[0].RemainingTransmitBitSize - StepSizeinNs * Port.TransmitSpeedinMbps /1000
                    #move this stream frame to next port when finished
                        if Port.BeingTransmitted[0].RemainingTransmitBitSize < 1:
                            Port.BeingTransmitted[0].RemainingTransmitBitSize = Port.BeingTransmitted[0].FrameSizeinByte * 8
                            #Mark the time of finishing transmit
                            Port.BeingTransmitted[0].PathLog[Port.BeingTransmitted[0].WhereAmI].EoT=i
                            Port.BeingTransmitted[0].PathLog[Port.BeingTransmitted[0].WhereAmI].UpdateDelay() ###Whey so complicated????

                            Port.IPGRemainingBits = Port.IPGBitSize
                            Port.State = 0

                            if Port.BeingTransmitted[0].WhereAmI < len(Port.BeingTransmitted[0].Path)-1:
                                #Find the next port and handover the frame
                                for NextPort in PortList:
                                    if Port.BeingTransmitted[0].Path[Port.BeingTransmitted[0].WhereAmI+1].PortName == NextPort.PortName:
                                        Port.BeingTransmitted[0].RemainingForwardTime = NextPort.InBoundForwardDelayinUs * 1000
                                        Port.BeingTransmitted[0].WhereAmI = Port.BeingTransmitted[0].WhereAmI + 1
                                        NextPort.BeingForwarded.append(Port.BeingTransmitted[0])     
                                        del Port.BeingTransmitted[0]
                                        break
                            else:                            
                                Sink.append(Port.BeingTransmitted[0])
                                del Port.BeingTransmitted[0]
                                break
                    else:
                       Port.SlotGateState = 0 # crucial

                #recording the schedule table
                Port.RecordScheduleTable(StepSizeinNs)
        #####################################################################################
        #End of the major for cycle

        PortList = PortPostProcessing(PortList,NoQbvClassOpenState)

        PortList = AddGuardBand(PortList,NoQbvClassOpenState)

        Sink = FramePostProcessing(Sink,PortList,StepSizeinNs)

        #print(len(Sink),' frames are sinked')

        #print(SentFrame, ' frames are sent')

        print('calculate finished...')

        result = [PortList,Sink]

        return  result

def AddGuardBand(PortList,NoQbvClassOpenState):

    #Add GuardBand
    for Port in PortList:
        if len(Port.Schedule) > 0:
            #Make a copy of the schdule
            print(Port.Schedule)
            TempSchedule = copy.deepcopy(Port.Schedule)
            print(TempSchedule)
            EndSize = Port.Schedule[0].Span
            HeadSize = Port.Schedule[-1].Span
            #attach the firts slot in the orignal schedule to the end of the new temp schedule
            if TempSchedule[-1].GateState == Port.Schedule[0].GateState:
                #when the gate state values are the same, extends by simple adding the span value
                TempSchedule[-1].Span = TempSchedule[-1].Span + Port.Schedule[0].Span
            else:
                #when the gate state values are not the same, extends by appending a new slot adding the span value
                TempSchedule.append(copy.deepcopy(Port.Schedule[0]))

            #attach the last slot in the orignal schedule to the head of the new temp schedule
            if TempSchedule[0].GateState == Port.Schedule[-1].GateState:
                #when the gate state values are the same, extends by simple adding the span value
                TempSchedule[0].Span = TempSchedule[0].Span + Port.Schedule[-1].Span
            else:
                TempSchedule.insert(0,copy.deepcopy(Port.Schedule[-1]))


            Target = len(TempSchedule)
            i = 0
            while i < Target:
                if TempSchedule[i].GateState == NoQbvClassOpenState:
                    if TempSchedule[i].Span < 2*Port.GuardBandTimeinMs + Port.MiniNoQbvSlotSizeinMs:
                        TempSchedule[i].GateState = 0
                    else:
                        if i ==0:
                            #only insert after
                            TempSchedule[i].Span = TempSchedule[i].Span - Port.GuardBandTimeinMs
                            TempSchedule.insert(1,QbvSystem.Slot(0,Port.GuardBandTimeinMs))
                            #TempSchedule.insert(1,[0,Port.GuardBandTimeinMs])
                            Target = Target +1
                        elif i == Target-1:
                            TempSchedule[i].Span = TempSchedule[i].Span - Port.GuardBandTimeinMs
                            TempSchedule.insert(i,QbvSystem.Slot(0,Port.GuardBandTimeinMs))
                            Target = Target +1
                            i = i+1
                        else:
                            TempSchedule[i].Span = TempSchedule[i].Span - 2* Port.GuardBandTimeinMs
                            TempSchedule.insert(i,QbvSystem.Slot(0,Port.GuardBandTimeinMs))
                            TempSchedule.insert(i+2,QbvSystem.Slot(0,Port.GuardBandTimeinMs))
                            Target = Target +2
                            i = i+1
                i = i + 1
            RemainingHead = HeadSize
            while RemainingHead > 0:
                if TempSchedule[0].Span>RemainingHead:
                    TempSchedule[0].Span = TempSchedule[0].Span - RemainingHead
                    RemainingHead = 0
                else:
                    RemainingHead = RemainingHead - TempSchedule[0].Span
                    del TempSchedule[0]
            
            RemainingEnd = EndSize
            LastSlotIndex = len(TempSchedule)-1
            while RemainingEnd >0:
                if TempSchedule[LastSlotIndex].Span>RemainingEnd:
                    TempSchedule[LastSlotIndex].Span= TempSchedule[LastSlotIndex].Span - RemainingEnd
                    RemainingEnd = 0
                else:
                    RemainingEnd = RemainingEnd -TempSchedule[LastSlotIndex].Span
                    del TempSchedule[LastSlotIndex]
                    LastSlotIndex = LastSlotIndex -1
            Port.Schedule = TempSchedule
    return PortList

def PortPostProcessing(PortList,NoQbvClassOpenState):

    print('Start Post Processing')
    print('Convert from count of step to ms')
    #Convert from count of step to ms
    for Port in PortList:
        for slot in Port.Schedule:
            slot.Span = slot.Span / 1000000  # StepSize has been taken care of previous

    print('Reduce the length to the schedule cycle of each Port itself.')
    #Reduce the length to the schedule cycle of each Port itself.
    for Port in PortList:
        accu_span=0
        for slot in Port.Schedule:
            if accu_span+slot.Span> Port.ScheduleCycle:
                slot.Span = Port.ScheduleCycle - accu_span
            accu_span = accu_span + slot.Span

    print('#Kill Zero Span Slot.')
    #Kill Zero Span Slot
    #Zero Span slot may be introduced by a frame that does not need queueing. But this is not certain. 
    #So keep the kill zero span slot function here just for safety.
    for Port in PortList:
        KillZeroDone = False
        while KillZeroDone == False and len(Port.Schedule)>0:
            for j in range(len(Port.Schedule)):
                if Port.Schedule[j].Span == 0:
                    del Port.Schedule[j]
                    break
                if j == len(Port.Schedule)-1:
                    KillZeroDone = True
       
    print('Opening Gate for no TSN data')
    #Opening Gate for no TSN data
    for Port in PortList:
        for i in range(len(Port.Schedule)):
            if Port.Schedule[i].GateState  == 0:
                Port.Schedule[i].GateState= NoQbvClassOpenState

    return PortList

def FramePostProcessing(Sink,PortList,StepSizeinNs):

    print(len(Sink),' frames are sinked')
    for Port in PortList:
        Sink = Sink + Port.BeingForwarded
        Sink = Sink + Port.BeingTransmitted
        for TC in Port.EgressQueue:
            Sink = Sink + TC

    print('Cover the time unit of sinked frames')
    #Cover the time unit of sinked frames
    for frame in Sink:
        for stop in frame.PathLog:
            stop.EoF = stop.EoF *StepSizeinNs /1000000 
            stop.EoQ = stop.EoQ *StepSizeinNs /1000000 
            stop.EoT = stop.EoT *StepSizeinNs /1000000
            stop.Delay = stop.Delay *StepSizeinNs /1000000
        frame.UpdateTotalDelay()
    return Sink

