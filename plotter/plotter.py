import logging
from enum import Enum
import math
import time

try:
    import RPi.GPIO as GPIO
except:
    import plotter.RPiDummy as GPIO

logger = logging.getLogger("plotterLog")


class Plotter:

    B = 360   # mm
    stepPerRot = 2048  # steps in one rotation
    sd = 79  # spool diameter 2piR mm

    leftMotorEnable = 36
    leftMotorPin = 32
    leftMotorDirPin = 16

    rightMotorEnable = 38
    rightMotorPin = 18
    rightMotorDirPin = 22

    penPin = 12  # servo pin PWM
    lastPenPos = False

    # pwm = None
    isDebugMode = False

    def __init__(self, orgX, orgY):
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

    def init(self, debug=False):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)  # BOARD pin-numbering scheme

        GPIO.setup(self.leftMotorEnable, GPIO.OUT)
        GPIO.setup(self.leftMotorPin, GPIO.OUT)
        GPIO.setup(self.leftMotorDirPin, GPIO.OUT)

        GPIO.setup(self.rightMotorEnable, GPIO.OUT)
        GPIO.setup(self.rightMotorPin, GPIO.OUT)
        GPIO.setup(self.rightMotorDirPin, GPIO.OUT)

        GPIO.setup(self.penPin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.penPin, 50)
        self.pwm.start(0)

        # make sure the pen is up
        self.movePen(PenDirection.Up)
        self.isDebugMode = debug

    def getThreadLength(self, x, y):
        leftSq = x*x + y*y
        rightSq = self.B*self.B - 2*self.B*x + leftSq

        leftCord = math.sqrt(abs(leftSq))
        rightCord = math.sqrt(abs(rightSq))

        left = leftCord if leftSq > 0 else leftCord * -1
        right = rightCord if rightSq > 0 else rightCord * -1

        logger.debug(
            "getThreadLength Current L=%s R=%s", self.currentLeft, self.currentRight)

        logger.debug(
            "getThreadLength to go X=%s Y=%s L=%s R=%s", x, y, left, right)

        # account for the current postion
        # TODO: i think using steps insted of the length would be more accurate. steps will more accurately represent the current length\situation
        left = left - self.currentLeft
        right = right - self.currentRight

        # store the cord length that would be out
        self.currentLeft = leftCord
        self.currentRight = rightCord

        logger.debug(
            "getThreadLength current pos accounted X=%s Y=%s L=%s R=%s", x, y, left, right)
        return {'left': left, 'right': right}

    def stepsToTake(self, leftLen, rightLen):
        # leftToMove = self.currentLeft-leftLen  # currentleft - leftLen
        # rightToMove = self.currentRight-rightLen  # currentRight - RightLen
        # now convert it to steps.
        leftSteps = round(leftLen*self.lenPerStep)
        rightSteps = round(rightLen*self.lenPerStep)

        logger.debug("stepsToTake L=%s R=%s LS=%s RS=%s",
                    leftLen, rightLen, leftSteps, rightSteps)
        return {'left': leftSteps, 'right': rightSteps}

    def doMove(self, leftSteps, rightSteps, penDown):
        # if positive move forward
        leftDir = CordDirection.Forward if leftSteps >= 0 else CordDirection.Backward
        # if positive move forward
        rightDir = CordDirection.Forward if rightSteps >= 0 else CordDirection.Backward

        # now that we have the direction we can focus just on the absolute values
        leftSteps = abs(leftSteps)
        rightSteps = abs(rightSteps)
        steppedLeft = 0
        steppedRight = 0
        # we have to move both the steps at the same time.. or one after the other.
        # so see which steps are larger left vs right and loop on the larger steps
        maxSteps = leftSteps if leftSteps > rightSteps else rightSteps

        logger.debug("doMove LS=%s RS=%s", leftSteps, rightSteps)
        logger.debug("doMove LD=%s RD=%s", "up" if leftDir == CordDirection.Forward
                    else "down", "up" if rightDir == CordDirection.Forward else "down")
        logger.debug("doMove MaxSteps=%s", maxSteps)
        logger.debug("doMove penDown=%s", penDown)

        self.movePen(penDown)
        a1 = 0
        a2 = 0
        for i in range(1, maxSteps):
            logger.debug("stepping {}/{}".format(i, maxSteps))
            a1 += leftSteps

            if a1 >= maxSteps:
                a1 -= maxSteps
                # bc.makeStep(0,d1)
                self.makeOneStep(self.leftMotorPin,
                                 self.leftMotorDirPin, leftDir)
            a2 += rightSteps
            if a2 >= maxSteps:
                a2 -= maxSteps
                # bc.makeStep(1,d2)
                self.makeOneStep(self.rightMotorPin,
                                 self.rightMotorDirPin, rightDir)

        # for i in range(1, maxSteps):
        #     if steppedLeft < leftSteps:  # if steppedLeft > leftSteps we have done our left steps. so dont do anything
        #         self.makeOneStep(self.leftMotorPin,
        #                          self.leftMotorDirPin, leftDir)
        #         steppedLeft += 1
        #     if steppedRight < rightSteps:  # if steppedRight < rightSteps we have done our left steps. so dont do anything
        #         self.makeOneStep(self.rightMotorPin,
        #                          self.rightMotorDirPin, rightDir)
        #         steppedRight += 1

    def makeOneStep(self, motorPin, dirPin, dir):
        logger.debug("makeOneStep MotorPin=%s DirPin=%s Dir=%s",
                     motorPin, dirPin, dir)
        # set direction
        GPIO.output(dirPin, GPIO.LOW if dir ==
                    CordDirection.Forward else GPIO.HIGH)
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
        logger.debug("dir %s", dir)
        logger.debug("lastPenPos %s", self.lastPenPos)
        if self.lastPenPos != dir:
            # true = down 180 degree
            # false = up 0 degree
            angle = 5 if dir == PenDirection.Down else 170
            logger.debug("angle %s", angle)
            duty = float(angle) / 18 + 2
            logger.debug("duty %s", duty)
            self.pwm.ChangeDutyCycle(duty)
            time.sleep(0.01)
            self.lastPenPos = dir

    def moveRight(self, dir, steps):
        logger.debug("moving right %s steps", steps)
        # set direction
        GPIO.output(self.rightMotorDirPin, GPIO.LOW if dir ==
                    CordDirection.Forward else GPIO.HIGH)
        for i in range(1, steps):
            GPIO.output(self.rightMotorPin, GPIO.HIGH)
            time.sleep(0.01)
            # reset
            GPIO.output(self.rightMotorPin, GPIO.LOW)
        logger.debug("done")

    def moveLeft(self, dir, steps):
        logger.debug("moving Left %s steps", steps)
        # set direction
        GPIO.output(self.leftMotorDirPin, GPIO.LOW if dir ==
                    CordDirection.Forward else GPIO.HIGH)
        for i in range(1, steps):
            GPIO.output(self.leftMotorPin, GPIO.HIGH)
            if not self.isDebugMode:
                time.sleep(0.01)
            # reset
            GPIO.output(self.leftMotorPin, GPIO.LOW)
        logger.debug("done")

    def finalize(self):
        logger.debug("finalize")
        self.movePen(PenDirection.Up)
        self.moveTo(self.orgX, self.orgY, False)
        self.disableSteppers()

    def disableSteppers(self):
        logger.debug("disableSteppers")
        # pull high to disable the easy drivers
        GPIO.output(self.leftMotorEnable, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(self.rightMotorEnable, GPIO.HIGH)
        time.sleep(0.01)

    def enableSteppers(self):
        logger.debug("enableSteppers")
        # pull low to enable the easy drivers
        GPIO.output(self.leftMotorEnable, GPIO.LOW)
        time.sleep(0.01)    
        GPIO.output(self.rightMotorEnable, GPIO.LOW)           
        time.sleep(0.01)
    
    def cleanup(self):
        GPIO.cleanup()
class CordDirection(Enum):
    Forward = 0
    Backward = 1


class PenDirection(Enum):
    Up = 1
    Down = 0
