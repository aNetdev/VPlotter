import os
import json
from xml.dom import minidom
from svg.path import Line, Arc, QuadraticBezier, CubicBezier, parse_path


class SVGParser:

    def pathToPoints(self, path, penDown, totalPoints):
        p = []
        for i in range(0, totalPoints+1):
            f = i/totalPoints
            cp = path.point(f)
            p.append((cp.real, cp.imag, penDown))
        return p
    
    # def applyPlotterCals(points):
        
    def getXYCordsFromSVG(self, svgString):
        #path = os.path.join( os.path.dirname(__file__), "..", "calibration", "bull.svg")
        #svg_string = open(path,"r",encoding="utf8").read()
        dom = minidom.parseString(svgString)
        svgPaths = [path.getAttribute('d')
                    for path in dom.getElementsByTagName('path')]
        points = []
        for svgPath in svgPaths:
            data = parse_path(svgPath)
            for seg in data:
                if isinstance(seg, Arc) or isinstance(seg, QuadraticBezier) or isinstance(seg, CubicBezier):
                    # everything except a straight line
                    points.extend(self.pathToPoints(seg, 1, 10))
                elif isinstance(seg, Line):
                    # straight line so just calculate 1 poinet start and end
                    points.extend(self.pathToPoints(seg, 1, 1))
                else:
                    # straight line move so just calculate 1 poinet start and end with pen up
                    points.extend(self.pathToPoints(seg, 0, 1))
        #xyCords = None
        # if formatAsString:
        #     xyCords = '\n'.join(map(lambda x: "{},{},{}".format(
        #         str(x[0]), str(x[1]), str(x[2])), points))
        # else:
        #     xyCords = points
        return points
    
    def covertXYToJson(self, cords):
        #{moveToX:[],
        # moveToY:[],
        # lineToX:[],
        # lineToY:[]}
        moveToX = [p[0] for p in cords if p[2] == 0]
        moveToY = [p[1] for p in cords if p[2] == 0]
        lineToX = [p[0] for p in cords if p[2] == 1]
        lineToY = [p[1] for p in cords if p[2] == 1]
        
        data ={}
        data['moveToX']=moveToX
        data['moveToY']=moveToY
        data['lineToX']=lineToX
        data['lineToY']=lineToY
        
        return json.dumps(data)


# p = SVGParser()
# f = open("D:\\Work\\RaspberryPi\\vplotter\\calibration\\Triangle.svg")
# xy = p.getXYCordsFromSVG(f.read())
# f.close()
# w = open("test.txt",'w')
# w.write(xy)
# w.close()
