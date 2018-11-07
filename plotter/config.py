import os
import yaml

class Config:
    _config = _webroot= os.path.join(os.path.dirname(__file__), '..','config','plotter.yaml') 
    def __init__(self):
        pass
     
    def getConfig(self):
         stream =  open(self._config, 'r')
         config =yaml.load(stream)
         return config
    
    def setConfig(self,newConfig):
        config =self.getConfig()
        nc =config.copy()
        nc.update(newConfig)
        yconfig =yaml.dump(nc)
        stream =  open(self._config, 'w')
        stream.write(yconfig)
        stream.close()


if __name__ =="__main__":
    c = Config()
    config= c.getConfig()
    config['plotter']['b']=370
    config['plotter']['pins']['leftDirPin']=99999
    c.setConfig(config)
