# Uses the test equipment communication scheme like in startCommV2.py

# The goal of this code is to accomplish a reliable initialization autoscale
# before the sweep begins. The autoscale will be in the time and voltage domain

# This code will let the user input amplitude, frequency and phase data for both
# channel 1 and channel 2. Channel 1 and channel 2 will be uncoupled, but
# frequency will remain constant between channel 1 and channel 2.

#This code will query the amplitude for both channels, frequency, and phase data.
#User will be asked if they want to enter new data, to which the user will respond wes or no.

import pyvisa as visa
import numpy as np
import time
import matplotlib.pyplot as plt
import math
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import inquirer

SLEEP_TIME = 0.1
DWELL_TIME = 0.25
WAIT_TIME = 0.75

INIT_TDIV_IND = 16

TIME_DIV = ['1NS', '2NS', '5NS', '10NS', '20NS', '50NS',
            '100NS', '200NS', '500NS', '1US', '2US',
            '5US', '10US', '20US', '50US', '100US',
            '200US', '500US', '1MS', '2MS', '5MS',
            '10MS', '20MS', '50MS', '100MS', '200MS',
            '500MS', '1S', '2S', '5S', '10S', '20s', '50S']

#Time divisions in Nanoseconds
TIME_DIV_FLT = [1E-9, 2E-9, 5E-9, 10E-9, 20E-9, 50E-9, 100E-9, 200E-9, 500E-9, 1000E-9,
                2000E-9,5000E-9, 10000E-9, 20000E-9, 50000E-9, 100000E-9, 200000E-9,
                500000E-9, 1000000E-9, 2000000E-9, 5000000E-9, 10000000E-9, 20000000E-9,
                50000000E-9, 100000000E-9, 200000000E-9, 500000000E-9, 1000000000E-9,
                2000000000E-9,5000000000E-9, 10000000000E-9, 20000000000E-9, 50000000000E-9]

#-------------------INSTRUMENT COMMAND FUNCTIONS------------------------------
#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------

def send_cmd(instr, cmd):
    #sends command to instrument.
    #cmd is a string, instr is a visa object
    instr.write(cmd)
    time.sleep(SLEEP_TIME)

def ask_cmd(instr, cmd):
    #queries information from the instrument.
    #cmd is a string, instr is a visa object
    resp = instr.query(cmd)
    time.sleep(SLEEP_TIME)
    return resp

def scopeON(scope):
    #Turn Scope Traces on
    scope.write('C1:TRA ON')
    time.sleep(DWELL_TIME)
    scope.write('C2:TRA ON')

def scopeOFF(scope):
    #Turn Scope Traces on
    scope.write('C1:TRA OFF')
    time.sleep(DWELL_TIME)
    scope.write('C2:TRA OFF')

def genON(gen):
    #Turn Scope Traces on
    send_cmd(gen, 'OUTP1 ON')
    time.sleep(DWELL_TIME)
    send_cmd(gen, 'OUTP2 ON')

def genOFF(gen):
    #Turn Scope Traces OFF
    send_cmd(gen, 'OUTP1 OFF')
    time.sleep(DWELL_TIME)
    send_cmd(gen, 'OUTP2 OFF')

    
#-------------------INSTRUMENT CONNECTION FUNCTIONS------------------------------
#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------

def openResources():
    rm = visa.ResourceManager()
    recs = rm.list_resources()
    # Convert recources to list type  and add 'enter manual' option to the list
    recsL = list(recs)
    recsL.append("Enter Manual")
    print('\n')
    return rm, recsL

def getAddressString(instr, rec):
    print('___________________'+instr+' Selection__________________')
    getInstr = getEquipString(instr, rec)
    #ask for user's input if they selected 'enter manual'
    if (getInstr['instrument'] == 'Enter Manual'):
        manual = input("Enter Generator's TCPIP Address: ")
        print('\n')
        getInstr['instrument'] = manual
    return getInstr

