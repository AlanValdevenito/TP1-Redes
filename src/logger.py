class Logger:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def log(self, message, quiet=False):
        if self.verbose or quiet:
            print(message)
