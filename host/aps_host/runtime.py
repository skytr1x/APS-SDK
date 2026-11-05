import threading

from .constants import ABI_VERSION
from .engine import WasmModule
from .errors import HostError


class Runtime:
    def __init__(self, store, loader=None):
        self.store = store
        self.loader = loader or WasmModule
        self.modules = {}
        self.lock = threading.RLock()

    def start(self, plugin_id):
        path = self.store.path(plugin_id)
        with self.lock:
            if plugin_id in self.modules:
                return
            if not self.store.has_file(plugin_id):
                raise HostError('err_plugin_file_missing')
            instance = self.loader(path)
            if instance.exec('aps_abi_version', []) != ABI_VERSION:
                raise HostError('err_abi')
            if instance.exec('aps_on_load', []) != 0:
                raise HostError('err_load_failed')
            self.modules[plugin_id] = instance

    def stop(self, plugin_id):
        with self.lock:
            instance = self.modules.pop(plugin_id, None)
            if instance is not None:
                instance.exec('aps_on_unload', [])

    def close(self):
        for plugin_id in list(self.modules):
            try:
                self.stop(plugin_id)
            except Exception:
                pass

    # hooks
    def app_event(self, code):
        with self.lock:
            for instance in list(self.modules.values()):
                if not instance.has('aps_on_app_event'):
                    continue
                try:
                    instance.exec('aps_on_app_event', [int(code)])
                except Exception:
                    pass  # one module must not block the others

    def send(self, account):
        with self.lock:
            for instance in list(self.modules.values()):
                if not instance.has('aps_on_send_message'):
                    continue
                result = instance.exec('aps_on_send_message', [int(account)])
                if result == 1:
                    return True
                if result != 0:
                    raise HostError('err_unknown_hook')
        return False
