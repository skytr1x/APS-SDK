use crate::bridge;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct AccountClient {
    account: i32,
}

impl AccountClient {
    pub const fn new(account: i32) -> Self {
        Self { account }
    }

    pub const fn account(self) -> i32 {
        self.account
    }

    pub fn send_text(self, peer: i64, text: &str) -> bool {
        bridge::send_text(self.account, peer, text) == 0
    }

    pub fn send_request(self, name: &str, json: &str) -> bool {
        bridge::send_request(self.account, name, json) >= 0
    }
}

pub fn get_selected_account() -> AccountClient {
    AccountClient::new(bridge::selected_account())
}
