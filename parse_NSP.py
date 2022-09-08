
from math import fabs
import sys
import traceback
import os
import operator
import sys
import random
import unittest
import numpy as np
from numpy import random
import csv
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdd
# import plotly.figure_factory as ff
from datetime import date, timedelta



#from inputdata import read_dat_file

def get_words(line):
    """Return a list of the tokens in line."""
    line = line.replace("\t", " ")
    line = line.replace("\v", " ")
    line = line.replace("\r", " ")
    line = line.replace("\n", " ")
    while line.count("  "):
        line = line.replace("  ", " ")
    line = line.strip()
    return [word + " " for word in line.split(" ")]


def read_dat_file(filename):
    """Return a list containing the data stored in the dat file.

    Single integers or floats are stored as their natural type.

    1-d arrays are stored as lists

    2-d arrays are stored as lists of lists.

    NOTE: the 2-d arrays are not in the list-of-lists matrix format
    that the python methods take as input for constraints.

    """
    ret = []
    continuation = False
    with open(filename) as f:
        for line in f:
            for word in get_words(line):
                if continuation:
                    entity = "".join([entity, word])
                else:
                    entity = word
                try:
                    ret.append(eval(entity))
                    continuation = False
                except SyntaxError:
                    continuation = True
    return ret




global epsilon
epsilon = 1e-8
global epsilon0
epsilon0 = 1e-4
def findKeys(lst, key, ll=[]):

    for i in range(len(lst)):
        dic = lst[i]
        ll.append(dic[key])


class ModelData(object):

    def __init__(self, path=None, path_folder=None, file_type=None):
        """
        Create a new ModelData object to wrap a model_data dictionary with some helper methods.

        Parameters
        ----------

        """
        # os.path.join(path_folder, inst)
        self.path = path
        self.source = os.path.join(path, path_folder, file_type)
        self.file_type = None

        if isinstance(self.source, dict):
            self.data = self.source
        elif isinstance(self.source, str):
            self.data = self._read_from_file(self.source, None)
        elif self.source is None:
            self.data = self.empty_model_data_dict(file_type)
        else:
            raise RuntimeError("Unrecognized source for ModelData")

    def empty_model_data_dict(self, type_file):
        """

        """
        if type_file[0] == 'H':
            return {"week": dict(), "scenario": dict(), "nurseHistory": dict()}
        if type_file[0] == 'S':
            return {'id': dict(), 'numberOfWeeks': dict(), 'skills': dict(), 'shiftTypes': dict(), 'forbiddenShiftTypeSuccessions': dict(), 'contracts': dict(), 'nurses': dict()}
        if type_file[0] == 'W':
            return{'scenario': dict(), 'requirements': dict(), 'shiftOffRequests': dict()}

    def _read_from_file(self, filename, file_type):

        valid_file_types = ['json', 'json.gz', 'm', 'dat']
        if file_type is not None and file_type not in valid_file_types:
            raise Exception("Unrecognized file_type {}. Valid file types are {}".format(
                file_type, valid_file_types))
        elif file_type is None:
            # identify the file type
            if filename[-5:] == '.json':
                file_type = 'json'
            elif filename[-8:] == '.json.gz':
                file_type = 'json.gz'
            elif filename[-2:] == '.m':
                file_type = 'm'
            elif filename[-4:] == '.dat':
                file_type = 'dat'
            else:
                raise Exception(
                    "Could not infer type of file {} from its extension!".format(filename))

        if file_type == 'json':
            import json
            with open(filename) as f:
                data = json.load(f)

        return data

    def read(self, cls, filename, file_type=None):
        """
        Reads data from a file into a new ModelData object

        """
        return cls(source=self._read_from_file(filename, file_type))


