def getGcd(Array):
    Small = Array[0]
    for Digit in Array:
        if Digit < Small:
            Small=Digit

    GCDCandidate = Small
    GCDisFound = False #Greated Common divisor, 最大公约数
    
    while GCDCandidate>0 and GCDisFound == False:
        #检查GCDCandidate是不是 Array中元素的最小公约数


        flag = False
        for Digit in Array:
            
            if Digit % GCDCandidate == 0:
                flag = True
            else:
                flag = False 
                break                
        
        if flag == True:
            GCDisFound = True
            GCD = GCDCandidate

        GCDCandidate = GCDCandidate -1

 #   print('GCD is ',GCD)

    return GCD

def getLcm(Array):
    MDArray=[]
    #GDC = getGcd(Array)
    M = 1
    for digit in Array:
        M = M*digit
 #   print('M is',M)
    for digit in Array:
        MDArray.append(M/digit)
 #   print('MD Array is',MDArray)

    GCDMDArray = getGcd(MDArray)

    Lcm = M/GCDMDArray 
 #   print('Lcm is',Lcm)
    return Lcm
