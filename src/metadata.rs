#[macro_export]
macro_rules! plugin_metadata {
    ($($key:ident : $value:literal),* $(,)?) => {
        const APS_METADATA_STR: &str = concat!(
            $( stringify!($key), "\0", $value, "\0" ),*
        );
        const APS_METADATA_LEN: usize = APS_METADATA_STR.len();
        const APS_METADATA_BYTES: [u8; APS_METADATA_LEN] = {
            let mut bytes = [0u8; APS_METADATA_LEN];
            let source = APS_METADATA_STR.as_bytes();
            let mut index = 0;
            while index < APS_METADATA_LEN {
                bytes[index] = source[index];
                index += 1;
            }
            bytes
        };
        #[link_section = "aps.meta"]
        #[used]
        static APS_METADATA: [u8; APS_METADATA_LEN] = APS_METADATA_BYTES;
    };
}
