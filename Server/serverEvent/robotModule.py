import serverEvent.module as module
import json
import time

class EventModule(module.EventModule):
    def __init__(self):
        super().__init__()
        self.Name = 'robot'
    
    def run() -> str:
        a = {
            'type': 'get_image',
            'data': '',
            'time': time.time() 
        }
        return (json.dumps(a), None)