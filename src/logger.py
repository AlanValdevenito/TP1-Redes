class Logger:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def log(self, message):
        if self.verbose:
            print(message)
