import logging
from enum import Enum
import math
import time

try:
    import RPi.GPIO as GPIO
except:
    import RPiDummy as GPIO

logger = logging.getLogger("plotterLog")
 
class Plotter:

    B =350   # mm
    stepPerRot = 2048  # steps in one rotation
    sd = 79  # spool diameter 2piR mm
   

    leftMotorPin = 32
    leftMotorDirPin = 16
    
    rightMotorPin = 18
    rightMotorDirPin = 22

    penPin = 12  # servo pin PWM
    lastPenPos =False

    #pwm = None
    isDebugMode=False
    def __init__(self, orgX, orgY ):
        self.currentLeft = 0
        self.currentRight = 0
        self.orgX = orgX
        self.orgY = orgY
        

        # tps = 79/2038  #thread per step mm
        self.lenPerStep = self.stepPerRot/self.sd

        intlenghts = self.getThreadLength(self.orgX, self.orgY)

        # OrgX*OrgX + OrgY*OrgY  # left thread
        self.intlenLeft = intlenghts['left']
        # B*B - 2*B*OrgX + intlenLeft    # right thread B^2 + 2BX + ll;
        self.intlenRight = intlenghts['right']

    def init(self,debug=False):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)  # BOARD pin-numbering scheme
    
        GPIO.setup(self.leftMotorPin, GPIO.OUT)
        GPIO.setup(self.leftMotorDirPin, GPIO.OUT)
        
        GPIO.setup(self.rightMotorPin, GPIO.OUT)
        GPIO.setup(self.rightMotorDirPin, GPIO.OUT)
        
        GPIO.setup(self.penPin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.penPin, 50)
        self.pwm.start(0)
        
        #make sure the pen is up
        self.movePen(PenDirection.Up)
        self.isDebugMode =debug

    def getThreadLength(self, x, y):
        leftSq = x*x + y*y
        rightSq = self.B*self.B - 2*self.B*x + leftSq

        leftCord = math.sqrt(abs(leftSq))
        rightCord = math.sqrt(abs(rightSq))

        left = leftCord if leftSq > 0 else leftCord * -1
        right = rightCord if rightSq > 0 else rightCord * -1

        logger.info(
            "getThreadLength Current L=%s R=%s", self.currentLeft, self.currentRight)

        logger.info(
            "getThreadLength Original X=%s Y=%s L=%s R=%s", x, y, left, right)
        
        # account for the current postion
        #TODO: i think using steps insted of the length would be more accurate. steps will more accurately represent the current length\situation
        left = left - self.currentLeft
        right = right - self.currentRight

        #store the cord length that would be out
        self.currentLeft = leftCord 
        self.currentRight = rightCord

        logger.info(
            "getThreadLength current pos accounted X=%s Y=%s L=%s R=%s", x, y, left, right)
        return {'left': left, 'right': right}

    def stepsToTake(self, leftLen, rightLen):
        # leftToMove = self.currentLeft-leftLen  # currentleft - leftLen
        # rightToMove = self.currentRight-rightLen  # currentRight - RightLen
        # now convert it to steps.
        leftSteps = round(leftLen*self.lenPerStep)
        rightSteps = round(rightLen*self.lenPerStep)

        logger.info("stepsToTake L=%s R=%s LS=%s RS=%s",
                          leftLen, rightLen, leftSteps, rightSteps)
        return {'left': leftSteps, 'right': rightSteps}

    def doMove(self, leftSteps, rightSteps, penDown):
        leftDir = CordDirection.Forward if leftSteps >= 0 else CordDirection.Backward  # if positive move forward
        rightDir = CordDirection.Forward if rightSteps >= 0 else CordDirection.Backward  # if positive move forward

        # now that we have the direction we can focus just on the absolute values
        leftSteps = abs(leftSteps)
        rightSteps = abs(rightSteps)
        steppedLeft = 0
        steppedRight = 0
        # we have to move both the steps at the same time.. or one after the other.
        # so see which steps are larger left vs right and loop on the larger steps
        maxSteps = leftSteps if leftSteps > rightSteps else rightSteps

        logger.info("doMove LS=%s RS=%s", leftSteps, rightSteps)
        logger.info("doMove LD=%s RD=%s", "up" if leftDir == CordDirection.Forward
                           else "down", "up" if rightDir == CordDirection.Forward else "down")
        logger.info("doMove MaxSteps=%s", maxSteps)
        logger.info("doMove penDown=%s", penDown)
        
        self.movePen(penDown)
        
        for i in range(1, maxSteps):
            if steppedLeft < leftSteps:  # if steppedLeft > leftSteps we have done our left steps. so dont do anything
                self.makeOneStep(self.leftMotorPin,
                                 self.leftMotorDirPin, leftDir)
                steppedLeft += 1
            if steppedRight < rightSteps:  # if steppedRight < rightSteps we have done our left steps. so dont do anything
                self.makeOneStep(self.rightMotorPin,
                                 self.rightMotorDirPin, rightDir)
                steppedRight += 1

    def makeOneStep(self, motorPin, dirPin, dir):
        logger.debug("makeOneStep MotorPin=%s DirPin=%s Dir=%s", motorPin, dirPin, dir)
        # set direction
        GPIO.output(dirPin, GPIO.LOW if dir == CordDirection.Forward else GPIO.HIGH)
        GPIO.output(motorPin, GPIO.HIGH)
        if not self.isDebugMode:
            time.sleep(0.01)
        # reset
        logger.debug("makeOneStep Reset")
        GPIO.output(motorPin, GPIO.LOW)
    
    def moveTo(self, x, y, penDown):
        try:
            len = self.getThreadLength(x, y)
            steps = self.stepsToTake(len['left'], len['right'])
            self.doMove(steps['left'], steps['right'], penDown)
        except Exception:
            logger.exception("something bad happed")
       
     
     
    def movePen(self, dir):
        if self.lastPenPos != dir :
            #true = down 180 degree
            #false = up 0 degree
            angle = 5 if dir == PenDirection.Down  else 170
            duty = float(angle) / 18 + 2
            self.pwm.ChangeDutyCycle(duty)     
            time.sleep(0.01)
            self.lastPenPos =dir

    def moveRight(self, dir, steps):
        logger.info("moving right %s steps", steps)
        # set direction
        GPIO.output(self.rightMotorDirPin, GPIO.LOW if dir == CordDirection.Forward else GPIO.HIGH)
        for i in range(1, steps):
            GPIO.output(self.rightMotorPin, GPIO.HIGH)
            time.sleep(0.01)
            # reset        
            GPIO.output(self.rightMotorPin, GPIO.LOW)
        logger.info("done")

    def moveLeft(self, dir, steps):
        logger.info("moving Left %s steps", steps)
        # set direction
        GPIO.output(self.leftMotorDirPin, GPIO.LOW if dir == CordDirection.Forward else GPIO.HIGH)
        for i in range(1, steps):
            GPIO.output(self.leftMotorPin, GPIO.HIGH)
            if not self.isDebugMode:  
                time.sleep(0.01)
            # reset        
            GPIO.output(self.leftMotorPin, GPIO.LOW)
        logger.info("done")

    def finalize(self):
        self.movePen(PenDirection.Up)
        self.moveTo(self.orgX, self.orgY, False)
        GPIO.cleanup()

class CordDirection(Enum):
    Forward =0
    Backward=1

class PenDirection(Enum):
    Up=1
    Down=0
