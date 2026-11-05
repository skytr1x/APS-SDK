#![no_std]
use aps_sdk::base_plugin::{BasePlugin, HookResult};
use aps_sdk::{export_plugin, plugin_metadata};

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
    fn on_send_message(_account: i32) -> HookResult {
        HookResult::pass()
    }
}

export_plugin!(Example);

#[cfg(target_arch = "wasm32")]
#[panic_handler]
fn panic(_info: &core::panic::PanicInfo) -> ! { loop {} }
