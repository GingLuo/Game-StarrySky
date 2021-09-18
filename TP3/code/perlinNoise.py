# This is the helper class of Perlin noise used in the game.

import itertools
import numpy as np
import math
import random
# My version of perlin Noise is adapted from the following github code:
# https://gist.github.com/eevee/26f547457522755cb1fb8739d0ea89a1
# I've made some changes to it:
# I've made the final loop be recursivly functioned, made the way to take dot product more intuitive
# I've also set new parameters for some of the features

# this is the smooth curve to fade out the diff
def smoothstep(t):
    return t * t * (3. - 2. * t)

# this is the Linear Interpolation
def lerp(t, a, b):
    return a + t * (b - a)

# this is our factory class
class PerlinNoiseFactory(object):

    def __init__(self, dimension):
        self.dimension = dimension
        self.gradient = {}

    # helper function to generate a random gradient vector, return as a tuple
    def generateRandomGradient(self):
        # Generate a unit vector
        # Use Gassian is better than
        # random.uniform(0,1)
        res = []
        for _ in range(self.dimension):
            res.append(random.gauss(0,1))
        res = np.array(res)
        res_mag = np.linalg.norm(res)
        res_hat = np.divide(res, res_mag)
        return res_hat

    # Recursive function that lerp the n dot product list with the point
    # The length of the dotList must be a power of 2
    # dIndex is from the last to the first because the way itertool,product change the order
    def combineLerp(self, point, dotList, dIndex):
        if (len(dotList) == 1):
            return dotList[0]
        else:
            t = point[dIndex]
            t = t - math.floor(t)
            newList = []
            for index in range(0,len(dotList),2):
                a, b = dotList[index], dotList[index+1]
                retVal = lerp(t, a, b)
                newList.append(retVal)
            res = self.combineLerp(point, newList, dIndex-1)
            return res

    # main calling function that returns a perlin value
    def getPerlinVal(self, *point):
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
        coordList = itertools.product(*gridList)

        # Compute the dot product
        dots = []
        for grid_point in coordList:
            if grid_point not in self.gradient:
                self.gradient[grid_point] = self.generateRandomGradient()
            gradient = self.gradient[grid_point]
            distVector = np.array(grid_point) - np.array(point)
            dot = np.dot(distVector,gradient)
            dots.append(dot)
        
        # Adds the dot product's influence together
        perlinValue = self.combineLerp(point, dots, self.dimension-1)

        # For n dimensions, the range of Perlin noise is ±sqrt(n/2); multiply by this to scale to ±1
        scale_factor = 2 * self.dimension ** -0.5
        perlinValue = perlinValue * scale_factor
        return perlinValue