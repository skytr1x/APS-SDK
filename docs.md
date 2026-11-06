# APS SDK: `base_plugin`

Документация по APS SDK для разработчиков.

## Быстрый старт

Минимальный плагин:

```rust
#![no_std]

use aps_sdk::base_plugin::{BasePlugin, HookResult};
use aps_sdk::{export_plugin, plugin_metadata};

plugin_metadata! {
    id: "MyPlugin",
    name: "My Plugin",
    description: "Minimal APS plugin",
    author: "@yourUsername",
    version: "1.0.0",
    category: "tools",
}

struct MyPlugin;

impl BasePlugin for MyPlugin {
    fn on_send_message(_account: i32) -> HookResult {
        HookResult::pass()
    }
}

export_plugin!(MyPlugin);

#[cfg(target_arch = "wasm32")]
#[panic_handler]
fn panic(_info: &core::panic::PanicInfo) -> ! {
    loop {}
}
```

`Cargo.toml`:

```toml
[package]
name = "my-plugin"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
# Репозиторий SDK лежит рядом с репозиторием плагина:
aps-sdk = { path = "../APS-SDK" }
# или
# aps-sdk = { git = "https://github.com/skytr1x/APS-SDK", branch = "main" }

[profile.release]
panic = "abort"
opt-level = "s"
```

`path` указывает на корень репозитория SDK, где лежит `Cargo.toml`. Имя папки зависит от того, как вы склонировали репозиторий.

`panic = "abort"` обязателен: паника завершает WASM-экземпляр.

Сборка:

```sh
rustup target add wasm32-unknown-unknown
RUSTFLAGS="-C target-feature=-bulk-memory,-reference-types,-multivalue,-sign-ext,-nontrapping-fptoint" \
  cargo build --release --target wasm32-unknown-unknown
```

Флаги убирают инструкции, которые не понимает встроенный pywasm. Чтобы не передавать их каждый раз, создайте `.cargo/config.toml`:

```toml
[target.wasm32-unknown-unknown]
rustflags = [
  "-C",
  "target-feature=-bulk-memory,-reference-types,-multivalue,-sign-ext,-nontrapping-fptoint",
]
```

Артефакт лежит в `target/wasm32-unknown-unknown/release/my_plugin.wasm`. Для быстрой проверки без сборки используйте `cargo check --target wasm32-unknown-unknown`.

Переименуйте `.wasm` в `MyPlugin.apl`, откройте в чате exteraGram и включите плагин в настройках APS. Имя файла задаёт ID; поле `id` в метаданных должно с ним совпадать.

## ID и файл

ID берётся из имени файла:

```text
Weather.apl      -> Weather
weather_tool.apl -> weather_tool
```

Правила: 2–32 символа. Первый символ обязан быть латинской буквой, когда как остальные могут быть буквами, цифрами и знаками `-, _`.

Хост принимает WASM-файлы до 2 МиБ. Повторный импорт с тем же ID отклоняется, поэтому старый плагин удалите перед установкой новой версии.

## Метаданные

Макрос `plugin_metadata!` записывает секцию `aps.meta` с парами `ключ\0значение\0` в UTF-8.

```rust
use aps_sdk::plugin_metadata;

plugin_metadata! {
    id: "weather",
    name: "Weather",
    description: "Показывает погоду в чатах",
    author: "@yourUsername",
    version: "1.0.0",
    icon: "exteraPlugins/1",
    app_version: ">=12.5.1",
    sdk_version: ">=1.0",
    requirements: "requests>=2.32",
    requires: "helper_plugin",
    category: "tools",
}
```

| Поле | По умолчанию | Значение |
| --- | --- | --- |
| `id` | имя файла | Идентификатор; должен совпадать с `<ID>.apl` |
| `name` | ID | Отображаемое имя |
| `description` | пусто | Описание в Markdown |
| `author` | пусто | Автор |
| `version` | `1.0.0` | Версия плагина |
| `icon` | пусто | Иконка в формате `StickerPackShortName/index` |
| `app_version` | пусто | Версия exteraGram, например `>=12.5.1` |
| `sdk_version` | пусто | Версия SDK, например `>=1.0` |
| `requirements` | пусто | Пакеты через запятую; сохраняются, не устанавливаются |
| `requires` | пусто | Плагины через запятую; сохраняются, не проверяются |
| `category` | пусто | До трёх категорий; поле можно повторять |

Категории: `appearance`, `chats`, `media`, `privacy`, `tools`, `integrations`, `fun`, `libraries`.

Секция необязательна. Без неё плагин работает, а отображаемое имя совпадает с ID. Если секция есть, `name` обязателен, `id` должен совпадать с именем файла, а размер секции не может превышать 64 КБ.

`requirements` и `requires` APS сохраняет для интерфейса и будущих версий: пакеты не устанавливаются, зависимости не проверяются.

## Хуки

`BasePlugin` объявляет статические методы. Методы реализуются для пустой структуры, а `export_plugin!` генерирует ABI-экспорты. Все методы имеют реализации по умолчанию, поэтому `impl BasePlugin for MyPlugin {}` компилируется.

