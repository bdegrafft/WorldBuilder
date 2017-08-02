from PIL import Image, ImageDraw
import numpy as np
import pickle
import os
from scipy import ndimage, spatial
import random


def loadSourceMaps(sourceFolder='SourceMaps'):
    '''Create arrays from a folder of source images, and
       return a new map object with these arrays as layers.
       '''
    sourceFolder = '\\'+sourceFolder+'\\'
    currentPath = os.path.dirname(os.path.abspath(__file__))
    images = os.listdir(currentPath + sourceFolder)
    layerToNameDict = {}
    for im in images:
        name = im[:-4]
        path = currentPath+sourceFolder+im
        if 'Mask' in name:  # 'Image is 1-bit'
            array = np.array(Image.open(path).convert('RGB').convert('1'))
        else:  # 'Assume Image is greyscale'
            array = np.array(Image.open(path).convert('RGB').convert('L'))
        layerToNameDict[name] = array  # For Human-Readability
        fullArray = np.dstack(layerToNameDict.values())
    return layerToNameDict, fullArray


class wrapArray(np.ndarray):
    """numpy Array view that allows for wrapping of out-of-bounds indices"""
    def __new__(cls, inputarr):
        return np.asarray(inputarr).view(cls)

    def __array_finalize__(self, obj):
        return self

    def __getitem__(self, index):
        return np.pad(self, self.shape[0], mode='wrap')[index]


class Layer(object):
    """Single Layer for tracking one variable over the map"""

    def __init__(self, name, array, containsNamableObjects,
                nameFilePath=None,wrapped=False,**kwargs):
        self.name = name
        self.array = array
        self.__dict__.update(kwargs)

        if containsNamableObjects:
            self.names = []
            for v in np.bincount(self.array.flatten()):
                self.names.append('Unnamed {} of Size: {}'.format(self.name[:-4], v))
            self.names[0] = 'None'
        if wrapped:
            self.labelObjects()

    def __getitem__(self, pos):
        index = self.array[pos]
        if hasattr(self, 'names'):
            try:
                return self.names[index]
            except IndexError:
                return 'Unnamed'
        else:
            return index

    def __str__(self):
        return '{} Layer Object'.format(self.name)

    def labelObjects(self):
        '''Labels unique objects in the layer with integer values
        wrapped objects should keep their values across the map'''

        # TODO this is very ugly and also broken

        struct = ndimage.generate_binary_structure(2, 2)
        array, _ = ndimage.label(self.array, struct)
        for value in range(1, 255):
            index = np.where(array[0] == value)[0]
            if len(index):
                for n in [array[-1][n] for n in range(index[0]-1, index[0]+2) if n < array.shape[0]]:
                    if n != 0:
                        array[array == n] = value
            index = np.where(array[:, 0] == value)[0]
            if len(index):
                for n in [array[:, -1][n] for n in range(index[0]-1, index[0]+2) if n < array.shape[1]]:
                    if n != 0:
                        array[array == n] = value
        self.array = np.unique(array, return_inverse=True)[1].reshape(array.shape)



    def loadNamesFromFile(self):
        if nameFilePath is not None:
            self.names = open(nameFilePath,'r').readlines()

    def gauss(self, stdDev, threshold):
        ocean = np.bincount(self.array.flatten()).argmax()
        gauss = ndimage.filters.gaussian_filter(np.where(self.array == ocean, 1.0, 0.0), stdDev, 0)
        DoG = np.where(self.array == ocean, 1, 0)-gauss
        return ndimage.label(np.where(DoG > t, 1, 0))[0]


