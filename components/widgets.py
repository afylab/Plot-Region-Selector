from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

from matplotlib.figure   import Figure
from matplotlib.colorbar import ColorbarBase
#import matplotlib.pyplot as plt
import matplotlib.cm     as cm

from PyQt4 import QtGui as gui, QtCore as core
import sys, random, numpy, matplotlib

class linePlotWidget(gui.QWidget):
    def __init__(self,
                 xData  = []     ,
                 yData  = []     ,
                 size   = [10,10],
                 dpi    = 100    ,
                 parent = None   ,
                 ):
        
        super(linePlotWidget,self).__init__(parent=parent)

        self.xData = xData
        self.yData = yData

        self.figure = Figure(figsize = size, dpi = dpi)
        self.axis   = self.figure.add_subplot(111)
        self.axis.hold(False)
        self.axis.plot(self.xData,self.yData,'ro')

        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout = gui.QVBoxLayout()     # Declare layout
        layout.addWidget(self.toolbar) # add the toolbar first
        layout.addWidget(self.canvas)  # add the canvas second
        self.setLayout(layout)         # set the layout

    def updatePlot(self):
        """Updates/redraws the plot"""
        self.axis.plot(self.xData,self.yData,'ro')
        self.canvas.draw()

    def setData(self,xData,yData):
        self.xData = xData
        self.yData = yData


class colorPlotWidget(gui.QWidget):
    def __init__(self,
                 data   = []     ,
                 size   = [10,10],
                 dpi    = 100    ,
                 parent = None   ,
                 data_units = 'Data units not set',
                 colorbarScale = 1.0,
                 ):

        super(colorPlotWidget,self).__init__(parent)

        self.data   = data
        self.figure = Figure(figsize = size, dpi = dpi)
        self.axis   = self.figure.add_subplot(111)#,aspect='equal')
        self.axis.hold(False)
        self.img = self.axis.imshow(
            self.data,
            aspect='auto',
            interpolation='none',
            origin='lower'
            )
        self.colorbar = self.figure.colorbar(
            self.img,
            pad = 0.0,
            shrink = colorbarScale,
            )

        self.colorbar.formatter.set_powerlimits((0, 0))
        self.colorbar.update_ticks()

        data_min = self.data.min()
        data_max = self.data.max()

        self.canvas  = FigureCanvas(self.figure)
        self.canvas.setParent(self)
        self.toolbar = NavigationToolbar(self.canvas,self)

        # click event
        self.figure.canvas.mpl_connect('button_press_event',self.clickEvent)

        layout = gui.QVBoxLayout()            # Declare layout
        layout.addWidget(self.toolbar)        # add the toolbar first
        layout.addWidget(self.canvas)         # add the canvas second
        self.setLayout(layout)                # set the layout

        # click recording
        self.recordingClicks = False # 
        self.clicks          = []    # list of clicks since recordin began
        self.nTarget         = 0     # number of clicks before returning data
        self.functionCall    = None  # function to pass the result to

        # arrows
        self.arrows = []

    def drawCanvas(self):
        self.canvas.draw()

    def updatePlot(self):
        self.arrows = []
        self.img = self.axis.imshow(
            self.data,
            aspect='auto',
            interpolation='none',
            origin='lower'
            )
        self.canvas.draw()

    def addArrow(self,startPos,displacement):
        arrowLength = numpy.linalg.norm(displacement)
        headWidth  = 0.0
        headLength = 0.0
        self.arrows.append(
            self.axis.arrow(
                startPos[0],
                startPos[1],
                displacement[0],
                displacement[1],
                fc='k',
                ec='k',
                head_width = headWidth,
                head_length = headLength,
                )
            )

    def setData(self,data):
        self.data = data
        self.updatePlot()

    def getClicks(self,nClicks,functionCall):
        self.recordingClicks = True         # start recording clicks
        self.clicks          = []           # empty click list
        self.nTarget         = nClicks      # set the target number
        self.functionCall    = functionCall # set the function to call when target is reached        

    def clickEvent(self,event):
        if not self.recordingClicks:
            return False
        if event.button == 1:
            click_x = event.xdata
            click_y = event.ydata
            print("click %i registered at [%f,%f]"%(1+len(self.clicks),click_x,click_y))
            self.clicks.append([click_x,click_y])
            if len(self.clicks) >= self.nTarget:
                print("Last click recieved, sending data")
                self.updatePlot() # remove old arrows
                self.functionCall(self.clicks)
                self.recordingClicks = False # reset click data
                self.clicsk          = []    #
                self.nTarget         = 0     #
                self.functionCall    = None  #
        #print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(event.button, event.x, event.y, event.xdata, event.ydata))

