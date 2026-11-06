use crate::bridge;

#[repr(i32)]
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Level {
    Debug = 0,
    Info = 1,
    Warn = 2,
    Error = 3,
}

/// static logger
pub struct Logger;

impl Logger {
    pub fn log(level: Level, message: &str) {
        bridge::log(level as i32, message)
    }

    pub fn debug(message: &str) {
        Self::log(Level::Debug, message)
    }

    pub fn info(message: &str) {
        Self::log(Level::Info, message)
    }

    pub fn warn(message: &str) {
        Self::log(Level::Warn, message)
    }

    pub fn error(message: &str) {
        Self::log(Level::Error, message)
    }
}
