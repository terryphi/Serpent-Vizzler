import re
import copy
import sys
import itertools as it
import os
import numpy as np
import subprocess
import pandas as pd
import natsort as ns
from PIL import Image
import scipy.misc as spm
import cv2
import matplotlib as mpl
import math
%matplotlib inline

#NB: Make sure the CWD is the vizzle file folder.

inputFileName = 'SS.SSSIN'
sssPath = r'/home/robot3/SSS/c757mnyws00/sss2'
inputFileFullPath=  os.getcwd() + '/' + inputFileName
U0Radius = 90.0 #The size of the 0th universe bounding box.
resolution = 20

def generateImages():
    os.system('rm ./visual/images/visual*')
    with open('SS.SSSIN','r') as f:
        inputFileData = f.readlines()

    plotCards = [f'plot 1 {resolution} {resolution} {x}' for x in np.linspace(-U0Radius, U0Radius,resolution)]

    with open('./visual/visualInputFile','w') as f:
        f.writelines(inputFileData)
        f.writelines('\n'.join(plotCards))

    termLine = '{0} -plot {1}'.format(sssPath,os.getcwd() + '/visual/visualInputFile')
    results = subprocess.run(termLine.split(),stdout=subprocess.PIPE) #PIPE indicates that a ppipe to the stdout should be oppened
    termLine

    with open('./visual/sssRunOutput','w') as f:
        f.writelines(results.stdout.decode('ascii'))

    os.system('mv ./visual/visualInputFile* ./visual/images/')


def genDataFrame(fileList,path):
    fileList = ns.natsorted(fileList, key = lambda y: y.lower());
    finalIdxOfPreviousImage = 0
    df = pd.DataFrame(columns=['X','Y','Z','BGR'])
    for idx,f in enumerate(fileList):
        if idx % 10 == 0:
            print(f'On image {f}')
        image = cv2.imread(f'{path}/{f}')
        z = int(re.search('(\d+).png', f)[1]) #the 1 refers to the first capture group.
        data = []
        for x,y in it.product(range(resolution),range(resolution)):
            imageR = image[y,x,0]
            imageB = image[y,x,1]
            imageG = image[y,x,2]
            data.append([x,y,z,f'{imageR} {imageB} {imageG}'])

        indexData = range(finalIdxOfPreviousImage,finalIdxOfPreviousImage+len(data))
        dfImg = pd.DataFrame(data,indexData,columns=['X','Y','Z','BGR'])
        #make surer I pull out the last index..
        finalIdxOfPreviousImage = dfImg.index[-1]
        df = df.append(dfImg)
    return df



def getRidOfBlackLines(image):
    """get the image through cv2.imread"""
    def getSurroundingPixelsDominateColor(image, p):
        #SETTINGS
        fuel = (0,0,255)
        #DEBUG
        #image = cv2.imread('./visual/images/visualInputFile_geom10.png')
        #p = (17,11)
        ##DEBUG:
        x = p[1]
        y = p[0] #NB: these need to be flipped.
        #maximum height and maximum width in the sense that
        #this is the pixel upon which the maximum is reached.
        #shapee is more like its extent
        height = image.shape[0] - 1 #subtract 1 since it's zero inded
        width = image.shape[1] - 1

        samplePoints = []
        samplePoints.append(image[y,x])
        if x > 0:
            samplePoints.append(image[y,x-1])
        if x < width:
            samplePoints.append(image[y,x+1])
        if y > 0:
            samplePoints.append(image[y-1,x])
        if y < height:
            samplePoints.append(image[y+1,x])
        # corners
        if y > 0 and x > 0:
            samplePoints.append(image[y-1,x-1])
        if y > 0 and x < width:
            samplePoints.append(image[y-1,x+1])
        if y < height and x > 0:
            samplePoints.append(image[y+1,x-1])
        if y < height and x < width:
            samplePoints.append(image[y+1,x+1])

        px = samplePoints
        #compare the pixels.
        pxAsTup = [tuple(x) for x in px]
        colors = list(set([tuple(x) for x in px]))
        colorCounts = [(x,pxAsTup.count(x)) for x in colors if x != (0,0,0)]
        colorCounts
        maxColorCount = max(colorCounts, key = lambda k: k[1])
        #if there are two colors
        if len(colorCounts)== 2:
            if fuel in [x[0] for x in colorCounts]:
                if colorCounts[0][1] == colorCounts[1][1]:
                    maxColorCount = (fuel,1) #the 1 is vestigial.
        return np.array(maxColorCount[0])

    ##DEBUG:
    #os.getcwd()
    #image = cv2.imread('./visual/images/visualInputFile_geom10.png')
    # fix left side
    image[:,0] = image[:,1]
    #fix right side
    image[:,-1] = image[:,-2]
    #fix top
    image[0,:] = image[1,:]
    #fix bottom
    image[-1,:] = image[-2,:]

    mask = np.zeros(image.shape[:2])
    blackPx = []
    for p,v in np.ndenumerate(mask):
        x = p[0]
        y = p[1]
        R = image[x,y,0]
        G = image[x,y,1]
        B = image[x,y,2]
        if R == 0 and G == 0 and B == 0:
            mask[x,y] = 125
            blackPx.append(p)

    blackPx
    newImage = copy.deepcopy(image)
    #NB: Dont' modify the fucking image while I'm filling it!
    for p in blackPx:
        toFill = getSurroundingPixelsDominateColor(image,p)
        newImage[p[0],p[1],:] = toFill
    return newImage




