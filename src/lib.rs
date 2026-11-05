#![no_std]
//! basically syntax of sdk

pub mod base_plugin;
mod metadata;

pub use base_plugin::{AppEvent, BasePlugin, HookResult, HookStrategy, ABI_VERSION};
pub mod prelude {
    pub use crate::base_plugin::{AppEvent, BasePlugin, HookResult, HookStrategy, ABI_VERSION};
    pub use crate::export_plugin;
    pub use crate::plugin_metadata;
}
