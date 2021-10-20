from tkinter import *
from tkinter import ttk
#Locales:
import loader

colors = {
			"backgroundColor": "#210b0e",
			"backgroundColorClear": "#281713",
			"detailColor": "#ec1708",
			"textColor": "#fff6f1",
			"butBackgroundColor": "#56423d",
			"butActiveBackColor": "#bea6a0",
			"butTextColor": "#ad0000"
}

root = Tk()
root.title("PdfEdit")
root.geometry("1050x750")
root.configure(bg=colors["backgroundColor"])

pdfStyle = ttk.Style()
pdfStyle.theme_create("pdfTheme", "default", settings={
    ".": {
        "configure":
            {"background": colors['backgroundColor'],
             "foreground": colors['backgroundColor'],
             "troughcolor": colors['backgroundColor'],
             "selectbackground": colors['backgroundColor'],
             "selectforeground": colors['textColor'],
             "fieldbackground": colors['backgroundColorClear'],
             "font": "Consolas 12 bold",
             "bordercolor": colors['detailColor'],
             "borderwidth": 0,
             "relief": 'flat'
             },
        "map": {"foreground": [("disabled", colors['textColor']), ("selected", colors['textColor']), ("pressed", colors['textColor']), ("!pressed", colors['textColor'])],
        		"background": [("disabled", colors['backgroundColor']), ("selected", colors['backgroundColor']), ("pressed", colors['backgroundColor']), ("!pressed", colors['backgroundColor'])]
        	   }
    	},
    "TButton": 	{	"configure": {"activestyle":"None", "borderwidth": 0, "justify":"center"},
    				"map": {"foreground": [("disabled", colors['butTextColor']), ("selected", colors['butTextColor']), ("pressed", colors['butTextColor']), ("!pressed", colors['butTextColor'])],
        					"background": [("disabled", colors['butBackgroundColor']), ("selected", colors['butBackgroundColor']), ("pressed", colors['butActiveBackColor']), ("!pressed", colors['butBackgroundColor'])]}
    			},
	"TScrollbar": 	{
						"configure": {"foreground":colors['detailColor'], "background":colors['butBackgroundColor'], "troughcolor":colors['butBackgroundColor']},
						"map": {"background":[("disabled", colors['detailColor']), ("selected", colors['detailColor']), ("pressed", colors["detailColor"]), ("!pressed", colors['detailColor'])]}
					},
	})
pdfStyle.theme_use("pdfTheme")

fileInfo = 0
openedFile = False
entryList = []
elementsToDestroy = []
autoDecompress = BooleanVar(value=True)
currentPage = 1

def updateTextChanges():
	global currentPage, entryList, fileInfo
	index = 0
	for entry in entryList:
		fileInfo.dataTagArray[fileInfo.pageIndex[str(currentPage)]][index].text = entry.get()
		index += 1
	return


def deleteAllEntries():
	global entryList, elementsToDestroy
	for entry in entryList:
		entry.destroy()
	entryList = []
	for element in elementsToDestroy:
		element.destroy()
	elementsToDestroy = []
	return


def showPage():
	global fileInfo, entryList, scrollable_frame, currentPage, fileLabel, canvas
	try:
		for tag in fileInfo.dataTagArray[fileInfo.pageIndex[str(currentPage)]]:
			entryBorder1 = Frame(scrollable_frame, bg=colors['backgroundColor'])
			entryBorder2 = Frame(entryBorder1, bd=1, bg=colors['detailColor'])
			tagEntry = Entry(entryBorder2,
						bg=colors['backgroundColor'],
						fg=colors['textColor'],
						font='Consolas 12 bold',
						cursor="xterm",
						selectbackground=colors['butActiveBackColor'],
						selectforeground=colors['textColor'],
						insertbackground=colors['textColor'],
						relief='flat',
						width=canvas.winfo_width()
						)
			tagEntry.insert(0, tag.text)
			entryBorder1.pack(fill="both", expand=True)
			entryBorder2.pack(fill="both", expand=True)
			tagEntry.pack(fill="both", expand=True)
			entryList.append(tagEntry)
			elementsToDestroy.append(entryBorder1)
			elementsToDestroy.append(entryBorder2)
		fileLabel.config(text = str(currentPage) + "/" + str(len(fileInfo.pageIndex)))
	except KeyError:
		return
	return


def saveButton(fileLoc):
	global fileInfo
	allTagsArray = []
	updateTextChanges()
	for page in fileInfo.dataTagArray:
		for tag in page:
			allTagsArray.append(tag)
	loader.savePdf(fileLoc, allTagsArray, fileInfo.fileData)
	return


def prevPage():
	global currentPage, fileLabel, canvas, fileInfo, openedFile
	if openedFile:
		updateTextChanges()
		deleteAllEntries()
		if currentPage > 1:
			currentPage -= 1
		else:
			currentPage = len(fileInfo.pageIndex)
		showPage()
		canvas.yview_moveto(0)
	return


