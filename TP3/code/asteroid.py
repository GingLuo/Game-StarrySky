# This file contains the builder class for instances in my game.
import random
import physics
import numpy as np

# The class for the player instance, the earth and the food, and the enemy
class Asteroid(object):

    # identity is a String: "Player", "Enemy", "Food"
    def __init__(self, identity, locationX, locationY, r=10, mass=1, vel=[0,0], acc=[0,0]):
        self.identity = identity
        self.pos = np.array([locationX, locationY])
        self.vel = np.array(vel)
        self.acc = np.array(acc)
        self.mass = mass
        self.r = r
        self.max_acc = 10
        self.min_acc = 0.01
        self.max_vel = 30
        self.min_vel = 0.01
    
    # applies a force on itself
    def applyForce(self,force, other):
        newAcc = physics.applyForce(force, self.mass)
        self.acc = np.add(newAcc, self.acc)

    # updates itself's pos and vel
    def update(self):
        self.vel = np.add(self.vel, self.acc)
        self.pos = np.add(self.vel, self.pos)

        self.checkMarginSpeed()

    # function that checks and limit too large and too small speed
    def checkMarginSpeed(self):
        if (np.linalg.norm(self.vel)<self.min_vel):
            self.vel = np.array([0,0])
        elif (np.linalg.norm(self.vel)>self.max_vel):
            self.vel = physics.setMag(self.vel, self.max_vel)

        if (np.linalg.norm(self.acc)<self.min_acc):
            self.acc = np.array([0,0])
        elif (np.linalg.norm(self.vel)>self.max_acc):
            self.acc = physics.setMag(self.acc, self.max_acc)



