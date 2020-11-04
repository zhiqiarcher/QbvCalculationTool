import QbvMath,copy

# IPG is not taken into consideration yet.

def TSA(Port):
    #8 means all queues are blocked.
    #Strictly priority
    result = 8
    for i in range(8):
        if len(Port.EgressQueue[7-i])>0:
            result = 7-i
            break

    return result