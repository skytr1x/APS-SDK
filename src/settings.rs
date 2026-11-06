use crate::bridge;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Error {
    Missing,
    TooLarge,
    Invalid,
}

/// Reads a setting into `out` and returns the UTF-8 slice.
pub fn get<'a>(key: &str, out: &'a mut [u8]) -> Result<&'a str, Error> {
    let needed = bridge::setting_get(key, core::ptr::null_mut(), 0);
    if needed < 0 {
        return Err(Error::Missing);
    }
    if needed as usize > out.len() {
        return Err(Error::TooLarge);
    }
    let written = bridge::setting_get(key, out.as_mut_ptr(), out.len());
    if written == -2 {
        return Err(Error::TooLarge);
    }
    if written < 0 {
        return Err(Error::Missing);
    }
    core::str::from_utf8(&out[..written as usize]).map_err(|_| Error::Invalid)
}

pub fn get_or<'a>(key: &str, default: &'a str, out: &'a mut [u8]) -> &'a str {
    get(key, out).unwrap_or(default)
}

pub fn set(key: &str, value: &str) -> bool {
    bridge::setting_set(key, value) == 0
}

pub fn get_bool(key: &str, default: bool) -> bool {
    let mut out = [0u8; 8];
    let text = get_or(key, if default { "true" } else { "false" }, &mut out);
    match text {
        "1" | "true" | "True" => true,
        "0" | "false" | "False" => false,
        _ => default,
    }
}

pub fn set_bool(key: &str, value: bool) -> bool {
    set(key, if value { "true" } else { "false" })
}
