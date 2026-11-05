from .constants import WASM_MAGIC
from .errors import HostError

SECTION = 'aps.meta'
MAX_SECTION = 64 * 1024
DEFAULT_VERSION = '1.0.0'
CATEGORIES = (
    'appearance',
    'chats',
    'media',
    'privacy',
    'tools',
    'integrations',
    'fun',
    'libraries',
)


def _defaults(plugin_id):
    return {
        'id': plugin_id,
        'name': plugin_id,
        'description': '',
        'author': '',
        'version': DEFAULT_VERSION,
        'icon': '',
        'app_version': '',
        'sdk_version': '',
        'min_version': '',
        'requirements': '',
        'requires': [],
        'category': [],
    }


def _uleb(data, pos, end):
    value = 0
    shift = 0
    while pos < end and shift < 35:
        byte = data[pos]
        pos += 1
        value |= (byte & 0x7f) << shift
        if not byte & 0x80:
            return value, pos
        shift += 7
    raise HostError('err_bad_metadata')


def _section(data, name):
    if not data.startswith(WASM_MAGIC):
        raise HostError('err_not_wasm')
    pos = len(WASM_MAGIC)
    end = len(data)
    while pos < end:
        section_id = data[pos]
        pos += 1
        size, pos = _uleb(data, pos, end)
        if size > end - pos:
            raise HostError('err_bad_metadata')
        start = pos
        pos += size
        if section_id != 0:
            continue
        name_len, name_pos = _uleb(data, start, pos)
        if name_len > pos - name_pos:
            raise HostError('err_bad_metadata')
        section_name = data[name_pos:name_pos + name_len]
        if section_name == name.encode('utf-8'):
            payload = data[name_pos + name_len:pos]
            if len(payload) > MAX_SECTION:
                raise HostError('err_meta_too_large')
            return payload
    return None


def _split(value):
    return [part.strip() for part in value.replace(';', ',').split(',') if part.strip()]


def _payload(payload):
    parts = payload.split(b'\0')
    if parts and parts[-1] == b'':
        parts.pop()
    if len(parts) % 2:
        raise HostError('err_bad_metadata')
    values = {}
    categories = []
    requires = []
    for index in range(0, len(parts), 2):
        try:
            key = parts[index].decode('utf-8').strip().strip('_').lower()
            value = parts[index + 1].decode('utf-8').strip()
        except UnicodeDecodeError as exc:
            raise HostError('err_bad_metadata') from exc
        if not key:
            continue
        if key == 'category':
            categories.extend(_split(value))
        elif key == 'requires':
            requires.extend(_split(value))
        else:
            values[key] = value
    return values, categories, requires


def _categories(values):
    result = []
    for value in values:
        if value in CATEGORIES and value not in result:
            result.append(value)
    return result[:3]


def parse_metadata(data, plugin_id, strict=False):
    try:
        payload = _section(data, SECTION)
    except HostError:
        if strict:
            raise
        return _defaults(plugin_id)
    if payload is None:
        return _defaults(plugin_id)
    try:
        values, categories, requires = _payload(payload)
        metadata_id = values.get('id', '').strip()
        if metadata_id and metadata_id != plugin_id and strict:
            raise HostError('err_meta_id')
        name = values.get('name', '').strip()
        if not name:
            if strict:
                raise HostError('err_meta_name')
            name = plugin_id
        min_version = values.get('min_version', '').strip()
        app_version = values.get('app_version', '').strip()
        if not app_version and min_version:
            app_version = '>=' + min_version
        return {
            'id': plugin_id,
            'name': name,
            'description': values.get('description', '').strip(),
            'author': values.get('author', '').strip(),
            'version': values.get('version', '').strip() or DEFAULT_VERSION,
            'icon': values.get('icon', '').strip(),
            'app_version': app_version,
            'sdk_version': values.get('sdk_version', '').strip(),
            'min_version': min_version,
            'requirements': values.get('requirements', '').strip(),
            'requires': requires,
            'category': _categories(categories),
        }
    except HostError:
        if strict:
            raise
        return _defaults(plugin_id)
