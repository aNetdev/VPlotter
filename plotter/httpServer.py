import os
from urllib.parse import parse_qs
from svgParser import SVGParser
from http.server import HTTPServer, BaseHTTPRequestHandler

class BasicServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path =='/':
            self.path="../web/index.html"
        else:
            self.path= "../web/" +  self.path
        try:
            index = open(self.path[1:]).read()
            self.send_response(200)
        except:
            index = "File not found"
            self.send_response(404)
        self.end_headers()
        self.wfile.write(bytes(index,'utf-8'))
  
    def do_POST(self):
        if self.path == '/uploadSVG':
            length = self.headers['content-length']
            field_data = self.rfile.read(int(length))
            # fields = parse_qs(field_data)
            # data =fields[1]
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            #now we have the svg data so start processing
            parser = SVGParser()
            cords =parser.getXYCordsFromSVG(field_data)            
            jsonData =parser.covertXYToJson(cords)      

            self.wfile.write(jsonData.encode())
            

 



httpd=HTTPServer(('localhost',8080), BasicServer)
httpd.serve_forever()

