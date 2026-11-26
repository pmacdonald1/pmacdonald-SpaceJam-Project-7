from direct.showbase.ShowBase import ShowBase
import DefensePaths as defensePaths
import SpaceJamClasses as spaceJamClasses
import CollideObjectBase as collideObjectBase
import Player as player
import math, random
from panda3d.core import CollisionTraverser, CollisionHandlerPusher, Vec3


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.cTrav = CollisionTraverser()
        self.cTrav.traverse(self.render)

        self.setScene()

        self.SetCamera()

        fullCycle = 60
        beltCycle = 100

        for j in range(fullCycle):
            spaceJamClasses.Drone.droneCount += 1
            nickName = "Drone" + str(spaceJamClasses.Drone.droneCount)

            self.DrawCloudDefense(self.Planet1, nickName)
            self.DrawBaseballSeams(self.SpaceStation1, nickName, j, fullCycle, 2)

            #self.DrawX(self.Planet2, nickName, j, fullCycle, 100)
            #self.DrawY(self.Planet3, nickName, j, fullCycle, 100)
            #self.DrawZ(self.Planet4, nickName, j, fullCycle, 100)

        for j in range(beltCycle):
            spaceJamClasses.Asteroids.AsteroidCount += 1
            astName = "Asteroid" + str(spaceJamClasses.Asteroids.AsteroidCount)
            self.DrawAsteroidBelt(self.Asteroids, astName)


        


        #the below code is the code used in Project4 and is subject to be added into a def
        self.pusher = CollisionHandlerPusher()
        self.pusher.addCollider(self.Hero.collisionNode, self.Hero.modelNode)
        self.cTrav.addCollider(self.Hero.collisionNode, self.pusher)

        self.cTrav.showCollisions(self.render)

    def setScene(self):
        self.Universe = spaceJamClasses.Universe(self.loader, "./Assets/Universe/Universe.x", self.render, 'Universe', "./Assets/Universe/Universe.jpg", (0, 0, 0), 10000)
        self.Planet1 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, 'Planet1', "./Assets/Planets/Planet1.jpg", (-6000, -3000, -800), 250)
        self.Planet2 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, 'Planet2', "./Assets/Planets/Planet2.jpg", (0, 6000, 0), 300)
        self.Planet3 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, 'Planet3', "./Assets/Planets/Planet3.jpg", (500, -5000, 200), 500)
        self.Planet4 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, 'Planet4', "./Assets/Planets/Planet4.jpg", (3000, 6000, 500), 150)
        self.Planet5 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, 'Planet5', "./Assets/Planets/Planet5.jpg", (700, -2000, 100), 500)
        self.Planet6 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, 'Planet6', "./Assets/Planets/Planet6.jpg", (0, -900, -1400), 700)
        self.SpaceStation1 = spaceJamClasses.SpaceStation(self.loader, "./Assets/Space Station/spaceStation.egg", self.render, 'Space Station', "./Assets/Space Station/SpaceStation1_Dif2.png", (1500, 1000, -100), 40)
        
        self.Hero = player.Spaceship(self.loader, self.taskMgr, self.accept, "./Assets/Spaceships/Dumbledore.egg", self.render, 'Hero', "./Assets/Spaceships/spacejet_C.png", Vec3(1000, 1200, -50), 50, self.cTrav, camera)

        self.Asteroids = spaceJamClasses.Asteroids(self.loader, "./Assets/Planets/protoPlanet.x", self.render, 'Asteroids', "./Assets/Asteroids/Asteroid.jpg", (7000, 0, 0), 0)

        self.Sentinal1 = spaceJamClasses.Orbiter(self.loader, self.taskMgr, "./Assets/DroneDefender/DroneDefender.obj", self.render, "Drone", 6.0, "./Assets/DroneDefender/octotoad1_auv.png", self. Planet5, 900, "MLB", self.Hero)
        self.Sentinal2 = spaceJamClasses.Orbiter(self.loader, self.taskMgr, "./Assets/DroneDefender/DroneDefender.obj", self.render, "Drone", 6.0, "./Assets/DroneDefender/octotoad1_auv.png", self. Planet6, 1000, "MLB", self.Hero)
        self.Sentinal3 = spaceJamClasses.Orbiter(self.loader, self.taskMgr, "./Assets/DroneDefender/DroneDefender.obj", self.render, "Drone", 6.0, "./Assets/DroneDefender/octotoad1_auv.png", self. Planet2, 500, "Cloud", self.Hero)
        self.Sentinal4 = spaceJamClasses.Orbiter(self.loader, self.taskMgr, "./Assets/DroneDefender/DroneDefender.obj", self.render, "Drone", 6.0, "./Assets/DroneDefender/octotoad1_auv.png", self. Planet3, 700, "Cloud", self.Hero)

        #self.Wanderer1 = spaceJamClasses.Wanderer(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, "Drone", 6.0, "./Assets/DroneDefender/octotoad1_auv.png", self.Hero)

    def DrawBaseballSeams(self, centralObject, droneName, step, numSeams, radius = 1):
        unitVec = defensePaths.BaseballSeams(step, numSeams, B = 0.4)
        unitVec.normalize()
        position = unitVec * radius * 250 + centralObject.modelNode.getPos()
        spaceJamClasses.Drone(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "./Assets/DroneDefender/octotoad1_auv.png", position, 5)

    def DrawCloudDefense(self, centralObject, droneName):
        unitVec = defensePaths.Cloud()
        unitVec.normalize()
        position = unitVec * 500 + centralObject.modelNode.getPos()
        spaceJamClasses.Drone(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "./Assets/DroneDefender/octotoad1_auv.png", position, 10)

    def DrawAsteroidBelt(self, centralObject, asteroidName):
        unitVec = defensePaths.Cloud()
        unitVec.normalize()
        position = unitVec * 3000 + centralObject.modelNode.getPos()
        spaceJamClasses.Asteroids(self.loader, "./Assets/Planets/protoPlanet.x", self.render, asteroidName, "./Assets/Asteroids/Asteroid.jpg", position, 50)

    def DrawX(self, centralObject, droneName, step, numDrones, radius = 1):
        unitVec = defensePaths.XDrones(step, numDrones)
        position = unitVec * radius + centralObject.modelNode.getPos()
        spaceJamClasses.Drone(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "./Assets/DroneDefender/octotoad1_auv.png", position, 5)

    def DrawY(self, centralObject, droneName, step, numDrones, radius = 1):
        unitVec = defensePaths.YDrones(step, numDrones)
        position = unitVec * radius + centralObject.modelNode.getPos()
        spaceJamClasses.Drone(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "./Assets/DroneDefender/octotoad1_auv.png", position, 5)

    def DrawZ(self, centralObject, droneName, step, numDrones, radius = 1):
        unitVec = defensePaths.ZDrones(step, numDrones)
        position = unitVec * radius + centralObject.modelNode.getPos()
        spaceJamClasses.Drone(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "./Assets/DroneDefender/octotoad1_auv.png", position, 5)


        

    def SetCamera(self):
        self.disableMouse()
        self.camera.reparentTo(self.Hero.modelNode)
        self.camera.setFluidPos(0, 1, 0)


app = MyApp()
app.run()