def nextPage():
	global currentPage, fileLabel, canvas, fileInfo, openedFile
	if openedFile:
		updateTextChanges()
		deleteAllEntries()
		if currentPage < len(fileInfo.pageIndex):
			currentPage += 1
		else:
			currentPage = 1
		showPage()
		canvas.yview_moveto(0)
	return


def openFile(filepath):
	global fileInfo, autoDecompress, fileLabel, openedFile
	global saveBut, prevBut, nextBut
	fileInfo = loader.giveTagList(filepath, autoDecompress.get())
	showPage()
	openedFile = True
	saveBut.config(state = NORMAL)
	prevBut.config(state = NORMAL)
	nextBut.config(state = NORMAL)

### Adresses Bar: ###
fileBar = Frame(root, bg=colors['backgroundColor'])
fileLabel = ttk.Label(fileBar, anchor="nw", text="File:")

autoDecompressCheck = Checkbutton(fileBar, 
									text="Auto-Decompress", 
									variable=autoDecompress, 
									font='Consolas 8 bold', 
									relief=FLAT, 
									bg=colors['butBackgroundColor'], 
									fg=colors['backgroundColor'],
									activebackground=colors['butBackgroundColor'],
									activeforeground=colors['backgroundColor']
									)

#Adress bar:
fileLocationBorder1 = Frame(fileBar, bg=colors['backgroundColor'])
fileLocationBorder2 = Frame(fileLocationBorder1, bd=1, bg=colors['detailColor'])
fileLocation = Entry(fileLocationBorder2,
					bg=colors['backgroundColor'],
					fg=colors['textColor'],
					font='Consolas 12 bold',
					cursor="xterm",
					selectbackground=colors['butActiveBackColor'],
					selectforeground=colors['textColor'],
					insertbackground=colors['textColor'],
					relief='flat',
					width=50
					)

fileLocation.bind('<Return>', lambda event:openFile(fileLocation.get()))

#Button to open the file:
openFileButBorder1 = Frame(fileBar, bg=colors['backgroundColor'])
openFileButBorder2 = Frame(openFileButBorder1, bd=1, bg=colors['detailColor'])
openFileBut = ttk.Button(openFileButBorder2,text="Open",command=lambda:openFile(fileLocation.get()))

fileBar.pack(pady=10, padx=5, fill=X)
autoDecompressCheck.grid(padx=(2, 10), row=0, column=0, sticky='w')
fileLabel.grid(padx=5, row=0, column=1)

fileLocationBorder1.grid(padx=2, row=0, column=2, sticky='ew')
fileLocationBorder2.pack(fill=X)
fileLocation.pack(fill=X)

openFileButBorder1.grid(padx=2, row=0, column=3, sticky='e')
openFileButBorder2.pack()
openFileBut.pack()

### FRAME WITH THE ENTRIES ARRAY: ###
container = ttk.Frame(root, width=1020, height=650)
canvas = Canvas(container, width=1020, height=650, bg=colors['backgroundColor'])
scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

def mousewheel(event):
	global canvas
	canvas.yview_scroll(int(-1*(event.delta/120)), "units") 


scrollable_frame.bind_all("<MouseWheel>", mousewheel)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

container.pack(fill="both", expand=True)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

### FILE SAVE BUTTON: ###
bottomFrame = Frame(root,  bg=colors['backgroundColor'])

saveButBorder1 = Frame(bottomFrame, bg=colors['backgroundColor'])
saveButBorder2 = Frame(saveButBorder1, bd=1, bg=colors['detailColor'])
saveBut = ttk.Button(saveButBorder2,text="Save",command=lambda:saveButton(fileLocation.get()))

# Menu to change pages:
pageButtonsFrame = Frame(bottomFrame, bg=colors['backgroundColor'])

prevButBorder1 = Frame(pageButtonsFrame, bg=colors['backgroundColor'])
prevButBorder2 = Frame(prevButBorder1, bd=1, bg=colors['detailColor'])
prevBut = ttk.Button(prevButBorder2,text=" < ",command=lambda:prevPage())

fileLabel = ttk.Label(pageButtonsFrame, anchor="nw", text="-")

nextButBorder1 = Frame(pageButtonsFrame, bg=colors['backgroundColor'])
nextButBorder2 = Frame(nextButBorder1, bd=1, bg=colors['detailColor'])
nextBut = ttk.Button(nextButBorder2,text=" > ",command=lambda:nextPage())

bottomFrame.pack(pady=10)

saveButBorder1.grid(row=0, column=0)
saveButBorder2.pack()
saveBut.pack()

pageButtonsFrame.grid(padx=(200, 5), row=0, column=1, sticky="e")

prevButBorder1.grid(padx=5, row=0, column=0)
prevButBorder2.pack()
prevBut.pack()

fileLabel.grid(row=0, column=1)

nextButBorder1.grid(padx=5, row=0, column=2)
nextButBorder2.pack()
nextBut.pack()

saveBut.config(state = DISABLED)
prevBut.config(state = DISABLED)
nextBut.config(state = DISABLED)

root.bind('<Prior>', lambda event:prevPage())
root.bind('<Next>', lambda event:nextPage())

root.mainloop()
