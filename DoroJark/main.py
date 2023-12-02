from .object import Object
from .service import Service
from .model import Model


class DoroJark(Object, Service, Model):
    def __init__(self, DeviceId, AppVersionString, region):
        self.region = region
        Service.__init__(self)
        Model.__init__(self)
