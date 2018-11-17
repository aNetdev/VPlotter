import asyncio
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from aiohttp import WSMsgType, web
from plotter.config import Config
from plotter.plotter import PenDirection, CordDirection, Plotter
from plotter.svgParser import SVGParser

logger = logging.getLogger("plotterLog")


class WebServer:
    _webroot = os.path.join(os.path.dirname(__file__), 'web')

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.loop = asyncio.get_event_loop()
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.progress = []
        self.isPlottingInProgress = False

    def doPlot(self, data):
        self.isPlottingInProgress = True
        self.progress.clear()
        logger.info("Starting  to Plot")
        orgX = int(data['orgX'])
        orgY = int(data['orgY'])
        cords = data['cords']
        config = Config().getConfig()
        plotter = Plotter(config, orgX, orgY)
        plotter.init(False)
        plotter.enableSteppers()
        minX = min(cords['x'])
        maxX = max(cords['x'])

        minY = min(cords['y'])
        maxY = max(cords['y'])

        ax =[] #additional coordinates
        ay =[] #additional coordinates
        ap =[]
        
        #move to origin, even if we are already there
        ax.append(orgX)
        ay.append(orgY)
        ap.append(0) #PenDirection.Up

        #plotter.moveTo(minX, minY, PenDirection.Up)
        ax.append(minX)
        ay.append(minY)
        ap.append(0) #PenDirection.Up

        # top left corner horizontal line
        #plotter.moveTo(minX+10, minY, PenDirection.Down)
        ax.append(minX+10)
        ay.append(minY)
        ap.append(1) #PenDirection.Down

        #plotter.moveTo(maxX-10, minY, PenDirection.Up)
        ax.append(maxX-10)
        ay.append(minY)
        ap.append(0) #PenDirection.up

        # top Right
        # top right corner horizontal line
        #plotter.moveTo(maxX, minY, PenDirection.Down)
        ax.append(maxX)
        ay.append(minY)
        ap.append(1) 

        # top right corner vertical line
        #plotter.moveTo(maxX, minY+10, PenDirection.Down)
        ax.append(maxX)
        ay.append(minY+10)
        ap.append(1) 

        #plotter.moveTo(maxX, maxY-10, PenDirection.Up)
        ax.append(maxX)
        ay.append(maxY-10)
        ap.append(0) 

        # bottom Right
        # bottom right corner vertical line
        #plotter.moveTo(maxX, maxY, PenDirection.Down)
        ax.append(maxX)
        ay.append(maxY)
        ap.append(0) 

        # bottom right corner horizontal line
        #plotter.moveTo(maxX-10, maxY, PenDirection.Down)
        ax.append(maxX-10)
        ay.append(maxY)
        ap.append(1) 
        #plotter.moveTo(minX+10, maxY, PenDirection.Up)
        ax.append(minX+10)
        ay.append(maxY)
        ap.append(0) 

        # bottom left
        # bottom left corner horizontal line
        #plotter.moveTo(minX, maxY, PenDirection.Down)
        ax.append(minX)
        ay.append(maxY)
        ap.append(1) 
        # bottom left corner vertical line
        #plotter.moveTo(minX, maxY-10, PenDirection.Down)
        ax.append(minX)
        ay.append(maxY-10)
        ap.append(1)

        ax.append(minX)
        ay.append(minY)
        ap.append(0)

        cords['x'] = ax + cords['x'] 
        cords['y'] = ay + cords['y'] 
        cords['p'] = ap + cords['p']       

        total = len(cords['x'])

        for index in range(0, total-1):
            x = int(cords['x'][index])
            y = int(cords['y'][index])
            pen = PenDirection.Down if cords['p'][index] == 0 else PenDirection.Up
            perComplete = round(index/total * 100, 2)
            self.progress.append((x, y, perComplete))
            plotter.moveTo(x, y, pen)            
            logger.debug("Plotting {}%%".format(perComplete))
        plotter.finalize()
        self.progress.append((plotter.orgX, plotter.orgY, 100))
        logger.info("Done Plotting")
        self.isPlottingInProgress = False
        return "Complete"


    def doStep(self, data):
        dir=data['dir']
        steps =int(data['steps'])
        self.isPlottingInProgress = True        
        logger.info("Starting to Step")
        config = Config().getConfig()
        plotter = Plotter(config, 0, 0)
        plotter.init(False)
        plotter.enableSteppers()
        plotter.movePen(PenDirection.Up)
        if dir == "leftUp" :
            plotter.moveLeft( CordDirection.Backward, steps)
        if dir == "leftDown" :
            plotter.moveLeft( CordDirection.Forward, steps)
        if dir == "rightUp" :
            plotter.moveRight( CordDirection.Backward, steps)
        if dir == "rightDown" :
            plotter.moveRight( CordDirection.Forward, steps)
        self.isPlottingInProgress = False        
        logger.info("Done Stepping")
        return 'done'



    async def index(self, request):
        logger.debug("Index request")
        return web.FileResponse(os.path.join(self._webroot, "index.html"))

    async def uploadSVG(self, request):
        logger.debug("uploadSVG Post")
        svg = await request.text()
        parser = SVGParser()
        cords = parser.getXYCordsFromSVG(svg)
        jsonData = parser.covertXYToJson(cords)
        return web.json_response(jsonData)

    def scrape_callback(self, return_value):
        return_value = return_value.result()
        if return_value:
            pass  # handle done plotting

    async def plot(self, request):
        logger.debug("plot Post")
        result = {}
        if not self.isPlottingInProgress:
            jData = await request.json()
            t = self.loop.run_in_executor(self.pool, self.doPlot, jData)
            t.add_done_callback(self.scrape_callback)
            result['status'] = 'Started'
        else:
            result['status'] = 'InProgress'
        return web.json_response(result)

    async def get_config(self, request):
        logger.debug("get_config get")
        data = Config().getConfig()
        return web.json_response(data)

    async def post_config(self, request):
        logger.debug("post_config post")
        jConfig = await request.json()         
        Config().setConfig(jConfig)

        data = Config().getConfig()  # send back the updated data.
        return web.json_response(data)

    async def progress_handler(self, request):
        app = request.app
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        logger.info("websocket connection opened")
        app["sockets"].append(ws)
        lastResultIndex = 0
        msg = await ws.receive()
        logger.info("websocket message received")
        if msg.type == WSMsgType.TEXT:
            # send the results up to the last read
            # lastResultIndex < len(self.progress) means the plot finished and we are out of the loop but we have more data to send
            while self.isPlottingInProgress or lastResultIndex < (len(self.progress)-1):         
                l = len(self.progress)
                x = []
                y = []               
                # read the progress array
                for i in range(lastResultIndex, l-1):
                    lastResultIndex = lastResultIndex + 1
                    x.append(self.progress[i][0])
                    y.append(self.progress[i][1])

                progress = self.progress[l-1][2] if l > 0 else 0
                logger.info("progress {}".format(progress))

                if len(x) > 0:  # send data only if there is progress
                    data = {}
                    data['x'] = x
                    data['y'] = y
                    data['prg'] = round(progress)
                    await ws.send_json(data)
                await asyncio.sleep(2)

        elif msg.type == WSMsgType.close:
            logger.info("websocket connection closed by client")
        elif msg.type == WSMsgType.ERROR:
            logger.info('ws connection closed with exception %s' %
                        ws.exception())
        app["sockets"].remove(ws)
        await ws.close()     
        logger.info("websocket connection closed")
        return ws

    async def step(self, request):
        logger.debug("step Post")
        result = {}
        if not self.isPlottingInProgress:
            jData = await request.json()
            t = self.loop.run_in_executor(self.pool, self.doStep, jData)
            t.add_done_callback(self.scrape_callback)
            result['status'] = 'Started'
        else:
            result['status'] = 'InProgress'
        return web.json_response(result)

    async def create_app(self):
        logger.debug("creating web app")
        app = web.Application()
        app.add_routes([
            web.get('/', self.index),
            web.post('/uploadSVG', self.uploadSVG),
            web.post('/plot', self.plot),
            web.get('/config', self.get_config),
            web.post('/config', self.post_config),
            web.get('/progress', self.progress_handler),
            web.post('/step', self.step),
        ])
        app.router.add_static('/', path=self._webroot, name='static')
        return app

    def run_app(self):
        logger.debug("running web app")
        loop = self.loop
        app = loop.run_until_complete(self.create_app())
        app["sockets"] = []
        web.run_app(app, host=self.host, port=self.port)


if __name__ == '__main__':
    s = WebServer(host='0.0.0.0', port=8080)
    s.run_app()