def openCommunication(rm, instrDict):
    #Establish Connections with instruments
    instr = rm.open_resource(instrDict['instrument'])
    return instr

def getEquipString(instr, recsL):
    #pass string of instrument type and list of resources
    question = [
      inquirer.List('instrument',
                    message="Choose " + instr + ", or choose ENTER MANUAL: ",
                    choices = recsL,
                ),
    ]
    answer = inquirer.prompt(question)
    return (answer)

def generatorVerification(gen):
    #Initialization routine of the generator. Verification that communication
    #is established. Cycles Output 1 ON then OFF, then does the same with
    #Output 2

    #Output 1
    send_cmd(gen, 'OUTP1 ON')
    time.sleep(DWELL_TIME)
    send_cmd(gen, 'OUTP1 OFF')
    #Output 2
    send_cmd(gen, 'OUTP2 ON')
    time.sleep(DWELL_TIME)
    send_cmd(gen, 'OUTP2 OFF')

def oscilloscopeVerification(scope):
    #Initialization routine of the oscilloscope. Verification that communication
    #is established. Cycles Channel 1 ON then OFF, then does the same with
    #Channel 2

    #Channel 1
    scope.write('C1:TRA ON')
    time.sleep(DWELL_TIME)
    scope.write('C1:TRA OFF')
    #Channel 2
    scope.write('C2:TRA ON')
    time.sleep(DWELL_TIME)
    scope.write('C2:TRA OFF')


def establishInstrument():
    rm, recsList = openResources()
    #Ask user to select the resource for GENERATOR and Establish Communication
    genStr = getAddressString("GENERATOR", recsList)
    gen = openCommunication(rm, genStr)
    genInfo = ask_cmd(gen, '*IDN?')
    print(genInfo)
    generatorVerification(gen)
    print('Connection Established')
    print('\n')

    #Ask user to select the resource for OSCILLOSCOPE and Establish Communication
    scopeStr = getAddressString("OSCILLOSCOPE", recsList)
    scope = openCommunication(rm, scopeStr)
    scopeInfo = ask_cmd(scope, '*IDN?')
    print(scopeInfo)
    oscilloscopeVerification(scope)
    print('Connection Established')
    print('\n')
    return gen, scope

#------------------------AUTOSCALER FUNCTIONS-----------------------------------
#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------

def setParam(instr, value, channel, typ):
    #Generator Setup Function.
    
    #instr -- instrument object
    #Value -- value of the parameter, integer or float
    #channel -- string, "Channel 1" or "Channel 2"
    #typ -- string, setting type: Vpp, frequency, or phase
    chStr = 'SOUR1'
    if (channel == 'Channel 2'):
        chStr = 'SOUR2'
    if (typ == 'Amplitude'):
        send_cmd(instr, ':'+chStr+':VOLT '+str(value))
    if (typ == 'Frequency'):
        send_cmd(instr, ':'+chStr+':FREQ '+str(value))
    if (typ == 'Phase'):
        send_cmd(instr, ':'+chStr+':PHAS '+str(value))

def coupleOutputs(instr):
    send_cmd(instr, ':SOUR1:TRACK ON')
    send_cmd(instr, ':SOUR1:PHAS:INIT')
    send_cmd(instr, ':SOUR2:PHAS:SYNC')

def checkTDIV(scope, freq):
    #Ask the scope for it's current time division
    tdv = ask_cmd(scope, 'TIME_DIV?')
    tdvflt = float(tdv[5:-2])
    curTDIV = TIME_DIV_FLT.index(tdvflt)  
    newInd = curTDIV
        
    #Automatically scales time scale to maintain proper zoom on the signals
    while True:
        if float(freq) >= (5/14)*(1/TIME_DIV_FLT[newInd]):
            newInd = newInd - 1
            print("Entered first conditional. New Index: " + str(newInd))
            continue
        elif float(freq) <= (2/14)*(1/TIME_DIV_FLT[newInd]):
            newInd = newInd + 1
            print("Entered second conditional. New Index: " + str(newInd))
            continue
        else:
            break
        
    if (newInd != curTDIV):
        curTDIV = newInd
        send_cmd(scope, 'TDIV ' + TIME_DIV[curTDIV])
        time.sleep(DWELL_TIME)