class textDisplay(gui.QLineEdit):
    def __init__(self,
                 text,
                 pos,
                 width,
                 height=23,
                 parent=None,
                 ):
        super(textDisplay,self).__init__(parent)
        self.setFixedSize(width,height)
        self.move(core.QPoint(pos[0],pos[1]))
        self.setReadOnly(True)
        self.setText(text)

class textInput(gui.QLineEdit):
    def __init__(self,
                 pos,
                 width,
                 height=23,
                 placeholderText='',
                 parent = None
                 ):
        super(textInput,self).__init__(parent)
        self.setFixedSize(width,height)
        self.move(core.QPoint(pos[0],pos[1]))
        self.setPlaceholderText(placeholderText)

class infoBoxWidget(gui.QWidget):
    def __init__(self,
                 pairs       = [],        # list of [[label, value], [], ...]
                 margins     = [0,0,0,0], # [top,bottom,left,right]
                 vSpacing    = 0 ,        # space (in pixels) to put between entries
                 hSpacing    = 0 ,        # space (in pixels) to put between labels and values
                 labelLength = 96,        # Lenght of label boxes, in pixels
                 valueLength = 96,        # Length of value boxes, in pixels
                 entryHeight = 23,        # height of entry boxes
                 pos         = [0,0],     # position
                 parent = None,
                 ):
        super(infoBoxWidget,self).__init__(parent)

        self.pairs        = pairs
        self.topMargin    = margins[0]
        self.bottomMargin = margins[1]
        self.leftMargin   = margins[2]
        self.rightMargin  = margins[3]
        self.vSpacing     = vSpacing
        self.hSpacing     = hSpacing
        self.labelLength  = labelLength
        self.valueLength  = valueLength
        self.entryHeight  = entryHeight
        self.pos          = pos

        self.doUI()

    def updateValue(self,n,newValue):
        self.pairs[n][1]=newValue
        self.values[n].setText(newValue)

    def doUI(self):
        width  = self.labelLength + self.valueLength + self.hSpacing + self.leftMargin + self.rightMargin
        height = self.topMargin + self.bottomMargin + len(self.pairs)*(self.entryHeight + self.vSpacing) - self.vSpacing
        if len(self.pairs) == 0: height += self.vSpacing # zero vertical spaces if number of pairs is 1 or 0
        self.setFixedSize(width,height)
        self.move(core.QPoint(self.pos[0],self.pos[1]))

        self.labels = []
        self.values = []
        for n in range(len(self.pairs)):
            label_x = self.leftMargin
            label_y = self.topMargin + n * (self.vSpacing + self.entryHeight)
            value_x = self.leftMargin + self.labelLength + self.hSpacing
            value_y = self.topMargin + n * (self.vSpacing + self.entryHeight)
            self.labels.append(textDisplay(
                self.pairs[n][0],
                [label_x,label_y],
                self.labelLength,
                self.entryHeight,
                self))
            self.values.append(textDisplay(
                self.pairs[n][1],
                [value_x,value_y],
                self.valueLength,
                self.entryHeight,
                self))

class simpleButton(gui.QPushButton):
    def __init__(self,
                 pos,
                 function,
                 text,
                 width,
                 height,
                 parent=None
                 ):
        super(simpleButton,self).__init__(text,parent)
        self.setFixedSize(width,height)
        self.move(core.QPoint(pos[0],pos[1]))
        self.clicked.connect(function)
        
                 

class dataViewWidget(gui.QWidget):
    def __init__(self,
                 data,
                 imgSize,
                 pos,

                 datasetName = 'Not set',
                 xUnits      = 'Not set',
                 yUnits      = 'Not set',
                 dataUnits   = 'Not set',

                 parent=None,
                 ):
        super(dataViewWidget,self).__init__(parent)

        self.data        = data
        self.imgSize     = imgSize
        self.pos         = pos
        self.datasetName = datasetName
        self.xUnits      = xUnits
        self.yUnits      = yUnits
        self.dataUnits   = dataUnits

        self.imageView = colorPlotWidget(self.data,parent=self)
        self.imageView.setFixedSize(self.imgSize[0],self.imgSize[1])

        infoPairs = [
            ['Dataset name',self.datasetName],
            ['X axis units',self.xUnits     ],
            ['Y axis units',self.yUnits     ],
            ['Data units'  ,self.dataUnits  ],
            ]

        self.infoBox = infoBoxWidget(
            infoPairs,
            [49,4,0,4],4,4,
            parent=self
            )

        self.imageView.move(0,0)
        self.infoBox.move(self.imgSize[0],0)
        self.setFixedSize(
            self.imageView.width()+self.infoBox.width(),
            max([self.imageView.height(),self.infoBox.height()])
            )

        self.move(core.QPoint(self.pos[0],self.pos[1]))

    def setData(self,data):
        self.imageView.setData(data)

















