%pwd
%cd /home/robot2/Documents/SSS/c757mnyws00/Sandbox/3D-Gen/images/
%cd ..
import os
from natsort import natsort_keygen, ns, natsorted
from PIL import Image
import itertools as IT

bbSize = -7*2
 #same as the BB in the input file.
imSize = 200
scaleFactor = bbSize/ float(imSize) #(units per pixel)

gen3DData()

def gen3DData():
    %cd ./images
    #FILE LIST
    #get the image list.
    fileListS1 = os.listdir()
    fileListS2 = [x for x in fileListS1 if 'png' in x and 'vizzle' in x]
    #sort by number.
    fileListS3 = natsorted(fileListS2, key = lambda y: y.lower());

    %cd ..
    f = open('vizzleDepths','r')
    depthsS1 = f.readlines()
    f.close()
    depthsS2 = [x.rstrip() for x in depthsS1]
    depthsS3 = [float(x) for x in depthsS2]

    #depths with files.
    depthFileL = list(zip(depthsS3,fileListS3))

    #RGB COLOR DATA
    #load the card RGB Data
    with open('cardRGBData','r') as f: rgbDataS1 = [ x.rstrip().split() for x in f.readlines()]
    rgbDataS2 = [(tuple(map(int,tuple(x[0:3]))),x[3]) for x in rgbDataS1]
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


    %cd ./images

    matNums = [x[0] for x in rgbDataS4]
    output = {}
    output['total'] = []
    for m in matNums: output[m] = []
    for d,f in depthFileL:
        print('working on image {0}'.format(f))
        im = Image.open(f)
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

    with open(r'../vizzleOutputTot.csv','w') as f:
        f.writelines('X-COORD,Y-COORD,Z-COORD,MAT-NUM\n')
        for idx, s in enumerate(output['total']):
            print('on idx {0}'.format(idx))
            f.writelines(s)
