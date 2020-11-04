import tkinter,xml
import os,sys
from tkinter import ttk
import QbvCalculator

if getattr(sys, 'frozen', False):
    FP = os.path.dirname(sys.executable)
elif __file__:
    FP = os.path.dirname(__file__)

SystemDescriptionXmlPath = os.path.join(FP,"Accessory","QbvSystemDescription.xml")
DisplayExcelPath = os.path.join(FP,"Accessory","QbvSchedulerDisplay.xlsm")
tempxmlPath = os.path.join(FP,"temp.xml")

DefaultPort = ["PortX",100,200]
DisplayOption = True
def AbstractValue(tagged):
    value = tagged.split(">")[1].split("<")[0]
    return value

def Reset(win):
    win.Script.delete("1.0","end")
    win.Script.insert("insert", "<System>\n  <Ports>\n  </Ports>\n  <Streams>\n  </Streams>\n  <Meta>\n    <AmtofQbvCls></AmtofQbvCls>\n    <GuardBandSizeinBits></GuardBandSizeinBits>\n    <MiniNoQbvSizeSlotinBits></MiniNoQbvSizeSlotinBits>\n  </Meta>\n</System>")


def Calculate(win):

    UpdateMeta()

    SystemDescription = win.Script.get("0.0","end")
    SystemDescription = SystemDescription.replace(" ","")
    SystemDescriptionList = SystemDescription.split("\n")

    StartofPorts = SystemDescriptionList.index("<Ports>")
    EndofPorts = SystemDescriptionList.index("</Ports>")

    if EndofPorts - StartofPorts > 1:
        PortDataList = SystemDescriptionList[StartofPorts+1:EndofPorts-1]
       #print(PortDataList)
    else:
        print("no port exist")
        return

    StartofStreams = SystemDescriptionList.index("<Streams>")
    EndofStreams = SystemDescriptionList.index("</Streams>")

    PortData = []
    for i in range(len(PortDataList)):
        if PortDataList[i] == "<Port>":
            PortData.append([AbstractValue(PortDataList[i+2]),int(AbstractValue(PortDataList[i+3]))]) # Port Name and transmit speed. Now in bound delay is only using default value
    print(PortData)


    if EndofStreams - StartofStreams > 1:
        StreamDataList = SystemDescriptionList[StartofStreams+1:EndofStreams-1]
        print(StreamDataList)
    else:
        print("no stream exist")
        return

    StreamData = []
    for i in range(len(StreamDataList)):
        if StreamDataList[i] == "<Stream>":
            PathString = AbstractValue(StreamDataList[i+6])
            PathinString = PathString.split("[")[1].split("]")[0].split(",")
            Path = []
            for item in PathinString:
                Path.append(int(item))
            StreamData.append([AbstractValue(StreamDataList[i+2]),int(AbstractValue(StreamDataList[i+1])),int(AbstractValue(StreamDataList[i+3])),int(AbstractValue(StreamDataList[i+4])),int(AbstractValue(StreamDataList[i+5])),Path]) # Port Name and transmit speed. Now in bound delay is only using default value
    print(StreamData)
    

    StartofMeta = SystemDescriptionList.index("<Meta>")
    EndofMeta = SystemDescriptionList.index("</Meta>")

    if EndofMeta - StartofMeta > 1:
        MetaDataList = SystemDescriptionList[StartofMeta+1:EndofMeta]
        MetaData = [int(AbstractValue(MetaDataList[0])),int(AbstractValue(MetaDataList[1])),int(AbstractValue(MetaDataList[2]))]
        print(MetaData)

       #print(MetaDataList)
    else:
        print("no meta exist")
        return

    System = [PortData,StreamData,MetaData[0],MetaData[1],MetaData[2]]

    QbvCalculator.Calculate(System)
    os.startfile(DisplayExcelPath)