| Метод | Когда вызывается | Возврат |
| --- | --- | --- |
| `on_plugin_load() -> i32` | При включении плагина или старте приложения | `0`; другое значение не даёт плагину загрузиться |
| `on_plugin_unload() -> i32` | При выключении, удалении SDK и завершении хоста | Игнорируется |
| `on_app_event(AppEvent) -> i32` | При событии приложения | Игнорируется |
| `on_send_message(account) -> HookResult` | Перед отправкой сообщения | `pass()` или `cancel()` |

`on_plugin_load` вызывается один раз после проверки `aps_abi_version`. Если метод вернул не `0`, упал с trap или модуль не экспортирует обязательную функцию, хост не добавляет плагин в активные.

`on_plugin_unload` для остановленного плагина повторно не вызывается.

Событие `AppEvent::Unknown` хост не отправляет. Trap в одном плагине не мешает остальным получить событие.

| Вариант | ABI-код | Python-аналог |
| --- | ---: | --- |
| `AppEvent::Start` | 0 | `AppEvent.START` |
| `AppEvent::Stop` | 1 | `AppEvent.STOP` |
| `AppEvent::Pause` | 2 | `AppEvent.PAUSE` |
| `AppEvent::Resume` | 3 | `AppEvent.RESUME` |
| `AppEvent::Unknown` | 4 | Неизвестное событие |

`account` в `on_send_message` задаёт индекс аккаунта Telegram, который инициировал отправку. Он не всегда совпадает с аккаунтом, открытым на экране.

| Метод | ABI | Результат |
| --- | ---: | --- |
| `HookResult::pass()` | 0 | Отправить сообщение |
| `HookResult::cancel()` | 1 | Отменить отправку |
| `HookResult::new(strategy)` | — | Задать стратегию явно |

ABI 1 поддерживает только `HookStrategy::Default` и `HookStrategy::Cancel`. Стратегии `MODIFY` и `MODIFY_FINAL` из Python недоступны: хост не передаёт сообщение, поэтому изменить текст, параметры или получателей плагин не может.

Если хук вернул значение вне `0` и `1`, хост выдаёт `Unknown result from the APS hook`, оставшиеся плагины не вызываются, отправка не отменяется. Trap даёт такой же результат.

## Мост SDK

`export_plugin!` экспортирует `aps_bridge_version` со значением `1`. Хост проверяет его, если символ есть, и подключает импорты модуля `aps`. Старые плагины без bridge загружаются как раньше.

```rust
use aps_sdk::client::{get_selected_account, AccountClient};
use aps_sdk::logger::Logger;
use aps_sdk::{settings, ui};

Logger::info("plugin started");

let mut buf = [0u8; 64];
let value = settings::get_or("api_key", "", &mut buf);
settings::set("api_key", "new value");

let client = AccountClient::new(account); // account from the hook
client.send_text(123456789, "Hello");
client.send_request("TL_account_updateStatus", r#"{"offline":true}"#);
let selected = get_selected_account(); // explicit UI-account opt-in

ui::post(on_ui_ready, 0);
ui::show_info("Done");
```

| Модуль | Назначение |
| --- | --- |
| `logger::Logger` | `debug`, `info`, `warn`, `error`; тег `plugin.<id>` |
| `settings` | `get`, `get_or`, `set`, `get_bool`, `set_bool`; значения строки |
| `client::AccountClient` | `send_text`, `send_request`; аккаунт обязателен |
| `client::get_selected_account` | явный выбор аккаунта из UI |
| `ui` | `post(fn, delay_ms)`, `show_info`, `show_error`, `show_success` |

Настройки хранятся с префиксом `aps.<id>.`, чтобы плагины не пересекались. `settings::get` читает в буфер вызывающего: сначала узнаётся размер, затем данные. Лог и UI уходят в `android_utils`, сообщения — в `client_utils`. Ответ `send_request` пока не возвращается в плагин; ошибка пишется в лог. Короткое имя `TL_...` раскрывается в `org.telegram.tgnet.TLRPC$TL_...`, полное имя Java-класса тоже принимается. JSON задаёт только плоские поля.

## Экспорты ABI 1

`export_plugin!(MyPlugin)` создаёт следующие экспорты:

| Символ | Сигнатура | Обязателен | Значение |
| --- | --- | ---: | --- |
| `aps_abi_version` | `() -> i32` | Да | Всегда `1` |
| `aps_bridge_version` | `() -> i32` | Нет | `1` при сборке с мостом |
| `aps_run_task` | `(i32) -> ()` | Нет | Выполняет задачу `ui::post` |
| `aps_on_load` | `() -> i32` | Да | `0` — успех |
| `aps_on_unload` | `() -> i32` | Да | Возврат игнорируется |
| `aps_on_app_event` | `(i32) -> i32` | Нет | Возврат игнорируется |
| `aps_on_send_message` | `(i32) -> i32` | Да | `0` — пропустить, `1` — отменить |

