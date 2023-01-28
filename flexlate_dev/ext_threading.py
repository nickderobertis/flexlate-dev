from threading import Thread


# See https://stackoverflow.com/a/31614591/6276321
class PropagatingThread(Thread):
    def run(self):
        self.exc = None
        self.ret = None
        try:
            self.ret = self._target(*self._args, **self._kwargs)  # type: ignore
        except BaseException as e:
            self.exc = e

    def join(self, timeout=None):
        super().join(timeout)
        if self.exc:
            raise self.exc
        return self.ret
