# APS SDK

APS SDK являеться рантаймом для Rust плагинов для APS (Another Plugin System) - плагин для exteraGram. Он повторяет и добавляет поддержку синтаксиса оригинального `base_plugin` API из [Python SDK](https://plugins.exteragram.app/docs) для Rust.

Метаданные плагина задаются макросом `plugin_metadata!` и хранятся в секции `aps.meta` внутри `.apl`. Поля и правила описаны в [`docs.md`](docs.md).

Слои SDK и граница с Python/Android описаны в [`docs/architecture.md`](docs/architecture.md).

Подробнее узнать о плагине можно уже в репозитории [плагина](https://github.com/skytr1x/APS).
