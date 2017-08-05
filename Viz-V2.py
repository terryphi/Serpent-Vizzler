%cd /home/robot2/Documents/SSS/c757mnyws00/Sandbox/SS4
import sys
import shutil
import numpy as np
import subprocess
import os
from natsort import natsort_keygen, ns, natsorted
from PIL import Image
import itertools as IT
import time

imSize = 200
fileName = sys.argv

#don't include the ./
toProcessFileName = 'toExec.SSSIN'
u0Radius = 80

scaleFactor = 2.0*u0Radius/ float(imSize) #(units per pixel)
#shutil.copyfile(fileName,'./Serpent-Vizzler/input')
#CLEANUP
#clearImagesFolder()

#files gnerated
#vizzleDepths -> lists deptsh
#cardRGBData -> the RGB data
#writes to vizzleOutputTOt.csv

genTheImages()
gen3DFile()


def gen3DFile():
    #FILE LIST
    #get the image list.
    fileListS1 = os.listdir('./images')
    fileListS2 = [x for x in fileListS1 if 'png' in x and 'vizzle' in x]
    #sort by number.
    fileListS3 = natsorted(fileListS2, key = lambda y: y.lower());


    with open('vizzleDepths','r') as f:
        depthsS1 = f.readlines()
        depthsS2 = [x.rstrip() for x in depthsS1]
        depthsS3 = [float(x) for x in depthsS2]

    #depths with files.
    depthFileL = list(zip(depthsS3,fileListS3))

    #RGB COLOR DATA
    #load the card RGB Data
    with open('cardRGBData','r') as f: rgbDataS1 = [ x.rstrip().split() for x in f.readlines()]
    rgbDataS2 = [(tuple(map(int,tuple(x[0:3]))),x[2]) for x in rgbDataS1]
    #the first element is the scalar value to pass into paraview.
    rgbDataS3 = [(idx+1,) + x for idx,x in enumerate(rgbDataS2)]
    rgbDataS4 = [(0,(0,0,0), 'void')] + rgbDataS3 #could of prepended back in the


    #write a new csv for each mat-num.
    #matNums = [x[0] for x in rgbDataS4]
    #for m in matNums:#
    #    toWriteS1 = [x for x in outputS1 if x[1] == m]
    #    toWriteS2 = ['{0},{1},{2},{3}\n'.format(*x[0],depth,x[1]) for x in toWriteS1]
    #    with open(r'vizzleOutput{0}.csv'.format(m),'w') as f:
    #        f.writelines('X-COORD,Y-COORD,Z-COORD,MAT-NUM\n')
    matNums = [x[0] for x in rgbDataS4]
    output = {}
    output['total'] = []
    for m in matNums: output[m] = []
    for d,f in depthFileL:
        print('working on image {0}'.format(f))
        im = Image.open('./images/' + f)
        imRGB = im.convert('RGB')
        pixels = list(IT.product(range(imSize),range(imSize)))
        #stage 1 is ((X,Y),SCALAR)
        outputS1 = []
        for p in pixels:
            color = imRGB.getpixel(p)
            for mat in rgbDataS4:
                if color == mat[1]:
                    outputS1.append((p,mat[0]))
        #Stage 2 output is ready to write.
        outputS2 = ['{0},{1},{2},{3}\n'.format(x[0][0]*scaleFactor,x[0][1]*scaleFactor,d,x[1]) for x in outputS1]
        output['total'].append(outputS2)

    with open(r'./vizzleOutputTot.csv','w') as f:
        f.writelines('X-COORD,Y-COORD,Z-COORD,MAT-NUM\n')
        for idx, s in enumerate(output['total']):
            print('on idx {0}'.format(idx))
            f.writelines(s)


def clearImagesFolder():
    files = os.listdir('./images')
    for f in files:
        os.remove('./images/' + f)


def genTheImages():
    slices = 100
    global imSize #size of plot
    global u0Radius
    global fileName
    vizzleFileName = 'vizzleFile'
    sssPath = r'/home/robot2/Documents/SSS/c757mnyws00/sss2'
    inputFileDir =  os.getcwd() + '/' + vizzleFileName
    #don't change the stuff below.

    with open('./vizzleDepths','w') as f:
        output = []
        for p in list(np.linspace(-u0Radius,u0Radius,slices)):
            output.append('plot 1 {0} {0} {1}'.format(imSize, p))
            f.write(str(p) + '\n')

    with open(toProcessFileName,'r') as f:
        fileData = f.readlines()

    #first, gen the cell card data.
    matLines = [x for x in fileData if 'mat ' in x]

    rgbData = []
    rgbData = [tuple(x.split()[-3:]) for x in matLines]

    with open('cardRGBData','w') as f:
        f.writelines([' '.join(x) + '\n' for x in rgbData])

    insertAt = [i for i,x in enumerate(fileData) if '%VIZZLE' in x][0]

    fileData[insertAt:insertAt] = output

    #write the cards to the vizzle file.
    with open(vizzleFileName, 'w') as f:
        f.writelines([x + '\n' for x in fileData])

    termLine = '{0} -plot {1}'.format(sssPath,inputFileDir)
    result = subprocess.run(termLine.split(),stdout=subprocess.PIPE)
    resultsToWrite = time.strftime('%c') + '\n' + result.stdout.decode('ascii')
    with open('sssRunOutput.txt','w') as f:
        print(resultsToWrite,file=f)


    #move the files.
    moveList = [x for x in os.listdir() if 'vizzleFile_geom' in x]

    for f in moveList:
        shutil.move(f, './images/' + f)
