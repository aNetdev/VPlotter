import asyncio
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor

from aiohttp import web

from plotter.config import Config
from plotter.plotter import PenDirection, Plotter
from plotter.svgParser import SVGParser

logger = logging.getLogger("plotterLog")
class WebServer:
    _webroot= os.path.join(os.path.dirname(__file__), 'web')
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.loop = asyncio.get_event_loop()
        self.pool = ThreadPoolExecutor(max_workers=1)   
        self.progress = []
        self.isPlottingInProgress=False

    def doPlot(self,data):
        self.isPlottingInProgress =True
        logger.info("Starting  to Plot")
        orgX = int(data['orgX'])
        orgY = int(data['orgY'])
        cords =data['cords']
        config = Config().getConfig()
        plotter = Plotter(config, orgX, orgY)
        plotter.init(False)
        plotter.enableSteppers()
        minX = min(cords['x'])
        maxX = max(cords['x'])

        minY = min(cords['y'])
        maxY = max(cords['y'])
        

        plotter.moveTo(minX, minY, PenDirection.Up)

        plotter.moveTo(minX+10, minY, PenDirection.Down)    #top left corner horizontal line
        plotter.moveTo(maxX-10, minY, PenDirection.Up)      

        #top Right
        plotter.moveTo(maxX, minY, PenDirection.Down) #top right corner horizontal line    
        plotter.moveTo(maxX, minY+10, PenDirection.Down)   #top right corner vertical line

        plotter.moveTo(maxX,maxY-10, PenDirection.Up)
        
        #bottom Right
        plotter.moveTo(maxX,maxY, PenDirection.Down)  #bottom right corner vertical line
        
        plotter.moveTo(maxX-10,maxY, PenDirection.Down)   #bottom right corner horizontal line
        plotter.moveTo(minX+10,maxY, PenDirection.Up)
        
        #bottom left
        plotter.moveTo(minX,maxY, PenDirection.Down) #bottom left corner horizontal line
        plotter.moveTo(minX,maxY-10, PenDirection.Down) #bottom left corner vertical line
        
        #input("Done with border. Enter to continue")

        total =len(cords['x'])

        for index in range(0,total-1):
            x = int(cords['x'][index])
            y = int(cords['y'][index])
            pen = PenDirection.Down if cords['p'][index] == 0 else PenDirection.Up
            plotter.moveTo(x, y, pen)            
            perComplete =round(index/total * 100 ,2)
            self.progress.append((x,y,perComplete))
            logger.info("Plotting {}%%".format(perComplete))
        plotter.finalize()
        logger.info("Done Plotting")
        self.isPlottingInProgress =False
        return "Complete"
  

    async def index(self, request):
        logger.debug("Index request")
        return web.FileResponse( os.path.join(self._webroot, "index.html"))

    async def uploadSVG(self, request):
        logger.debug("uploadSVG Post")
        svg = await request.content.read()
        parser = SVGParser()
        cords =parser.getXYCordsFromSVG(svg)            
        jsonData =parser.covertXYToJson(cords)
        return web.json_response(jsonData)
    
    def scrape_callback(self, return_value):
        return_value = return_value.result()
        if return_value:
            pass # handle done plotting
    
    async def plot(self, request):        
        logger.debug("plot Post")
        result =""        
        if not self.isPlottingInProgress:
            data = await request.content.read()
            jData = json.loads(data)
            t= self.loop.run_in_executor(self.pool, self.doPlot, jData)
            t.add_done_callback(self.scrape_callback)
            result ="{status:'Plotting Started'}"
        else:   
            result ="{status:'Plotting in Progress'}"
        return web.json_response(result)

    async def get_config(self, request):
        logger.debug("get_config get")
        data = Config().getConfig()
        return web.json_response(data)

    async def post_config(self, request):
        logger.debug("post_config post")
        txt = await request.text()
        jConfig = json.loads(txt)
        Config().setConfig(jConfig[0])
        
        data = Config().getConfig() #send back the updated data.
        return web.json_response(data)

    async def progress_handler(self,request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        s = 'a' * 1024

        i = 0
        while True:
            i += 1
            print('send ', len(s) * i)
            ws.send_str(s)
            await asyncio.sleep(0.1)

        return ws

    async def create_app(self):
        logger.debug("creating web app")
        app = web.Application()
        app.add_routes([
            web.get('/', self.index),
            web.post('/uploadSVG', self.uploadSVG),
            web.post('/plot', self.plot),
            web.get('/config', self.get_config),
            web.post('/config', self.post_config),

        ])
        app.router.add_static('/',path=self._webroot,name='static')
        return app
    
    
    
    def run_app(self):
        logger.debug("running web app")
        loop = self.loop
        app = loop.run_until_complete(self.create_app())
        web.run_app(app, host=self.host, port=self.port)

if __name__ == '__main__':
    s = WebServer(host='0.0.0.0', port=8080)
    s.run_app()
