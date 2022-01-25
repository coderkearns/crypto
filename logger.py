
class Logger:
    def __init__(self):
        self.log = []

    def __call__(self, type, *args, **kwargs):
        self.log.append({ "type": type.upper(), **kwargs })

    def __str__(self):
        return "\n".join([ Logger.format(log) for log in self.log ])

    def save(self, file):
        with open(file, "w") as f:
            f.write(self.__str__())

    def save_append(file):
        with open(file, "a") as f:
            f.write(self.__str__())

    def print(self):
        print(self.__str__())

    @property
    def last(self):
        return self.log[-1]

    @staticmethod
    def format(log):
        kwargs = ", ".join([f"{k}={repr(v)}" for k, v in log.items()])
        return f"[{log['type']}] {kwargs}"