def checkVDIV(scope):
    checkAgain1 = True
    checkAgain2 = True
    while checkAgain1:
        amplC1str = ask_cmd(scope, 'C1:PAVA? PKPK')
        amplC1 = float(amplC1str[amplC1str.find(',')+1:-2])
        vdivC1 = amplC1 / 7
        send_cmd(scope, 'C1:VDIV '+str(vdivC1))
        amplC1str2 = ask_cmd(scope, 'C1:PAVA? PKPK')
        amplC12 = float(amplC1str2[amplC1str2.find(',')+1:-2])
        vdivC12 = amplC12 / 7
        if (abs(1-(vdivC1/vdivC12))<= 0.01):
            checkAgain1 = False

    while checkAgain2:
        amplC2str = ask_cmd(scope, 'C2:PAVA? PKPK')
        amplC2 = float(amplC2str[amplC2str.find(',')+1:-2])
        vdivC2 = amplC2 / 7
        send_cmd(scope, 'C2:VDIV '+str(vdivC2))
        amplC2str2 = ask_cmd(scope, 'C2:PAVA? PKPK')
        amplC22 = float(amplC2str2[amplC2str2.find(',')+1:-2])
        vdivC22 = amplC22 / 7
        if (abs(1-(vdivC2/vdivC22)) <= 0.01):
            checkAgain2 = False

            
#------------------------MEASUREMENT FUNCTIONS-----------------------------------
#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------

def defineParameters(scope):
    send_cmd(scope, 'PACU PKPK,C1')
    send_cmd(scope, 'PACU PKPK,C2')
    send_cmd(scope, 'PACU FREQ,C1')
    send_cmd(scope, 'MEAD PHA,C1-C2')

def resetStats(scope):
    send_cmd(scope, 'PASTAT ON')
    time.sleep(WAIT_TIME)

def measParams(scope):
    resetStats(scope)
    meas1 = ask_cmd(scope, 'PAVA? STAT1').split(',')[3]
    meas2 = ask_cmd(scope, 'PAVA? STAT2').split(',')[3]
    #meas3 = ask_cmd(scope, 'PAVA? STAT3').split(',')[3]
    meas4 = ask_cmd(scope, 'PAVA? STAT4').split(',')[3]
    measFlt1 = float(meas1[:-1])
    measFlt2 = float(meas2[:-1])
    #measFlt3 = float(meas3[:-2])
    measFlt4 = float(meas4[:-6])
    measFlt = [measFlt1, measFlt2, measFlt4]
    return measFlt

'''
Examples of measurment command and responses

scope.query("PAVA? STAT1")
'PAVA STAT1 C1 PKPK:cur,5.08E+00V,mean,5.09E+00V,min,5.04E+00V,max,5.12E+00V,std-dev,1.91E-02V,count,664\n'

 scope.query("PAVA? STAT1").split(",")[3]
'5.09E+00V'

scope.query("PAVA? STAT2").split(",")[3]
'5.08E+00V'

scope.query("PAVA? STAT3").split(",")[3]
'5.00E+03Hz'

scope.query("PAVA? STAT4").split(",")[3]
'92.39degree'
'''
#---------------------------SWEEP FUNCTIONS-------------------------------------
#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------
def sweep(gen, scope, ampl, start, stop, length):
    listFreq = []
    amplListC1 = []
    amplListC2 = []
    phaseList = []

    # Initializations
    genON(gen)
    defineParameters(scope)
    coupleOutputs(gen)
    
    #generate a list of frequencies
    lstFrq = np.geomspace(start, stop, length, endpoint=True)
    for i in range(length):
        listFreq.append("%.2f" % lstFrq[i])

    #Set Amplitude
    send_cmd(gen, ':SOUR1:VOLT ' + str(ampl))
    send_cmd(gen, 'SOUR1:FREQ '+listFreq[0])

    #Ask User to Set Voltage divisions on the scope
    print("Set Voltage and Time divisions on scope so both waveforms are clearly visible within the scope's screen.")
    input("Press ENTER to Continue: ")

    #Sweep with data acquisition
    for j in range(length):
        send_cmd(gen, 'SOUR1:FREQ '+listFreq[j])
        #Autoscale
        checkTDIV(scope, listFreq[j])
        checkVDIV(scope)
        #Reset Statistics before measurement
        amplC1, amplC2, phase = measParams(scope)
        #Append information to list
        amplListC1.append(amplC1)
        amplListC2.append(amplC2)
        phaseList.append(phase*(-1))
        #Adjust Vertical scaling
        print("Measurement Complete: " +str(j))
        
    return amplListC1, amplListC2, phaseList, listFreq


