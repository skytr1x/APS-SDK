# abi code is the index
NAMES = ('START', 'STOP', 'PAUSE', 'RESUME')


def event_code(events, event_type):
    for code, name in enumerate(NAMES):
        value = getattr(events, name, None)
        if value is not None and event_type == value:
            return code
    return None
