import os
import tempfile
import threading

from . import wasm
from .constants import ABI_VERSION
from .errors import HostError

# module exporting aps_abi_version
PROBE = bytes.fromhex('0061736d010000000105016000017f030201000713010f6170735f6162695f76657273696f6e00000a0601040041010b')


class WasmModule:
    def __init__(self, path, bridge=None):
        self.engine = wasm.core.Runtime()
        self.lock = threading.RLock()
        imports = {}
        if bridge is not None:
            bridge.bind(self)
            imports['aps'] = bridge.imports()
        self.module = self.engine.instance_from_file(path, imports)

    def has(self, name):
        return any(export.name == name for export in self.module.exps)

    def exec(self, name, args):
        with self.lock:
            result = self.engine.invocate(self.module, name, args)
        if len(result) == 0:
            return None
        if len(result) == 1:
            return result[0]
        return result


def check_engine(directory):
    os.makedirs(directory, exist_ok=True)
    fd, path = tempfile.mkstemp(prefix='.engine-test-', suffix='.wasm', dir=directory)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(PROBE)
        if WasmModule(path).exec('aps_abi_version', []) != ABI_VERSION:
            raise HostError('err_engine_check')
    except HostError:
        raise
    except Exception as exc:
        raise HostError('err_engine_check') from exc
    finally:
        os.unlink(path)
