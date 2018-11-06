import os
import json
from aiohttp import web
from svgParser import SVGParser
from config import Config

_webroot= os.path.join(os.path.dirname(__file__), '..','web')
_scripts= os.path.join(_webroot, "scripts")

async def index(request):
    return web.FileResponse( os.path.join(_webroot, "index.html"))

async def uploadSVG(request):
    svg = await request.content.read()
    parser = SVGParser()
    cords =parser.getXYCordsFromSVG(svg)            
    jsonData =parser.covertXYToJson(cords)
    return web.json_response(jsonData)

async def plot(request):
      cords = await request.content.read()
      jdata = json.loads(cords)

async def get_config(request):
    data = Config().getConfig()
    return web.json_response(data)

async def post_config(request):
    txt = await request.text()
    jconfig = json.loads(txt)
    Config().setConfig(jconfig[0])
    
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
app.router.add_static('/scripts/',path=_scripts,name='static')
web.run_app(app)