#----------------------------PLOT FUNCTION---------------------------------------
#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------
    
def plotBode(mag, pha, fre):
    plt.figure()
    
    #Top Plot: Magnitude Response
    plt.subplot(211)
    plt.plot(fre, mag)
    plt.xscale('log')
    plt.title('Magnitude(dB)')
    plt.grid(True)

    #Bottom Plot: Frequency Response
    plt.subplot(212)
    plt.plot(fre, pha)
    plt.xscale('log')
    plt.title('Phase')
    plt.xlabel('Frequency')
    plt.grid(True)

    #Show Plot
    plt.show()
    
#----------------------------MAIN FUNCTION---------------------------------------
#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------
    
def main():
    #Establish communication with the instruments
    gen, scope = establishInstrument()
    
    # Turn Scope Traces ON
    scopeON(scope)

    # Set Initial Horizontal Setting
    send_cmd(scope, 'TDIV ' + TIME_DIV[INIT_TDIV_IND])

    run = True
    while run:
        #Ask User to input Amplitude for channel 1 and 2, Phase and Frequency
        # Vpp Channel 1
        ampl = input('Signal Generator Amplitude (Vpp)?: ')
        freqStart = input('Start Frequency?: ')
        freqStop = input('Stop Frequency?: ')
        points = input('Number of data points?: ')
        
        #Sweep
        ampC1, ampC2, pha, freq = sweep(gen,
                                          scope,
                                          ampl,
                                          float(freqStart),
                                          float(freqStop),
                                          int(points))


        #Convert frequency list from string to float
        freFl = []
        for i in range(len(freq)):
            freFl.append(float(freq[i]))

        #convert amplitude lists to magnitude list in dB
        mag = []
        for i in range(len(freq)):
            mag.append(20*math.log10(ampC2[i]/ampC1[i]))

        #Export Data to an Excel File
        dataList = list(zip(ampC1, ampC2, mag, pha, freFl))
        df = pd.DataFrame(dataList,
                          columns = ['Ampl C1', 'Ampl C2', 'Mag (dB)','Phase', 'Frequency'])
        
        export_file_path = filedialog.asksaveasfilename(defaultextension='.xlsx')
        df.to_excel(export_file_path, index = False, header=True)
        
        #Create the Bode Plot
        plotBode(mag, pha, freFl)
        
        #Run Again?
        answer = input("Would you like to try again?: ").lower()
        while True:
            if answer == 'yes' or answer == 'YES' or answer == 'Y' or answer == 'y':
                run = True
                print('\n')
                break
            elif answer == 'no' or answer == 'NO' or answer == 'N' or answer == 'n':
                run = False
                scopeOFF(gen)
                genOFF(gen)
                print('\n')
                break
            else:
                answer = input('Incorrect option. Type "YES" to try again or "NO" to leave": ').lower()
          
if __name__ == '__main__':
    main()