`aps_on_app_event` появился в SDK `0.3.0`. Старые модули без него загружаются, но события не получают.

Хост создаёт экземпляр с импортами `aps` (см. «Мост SDK»). WASI, `std`, файловая система, сеть, время, случайные числа и Java/Android API напрямую недоступны; собирайте с `#![no_std]` и `panic = "abort"`.

Экспорт `memory` использует компилятор. Хост читает и пишет память только для строк моста: лог, настройки, текст сообщений и JSON запроса.

### Перенос с Python `BasePlugin`

| Python | Rust |
| --- | --- |
| `on_plugin_load`, `on_plugin_unload`, `on_app_event` | Одноимённые методы `BasePlugin` |
| `on_send_message_hook(account, params)` | `on_send_message(account)` без `params` |
| `HookStrategy.MODIFY`, `MODIFY_FINAL` | Только `pass()` и `cancel()` |
| `create_settings`, `add_menu_item` | Не перенесены |
| `get_setting`, `set_setting` | `settings::get`, `settings::get_or`, `settings::set` |
| `self.logger` | `logger::Logger` |
| `client_utils.send_text` | `AccountClient::send_text` |
| `send_request` | `AccountClient::send_request` с JSON полей |
| `run_on_ui_thread`, `BulletinHelper` | `ui::post`, `ui::show_*` |
| `add_hook`, `pre_request_hook`, `post_request_hook`, `on_update_hook` | Не перенесены |
| Java-объекты, `dynamic_proxy`, class proxy | Недоступны |

## Ограничения

- Нет лимитов времени выполнения и памяти. Бесконечный цикл или утечка памяти могут зависнуть или завершить клиент.
- Плагин видит только свой WASM-модуль и память. Java-объекты, reflection и `dynamic_proxy` через мост пока не передаются.
- `send_request` не возвращает ответ в плагин; ошибки только логируются. Вложенные TL-объекты в JSON не собираются.
- `ui::post` принимает `fn()` без захвата; задачи с замыканиями появятся вместе с аллокатором.
- Нет подписи или закреплённого хеша SDK. Установщик доверяет ветке `main` репозитория `skytr1x/APS-SDK`.
- Хост написан на Python, лежит в архиве SDK и исполняется в клиенте с правами плагина. Доверие к ветке `main` означает доверие к исполняемому коду, а не только к исходникам.
- Устанавливайте и включайте только доверенные плагины.

## Ошибки

| Сообщение | Причина | Что делать |
| --- | --- | --- |
| `The SDK runtime failed to load` | Пакет хоста не импортировался: повреждён файл или несовместимая версия Python | Переустановите SDK |
| `Plugin failed to start` | `on_plugin_load` вернул не `0`, сработал trap или нет обязательного экспорта | Проверьте `on_plugin_load` и список экспортов |
| `Unsupported ABI version` | `aps_abi_version` или `aps_bridge_version` не совпал с хостом | Пересоберите плагин с SDK `1.0` |
| `Unsupported ABI version` при импорте `aps.*` | Плагин собран с мостом, а хост старый | Обновите SDK |
| `File name must be ID.apl...` | Неверное расширение или ID | Переименуйте файл по правилам выше |
| `Invalid plugin metadata` | Секция `aps.meta` повреждена: неверная длина, кодировка или структура | Пересоберите плагин |
| `Metadata ID does not match the file name` | Поле `id` не совпадает с именем файла | Укажите имя файла без расширения или уберите `id` |
| `Metadata must contain a name` | В секции метаданных нет поля `name` | Добавьте `name` |
| `Plugin metadata is too large` | Секция `aps.meta` больше 64 КБ | Сократите описание и лишние поля |
| `Unknown result from the APS hook` | `on_send_message` вернул не `0` и не `1` | Возвращайте `HookResult::pass()` или `HookResult::cancel()` |
| `The plugin failed to start` после обновления Rust | Компилятор добавил WASM-инструкции, которые не понимает pywasm | Соберите с `RUSTFLAGS` из быстрого старта или обновите движок |

## Интеграция хоста

`host/aps_host/` содержит Python-пакет, который Elyx импортирует после установки SDK. Манифест `aps-sdk.json` объявляет `"host": 1`; SDK без этого поля плагин считает устаревшим.

`Host(home, get_setting, set_setting, logger=None, loader=None)` хранит файлы в `<home>/plugins`, а флаги включения хранятся в настройках `aps_enabled_<ID>`. Хост импортируется целиком и выгружается при удалении или обновлении SDK, поэтому внутри пакета используются только относительные импорты.

Основные модули: `host.py` (жизненный цикл и флаги), `runtime.py` (вызовы WASM и проверка bridge), `bridge.py` (импорты `aps.*` и связь с Python SDK), `metadata.py`, `store.py`, `engine.py` (обёртка pywasm), `events.py`, `errors.py`. `engine.check_engine(directory)` проверяет, что pywasm запускает пробный модуль. `HostError.key` хранит ключ локализации, APS превращает его в текст ошибки.
