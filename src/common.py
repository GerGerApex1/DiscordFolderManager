# type: ignore
import threading
import credentials_manager
class CustomThread(threading.Thread):
    def __init__(self, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        threading.Thread.__init__(self, target=target, name=name, args=args, kwargs=kwargs)
        self._return = None
    def join(self, *args) -> None:
        threading.Thread.join(self, *args)
        return self._return
    def run(self) -> None:
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
def _saveToken(token):
    thread = threading.Thread(target=credentials_manager.store_token, args=(f'{token}',))