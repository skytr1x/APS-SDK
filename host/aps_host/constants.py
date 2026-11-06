import re

ABI_VERSION = 1
BRIDGE_VERSION = 1
PLUGIN_EXT = '.apl'
MAX_WASM = 2 * 1024 * 1024
ID_RE = re.compile(r'^[A-Za-z][A-Za-z0-9_]{1,31}$')
WASM_MAGIC = b'\0asm\x01\0\0\0'
FLAG_PREFIX = 'aps_enabled_'