def AddPort(win):
    Content = win.PortScript.get("0.0","end").split("\n")[0]
    PortPara = Content.split(",")
    SplitResult = win.Script.get("0.0","end").split("\n")
    
    win.Script.delete("1.0","end")

    location = SplitResult.index("  </Ports>")

    SplitResult.insert(location, "    <Port>\n" + "        <PortID>"+ str(PortPara[0]) + "</PortID>\n" + "        <PortName>"+ str(PortPara[1]) + "</PortName>\n"+  "        <TransmitSpeedInMbps>"+ str(PortPara[2]) + "</TransmitSpeedInMbps>\n"+ "        <InBoundDelayinUs>"+ str(PortPara[3]) + "</InBoundDelayinUs>\n" + "    </Port>")

    rebuild = ""
    for line in SplitResult:
        rebuild = rebuild + line + "\n"
    
    win.Script.insert("insert",rebuild)

def AddStream(win):
    Content = win.StreamScript.get("0.0","end").split("\n")[0]
    Path ="[" +Content.split("[")[1]
    Para = Content.split("[")[0].split(",")

    SplitResult = win.Script.get("0.0","end").split("\n")
    
    win.Script.delete("1.0","end")

    location = SplitResult.index("  </Streams>")

    SplitResult.insert(location, "    <Stream>\n" + "        <StreamID>"+ str(Para[0]) + "</StreamID>\n" + "        <StreamName>"+ str(Para[1]) + "</StreamName>\n"+  "        <FrameSizeinBytes>"+ str(Para[2]) + "</FrameSizeinBytes>\n"+ "        <FrameSendIntervalinMs>"+ str(Para[3]) + "</FrameSendIntervalinMs>\n" + "        <RequiredDelayinMs>"+ str(Para[4]) + "</RequiredDelayinMs>\n" + "        <Path>"+ Path + "</Path>\n" +"    </Stream>")

    rebuild = ""
    for line in SplitResult:
        rebuild = rebuild + line + "\n"
    
    win.Script.insert("insert",rebuild)

def UpdateMeta(win):
    SplitResult = win.Script.get("0.0","end").split("\n")
    
    start = SplitResult.index("  <Meta>")
    end = SplitResult.index("  </Meta>")

    AmtofQbvCls = win.AmountofQbvClasstxt.get("0.0","end").split("\n")[0]
    GuardBandSizeinBits = win.GuardBandSizeinBitstxt.get("0.0","end").split("\n")[0]
    MiniNoQbvSlotSizeinBits = win.MiniNoQbvSlotSizeinBitstxt.get("0.0","end").split("\n")[0]

    if end - start >1:
        for i in range(end -start-1):
            del SplitResult[start +1]
    pass

    SplitResult.insert(start+1,"    <AmtofQbvCls>" + AmtofQbvCls + "</AmtofQbvCls>\n    <GuardBandSizeinBits>" + GuardBandSizeinBits + "</GuardBandSizeinBits>\n    <MiniNoQbvSizeSlotinBits>" + MiniNoQbvSlotSizeinBits + "</MiniNoQbvSizeSlotinBits>")


    win.Script.delete("1.0","end")

    rebuild = ""
    for line in SplitResult:
        rebuild = rebuild + line + "\n"
    
    win.Script.insert("insert",rebuild)

def Save(win):
    f = open(SystemDescriptionXmlPath,'w')
    f.truncate()
    f.write(win.Script.get("0.0","end"))
    f.close()

def Load(win):
    f = open(SystemDescriptionXmlPath,'r')
    Data = f.read()
    f.close()
    win.Script.delete("1.0","end")
    win.Script.insert("insert",Data)

