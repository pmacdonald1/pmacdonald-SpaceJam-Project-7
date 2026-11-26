from CollideObjectBase import SphereCollideObject
from panda3d.core import Loader, NodePath, Vec3, TransparencyAttrib, CollisionHandlerEvent
from direct.task.Task import TaskManager
from typing import Callable
from direct.task import Task
from direct.gui.OnscreenImage import OnscreenImage
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval
from direct.particles.ParticleEffect import ParticleEffect
import re


from direct.interval.IntervalGlobal import Sequence, Func

class Missile(SphereCollideObject):
    fireModels = {}
    cNodes = {}
    collisionSolids = {}
    Intervals = {}

    missileCount = 0

    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, posVec: Vec3, scaleVec: float = 1.0):
        super(Missile, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 3.0)
        self.modelNode.setScale(scaleVec)
        self.modelNode.setPos(posVec)

        Missile.missileCount += 1
        Missile.fireModels[nodeName] = self.modelNode
        Missile.cNodes[nodeName] = self.collisionNode

        # we retrieve the solid for our collisionNode for debugging
        Missile.collisionSolids[nodeName] = self.collisionNode.node().getSolid(0)
        Missile.cNodes[nodeName].show()
        print("Fire torpedo #" + str(Missile.missileCount))

class Spaceship(SphereCollideObject):
    
    def __init__(self, loader: Loader, taskMgr: TaskManager, accept: Callable[[str, Callable]], modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float, traverser, camera):
        super(Spaceship, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 1.2)
        self.taskMgr = taskMgr
        self.accept = accept
        self.render = parentNode
        self.loader = loader
        self.traverser = traverser

        self.camera = camera

        self.reloadTime = .25
        self.missileDistance = 4000
        self.missileBay = 1
        self.cntExplode = 0
        self.explodeIntervals = {}

        self.handler = CollisionHandlerEvent()
        self.handler.addInPattern('into')
        self.accept('into', self.HandleInto)

        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        self.modelNode.setName(nodeName)
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)

        self.taskMgr.add(self.CheckIntervals, 'checkMissiles', 34)

        self.EnableHUD()
        self.SetKeyBindings()
        self.SetParticles()

    #at the moment a testing feature
    def thirdPerson(self):
        if hasattr(self, 'turnSequence') and self.turnSequence.isPlaying():
            return

        cameraStart = self.camera.getPos(self.modelNode)
        cameraBack = cameraStart + Vec3(0, -30, 0)

        zoomOut = LerpPosInterval(self.camera, 1.0, cameraBack, startPos=cameraStart, other=self.modelNode)
        self.turnSequence = Sequence(zoomOut)
        self.turnSequence.start()

    def ChangeColor(self, color):
        self.modelNode.setColor(color[0], color[1], color[2])

    def Turn180(self):
        self.taskMgr.remove('left-turn')
        self.taskMgr.remove('right-turn')
        self.taskMgr.remove('pitch-forward')
        self.taskMgr.remove('pitch-backward')
        self.taskMgr.remove('roll-left')
        self.taskMgr.remove('roll-right')

        if hasattr(self, 'turnSequence') and self.turnSequence.isPlaying():
            return

        cameraStart = self.camera.getPos(self.modelNode)
        cameraBack = cameraStart + Vec3(0, -30, 5)

        zoomOut = LerpPosInterval(self.camera, 1.0, cameraBack, startPos=cameraStart, other=self.modelNode)
        turn = LerpHprInterval(self.modelNode, 1.5, Vec3(self.modelNode.getH() + 180, self.modelNode.getP(), self.modelNode.getR()))
        zoomIn = LerpPosInterval(self.camera, 1.0, cameraStart, startPos=cameraBack, other=self.modelNode)

        self.taskMgr.add(self.ApplyThrust, 'forward-thrust')
        self.turnSequence = Sequence(zoomOut, turn, zoomIn, Func(self.StopThrust))
        self.turnSequence.start()

    def BarrelRoll(self):
        self.taskMgr.remove('left-turn')
        self.taskMgr.remove('right-turn')
        self.taskMgr.remove('pitch-forward')
        self.taskMgr.remove('pitch-backward')
        self.taskMgr.remove('roll-left')
        self.taskMgr.remove('roll-right')

        if hasattr(self, 'turnSequence') and self.turnSequence.isPlaying():
            return

        cameraStart = self.camera.getPos(self.modelNode)
        cameraBack = cameraStart + Vec3(0, -30, 0)

        zoomOut = LerpPosInterval(self.camera, 1.0, cameraBack, startPos=cameraStart, other=self.modelNode)
        turn = LerpHprInterval(self.modelNode, 1.5, Vec3(self.modelNode.getH(), self.modelNode.getP(), self.modelNode.getR() + 360))
        zoomIn = LerpPosInterval(self.camera, 1.0, cameraStart, startPos=cameraBack, other=self.modelNode)

        self.taskMgr.add(self.ApplyThrust, 'forward-thrust')
        self.turnSequence = Sequence(zoomOut, turn, zoomIn, Func(self.StopThrust))
        self.turnSequence.start()

    
    def StopThrust(self):
        self.taskMgr.remove('forward-thrust')

    def HandleInto(self, entry):
        fromNode = entry.getFromNodePath().getName()
        print("fromNode: " + fromNode)
        intoNode = entry.getIntoNodePath().getName()
        print("intoNode: " + intoNode)
        intoPosition = Vec3(entry.getSurfacePoint(self.render))

        tempVar = fromNode.split('_')
        print("tempVar: " + str(tempVar))
        shooter = tempVar[0]
        print("Shooter: " + str(shooter))
        tempVar = intoNode.split('-')
        print("TempVar1: " + str(tempVar))
        tempVar = intoNode.split('_')
        print("TempVar2: " + str(tempVar))
        victim = tempVar[0]
        print("Victim: " + str(victim))

        pattern = r'[0-9]'
        strippedString = re.sub(pattern, '', victim)

        if(strippedString == "Drone" or strippedString == "Planet" or strippedString == "Space Station" or strippedString == "Asteroid"):
            print(victim, ' hit at ', intoPosition)
            self.DestroyObject(victim, intoPosition)

        print(shooter + ' is DONE.')
        Missile.Intervals[shooter].finish()

    def DestroyObject(self, hitID, hitPosition):
        nodeID = self.render.find(hitID)
        nodeID.detachNode()

        self.explodeNode.setPos(hitPosition)
        self.Explode()

    def Explode(self):
        self.cntExplode += 1
        tag = 'particles-' + str(self.cntExplode)

        self.explodeIntervals[tag] = LerpFunc(self.ExplodeLight, duration = 4.0)
        self.explodeIntervals[tag].start()

    def ExplodeLight(self ,t):
        if t == 1.0 and self.explodeEffect:
            self.explodeEffect.disable()

        elif t == 0:
            self.explodeEffect.start(self.explodeNode)

    def SetParticles(self):
        base.enableParticles()
        self.explodeEffect = ParticleEffect()
        self.explodeEffect.loadConfig("./Assets/Particles/basic_xpld_efx.ptf")
        self.explodeEffect.setScale(20)
        self.explodeNode = self.render.attachNewNode('ExplosionEffects')


    def SetKeyBindings(self):
        # All of our key binding for our spaceship's movement.
        self.accept('space', self.Thrust, [1])
        self.accept('space-up', self.Thrust, [0])

        self.accept('a', self.LeftTurn, [1])
        self.accept('a-up', self.LeftTurn, [0])

        self.accept('d', self.RightTurn, [1])
        self.accept('d-up', self.RightTurn, [0])

        self.accept('w', self.PitchForward, [1])
        self.accept('w-up', self.PitchForward, [0])

        self.accept('s', self.PitchBack, [1])
        self.accept('s-up', self.PitchBack, [0])

        self.accept('q', self.RollLeft, [1])
        self.accept('q-up', self.RollLeft, [0])

        self.accept('e', self.RollRight, [1])
        self.accept('e-up', self.RollRight, [0])

        self.accept('f', self.Fire)

        self.accept('r', self.Turn180)
        self.accept('b', self.BarrelRoll)

        self.accept('p', self.thirdPerson)

        self.accept('1', self.ChangeColor, [(1, 0, 0)])     # Red
        self.accept('2', self.ChangeColor, [(0, 0, 1)])     # Blue
        self.accept('3', self.ChangeColor, [(0, 1, 0)])     # Green
        self.accept('4', self.ChangeColor, [(1, 1, 0)])     # Yellow
        self.accept('5', self.ChangeColor, [(1, 0, 1)])     # Purple
        self.accept('0', self.ChangeColor, [(1, 1, 1)])     # White
        self.accept('6', self.ChangeColor, [(0, 0, 0)])     # Black

    
    def Thrust(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyThrust, 'forward-thrust')
        else:
            self.taskMgr.remove('forward-thrust')

    def ApplyThrust(self, task):
        rate = 10
        trajectory = render.getRelativeVector(self.modelNode, Vec3.forward())
        trajectory.normalize()
        self.modelNode.setFluidPos(self.modelNode.getPos() + trajectory * rate)
        return Task.cont

    def LeftTurn(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyLeftTurn, 'left-turn')
        else:
            self.taskMgr.remove('left-turn')

    def ApplyLeftTurn(self, task):
        # Half a degree every frame.
        rate = 0.5
        self.modelNode.setH(self.modelNode.getH() + rate)
        return Task.cont


    def RightTurn(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyRightTurn, 'right-turn')
        else:
            self.taskMgr.remove('right-turn')

    def ApplyRightTurn(self, task):
        rate = 0.5
        self.modelNode.setH(self.modelNode.getH() - rate)
        return Task.cont


    def PitchForward(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyPitchForward, 'pitch-forward')
        else:
            self.taskMgr.remove('pitch-forward')

    def ApplyPitchForward(self, task):
        rate = 0.5
        self.modelNode.setP(self.modelNode.getP() + rate)
        return Task.cont

    def PitchBack(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyPitchBackward, 'pitch-backward')
        else:
            self.taskMgr.remove('pitch-backward')

    def ApplyPitchBackward(self, task):
        rate = 0.5
        self.modelNode.setP(self.modelNode.getP() - rate)
        return Task.cont

    def RollLeft(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyRollLeft, 'roll-left')
        else:
            self.taskMgr.remove('roll-left')

    def ApplyRollLeft(self, task):
        rate = 0.5
        self.modelNode.setR(self.modelNode.getR() + rate)
        return Task.cont

    def RollRight(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyRollRight, 'roll-right')
        else:
            self.taskMgr.remove('roll-right')

    def ApplyRollRight(self, task):
        rate = 0.5
        self.modelNode.setR(self.modelNode.getR() - rate)
        return Task.cont


    def Fire(self):
        if self.missileBay:
            travRate = self.missileDistance
            aim = self.render.getRelativeVector(self.modelNode, Vec3.forward())
            aim.normalize()

            fireSolution = aim * travRate
            inFront = aim * 150

            travVec = fireSolution + self.modelNode.getPos()
            self.missileBay -= 1
            tag = 'missile' + str(Missile.missileCount)
            posVec = self.modelNode.getPos() + inFront
            currentMissile = Missile(self.loader, './Assets/Phaser/phaser.egg', self.render, tag, posVec, 4.0)
            
            self.traverser.addCollider(currentMissile.collisionNode, self.handler)

            Missile.Intervals[tag] = currentMissile.modelNode.posInterval(2.0, travVec, startPos = posVec, fluid = 1)
            Missile.Intervals[tag].start()
        else:
            if not self.taskMgr.hasTaskNamed('reload'):
                print('Initializing reload...')
                self.taskMgr.doMethodLater(0, self.Reload, 'reload')
                return Task.cont

    def Reload(self, task):
        if task.time > self.reloadTime:
            self.missileBay += 1
            if self.missileBay > 1:
                self.missileBay = 1

            #print is for debugging
            print("Reload complete.")
            return Task.done
        
        elif task.time <= self.reloadTime:
            print("Reload proceeding...")
            return Task.cont

    def CheckIntervals(self, task):
        for i in Missile.Intervals:
            if not Missile.Intervals[i].isPlaying():
                Missile.cNodes[i].detachNode()
                Missile.fireModels[i].detachNode()

                del Missile.Intervals[i]
                del Missile.fireModels[i]
                del Missile.cNodes[i]
                del Missile.collisionSolids[i]
                
                #debug line
                print(i + ' has reached the end of its fire solution.')
                break
        return Task.cont
    
    def EnableHUD(self):
        self.Hud = OnscreenImage(image = "./Assets/Hud/Reticle3b.png", pos = Vec3(0, 0, 0), scale = 0.1)
        self.Hud.setTransparency(TransparencyAttrib.MAlpha)
