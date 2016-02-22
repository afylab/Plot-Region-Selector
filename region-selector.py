from PyQt4 import QtGui as gui, QtCore as core
import sys, numpy, os

from components.widgets import dataViewWidget, textInput, simpleButton, infoBoxWidget

class interface(gui.QDialog):
    def __init__(self):
        super(interface,self).__init__()

        emptyData = numpy.zeros([16,16]).astype(float)

        img_size = [320,320]

        self.dataView = dataViewWidget(
            emptyData,
            img_size,
            [0,0],
            'No set loaded',
            'No set loaded',
            'No set loaded',
            'No set loaded',
            self
            )

        # origin for loading data
        originDataLoading = [img_size[0],0]
        buttonLoadFile=simpleButton(
            originDataLoading,
            self.loadFile,
            "Load data set",
            96,
            24,
            self
            )
        self.inputFileName=textInput(
            [originDataLoading[0],originDataLoading[1]+24],
            196,22,"Filename",self)

        self.nChoices = 1
        self.column = 0
        self.buttonUseColumn=simpleButton(
            [originDataLoading[0]+96,originDataLoading[1]],
            self.changeColumn,
            "Use column",
            64,
            24,
            self
            )
        self.inputColumn = textInput(
            [originDataLoading[0]+96+64,originDataLoading[1]+1],
            36,22,"col",self)
            

        # origin for rectangle selection panel
        originRectangleSelector = [img_size[0],self.dataView.infoBox.height()+22]
        buttonSelectPoints=simpleButton(
            originRectangleSelector,
            self.selectPoints,
            "Select region",
            96,
            24,
            self
            )
        rectangleInfo = [
            ['center'  ,'undefined'],
            ['corner'  ,'undefined'],
            ['vector 1','undefined'],
            ['vector 2','undefined'],
            ]
        self.infoRectangle=infoBoxWidget(
            rectangleInfo,
            [4,4,0,4],4,4,
            valueLength = 192,
            parent = self,
            pos = [originRectangleSelector[0],originRectangleSelector[1]+24]
            )
        self.checkboxForceRectangle=gui.QCheckBox("Force rectangle",self)
        self.checkboxForceRectangle.move(
            originRectangleSelector[0]+96+4,
            originRectangleSelector[1]+4
            )
        self.checkboxForceRectangle.setChecked(True)

        self.show()
        self.setWindowTitle("Region Selector 1.0.0")

    def selectPoints(self):
        print("Rectangle selection has begun. Click on three points on the image to select the rectangle.")
        print("First click will decide one corner of the rectangle.")
        print("The second and third clicks will define the vectors from the first corner to the two adjacent corners.")
        self.dataView.imageView.getClicks(3,self.rectSelect)

    def rectSelect(self,clicks):
        r1 = numpy.array(clicks[0])
        r2 = numpy.array(clicks[1])
        r3 = numpy.array(clicks[2])

        v12 = r2 - r1
        v13 = r3 - r1

        r12 = v12.copy()
        r13 = v13.copy()
        if self.checkboxForceRectangle.checkState(): r13 -= v12 * ((numpy.linalg.norm(v12))**(-2.0))*(numpy.dot(v12,v13))

        print('\n')
        print("Succesfully determined rectangle.")
        print("first corner position          : %s"%str(r1))
        print("vector to first adjacent side  : %s"%str(r12))
        print("vector to second adjacent side : %s"%str(r13))
        print("Location of rectangle center   : %s"%str(r1+0.5*(r12+r13)))

        self.infoRectangle.updateValue(0,str(r1+0.5*(r12+r13)))
        self.infoRectangle.updateValue(1,str(r1))
        self.infoRectangle.updateValue(2,str(r12))
        self.infoRectangle.updateValue(3,str(r13))

        self.dataView.imageView.addArrow(r1,r12)
        self.dataView.imageView.addArrow(r1,r13)
        self.dataView.imageView.addArrow(r1+r12,r13)
        self.dataView.imageView.addArrow(r1+r13,r12)
        self.dataView.imageView.drawCanvas()

    def loadFile(self):
        fileName = self.inputFileName.text()
        if (fileName == ''):
            print("Please enter a filename.")
            return False
        else:
            filepath = os.getcwd()+'\\datasets\\%s'%fileName
            fileExists = os.path.exists(filepath)

            if not fileExists:
                print("File does not exist. Please make sure that the file is placed in the \"datasets\" directory.")
                return False

            else:
                contents = numpy.genfromtxt(filepath,delimiter=',')
                print("File contents loaded.")
                xDim = int(contents[-1][1]+1)
                yDim = int(contents[-1][0]+1)
                self.data = contents.reshape([xDim,yDim,int(contents.shape[1])])

                self.nChoices = self.data.shape[2]-2
                print("Found %s different data columns"%str(self.nChoices))
                print("To change which column is viewed, enter the desired number into the box labeled 'col'")
                print("For this dataset the number must be between 0 and %i"%(self.nChoices - 1))

                self.column = 0 # reset column
                self.dataView.setData(self.data[:,:,2+self.column])

                # update set info
                self.dataView.infoBox.updateValue(0,fileName)  # dataset name
                self.dataView.infoBox.updateValue(1,"unknown") # units are unknown
                self.dataView.infoBox.updateValue(2,"unknown") # since we loaded from a csv files
                self.dataView.infoBox.updateValue(3,"unknown") # (need data value / labrad to tell units)
                

    def changeColumn(self):
        try:
            newColumn = int(self.inputColumn.text())
        except:
            print("Error: you must enter a valid column (integer).")
            return False
        if not (newColumn in range(0,self.nChoices)):
            print("Error: invalid column. Must be between 0 and %i"%(self.nChoices-1))
            return False
        self.column = newColumn
        self.dataView.setData(self.data[:,:,2+self.column])
                
            


if __name__ == '__main__':
    app = gui.QApplication(sys.argv)
    i = interface()
    sys.exit(app.exec_())