class Map(object):
    '''Main object for a generated map, contains layer dictionary'''
    def __init__(self, layerDict, fullArray):
        self.fullArray = fullArray  # keep this updated as a @property? too slow?
        self.depth = fullArray.shape[2]
        self.layerDict = layerDict
        self.layers = {}
        self.shape = fullArray.shape[:2]

        for layer in layerDict.keys():
            if 'Mask' in layer:
                containsNamableObjects = True
            else:
                containsNamableObjects = False
            self.layers[layer] = Layer(layer, layerDict[layer], containsNamableObjects)

    def __str__(self):
        return 'Map Object of Size:{} with {} layers'.format(self.shape,len(self.layers))

    def __getitem__(self, pos):
        """Returns data from either a single layer's array, or a slice of the
        whole map. Individual layers may be specified by name as a string or
        or as an index"""

        if str in [type(i) for i in pos]:  # if theres a string somewhere in the slice
            if type(pos) is str:  # only a string corrisponding to a layer was passed
                return self.layers[pos]
            else:
                string = filter(lambda x: type(x) is str, pos)[0]  # string part
                nums = filter(lambda x: type(x) is not str, pos)  # number part
                layerIndex = self.layerDict[pos[0]]
                return self.layerDict[string][nums]
        else:
            return self.fullArray[pos]

    def getTile(self, x, y):
        """Return data from all layers on a x,y coordinate"""#TODO Make this a dictionary, and make a pprint function
        o = {}
        for layer in self.layers.keys():
            o[layer] = str(self.layers[layer][x, y])
        return o

    def addVoronoi(self,name,density):
        h,w = self.shape
        p = [(random.randint(0,h),random.randint(0,w)) for _ in range(density)]
        vor = spatial.Voronoi(p)
        i = Image.new('L', (h, w),255)
        draw = ImageDraw.Draw(i)
        for v in vor.ridge_vertices:
            x1,y1 = vor.vertices[v].astype(int)[0]
            x2,y2 = vor.vertices[v].astype(int)[1]
            if abs(x1-x2) > h//2 or abs(y1-y2) > w//2: # I dont know why this happens
                pass
            else:
                draw.line((x1,y1,x2,y2),fill=0)

        del draw
        a = np.array(i.convert('RGB').convert('L'))
        a = ndimage.label(a)[0]
        a = ndimage.grey_dilation(a,size=(2,2))

        neighbors = {}
        for p1, p2 in vor.ridge_points:
            p1, p2 = vor.points[p1].astype(int),vor.points[p2].astype(int)
            p1, p2 = (p1[1], p1[0]), (p2[1], p2[0])

            try:
                p1, p2 = a[p1], a[p2]
                try:
                    if p2 in neighbors[p1]:
                        pass
                    elif p2 == p1:
                        pass
                    else:
                        neighbors[p1].append(p2)
                except KeyError:
                    neighbors[p1] = [p2]
            except IndexError: pass
            try:
                if p1 in neighbors[p2]:
                    pass
                elif p1 == p1:
                    pass
                else:
                    neighbors[p2].append(p1)
            except KeyError: neighbors[p2] = [p1]

        self.addLayer(name,a,containsNamableObjects=True, neighbors=neighbors)
        #print(np.unique(self.layers['countries'].array))


    def addLayer(self, name, array, containsNamableObjects=False,**kwargs):
        self.layers[name] = Layer(name, array, containsNamableObjects,**kwargs)

    def render(self, layer, loc='C:\\Users\\Brendan\\Documents\\World Builder\\'):
        layer = self[layer]
        x,y = self.shape
        if len(np.unique(layer.array)) == 2:
            o = Image.new('1', (x, y))  # if there are only 2 values, layer is rendered as a bitmap for readability
        else:
            o = Image.new('L', (x, y))
        px = o.load()
        for lx in range(x):
            for ly in range(y):
                px[ly, lx] = int((layer.array[lx, ly]))
        o.save('{}{}.png'.format(loc,layer.name))

    def save(self):
        currentPath = os.path.dirname(os.path.abspath(__file__))
        output = open('{}data.pkl'.format(currentPath, 'wb'))
        pickle.dump(self, output)
        output.close()
