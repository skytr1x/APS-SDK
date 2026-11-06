use core::sync::atomic::{AtomicUsize, Ordering};

use crate::bridge;

const MAX_TASKS: usize = 32;
static TASKS: [AtomicUsize; MAX_TASKS] = [const { AtomicUsize::new(0) }; MAX_TASKS];

#[repr(i32)]
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Bulletin {
    Info = 0,
    Error = 1,
    Success = 2,
}

/// schedules a plain function on the android ui thread
pub fn post(task: fn(), delay_ms: i32) -> bool {
    for (id, slot) in TASKS.iter().enumerate() {
        if slot
            .compare_exchange(0, task as usize, Ordering::Relaxed, Ordering::Relaxed)
            .is_err()
        {
            continue;
        }
        if bridge::ui_post(id as i32, delay_ms) == 0 {
            return true;
        }
        slot.store(0, Ordering::Relaxed);
        return false;
    }
    false
}

pub fn show(kind: Bulletin, text: &str) -> bool {
    bridge::show_bulletin(kind as i32, text) == 0
}

pub fn show_info(text: &str) -> bool {
    show(Bulletin::Info, text)
}

pub fn show_error(text: &str) -> bool {
    show(Bulletin::Error, text)
}

pub fn show_success(text: &str) -> bool {
    show(Bulletin::Success, text)
}

pub fn run_task(task: i32) {
    if task < 0 || task as usize >= MAX_TASKS {
        return;
    }
    let ptr = TASKS[task as usize].swap(0, Ordering::Relaxed);
    if ptr != 0 {
        let task: fn() = unsafe { core::mem::transmute(ptr) };
        task();
    }
}
