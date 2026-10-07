# Архитектура и протокол

GNSS → MCU nRF52840 → LTE-модем BG95 → HTTPS сервер.
Резерв: MCU → BLE GATT → приложение телефона → HTTPS сервер.
Нет сети: локальный журнал; после восстановления — отправка очереди с подтверждением каждой точки.

Концептуальные модули: nRF52840, BG95 с GNSS (вариант уточнить), eUICC MFF2 с доступным профилем оператора, LTE/GNSS/BLE антенны, LiPo, зарядное устройство с power-path и защитой, отдельное питание модема и MCU, преобразователь уровней UART по спецификации выбранного модуля. eUICC подключается к SIM интерфейсу модема; SIM clock/reset/data не являются UART.
Питание, пиковые токи, развязку и RF-геометрию проектировать по hardware design конкретного варианта. Напрямую соединять произвольные GPIO модема и MCU нельзя без проверки уровней.

Пакет: {"device_id":"tracker-001","session_id":"boot-uuid","id":42,"timestamp":"2026-10-07T10:00:00Z","lat":43.238,"lon":76.945,"accuracy_m":8,"battery_mv":3900}.
ACK: {"device_id":"tracker-001","session_id":"boot-uuid","id":42,"stored":true}.
Сервер ACK только после durable commit; UNIQUE(device_id,session_id,id), повтор возвращает тот же ACK. TLS проверяет CA и имя сервера; индивидуальные ключи устройства, BLE bonding и авторизация телефона. Геолокация хранится с разграничением доступа и сроком удаления.

Демонстрация упрощает протокол до булевого ACK; по настоящей сети этот пакет не отправляется. Приоритет LTE, затем телефон с интернетом, затем очередь. 256 точек RAM в демонстрации; flash журнал и wear levelling нужны для реального изделия.

Источники:
https://www.quectel.com/product/lpwa-bg95-cat-m1-cat-nb2-egprs-series/
https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/keyfeatures_html5.html
https://nrfconnectdocs.nordicsemi.com/ncs/latest/nrf/libraries/bluetooth/services/nus.html