# I have my dataframe.
# Todo:  map rgb onto material number.
# image-space to world-space transformation.
def genProcessedImages():
    generateImages()
    fileList = os.listdir('./visual/images')
    imageFileList = [f'./visual/images/{x}' for x in fileList if 'png' in x]
    imageList = [(x,cv2.imread(x)) for x in imageFileList]
    processedImageList = [('p-'+os.path.basename(x[0]),getRidOfBlackLines(x[1])) for x in imageList]
    os.system('rm ./visual/processedImages/p*')
    for x in processedImageList:
        cv2.imwrite('./visual/processedImages/{}'.format(x[0]),x[1])

def extractMaterialBGRMaps(fileName):
    '''returns a dictioanry in the format (BGR: (index, name)'''
    with open(f'./{fileName}','r') as f:
        data = f.readlines()
    matLines = [x.rstrip() for x in data if 'mat ' in x]
    #use reversed to go from RGB to BGR.
    maps = {' '.join(reversed(x.split()[-3:])) : x.split()[1] for x in matLines}
    return maps

#I now have the processed images.

#maybe implement something to clean up the processed image files.
#serialize the datarame.
def doColorMap(df):
    colorMaps = extractMaterialBGRMaps('SS.SSSIN')
    df['material'] = df.BGR.map(colorMaps)
    indexedMaterialsMap = {v : idx for idx,(k,v) in enumerate(colorMaps.items())}
    df['matNum'] = df.material.map(indexedMaterialsMap)
    return df

genProcessedImages()
fileList = os.listdir('./visual/processedImages/')
fileList = [x for x in fileList if '.png' in x]
fileList = ns.natsorted(fileList, key = lambda y: y.lower());
#ndenumerate

df = genDataFrame(fileList, './visual/processedImages')
df = doColorMap(df)


#do IS to WS transformation
def IStoWS(p,ISDiameter):
    """p is the pixel as an IS location. ISDiamter with the breadth of the IS volume"""
    #DEBUG
    #p = 19
    #ISDiameter = resolution-1
    #ENDDEBUG
    ISCenter = (ISDiameter/2.0)
    scale = (2*U0Radius/ISDiameter) #units per pixel
    #return scale*(p - ISCenter)
    return scale*(p - ISCenter)

df['wsX'] = df.X.apply(lambda p : IStoWS(p,resolution-1)) #subtract 1 from the resolution
df['wsY'] = df.Y.apply(lambda p : IStoWS(p,resolution-1)) #b/c it's 0 indexed and resolution
df['wsZ'] = df.Z.apply(lambda p : IStoWS(p,resolution-1)) #is count-indexed.

df.to_csv('visData.txt')
