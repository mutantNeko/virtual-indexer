import numpy as np
import random
from collections import defaultdict, deque
import pickle

class VirtualIndexer:
    def __init__(self, maxLength=3, return_per_trigger = False):
        
        self.currentIndex = 0
        self.maxLength = maxLength  
        
        self.masterDict = defaultdict(list)
        self.masterDict['State'] = 1
        
        self.deq = deque(maxlen=self.maxLength)
        
        self.return_per_trigger = return_per_trigger
        
    def trigger(self,data):
        key, val = data

        #Transition to State 2
        if key and self.masterDict.get('State') == 1:

            self.currentIndex = 0
            
            self.masterDict.pop('State')                                        ## Remove State key
            self.masterDict = {int(k):v for k,v in self.masterDict.items()}     ## Cast all keys to int for processing 
            oldKey = [key for key in list(self.masterDict.keys())]              ## Get all state 1 indices
            ## If there are previous items before StateChange
            if len(oldKey) > 0:
                ## Reflect oldKey indices by 0 on the number line 
                maxKey = -(max(oldKey)+1) 
                newKey = np.arange(maxKey, 0)
                ## Create a duplicate of the original dictionary
                masterDictDup = self.masterDict.copy()
                ## Recreate the dictionary at State 2
                self.masterDict.clear()
                self.masterDict = defaultdict(list)
                self.masterDict['State'] = 2  
                ## Transfer all previous data to new dict with new keys
                for j in (newKey):
                    self.masterDict[j] = masterDictDup.get(j-maxKey)
                    self.masterDict = {str(k):v for k,v in self.masterDict.items()}   
                 
            ## If there are no previous items before StateChange
            else:
                ## Create empty Dictionary with State 2
                self.masterDict.clear()
                self.masterDict = defaultdict(list)
                self.masterDict['State'] = 2

        #Transition to State 3   
        elif key and self.masterDict.get('State') == 2:

            ## Remove State Item from dict
            self.masterDict.pop('State')
            
            self.masterDict = {int(k):v for k,v in self.masterDict.items()}        ## Convert keys to int for processing
            oldKey = [key for key in list(self.masterDict.keys())]
            oldKey.sort(reverse=True)                                              ## Reverse the keys
            self.masterDict = {str(k):v for k,v in self.masterDict.items()}

            ## Iterate through the keys to match negative keys to their actual index
            for j in (oldKey): 
                if j<0:
                    ## Find the highest index
                    maxKey = max(oldKey)+1
                    ## Sum the negative index with the highest index to find the corresponding index
                    newKey = maxKey+j
                    ## Get the data of the negative index and append left
                    entry = self.masterDict.get(str(j))
                    if entry == None:
                    	entry = deque(maxlen=self.maxLength)
                    for item in entry:
                        self.deq = self.masterDict.get(str(newKey))
                        self.masterDict[str(newKey)] = entry+self.deq
                        self.masterDict.pop(str(j), None)
                        
            ## Set the State to 3
            self.masterDict['State'] = 3 
            ## Reset the currentIndex
            self.currentIndex = 0
        
        #In State 3    
        elif key and self.masterDict.get('State') == 3:
            ## State 3 is steady state and only reset former index on StateChange
            self.currentIndex = 0

        #System receive result  
        self.deq = self.masterDict.get(str(self.currentIndex))

        if self.deq == None:
            self.deq = deque(maxlen=self.maxLength)
        #Add result into deque
        self.deq.append(val)
        #Update deque into master dict
        self.masterDict[str(self.currentIndex)] = self.deq
        self.currentIndex += 1
        
        
        if self.return_per_trigger:
            return self.masterDict
        else:
            return None
        
    def exportData(self,path):
        
        with open(path, 'wb') as handle:
            pickle.dump(self.masterDict, handle, protocol=pickle.HIGHEST_PROTOCOL)
            
    def loadData(self,path):
        
        with open(path, 'rb') as handle:
            self.masterDict = pickle.load(handle)
        
    def setMaxLength(self,length):
        self.maxLength = length
        
        ## Iterate through all existing data in master dict to update deque maxLength
        # Save current state
        state = self.masterDict.get('State')
        self.masterDict.pop('State')
        ## Iterate through dict items and increase deque maxlen
        for key,dq in self.masterDict.items():
            dq_new = deque(dq,maxlen=length)
            self.masterDict[key] = dq_new
            
        self.masterDict['State'] = state
        
    def getCurrentDict(self):
        return self.masterDict
    
    def getMaxLength(self):
        return self.maxLength
        
    def getcurrentIndex(self):
        return self.currentIndex
        
    def getState(self):
        return self.masterDict.get('State')
        
    def help(self):
        
        print('This function create a virtual index for incoming (trigger,result) value pairs\n')
        print('The indexing works on an anchor(1) basis where the anchor(1) in the trigger input acts as the reference.\n ')
        print('The indexes and the respective number(maxLength) of results will be stored in a dictionary key-value pair.\n')
        print('The dictionary can be exported using the exportData function and loaded using loadData function.\n')
        
        
        
        