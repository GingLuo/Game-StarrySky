# This is the helper class of simple noise used in the game.
import numpy as np
import math
import random
import itertools

# Adapted the idea here
# Also evolved from my own code of PErlin noise
# https://www.scratchapixel.com/lessons/procedural-generation-virtual-worlds/procedural-patterns-noise-part-1/creating-simple-2D-noise

# this is the smooth curve to fade out the diff
def smoothstep(t):
    return t * t * (3. - 2. * t)

# this is the Linear Interpolation
def lerp(t, a, b):
    return a + t * (b - a)

# this is our factory class
class simpleNoiseFactory(object):

    def __init__(self, dimension, width, height):
        self.dimension = dimension
        self.randTable = [[0]*width for _ in range(height)]
        for row in range(height):
            for col in range(width):
                self.randTable[row][col] = random.uniform(-1,1)


    # Recursive function that lerp the n list with the point
    # The length of the L must be a power of 2
    def combineLerp(self, point, L, dIndex):
        if (len(L) == 1):
            return L[0]
        else:
            t = point[dIndex]
            t = t - math.floor(t)
            newList = []
            for index in range(0,len(L),2):
                a, b = L[index], L[index+1]
                retVal = lerp(t, a, b)
                newList.append(retVal)
            res = self.combineLerp(point, newList, dIndex-1)
            return res

    # main calling function that returns a noise value
    def getSimpleNoiseVal(self, *point):
        if len(point) != self.dimension:
            # dimension is wrong
            return False

        # the grid the point is in
        gridList = []
        for elem in point:
            minVal = math.floor(elem)
            maxVal = minVal + 1
            gridList.append((minVal, maxVal))

        # The way I use product is from here:
        # https://stackoverflow.com/questions/533905/get-the-cartesian-product-of-a-series-of-lists
        coordList = list(itertools.product(*gridList))
        weightList = []
        for (row, col, time) in coordList:
            a, b = (row+time)%3, (col+time)%3
            val = self.randTable[a][b]
            weightList.append(val)
        
        # Adds the influence together
        noiseValue = self.combineLerp(point, weightList, self.dimension-1)

        # For n dimensions, the range of noise noise is ±sqrt(n/2); multiply by this to scale to ±1
        scale_factor = 2 * self.dimension ** -0.5
        noiseValue = noiseValue * scale_factor
        return noiseValue