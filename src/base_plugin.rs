pub const ABI_VERSION: i32 = 1;

#[repr(i32)]
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum HookStrategy {
    Default = 0,
    Cancel = 1,
}

impl Default for HookStrategy {
    fn default() -> Self {
        Self::Default
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct HookResult {
    pub strategy: HookStrategy,
}

impl HookResult {
    pub const fn new(strategy: HookStrategy) -> Self {
        Self { strategy }
    }

    pub const fn pass() -> Self {
        Self::new(HookStrategy::Default)
    }

    pub const fn cancel() -> Self {
        Self::new(HookStrategy::Cancel)
    }
}

impl Default for HookResult {
    fn default() -> Self {
        Self::pass()
    }
}

// lifecycle
#[repr(i32)]
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum AppEvent {
    Start = 0,
    Stop = 1,
    Pause = 2,
    Resume = 3,
    /// event unknown to this SDK.
    Unknown = 4,
}

impl AppEvent {
    pub const fn from_i32(value: i32) -> Self {
        match value {
            0 => Self::Start,
            1 => Self::Stop,
            2 => Self::Pause,
            3 => Self::Resume,
            _ => Self::Unknown,
        }
    }

    // return the abi code
    pub const fn as_i32(self) -> i32 {
        self as i32
    }
}

pub trait BasePlugin {
    fn on_plugin_load() -> i32 {
        0
    }

    fn on_plugin_unload() -> i32 {
        0
    }

    fn on_app_event(_event: AppEvent) -> i32 {
        0
    }

    fn on_send_message(_account: i32) -> HookResult {
        HookResult::pass()
    }
}

#[macro_export]
macro_rules! export_plugin {
    ($plugin:ty) => {
        #[no_mangle]
        pub extern "C" fn aps_abi_version() -> i32 {
            $crate::base_plugin::ABI_VERSION
        }

        #[no_mangle]
        pub extern "C" fn aps_bridge_version() -> i32 {
            $crate::bridge::BRIDGE_VERSION
        }

        #[no_mangle]
        pub extern "C" fn aps_run_task(task: i32) {
            $crate::ui::run_task(task)
        }

        #[no_mangle]
        pub extern "C" fn aps_on_load() -> i32 {
            <$plugin as $crate::base_plugin::BasePlugin>::on_plugin_load()
        }

        #[no_mangle]
        pub extern "C" fn aps_on_unload() -> i32 {
            <$plugin as $crate::base_plugin::BasePlugin>::on_plugin_unload()
        }

        #[no_mangle]
        pub extern "C" fn aps_on_app_event(event: i32) -> i32 {
            <$plugin as $crate::base_plugin::BasePlugin>::on_app_event(
                $crate::base_plugin::AppEvent::from_i32(event),
            )
        }

        #[no_mangle]
        pub extern "C" fn aps_on_send_message(account: i32) -> i32 {
            <$plugin as $crate::base_plugin::BasePlugin>::on_send_message(account).strategy as i32
        }
    };
}
