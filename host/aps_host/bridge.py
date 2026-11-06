import importlib
import json


class Bridge:
    # host functions for one wasm plugin
    def __init__(self, plugin_id, get_setting, set_setting, logger=None):
        self.plugin_id = plugin_id
        self.get_setting = get_setting
        self.set_setting = set_setting
        self.logger = logger
        self.module = None

    def bind(self, module):
        self.module = module

    def imports(self):
        return {
            'aps_log': self._log,
            'aps_setting_get': self._setting_get,
            'aps_setting_set': self._setting_set,
            'aps_selected_account': self._selected_account,
            'aps_send_text': self._send_text,
            'aps_send_request': self._send_request,
            'aps_ui_post': self._ui_post,
            'aps_show_bulletin': self._show_bulletin,
        }

    # memory
    @staticmethod
    def _memory(machine):
        return machine.store.mems[machine.stack.frame[-1].module.mems[0]].data

    def _read(self, machine, ptr, length):
        if ptr < 0 or length < 0:
            return None
        memory = self._memory(machine)
        if ptr + length > len(memory):
            return None
        try:
            return bytes(memory[ptr:ptr + length]).decode('utf-8')
        except UnicodeDecodeError:
            return None

    def _write(self, machine, ptr, cap, data):
        if ptr < 0 or cap < 0:
            return -1
        if ptr == 0:
            return len(data)  # size probe
        memory = self._memory(machine)
        if len(data) > cap or ptr + len(data) > len(memory):
            return -2
        memory[ptr:ptr + len(data)] = data
        return len(data)

    # settings
    def _setting_key(self, key):
        return 'aps.' + self.plugin_id + '.' + key

    @staticmethod
    def _encode(value):
        if isinstance(value, bool):
            return b'true' if value else b'false'
        if isinstance(value, (str, int, float)):
            return str(value).encode('utf-8')
        return json.dumps(value, ensure_ascii=False).encode('utf-8')

    def _setting_get(self, machine, key_ptr, key_len, out_ptr, out_cap):
        key = self._read(machine, key_ptr, key_len)
        if not key:
            return -1
        value = self.get_setting(self._setting_key(key), None)
        if value is None:
            return -1
        return self._write(machine, out_ptr, out_cap, self._encode(value))

    def _setting_set(self, machine, key_ptr, key_len, value_ptr, value_len):
        key = self._read(machine, key_ptr, key_len)
        value = self._read(machine, value_ptr, value_len)
        if not key or value is None:
            return -1
        self.set_setting(self._setting_key(key), value)
        return 0

    # client
    def _selected_account(self, _machine):
        try:
            client_utils = importlib.import_module('client_utils')
            return int(client_utils.get_selected_account())
        except Exception:
            self._exception('APS: failed to read the selected account')
            return -1

    def _send_text(self, machine, account, peer, ptr, length):
        text = self._read(machine, ptr, length)
        if text is None:
            return -1
        try:
            client_utils = importlib.import_module('client_utils')
            client_utils.send_text(int(peer), text, account=int(account))
            return 0
        except Exception:
            self._exception('APS: failed to send a message')
            return -1

    def _send_request(self, machine, account, name_ptr, name_len, json_ptr, json_len):
        name = self._read(machine, name_ptr, name_len)
        payload = self._read(machine, json_ptr, json_len)
        if not name or payload is None:
            return -1
        try:
            fields = json.loads(payload) if payload.strip() else {}
            if not isinstance(fields, dict):
                return -1
            hook_utils = importlib.import_module('hook_utils')
            client_utils = importlib.import_module('client_utils')
            if '.' not in name:
                name = 'org.telegram.tgnet.TLRPC$' + name
            request_type = hook_utils.find_class(name)
            if request_type is None:
                return -1
            request = request_type()
            for key, value in fields.items():
                setattr(request, key, value)

            def callback(_response, error):
                if error is not None:
                    self._warning('APS: request %s failed: %s',
                                  name, getattr(error, 'text', error))

            result = client_utils.send_request(request, callback, account=int(account))
            return int(result) if result is not None else 0
        except Exception:
            self._exception('APS: failed to send request %s', name)
            return -1

    # ui
    def _ui_post(self, _machine, task, delay_ms):
        module = self.module
        if module is None:
            return -1
        try:
            android_utils = importlib.import_module('android_utils')

            def run():
                try:
                    module.exec('aps_run_task', [int(task)])
                except Exception:
                    self._exception('APS: UI task failed')

            android_utils.run_on_ui_thread(run, int(delay_ms))
            return 0
        except Exception:
            self._exception('APS: failed to post a UI task')
            return -1

    def _show_bulletin(self, machine, kind, ptr, length):
        text = self._read(machine, ptr, length)
        if text is None:
            return -1
        try:
            bulletin = importlib.import_module('ui.bulletin').BulletinHelper
            show = (bulletin.show_info, bulletin.show_error, bulletin.show_success)
            show[int(kind)](text)
            return 0
        except Exception:
            self._exception('APS: failed to show a bulletin')
            return -1

    # logging
    def _log(self, machine, level, ptr, length):
        text = self._read(machine, ptr, length)
        if text is None:
            return
        line = '[%s] %s' % (self.plugin_id, text)
        if self.logger is not None:
            names = ('debug', 'info', 'warning', 'error')
            name = names[level] if 0 <= level < len(names) else 'info'
            getattr(self.logger, name, self.logger.info)(line)
            return
        try:
            android_utils = importlib.import_module('android_utils')
            android_utils.log(line)
        except Exception:
            pass

    def _warning(self, message, *args):
        if self.logger is not None:
            self.logger.warning(message, *args)

    def _exception(self, message, *args):
        if self.logger is not None:
            self.logger.exception(message, *args)