class ProbData():
    # Read a NSP instance from an input file

    def __init__(self, path, path_folder, inst):
        self.path_folder = path_folder
        self.inst = inst
        self.path = path
        self.nbJSON = 13
        self.JSONfileList = []
        for i in range(13):
            if i < 3:
                global str1
                str1 = 'H'+str(i)+'-' + path_folder+'-'+str(i)

                globals()[str1] = ModelData(path=self.path,
                                            path_folder=self.path_folder,
                                            file_type=str('H0'+'-' + path_folder+'-'+str(i))+'.json')
                self.JSONfileList.append(
                    globals()['H'+str(i)+'-' + path_folder+'-'+str(i)])
            elif i < 4:
                global str2
                str2 = 'Sn'+'-' + path_folder
                globals()[str2] = ModelData(path=self.path,
                                            path_folder=self.path_folder,
                                            file_type=str('Sc'+'-' + path_folder)+'.json')
                self.JSONfileList.append(globals()['Sn'+'-' + path_folder])
            else:
                global str3
                str3 = 'WD'+'-' + path_folder+'-'+str(i-4)
                globals()[str3] = ModelData(path=self.path,
                                            path_folder=self.path_folder,
                                            file_type=str('WD'+'-' + path_folder+'-'+str(i-4))+'.json')
                self.JSONfileList.append(
                    globals()['WD'+'-' + path_folder+'-'+str(i-4)])

        # read the data in filename
        dataH0 = self.get_json_files()[0].data

        l_h0 = [*dataH0]
        global W0nbAss
        W0nbAss = []
        findKeys(
            dataH0[l_h0[2]], 'numberOfAssignments', W0nbAss)

        global W0nbWWeehend
        W0nbWWeehend = []
        findKeys(
            dataH0[l_h0[2]], 'numberOfWorkingWeekends', W0nbWWeehend)

        global W0LastAssShftType
        W0LastAssShftType = []
        findKeys(
            dataH0[l_h0[2]], 'lastAssignedShiftType', W0LastAssShftType)

        global W0nbCscDays
        W0nbCscDays = []
        findKeys(
            dataH0[l_h0[2]], 'numberOfConsecutiveAssignments', W0nbCscDays)
        global W0LastAssShftTypeOff
        W0LastAssShftTypeOff = []
        findKeys(
            dataH0[l_h0[2]], 'numberOfConsecutiveWorkingDays', W0LastAssShftTypeOff)

        global W0nbCscDaysOff
        W0nbCscDaysOff = []
        findKeys(
            dataH0[l_h0[2]], 'numberOfConsecutiveDaysOff', W0nbCscDaysOff)

        dataH1 = self.get_json_files()[1].data

        l_h1 = [*dataH1]
        global W1nbAss
        W1nbAss = []
        findKeys(
            dataH1[l_h1[2]], 'numberOfAssignments', W1nbAss)

        global W1nbWWeehend
        W1nbWWeehend = []
        findKeys(
            dataH1[l_h1[2]], 'numberOfWorkingWeekends', W1nbWWeehend)

        global W1LastAssShftType
        W1LastAssShftType = []
        findKeys(
            dataH1[l_h1[2]], 'lastAssignedShiftType', W1LastAssShftType)

        global W1nbCscDays
        W1nbCscDays = []
        findKeys(
            dataH1[l_h1[2]], 'numberOfConsecutiveAssignments', W1nbCscDays)
        global W1LastAssShftTypeOff
        W1LastAssShftTypeOff = []
        findKeys(
            dataH1[l_h1[2]], 'numberOfConsecutiveWorkingDays', W1LastAssShftTypeOff)

        global W1nbCscDaysOff
        W1nbCscDaysOff = []
        findKeys(
            dataH1[l_h1[2]], 'numberOfConsecutiveDaysOff', W1nbCscDaysOff)

        dataH2 = self.get_json_files()[2].data

        l_h2 = [*dataH2]
        global W2nbAss
        W2nbAss = []
        findKeys(
            dataH2[l_h2[2]], 'numberOfAssignments', W2nbAss)

        global W2nbWWeehend
        W2nbWWeehend = []
        findKeys(
            dataH2[l_h2[2]], 'numberOfWorkingWeekends', W2nbWWeehend)

        global W2LastAssShftType
        W2LastAssShftType = []
        findKeys(
            dataH2[l_h2[2]], 'lastAssignedShiftType', W2LastAssShftType)

        global W2nbCscDays
        W2nbCscDays = []
        findKeys(
            dataH2[l_h2[2]], 'numberOfConsecutiveAssignments', W2nbCscDays)
        global W2LastAssShftTypeOff
        W2LastAssShftTypeOff = []
        findKeys(
            dataH2[l_h2[2]], 'numberOfConsecutiveWorkingDays', W2LastAssShftTypeOff)

        global W2nbCscDaysOff
        W2nbCscDaysOff = []
        findKeys(
            dataH2[l_h2[2]], 'numberOfConsecutiveDaysOff', W2nbCscDaysOff)

        dataSc = self.get_json_files()[3].data

        l_s = [*dataSc]

        global nbWeeks
        nbWeeks = dataSc[l_s[1]]
        global setSkl
        setSkl = dataSc[l_s[2]]

        global setShifts
        setShifts = []
        findKeys(dataSc[l_s[3]], 'id', setShifts)

        global ShiftsMinAss
        ShiftsMinAss = []
        findKeys(
            dataSc[l_s[3]], 'minimumNumberOfConsecutiveAssignments', ShiftsMinAss)

        global ShiftsMaxAss
        ShiftsMaxAss = []
        findKeys(
            dataSc[l_s[3]], 'maximumNumberOfConsecutiveAssignments', ShiftsMaxAss)

        global forbidShiftPrec
        forbidShiftPrec = []
        findKeys(dataSc[l_s[4]], 'precedingShiftType',
                 forbidShiftPrec)

        global forbidShiftSucc
        forbidShiftSucc = []
        findKeys(dataSc[l_s[4]], 'succeedingShiftTypes', forbidShiftSucc)

        global setContract
        setContract = []
        findKeys(dataSc[l_s[5]], 'id', setContract)

        global contractMinAss
        contractMinAss = []
        findKeys(
            dataSc[l_s[5]], 'minimumNumberOfAssignments', contractMinAss)

        global setShiftsMaxAss
        setShiftsMaxAss = []
        findKeys(
            dataSc[l_s[5]], 'maximumNumberOfAssignments', setShiftsMaxAss)

        global contractMinCscWdays
        contractMinCscWdays = []
        findKeys(
            dataSc[l_s[5]], 'minimumNumberOfConsecutiveWorkingDays', contractMinCscWdays)

        global contractMaxCscWdays
        contractMaxCscWdays = []
        findKeys(
            dataSc[l_s[5]], 'maximumNumberOfConsecutiveWorkingDays', contractMaxCscWdays)
        global contractMinCscWdaysOff
        contractMinCscWdaysOff = []
        findKeys(
            dataSc[l_s[5]], 'minimumNumberOfConsecutiveDaysOff', contractMinCscWdaysOff)

        global contractMaxCscWdaysOff
        contractMaxCscWdaysOff = []
        findKeys(
            dataSc[l_s[5]], 'maximumNumberOfConsecutiveDaysOff', contractMaxCscWdaysOff)

        global contractMaxCscWweekend
        contractMaxCscWweekend = []
        findKeys(dataSc[l_s[5]], 'maximumNumberOfWorkingWeekends',
                 contractMaxCscWweekend)

        global contractCompweekend
        contractCompweekend = []
        findKeys(dataSc[l_s[5]], 'completeWeekends', contractCompweekend)

        global setNurse
        setNurse = []
        findKeys(dataSc[l_s[6]], 'id', setNurse)

        global NurseCntrct
        NurseCntrct = []
        findKeys(dataSc[l_s[6]], 'contract', NurseCntrct)

        global NurseSkll
        NurseSkll = []
        findKeys(dataSc[l_s[6]], 'skills', NurseSkll)
        global dataWD0
        dataWD0 = self.get_json_files()[0+4].data
        global l_wd0
        l_wd0 = [*dataWD0]
        # print("l_wd0l_wd0", l_wd0)
        # print("l_wd0l_wd0", len(l_wd0[1]))
        global l_wd0_req
        l_wd0_req = [*(dataWD0[l_wd0[1]][0])]

        global nbNurses
        nbNurses = len(setNurse)

        global nbDays
        nbDays = 7

        global nbShft
        nbShft = 4

        global nbSkll
        nbSkll = len(setSkl)

    def get_path_folder(self):
        return self.path_folder

    def get_inst(self):
        return self.inst

    def get_path(self):
        return self.path

    def get_json_files(self):
        return self.JSONfileList


