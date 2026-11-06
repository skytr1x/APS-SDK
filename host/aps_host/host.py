from .bridge import Bridge
from .constants import FLAG_PREFIX
from .events import event_code
from .runtime import Runtime
from .store import Store


class Host:
    def __init__(self, home, get_setting, set_setting, logger=None, loader=None):
        self.get_setting = get_setting
        self.set_setting = set_setting
        self.logger = logger
        self.store = Store(home)
        self.runtime = Runtime(self.store, loader, self._bridge)

    def _bridge(self, plugin_id):
        return Bridge(plugin_id, self.get_setting, self.set_setting, self.logger)

    # plugins
    def ids(self):
        return self.store.ids()

    def import_plugin(self, source):
        return self.store.import_file(source)

    def metadata(self, plugin_id):
        return self.store.metadata(plugin_id)

    def remove_plugin(self, plugin_id):
        try:
            self.runtime.stop(plugin_id)
        finally:
            self.set_enabled(plugin_id, False)
        self.store.delete(plugin_id)

    # flags
    def enabled(self, plugin_id):
        return self.get_setting(FLAG_PREFIX + plugin_id, False) is True

    def set_enabled(self, plugin_id, enabled):
        self.set_setting(FLAG_PREFIX + plugin_id, bool(enabled))

    def enabled_ids(self):
        return [name for name in self.ids() if self.enabled(name)]

    def disable_all(self):
        for name in self.ids():
            self.set_enabled(name, False)

    # lifecycle
    def toggle(self, plugin_id, enabled):
        try:
            if enabled:
                self.runtime.start(plugin_id)
            else:
                self.runtime.stop(plugin_id)
        except Exception:
            self.set_enabled(plugin_id, False)
            raise
        self.set_enabled(plugin_id, enabled)

    def start_enabled(self):
        for name in self.enabled_ids():
            try:
                self.runtime.start(name)
            except Exception:
                if self.logger:
                    self.logger.exception('APS: failed to start %s', name)

    def close(self):
        self.runtime.close()

    # hooks
    def app_event(self, events, event_type):
        code = event_code(events, event_type)
        if code is not None:
            self.runtime.app_event(code)

    def send(self, account):
        return self.runtime.send(account)
