class EventModule:
    def __init__(self):
        self.Name: str = 'test'
        print('Loaded Event')
    def run() -> tuple:
        return 'send_client_message', 'send_server_message'