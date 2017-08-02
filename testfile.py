import pickle
from ParseImage import loadSourceMaps, Map
import numpy as np
from random import choice
import re
from ParentClasses.agent import *
from scipy import ndimage

sourcePath = 'C:\\Users\\Brendan\\Documents\\World Builder\\'


def loadMap(fn):
    return pickle.load(open(sourcePath+fn, "rb"))


board = Map(*loadSourceMaps())

board.addVoronoi('countries',100)



print (board['countries'].__dict__)
coast =np.logical_and(np.where(board['landMask'].array!=0,True,False),np.where(board['elevation'].array<=100,True,False))
coast= np.logical_or(board['riverMask'].array,coast)






#print (board.getTile(1050,930))

#board.render('countries')
#
# s='abcd'
# civs=[]
#
# for name in s:
#     civs.append(Civilization(name))
#
#
# for _ in range(5):
#     for c in civs:
#         c.expand(10000,coast)
#         coast = np.where(coast-c.territory==1,True,False)
#
# for c in civs:
#     board.addLayer(c.name,c.territory)
#     board.render(c.name)
#
# board.addLayer('coast',coast)
# board.render('coast')
#
# civs=[]


# for l in 'abcdef':
#     civs.append(Civilization(l))
# for civ in civs:
#     civ.expand(100000, coast)
#     board.addLayer(civ.name, civ.territory)
    #coast = coast - civ.territory



# for civ in civs:
#     board.render(civ.name)

# board.addLayer('Cities',np.zeros(board.shape,dtype=int))
# for city in mongols.cities:
#     city.addToMap(board['Cities'].array)
#      (board.getTile(*city.pos))

# board.render('riverMask')

# board.addLayer('coves',board['landMask'].gauss(20,0.6))
#
# board.addLayer('bays',board['landMask'].gauss(150,0.4))
# board.render('coves')
# board.render('bays')
# board.addLayer('points',board['seaMask'].gauss(20,0.6))
#
# board.addLayer('peninsulas',board['seaMask'].gauss(150,0.4))
# board.render('points')
# board.render('peninsulas')
#

# board.addLayer('deltas',board['riverMask'].gauss(1,.5))
# board.render('deltas')
