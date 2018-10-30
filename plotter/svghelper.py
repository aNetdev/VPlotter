from xml.dom import minidom
from svg.path import parse_path

svg_string = open("D:\\Work\\raspberrypi\\vplotter\\calibration\\Rectangle.svg","r",encoding="utf8").read()
svg_dom = minidom.parseString(svg_string)

path_strings = [path.getAttribute('d') for path in svg_dom.getElementsByTagName('path')]

for path_string in path_strings:
    path_data = parse_path(path_string)
    print(path_data)

    #  now use methods provided by the path_data object
    #  e.g. points can be extracted using 
    #  point = path_data.pos(pos_val) 
    #  where pos_val is anything between 0 and 1