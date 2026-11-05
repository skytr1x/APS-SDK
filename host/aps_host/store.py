import os

from .constants import ID_RE, MAX_WASM, PLUGIN_EXT, WASM_MAGIC
from .errors import HostError
from .metadata import parse_metadata


def read_limited(stream, limit):
    data = bytearray()
    while True:
        block = stream.read(min(65536, limit + 1 - len(data)))
        if not block:
            break
        data.extend(block)
        if len(data) > limit:
            raise HostError('err_too_large')
    return bytes(data)


class Store:
    def __init__(self, home):
        self.folder = os.path.join(home, 'plugins')

    def path(self, plugin_id):
        if not ID_RE.fullmatch(plugin_id):
            raise HostError('err_bad_plugin_id')
        return os.path.join(self.folder, plugin_id + PLUGIN_EXT)

    def has_file(self, plugin_id):
        path = self.path(plugin_id)
        return os.path.isfile(path) and not os.path.islink(path)

    def ids(self):
        if not os.path.isdir(self.folder):
            return []
        cut = len(PLUGIN_EXT)
        return sorted(n[:-cut] for n in os.listdir(self.folder)
                      if n.endswith(PLUGIN_EXT) and ID_RE.fullmatch(n[:-cut])
                      and self.has_file(n[:-cut]))

    def import_file(self, source):
        name = os.path.basename(source)
        plugin_id = name[:-len(PLUGIN_EXT)]
        if not name.endswith(PLUGIN_EXT) or not ID_RE.fullmatch(plugin_id):
            raise HostError('err_bad_name')
        with open(source, 'rb') as src:
            data = read_limited(src, MAX_WASM)
        if not data.startswith(WASM_MAGIC):
            raise HostError('err_not_wasm')
        os.makedirs(self.folder, exist_ok=True)
        dest = os.path.join(self.folder, name)
        if os.path.exists(dest):
            raise HostError('err_exists')
        parse_metadata(data, plugin_id, strict=True)
        with open(dest, 'xb') as out:  # never overwrite
            out.write(data)
        return plugin_id

    def metadata(self, plugin_id):
        if not self.has_file(plugin_id):
            raise HostError('err_plugin_file_missing')
        with open(self.path(plugin_id), 'rb') as src:
            data = read_limited(src, MAX_WASM)
        return parse_metadata(data, plugin_id)

    def delete(self, plugin_id):
        if not self.has_file(plugin_id):
            raise HostError('err_plugin_file_missing')
        os.unlink(self.path(plugin_id))
