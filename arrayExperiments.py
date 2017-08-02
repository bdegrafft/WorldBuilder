import numpy as np
import random
from scipy import ndimage,spatial
from PIL import Image, ImageDraw


a = np.zeros([2100,2100],dtype=bool)
a[1795,1019]=True

def getNeighbors(array,point,size):
    """Return list of True x,y coordinates within size number of tiles"""
    x,y=point[0],point[1]+1
    relative=zip(*np.where(array[x-size:x+size+1,y-size:y+size+1]==False))
    return [(p[0]-size+x,p[1]-size+y) for p in relative]




def drawVoronoi(size,density):
    h,w=(size)
    p=[(random.randint(0,h),random.randint(0,w)) for _ in range(density)]
    vor=spatial.Voronoi(p)
    i= Image.new('L', (h, w),255)
    draw=ImageDraw.Draw(i)
    for v in vor.ridge_vertices:
        x1,y1=vor.vertices[v].astype(int)[0]
        x2,y2=vor.vertices[v].astype(int)[1]
        if abs(x1-x2)>h//3 or abs(y1-y2)>w//3:# I dont know why this happens
            pass
        else:
            draw.line((x1,y1,x2,y2),fill=0)
    del draw

    a=np.array(i.convert('RGB').convert('L'))
    a=ndimage.label(a)[0]
    a=ndimage.grey_dilation(a,size=(2,2))

    n={}
    for p1,p2 in vor.ridge_points:
        p1,p2=vor.points[p1].astype(int),vor.points[p2].astype(int)
        p1,p2=(p1[0],p1[1]),(p2[0],p2[1])
        p1,p2=a[p1],a[p2]
        try: n[p1].append(p2)
        except KeyError: n[p1]=[p2]
        try: n[p2].append(p1)
        except KeyError: n[p2]=[p1]
    print (n)
    return a
