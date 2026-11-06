pub const BRIDGE_VERSION: i32 = 1;

#[cfg(target_arch = "wasm32")]
mod sys {
    #[link(wasm_import_module = "aps")]
    extern "C" {
        pub fn aps_log(level: i32, ptr: *const u8, len: usize);
        pub fn aps_setting_get(
            key_ptr: *const u8,
            key_len: usize,
            out_ptr: *mut u8,
            out_cap: usize,
        ) -> i32;
        pub fn aps_setting_set(
            key_ptr: *const u8,
            key_len: usize,
            value_ptr: *const u8,
            value_len: usize,
        ) -> i32;
        pub fn aps_selected_account() -> i32;
        pub fn aps_send_text(account: i32, peer: i64, ptr: *const u8, len: usize) -> i32;
        pub fn aps_send_request(
            account: i32,
            name_ptr: *const u8,
            name_len: usize,
            json_ptr: *const u8,
            json_len: usize,
        ) -> i32;
        pub fn aps_ui_post(task: i32, delay_ms: i32) -> i32;
        pub fn aps_show_bulletin(kind: i32, ptr: *const u8, len: usize) -> i32;
    }
}

#[cfg(not(target_arch = "wasm32"))]
mod sys {
    pub unsafe fn aps_log(_level: i32, _ptr: *const u8, _len: usize) {}
    pub unsafe fn aps_setting_get(
        _key_ptr: *const u8,
        _key_len: usize,
        _out_ptr: *mut u8,
        _out_cap: usize,
    ) -> i32 {
        -1
    }
    pub unsafe fn aps_setting_set(
        _key_ptr: *const u8,
        _key_len: usize,
        _value_ptr: *const u8,
        _value_len: usize,
    ) -> i32 {
        -1
    }
    pub unsafe fn aps_selected_account() -> i32 {
        0
    }
    pub unsafe fn aps_send_text(_account: i32, _peer: i64, _ptr: *const u8, _len: usize) -> i32 {
        -1
    }
    pub unsafe fn aps_send_request(
        _account: i32,
        _name_ptr: *const u8,
        _name_len: usize,
        _json_ptr: *const u8,
        _json_len: usize,
    ) -> i32 {
        -1
    }
    pub unsafe fn aps_ui_post(_task: i32, _delay_ms: i32) -> i32 {
        -1
    }
    pub unsafe fn aps_show_bulletin(_kind: i32, _ptr: *const u8, _len: usize) -> i32 {
        -1
    }
}

pub(crate) fn log(level: i32, message: &str) {
    unsafe { sys::aps_log(level, message.as_ptr(), message.len()) }
}

pub(crate) fn setting_get(key: &str, out_ptr: *mut u8, out_cap: usize) -> i32 {
    unsafe { sys::aps_setting_get(key.as_ptr(), key.len(), out_ptr, out_cap) }
}

pub(crate) fn setting_set(key: &str, value: &str) -> i32 {
    unsafe { sys::aps_setting_set(key.as_ptr(), key.len(), value.as_ptr(), value.len()) }
}

pub(crate) fn selected_account() -> i32 {
    unsafe { sys::aps_selected_account() }
}

pub(crate) fn send_text(account: i32, peer: i64, text: &str) -> i32 {
    unsafe { sys::aps_send_text(account, peer, text.as_ptr(), text.len()) }
}

pub(crate) fn send_request(account: i32, name: &str, json: &str) -> i32 {
    unsafe {
        sys::aps_send_request(
            account,
            name.as_ptr(),
            name.len(),
            json.as_ptr(),
            json.len(),
        )
    }
}

pub(crate) fn ui_post(task: i32, delay_ms: i32) -> i32 {
    unsafe { sys::aps_ui_post(task, delay_ms) }
}

pub(crate) fn show_bulletin(kind: i32, text: &str) -> i32 {
    unsafe { sys::aps_show_bulletin(kind, text.as_ptr(), text.len()) }
}
