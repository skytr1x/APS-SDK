#![no_std]

pub mod base_plugin;
pub mod bridge;
pub mod client;
pub mod logger;
mod metadata;
pub mod settings;
pub mod ui;

pub use base_plugin::{AppEvent, BasePlugin, HookResult, HookStrategy, ABI_VERSION};
pub use bridge::BRIDGE_VERSION;

pub mod prelude {
    pub use crate::base_plugin::{AppEvent, BasePlugin, HookResult, HookStrategy, ABI_VERSION};
    pub use crate::client::{get_selected_account, AccountClient};
    pub use crate::export_plugin;
    pub use crate::logger::Logger;
    pub use crate::plugin_metadata;
    pub use crate::{settings, ui};
}
