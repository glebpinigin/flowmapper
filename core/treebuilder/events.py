class AbstractEvent():
    
    def __init__(self):
        pass
    
    def run(self):
        pass
    
    def __call__(self):
        self.run()


class TerminalEvent():
    
    def __init__(self):
        pass


class JoinPointEvent():
    
    def __init__(self):
        pass


class VertexEvent():
    
    def __init__(self):
        pass
