import subprocess
import os

class DataTag:
	startPos = 0
	endPos = 0
	text = ""
	def __init__(self, _startPos, _endPos=0, _text=""):
		self.startPos = _startPos
		self.endPos = _endPos
		self.text = _text


class fileInfo:
	def __init__(self, _fileData, _dataTagArray, _pageIndex):
		self.fileData = _fileData
		self.dataTagArray = _dataTagArray
		self.pageIndex = _pageIndex


def pp_char(character):
	return int(character)


def decompress(filename):
	result = subprocess.run(["qpdf\\qpdf.exe", "--qdf", "--object-streams=disable", filename, "qpdf\\temp.pdf"])
	return


def compress(filename):
	result = subprocess.run(["qpdf\\qpdf.exe", "qpdf\\temp.pdf", "--compress-streams=y", filename])
	return


tok1 = 84                      #T
tok2 = [109, 100, 68, 102, 42] #m, d, D, f, *
tok3 = [10, 32]                # , 
tok4 = [40, 91]                #(, [

fakeIndToken = "\\"
endToken = ")"
endBigToken = "]"

token = [tok1, tok2, tok3, tok4]

# endobj..
endObjToken = [101, 110, 100, 111, 98, 106, 10, 10]

# %% Contents for page X
pageToken = [37, 37, 32, 67, 111, 110, 116, 101, 110, 116, 115, 32, 102, 111, 114, 32, 112, 97, 103, 101, 32]
pageEndToken = 10

