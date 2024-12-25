
from threading import Thread, Lock

class SynchronizedThread(Thread):
    def __init__(self, target, name, *args, **kwargs):
        self.target = lambda *args, **kwargs: target(*args, **kwargs)
        super().__init__(target=target, name=name, args=args, kwargs=kwargs)

    def run(self):
        with self.lock:
            self.target(*self._args, **self._kwargs)