def parse():

    

    print(nbNurses)
    print(nbDays)
    print(nbShft)
    print(nbSkll)
    print(len(dataWD0[l_wd0[1]]))
    print("\n")

    for i in range(len(setNurse)):
        # print(setNurse[i], end=' ')
        if NurseCntrct[i] == 'FullTime':
            print(2, end=' ')
        if NurseCntrct[i] == 'PartTime':
            print(0, end=' ')
        if NurseCntrct[i] == 'HalfTime':
            print(1, end=' ')
    print("\n")

    

    for i in range(nbNurses):
        
        for k in range(len(setSkl)):
            if setSkl[k] in NurseSkll[i]:
                 print(1, end=' ')
            else:
                print(0, end=' ')
        print("\n")

    
    for r in range(len(dataWD0[l_wd0[1]])):
        s = setShifts.index(dataWD0[l_wd0[1]][r][l_wd0_req[0]])
        sk = setSkl.index(dataWD0[l_wd0[1]][r][l_wd0_req[1]])
        print(s, end=' ')
        print(sk, end=' ')
        for d in range(nbDays):
            print(dataWD0[l_wd0[1]][r][l_wd0_req[2+d]]['minimum'], end=' ')
            print(dataWD0[l_wd0[1]][r][l_wd0_req[2+d]]['optimal'], end=' ')
        print("\n")
    print("\n")
    for i in range(nbShft):
        print(ShiftsMinAss[i], end=' ')
    print("\n")
    for i in range(nbShft):
        print(ShiftsMaxAss[i], end=' ')

    print("\n")
    print(2)    
    print(0)    
    print(1)
    

    for i in range(3):
        print(contractMinCscWdays[i])
    print("\n")
    


    for i in range(3):
        print(contractMinAss[i], end=' ')
    print("\n")
    for i in range(3):
        print(setShiftsMaxAss[i], end=' ')
    print("\n")
    for i in range(3):
        print(contractMinCscWdays[i], end=' ')
    print("\n")
    for i in range(3):
        print(contractMaxCscWdays[i], end=' ')
    print("\n")
    for i in range(3):
        print(contractMinCscWdaysOff[i], end=' ')
    print("\n")
    for i in range(3):
        print(contractMaxCscWdaysOff[i], end=' ')
    print("\n")
    for i in range(3):
        print(contractMaxCscWweekend[i], end=' ')
    print("\n")
    for i in range(3):
        print(contractCompweekend[i], end=' ')
    print("\n")


    
    #for i in range(len(setShifts)):
    #    print(setShifts[i], end=' ')
    #print("\n")
    #
    #for i in range(len(setSkl)):
    #    print(setSkl[i], end=' ')
    #print("\n")

    


def nsp_parse(filename):
    #
    path = os.getcwd()
    inst = 'H0-' + filename + '-0.json'
    
    

    # Read arc costs from data file (9 city problem)
    data = ProbData(path, filename, inst)
    
    #print("Majid")
    parse()
    



def main():
    
    if len(sys.argv) == 2:
        filename = sys.argv[1]
    else:
        filename = 'n040w4'
    
    
    
    nsp_parse(filename)


if __name__ == "__main__":
    
    main()
