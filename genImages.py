%pwd
%cd /home/robot2/Documents/SSS/c757mnyws00/Sandbox/3D-Gen
import numpy as np
import os
import psutil
import shutil

sssPath = r'/home/robot2/Documents/SSS/c757mnyws00/sss2'
fileDir = r'/home/robot2/Documents/SSS/c757mnyws00/Sandbox/3D-Gen/vizzleFile'



bounds = (-51,51)
slices = 100
size = 200

f = open('./vizzleDepths','w')
output = []
for p in list(np.linspace(*bounds,slices)):
    output.append('plot 1 {0} {0} {1}'.format(size, p))
    f.write(str(p) + '\n')

f.close()


f = open('./Unit1','r')
fileData = f.readlines()
f.close()

#first, gen the cell card data.
matLines = [x for x in fileData if 'mat' in x]
rgbData = []
for l in matLines:
    tokens = l.split()
    name = tokens[1]
    vals = []
    #get the index of the rgb token.
    for idx, t in enumerate(tokens):
        if t == 'rgb':
             vals = tokens[idx+1:] #extractthe rgb data.
    rgbData.append('{0} {1} {2} {3}\n'.format(*vals,name))

with open('cardRGBData','w') as f:
    f.writelines(rgbData)


insertAt = [idx for idx, s in enumerate(fileData) if s.startswith('%VIZZLE')][0]
for s in reversed(output):
    fileData.insert(insertAt,s)


f = open('./vizzleFile', 'w')
f.writelines([x + '\n' for x in fileData])
f.close()

termLine = '{0} -plot {1}'.format(sssPath,fileDir)
os.system(termLine)

#move the files.
moveList = [x for x in os.listdir() if 'vizzleFile_geom' in x]

for f in moveList:
    shutil.move(f, './images/' + f)
