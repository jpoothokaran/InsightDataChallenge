# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 12:15:15 2018

@author: John Martin
"""

import numpy as np
import time

DATA_FILE = './itcont.txt'

# Step 1: read in data from the .txt file
inputFile = open(DATA_FILE,'r')
pfile = open('./percentile.txt','r')
percentile = int(pfile.read())
outputFile = open('repeat-donors.txt','w')


def parseLine(line):
    parts = line.split('|')
    if (parts[0] and
        parts[7] and
        len(parts[7]) <= 30 and
        len(parts[10])>=5 and
        parts[10].isdigit() and
        parts[13] and
        parts[14] and
        parts[15] == ''):
        
        lineInfo = dict(
            CMTE_ID =parts[0],
            NAME =parts[7],
            ZIP_CODE =int(parts[10][0:5]),
            D_DATE =stringToDate(parts[13]),
            D_AMT =int(parts[14]))
    else:
        lineInfo = None
    
    return lineInfo

def stringToDate(dateString):
    month = int(dateString[0:2])
    day = int(dateString[2:4])
    year = int(dateString[4:8])
    date = { 'day': day,
            'month': month,
            'year': year}
    return date

def isCurrentDateMoreRecent(currentDate, logDate):
    if (currentDate['year'] >= logDate['year']):
        if (currentDate['year'] == logDate['year']):
            if (currentDate['month'] >= logDate['month']):
                if (currentDate['month'] == logDate['month']):
                    if (currentDate['day'] >= logDate['day']):
                        return True
                    return False
                return True
            return False
        return True
    return False

def updateDate(donorLog, donorID, transaction):
    currentDate = transaction['Date']
    if(donorLog.get(donorID) is not None):
        logDate = donorLog[donorID]['Date']
        if(isCurrentDateMoreRecent(currentDate, logDate)):
            donorLog[donorID] = transaction
        else:
            transaction = donorLog[donorID]
    

def addDonorToCampaignInfo(campaignInfo, campaignID, transaction):
    if(campaignID in campaignInfo):
        transactionLists = campaignInfo[campaignID]
    else:
        transactionLists = ([],[],[])
    transactionLists[0].append(transaction['Donor'])
    transactionLists[1].append(transaction['Amount'])
    transactionLists[2].append(transaction['Date'])
    campaignInfo[campaignID] = transactionLists


def getInfo(campaignInfo, campaignID):
    transactionLists = campaignInfo[campaignID]
    donationList = transactionLists[1]
    total = np.sum(donationList)
    number = len(donationList)
    donationList = np.sort(donationList)
    percentileIndex = int(percentile/100.0 * len(donationList))
    percentileNumber = donationList[percentileIndex]
    
    return total, number, percentileNumber


def printCurrentTransaction(campaignInfo, campaignID):
    
    totalAmount, numberOfDonations, percentileNumber = getInfo(campaignInfo, campaignID)
    #print(campaignID[0], campaignID[1], campaignID[2], percentileNumber, totalAmount, numberOfDonations)
    outputFile.write(campaignID[0])
    outputFile.write('|')
    outputFile.write(str(campaignID[1]))
    outputFile.write('|')
    outputFile.write(str(campaignID[2]))
    outputFile.write('|')
    outputFile.write(str(percentileNumber))
    outputFile.write('|')
    outputFile.write(str(totalAmount))
    outputFile.write('|')
    outputFile.write(str(numberOfDonations))
    outputFile.write('\n')

setOfDonors = set()
setOfRepeatDonors = set()
donorLog = {}
campaignInfo = {} #campaignID: transactionList

i = 0
start = time.time()
for singleLine in inputFile:
    
    i+=1
    if i%10000 == 0:
        print(i)
    # Read a single line from file and parse for relevant info
    #singleLine = f.readline()
    singleEntry = parseLine(singleLine)
    
    # Proceed if the entry is valid and comes back as not None
    if(singleEntry is not None):
        
        donorID = (singleEntry['NAME'],singleEntry['ZIP_CODE'])
        currentDate = singleEntry['D_DATE']
        amount = singleEntry['D_AMT']
        recipientID = singleEntry['CMTE_ID']
        
        campaignID = ( recipientID,
                       singleEntry['ZIP_CODE'],
                       currentDate['year'])
        
        transaction = { 'Donor': donorID,
                        'Amount': amount,
                        'Date': currentDate}
        
        if(donorID in setOfRepeatDonors):
            addDonorToCampaignInfo(campaignInfo, campaignID, transaction)
            printCurrentTransaction(campaignInfo, campaignID)
        
        if(donorID in setOfDonors and donorID not in setOfRepeatDonors):
            setOfRepeatDonors.add(donorID)
            updateDate(donorLog, donorID, transaction)
            addDonorToCampaignInfo(campaignInfo, campaignID, transaction)
            printCurrentTransaction(campaignInfo, campaignID)
            
        if(donorID not in setOfDonors):
            setOfDonors.add(donorID)
            donorLog[donorID] = transaction
outputFile.close()
end = time.time()
elapsed = end - start
print('Time Taken:',elapsed)


