#!/usr/bin/python
########################################################################
#
#	Author: Eirik Taylor, December 2015
#
########################################################################
def createCompletePacket(inputData):
	dataStartIndex = 0
	startIndex = 0
	stopIndex = 0
	fullPacketsList = []
	
	while ((startIndex > -1) and (stopIndex > -1)):
		# String together bits and pieces into a full message string between recv calls
		startIndex = inputData.find('<', dataStartIndex)
		stopIndex = inputData.find('>', dataStartIndex)
		if (stopIndex != -1):
			stopIndex = stopIndex + 1
		
		if ((startIndex != -1) and (stopIndex != -1)):
			if (startIndex < stopIndex):
				# Full string ready
				fullPacketsList.append(inputData[startIndex:stopIndex])
				
			elif (createCompletePacket.NewMessageStarted):
				createCompletePacket.NewMessageStarted = False
				stringList = []
				stringList.append(createCompletePacket.TempPacketContents)
				stringList.append(inputData[dataStartIndex:stopIndex])
				fullpacket = ''.join(stringList)
				createCompletePacket.TempPacketContents = ''
				# Full string ready
				fullPacketsList.append(fullpacket)
			
		elif ((not createCompletePacket.NewMessageStarted) and (startIndex != -1)):
			createCompletePacket.NewMessageStarted = True
			createCompletePacket.TempPacketContents = inputData[startIndex:]
			
		elif (createCompletePacket.NewMessageStarted):
			if (stopIndex != -1):
				createCompletePacket.NewMessageStarted = False
				stringList = []
				stringList.append(createCompletePacket.TempPacketContents)
				stringList.append(inputData[dataStartIndex:stopIndex])
				fullpacket = ''.join(stringList)
				createCompletePacket.TempPacketContents = ''
				# Full string ready
				fullPacketsList.append(fullpacket)
			else:
				stringList = []
				stringList.append(createCompletePacket.TempPacketContents)
				stringList.append(inputData)
				createCompletePacket.TempPacketContents = ''.join(stringList)
			
		
		# Set the next search starting point
		if (startIndex > stopIndex):
			dataStartIndex = startIndex
		else:
			dataStartIndex = stopIndex

	return fullPacketsList
createCompletePacket.NewMessageStarted = False
createCompletePacket.TempPacketContents = ''

########################################################################
