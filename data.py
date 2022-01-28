import os
import pickle

from GenshinMember import GenshinMember

class Data:
        
    def getMember(self, memberId):
        filePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "members", "{}.pickle".format(memberId))
        if os.path.isfile(filePath):
            with open(filePath,'rb') as f:
                return pickle.load(f)
        else:
            return GenshinMember(memberId)
    