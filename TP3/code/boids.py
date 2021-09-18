# This is the file that builds the food
import random
import numpy as np
from asteroid import * 
from cmu_112_graphics import *
import physics

# class that inherits the asteroid class
class Boid(Asteroid):

    def __init__(self, identity, locationX, locationY, r, mass, vel, acc, cx, cy, cr, dir):
        super().__init__(identity, locationX, locationY, r, mass, vel, acc)
        self.max_acc = 1
        self.max_vel = 5
        self.sight = 40
        self.force = 1
    
        self.cx = cx
        self.cy = cy
        self.cr = cr
        self.dir = dir


        self.at = acc
        self.vt = vel
        self.circularMotion()

        self.forbidUpdate = False
        self.isEnemy = False
        self.hasBeenMoved = False
        self.hasBeenEaten = False
        self.isMerged = False

    # circular motion is described here
    def circularMotion(self):
        self.center = np.array([self.cx, self.cy])
        an_hat = np.subtract(self.center, self.pos)
        an_hat = np.divide(an_hat, np.linalg.norm(an_hat))
        an_mag = 1
        self.an = an_hat * an_mag

        
        vn_hat = np.array([self.dir*an_hat[1], (-self.dir)*an_hat[0]])
        vn_mag = (an_mag*self.cr)**0.5
        self.vn = vn_hat * vn_mag

        self.vel = self.vn + self.vt
        self.acc = self.an + self.at

    def update(self):
        if self.forbidUpdate==False:
            super().update()
            self.circularMotion()

    # function that turns the food into an enemy
    def turnEnemy(self):
        self.identity = "Enemy"
        self.isEnemy = True
        self.forbidUpdate = True
        self.vel = np.array([0.0,0.0])
        return self.mass


    # The following three boids algorithms are adapted from here:
    # https://betterprogramming.pub/boids-simulating-birds-flock-behavior-in-python-9fff99375118
    def separation(self, flock):
        # they shouldn't remain too close
        average = np.array([0.,0.])
        for boid in flock:
            d = np.linalg.norm(boid.pos - self.pos)
            if (self != boid) and (d <= self.sight):
                diff = self.pos - boid.pos
                d_hat = np.divide(diff, d)
                average = np.add(diff, average)
        
        # if (self.pos[0])

        if average.all() == np.array([0,0]).all(): return average
        average = np.divide(average, len(flock))
        a_hat = np.divide(average, np.linalg.norm(average))
        targetVel = a_hat * (self.max_vel)
        steerForce = targetVel - self.vel

        return steerForce


    def alignment(self, flock):
        # alignment

        average = np.array([0.,0.])
        for boid in flock:
            if np.linalg.norm(boid.pos - self.pos) < self.sight:
                average = np.add(boid.vel, average)
        if average.all() == np.array([0,0]).all(): return average
        average = np.divide(average, len(flock))
        a_hat = np.divide(average, np.linalg.norm(average))
        targetVel = a_hat * self.max_vel
        steerForce = targetVel - self.vel

        return steerForce


    def cohesion(self, flock):
        # make their locationY close
        center = np.array([0.,0.])
        for boid in flock:
            center = np.add(boid.vel, center)

        if center.all() == np.array([0,0]).all(): return center
        center = np.divide(center, len(flock))
        center = center - self.pos
        c_hat = np.divide(center, np.linalg.norm(center))
        newDir = np.array([c_hat[0],1])
        targetVel = c_hat * self.max_vel
        steerForce = targetVel - self.vel

        return steerForce

    