def giveTagList(filepath, checkDecompress):
	global pageToken, pageEndToken
	global token, endToken, fakeIndToken, endBigToken
	global endObjToken

	if(checkDecompress):
		decompress(filepath)
		#time.sleep(5)
		file = open("qpdf\\temp.pdf", "rb")
	else:
		file = open(filepath, "rb")
	
	fileData = file.read()
	
	pageTokenCounter = 0
	tokenCounter = 0
	endObjTokenCounter = 0
	currentPosition = 0		 #Current position of the pointer in the document. 
	onFirstPage = True		 #Indicates if we are on the first page or not (to do different things in the first page cycle)
	onPageField = False		 #Indicates if we are reading the page number in '%% Contents for page X'.
	onField = False			 #Indicates if we are reading the text of a tag. 
	onBigField = False  	 #Tag field made with square brackets (tag containing other tags) 
	onSmallField = False	 #Field of tag inside onBigField (tag only enclosed in parentheses) 
	onSpecialTag = False	 #Tags of the shape "Td  [("
	fakeInd = False			 #It indicates if we read a '\' character that indicates that the parentheses are text and not tokens of the file to separate tags. 
	pageIndex = {}			 #Page index, where the key is the page number and the value is the index of the array where the corresponding dataTagCollection will be. 
	pageTags = []			 #Array with dataTagCollection for each page. 
	
	#The index in pageTags does not necessarily correspond to the actual page number. We will read that page equivalence from the 
	#pageIndex where the index of the array will be placed in pageTags and the real number of the page as key.
	
	pageCounter = 0     	 #Page counter to see how many pages the pageTags array should have 
	pageNumber = ""			 #The page number that we read in the document, we will use it as a key in the pageIndex dictionary 
	currentPage = ""		 #The current page number. 
	dataTagCollection = []	 #Array of DataTags with all the tags read on the current page. 
	
	for char in fileData:
		currentPosition += 1
		
		#Parser of page number:
		if not onPageField:
			if pp_char(char) == pageToken[pageTokenCounter]:
				pageTokenCounter += 1
			else:
				pageTokenCounter = 0
			if pageTokenCounter == len(pageToken):
				onPageField = True
				if onFirstPage:
					onFirstPage = False
				else:
					try:
						pageTags[pageIndex[currentPage]].extend(dataTagCollection)
					except IndexError:
						pageTags.insert(pageIndex[currentPage], dataTagCollection)
					except KeyError:
						try:
							pageTags[pageCounter].extend(dataTagCollection)
						except IndexError:
							pageTags.insert(pageCounter, dataTagCollection)
					dataTagCollection = []
				pageNumber = ""
				pageTokenCounter = 0
				continue

		if onPageField:
			if pp_char(char) == pageEndToken:
				onPageField = False
				if not pageNumber in pageIndex:
					pageIndex[pageNumber] = pageCounter
					pageCounter += 1
				currentPage = pageNumber
				continue
			pageNumber += chr(char)

		#Parsers of Tags:
		if not onField and not onBigField and not onSpecialTag:
			if tokenCounter==0: 
				if pp_char(char)==token[tokenCounter]:
					tokenCounter += 1
				else:
					tokenCounter = 0
			elif tokenCounter==1:
				if pp_char(char) in token[tokenCounter]:
					tokenCounter += 1
				else:
					tokenCounter = 0
					if pp_char(char)==token[tokenCounter]: tokenCounter+=1
			elif tokenCounter==2:
				if pp_char(char)==token[tokenCounter][0]:
					tokenCounter += 1
				elif pp_char(char)==token[tokenCounter][1]:
					onSpecialTag = True
					tokenCounter += 1
				else:
					tokenCounter = 0
					if pp_char(char)==token[tokenCounter]: tokenCounter+=1
			elif tokenCounter==3:
				if pp_char(char)==token[tokenCounter][0]:
					tokenCounter += 1
				elif pp_char(char)==token[tokenCounter][1]:
					tokenCounter = 0
					onBigField = True
				else:
					tokenCounter = 0
					if pp_char(char)==token[tokenCounter]: tokenCounter+=1

			#Parser of endobj..
			if pp_char(char) == endObjToken[endObjTokenCounter]:
				endObjTokenCounter += 1
			else:
				endObjTokenCounter = 0
			if endObjTokenCounter == len(endObjToken):
				if dataTagCollection:
					try:
						pageTags[pageIndex[currentPage]].extend(dataTagCollection)
					except IndexError:
						pageTags.insert(pageIndex[currentPage], dataTagCollection)
					except KeyError:
						try:
							pageTags[pageCounter].extend(dataTagCollection)
						except IndexError:
							pageTags.insert(pageCounter, dataTagCollection)
				dataTagCollection = []
				endObjTokenCounter = 0
				continue

		if onField:
			if chr(char)==fakeIndToken:
				fakeInd = True
			if chr(char)==endToken and not fakeInd:
				onField = False
				newDataTag.endPos = currentPosition
				if newDataTag.text.strip() != "":
					dataTagCollection.append(newDataTag)
				continue
			if chr(char)!=fakeIndToken:
				fakeInd = False
			newDataTag.text += chr(char)

		if onSpecialTag:
			if tokenCounter==3:
				if pp_char(char)==token[2][1]:
					tokenCounter += 1
				else:
					tokenCounter = 0
					onSpecialTag = False
			elif tokenCounter==4:
				if pp_char(char)==token[2][1]:
					tokenCounter += 1
				elif pp_char(char)==token[3][1]:
					tokenCounter = 0
					onSpecialTag = False
					onBigField = True
				else:
					tokenCounter = 0
					onSpecialTag = False
			elif tokenCounter==5:
				if pp_char(char)==token[3][1]:
					tokenCounter = 0
					onSpecialTag = False
					onBigField = True
				else:
					tokenCounter = 0
					onSpecialTag = False

		if onBigField:
			if chr(char)==fakeIndToken:
				fakeInd = True
			if not onSmallField:
				if pp_char(char)==token[3][0] and not fakeInd:
					onSmallField = True
					newDataTag = DataTag(currentPosition)
					continue
				if chr(char)==endBigToken and not fakeInd:
					onBigField = False
					continue
			else:
				if chr(char)==endToken and not fakeInd:
					onSmallField = False
					newDataTag.endPos = currentPosition
					if newDataTag.text.strip() != "":
						dataTagCollection.append(newDataTag)
					continue
				newDataTag.text += chr(char)
			if chr(char) != fakeIndToken:
				fakeInd = False

		if tokenCounter==len(token) and not onSpecialTag:
			tokenCounter = 0
			onField = True
			newDataTag = DataTag(currentPosition)
	
	if dataTagCollection:
		try:
			pageTags[pageIndex[currentPage]].extend(dataTagCollection)
		except IndexError:
			pageTags.insert(pageIndex[currentPage], dataTagCollection)
		except KeyError:
			try:
				pageTags[pageCounter].extend(dataTagCollection)
			except IndexError:
				pageTags.insert(pageCounter, dataTagCollection)

	file.close()

	print(pageIndex)
	for page in pageTags:
		print(str(len(page)))

	return fileInfo(fileData, pageTags, pageIndex)


def savePdf(filepath, fileInfo, fileData):
	file = open("qpdf\\temp.pdf", "wb")
	
	inTag = False
	listIndex = 0
	currentPosition = 0
	for char in fileData:
		currentPosition += 1
		try:
			if currentPosition <= fileInfo[listIndex].startPos:
				file.write(char.to_bytes(1,"little"))
			if currentPosition == fileInfo[listIndex].startPos:
				file.write(fileInfo[listIndex].text.encode("cp1252"))
				inTag = True
			if inTag and currentPosition < fileInfo[listIndex].endPos:
				continue
			if inTag and currentPosition == fileInfo[listIndex].endPos:
				inTag = False
				listIndex += 1
				file.write(char.to_bytes(1,"little"))
		except IndexError:
			file.write(char.to_bytes(1,"little"))

	file.close()
	compress(filepath)
	os.remove("qpdf\\temp.pdf")
	return
