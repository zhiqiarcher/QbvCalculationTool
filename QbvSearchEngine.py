import QbvMath,QbvSystem,copy,TransmissionSelectionAlgorithm,NetworkingEngine

# IPG is not taken into consideration yet.

def Search(System):

        KeepSearching = True
        while KeepSearching:
            result = NetworkingEngine.Networking(System)
            NextIteration = SearchMaster(result,System)
            KeepSearching = NextIteration[1]
        
        return  result

def SearchMaster(result,System):
    System = System
    ContinueSearching = False
    return [System,ContinueSearching]