def main():
    # Initializing all the UI
    win = tkinter.Tk()
    win.geometry("650x600")
    win.title("Qbv Gate Control List Calculator")
    ScriptLable = tkinter.Label(win,text = "Script",width = 10,height = 2)
    ScriptLable.place(x = 0,y = 0)

    Script = tkinter.Text(win,width=89, height=27)
    Script.place(x = 10,y = 10,)
    Load(win)
    #Script.insert("insert", "<System>\n  <Ports>\n  </Ports>\n  <Streams>\n  </Streams>\n  <Meta>\n    <AmtofQbvCls></AmtofQbvCls>\n    <GuardBandSizeinBits></GuardBandSizeinBits>\n    <MiniNoQbvSizeSlotinBits></MiniNoQbvSizeSlotinBits>\n  </Meta>\n</System>")

    PortScript = tkinter.Text(win,width=60, height=1)
    PortScript.place(x = 100,y = 390)
    PortScript.insert("insert", "0,Port0,100,200")
    PortParameterDescriptionLable = tkinter.Label(win,text = "Port ID, Port Name, Transmist Speed in Mbps, Inbound Delay in Us",width = 67,height = 1)
    PortParameterDescriptionLable.place(x = 60, y= 410)
    AddPortButton = ttk.Button(win,text = "Add Port",command = AddPort)
    AddPortButton.place(x= 10,y= 385, width=80,height = 30)



    StreamScript = tkinter.Text(win,width=60, height=1)
    StreamScript.place(x = 100,y = 460)
    StreamScript.insert("insert", "0,Stream1,100,500,2,[1,2,3]")
    StreamParameterDescriptionLable = tkinter.Label(win,text = "Stream ID, Stream Name, Frame Size in Bytes, Send interval in Ms, \n Required delay in Ms, Path",width = 66,height = 2)
    StreamParameterDescriptionLable.place(x = 60, y= 480)
    AddStreamButton = ttk.Button(win,text = "Add Stream", command = AddStream)
    AddStreamButton.place(x= 10,y= 455, width=80,height = 30)

    AmountofQbvClassLable = tkinter.Label(win,text = "Amount of Qbv Class",width = 20,height = 1)
    AmountofQbvClassLable.place(x = 0,y = 535)
    AmountofQbvClasstxt = tkinter.Text(win,width=20, height=1)
    AmountofQbvClasstxt.insert("insert","3")
    AmountofQbvClasstxt.place(x = 10,y = 555)

    GuardBandSizeinBits = tkinter.Label(win,text = "Guard Band Size in Bits",width = 19,height = 1)
    GuardBandSizeinBits.place(x = 180,y = 535)
    GuardBandSizeinBitstxt = tkinter.Text(win,width=20, height=1)
    GuardBandSizeinBitstxt.insert("insert","1000")
    GuardBandSizeinBitstxt.place(x = 180,y = 555)

    MiniNoQbvSlotSizeinBits = tkinter.Label(win,text = "Mini No Qbv Slot Size in Bits",width = 23,height = 1)
    MiniNoQbvSlotSizeinBits.place(x = 360,y = 535)
    MiniNoQbvSlotSizeinBitstxt = tkinter.Text(win,width=20, height=1)
    MiniNoQbvSlotSizeinBitstxt.insert("insert","0")
    MiniNoQbvSlotSizeinBitstxt.place(x = 360,y = 555)

    Resetbt = ttk.Button(win,text = "Reset", command = Reset)
    Resetbt.place(x = 550,y = 430)

    Savebt = ttk.Button(win,text = "Save", command = Save)
    Savebt.place(x = 550,y = 460)

    Loadbt = ttk.Button(win,text = "Load", command = Load)
    Loadbt.place(x = 550,y = 490)

    UpdateMetabt = ttk.Button(win,text = "Update Meta",command = UpdateMeta)
    UpdateMetabt.place(x = 550,y = 520)


    '''

    check1 = tkinter.Checkbutton(win, text="Display", variable=DisplayOption, state='active')    # text为该复选框后面显示的名称, variable将该复选框的状态赋值给一个变量，当state='disabled'时，该复选框为灰色，不能点的状态
    check1.select()     # 该复选框是否勾选,select为勾选, deselect为不勾选
    check1.place(x = 550,y = 575)
    '''
    Calculatebt = ttk.Button(win,text = "Calculate",command = Calculate)
    Calculatebt.place(x = 550,y = 550)

    Contact = tkinter.Label(win,text = "Q&A:   zhiqi.liu@foxmail.com  www.ethernet-engineering.com",width = 50,height = 1)
    Contact.place(x = 10,y = 575)

    win.mainloop()

# Finish Initializing all the UI

# handling xml


# finish handling xml

if __name__ == "__main__":
    main()



