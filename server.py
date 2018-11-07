import os
import json
import asyncio
from aiohttp import web
from plotter.svgParser import SVGParser
from plotter.plotter import Plotter,PenDirection
from plotter.config import Config

_webroot= os.path.join(os.path.dirname(__file__), 'web')
#_scripts= os.path.join(_webroot, "scripts")

async def index(request):
    return web.FileResponse( os.path.join(_webroot, "index.html"))

async def uploadSVG(request):
    svg = await request.content.read()
    parser = SVGParser()
    cords =parser.getXYCordsFromSVG(svg)            
    jsonData =parser.covertXYToJson(cords)
    return web.json_response(jsonData)



async def doPlot(data):
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
    

    await plotter.moveTo(minX, minY, PenDirection.Up)

    await plotter.moveTo(minX+10, minY, PenDirection.Down)    #top left corner horizontal line
    await plotter.moveTo(maxX-10, minY, PenDirection.Up)      

    #top Right
    await plotter.moveTo(maxX, minY, PenDirection.Down) #top right corner horizontal line    
    await plotter.moveTo(maxX, minY+10, PenDirection.Down)   #top right corner vertical line

    await plotter.moveTo(maxX,maxY-10, PenDirection.Up)
    
    #bottom Right
    await plotter.moveTo(maxX,maxY, PenDirection.Down)  #bottom right corner vertical line
    
    await plotter.moveTo(maxX-10,maxY, PenDirection.Down)   #bottom right corner horizontal line
    await plotter.moveTo(minX+10,maxY, PenDirection.Up)
    
    #bottom left
    await plotter.moveTo(minX,maxY, PenDirection.Down) #bottom left corner horizontal line
    await plotter.moveTo(minX,maxY-10, PenDirection.Down) #bottom left corner vertical line
    
    #input("Done with border. Enter to continue")

    total =len(cords['x'])

    for index in range(0,total-1):
        x = int(cords['x'][index])
        y = int(cords['y'][index])
        pen = PenDirection.Down if cords['p'][index] == 0 else PenDirection.Up
        await plotter.moveTo(x, y, pen)
        #perComplete =round(current/total * 100 ,2)
        

async def plot(request):
      data = await request.content.read()
      jData = json.loads(data)
      asyncio.ensure_future( doPlot(jData))
      return web.Response()
      
     
      



async def get_config(request):
    data = Config().getConfig()
    return web.json_response(data)

async def post_config(request):
    txt = await request.text()
    jConfig = json.loads(txt)
    Config().setConfig(jConfig[0])
    
    data = Config().getConfig() #send back the updated data.
    return web.json_response(data)
    




app = web.Application()
app.add_routes([
    web.get('/', index),
    web.post('/uploadSVG', uploadSVG),
    web.post('/plot', plot),
    web.get('/config', get_config),
    web.post('/config', post_config),

])
app.router.add_static('/',path=_webroot,name='static')
web.run_app(app)
