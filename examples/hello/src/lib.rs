#![no_std]
use aps_sdk::base_plugin::{BasePlugin, HookResult};
use aps_sdk::logger::Logger;
use aps_sdk::{export_plugin, plugin_metadata, settings};

plugin_metadata! {
    id: "Hello",
    name: "Hello",
    description: "Example APS plugin",
    author: "@skytr1x",
    version: "1.0.0",
    app_version: ">=12.5.1",
    sdk_version: ">=1.0",
    category: "tools",
}

struct Example;

impl BasePlugin for Example {
    fn on_plugin_load() -> i32 {
        Logger::info("Hello plugin loaded");
        0
    }

    fn on_send_message(_account: i32) -> HookResult {
        if settings::get_bool("enabled", true) {
            Logger::debug("outgoing message allowed");
        }
        HookResult::pass()
    }
}

export_plugin!(Example);

#[cfg(target_arch = "wasm32")]
#[panic_handler]
fn panic(_info: &core::panic::PanicInfo) -> ! { loop {} }
