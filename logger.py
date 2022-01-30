
class Logger:
    def __init__(self, *args, file=None, save_each=False):
        self.log = []
        self.save_each = save_each
        if file:
            self.file = file
        else:
            if save_each:
                self.file = "blockchain.log"

    def _potential_save(self):
        if self.save_each:
            self.save_append(self.file)

    def __call__(self, type, *args, **kwargs):
        self.log.append({ "type": type.upper(), **kwargs })
        self._potential_save()

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
        kwargs = ", ".join([f"{k}={repr(v)}" for k, v in log.items() if k != "type"])
        return f"[{log['type']}] {kwargs}"
