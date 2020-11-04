import os
import QbvCalculator as Cal
from PyQt5 import QtCore, QtGui, QtWidgets

def run():
    '''
    #this main function serves as a interface to the user
    #any other used GUI shall also call the calculator as shown in this main function
    os.system('cls')

    #Datas. This part is the input area, shall be handled manually
    PortData = [['N0P0',100],['N1P0',100],['N2P0',100],['N3P0',100],['N4P0',100],['S0P0',100],['S0P1',100],['S0P2',100],['S1P0',100],['S1P1',100],['S1P2',100],['S1P3',100]]
    StreamData = [['N0P0toN4P0_0',1,1000,2,10,[0,7,11]],['N1P0toN4P0_0',2,1000,5,10,[1,7,11]]]
    AmountofQbvClass = 3
    GuardBandSizeinBits = 1000
    MiniNoQbvSlotSizeinBits = 1000
    #End of data
    

    InputData =[PortData,StreamData,AmountofQbvClass,GuardBandSizeinBits,MiniNoQbvSlotSizeinBits]
    Cal.Calculate(InputData)
    '''
    while True:
        pass     
    
if __name__ == "__main__":


    run()
    


   
    
   

    



