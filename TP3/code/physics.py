# This file contains all the physics I need for the game
import numpy as np
import random
# The physics equations are from my memory of physics class 33141 
# Independent work

# The idea of putting vector into numpy array is inspired by this stack overflow post
# https://stackoverflow.com/questions/27340042/converting-velocity-components-to-speeds-in-three-dimensional-array-with-python

# set the magnitute of sth into n
def setMag(V, scaling):
    V_hat = np.divide(V, np.linalg.norm(V))
    return np.multiply(V_hat, scaling)

# apply force by calling the instance's apply force method
def applyForce(force, mass):
    # takes in force as a vector, mass as an integer
    acc = np.divide(force, mass)
    return acc

def distance(x1, y1, x2, y2):
    return ((x1-x2)**2+(y1-y2)**2)**0.5

# calculate gravity
def gravity(mass, g):
    direction = np.array([0,1])
    force = np.multiply(direction, g)
    return force


# calculate gravitational pull
def gravitationalForce(mass1, mass2, G, dVector):
    direction = np.divide(dVector, np.linalg.norm(dVector))    # a unit vector
    dMag = np.linalg.norm(dVector)
    # constrain the magnitude
    if (dMag < 50):
        dMag = 80
    elif (dMag > 150):
        dMag = 80
    magnitute = mass1*mass2*G/(dMag**2)
    force = np.multiply(direction, magnitute)
    return force


# determine whether it's a rigid body collision
# return True if it is, None if it's N/A to determine (not rigid)
# return False if not colliding 
def detectRigidBodyCollision(asteroid1, asteroid2):
    dx = asteroid1.pos[0] - asteroid2.pos[0]
    dy = asteroid1.pos[1] - asteroid2.pos[1]

    epsilon = 1
    distance = (dx**2 + dy**2)**0.5
    if (asteroid1.r + asteroid2.r - epsilon < distance < asteroid1.r + asteroid2.r + epsilon):
        return True
    elif (distance < asteroid1.r + asteroid2.r - epsilon):
        return None
    else:
        return False
    '''
    elif (distance < asteroid1.r + asteroid2.r):
        lastPos = asteroid1.pos
        x = lastPos[0]
        y = lastPos[1]
        ex,ey = asteroid2.pos[0], asteroid2.pos[1]
        while (((ex-x)**2 + (ey-y)**2)**0.5 < asteroid1.r+asteroid2.r):
            y -= 0.1
        asteroid1.pos = np.array([x,y])
        return True'''
    

# calculate the normal force 
def normalForce(force):
    return np.multiply(force, -1)

# function that describes the rigidbody collision behavior
# prior knowledge: momentum conservation, elastic vs inelastic collisions
def rigidBodyCollision(asteroid1, asteroid2):
    # m1*v1 = m2*v2
    m1 = asteroid1.mass
    m2 = asteroid2.mass
    v1 = asteroid1.vel
    v2 = asteroid2.vel
    a1 = asteroid1.acc
    a2 = asteroid2.acc
    coeff = 0.05
    if (m2 > 1000*m1):
        # if m2 is far more greater than m1
        newVel = -1*v1*coeff
        newAcc = -1*a1*coeff
        
        min_val = np.array([0.00001,0.00001])
        if (np.linalg.norm(newVel)<np.linalg.norm(min_val)):
            newVel = np.array([0,0])
        if (np.linalg.norm(newAcc)<np.linalg.norm(min_val)):
            newAcc = np.array([0,0])
        asteroid1.vel = newVel
        asteroid1.acc = newAcc
    else:
        pass
        # maybe implemented further


