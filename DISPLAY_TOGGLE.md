# MiniKB Toggle Scripts Setup

Переключение встроенного экрана и HyperHDR через кнопки на MiniKB.

## Кнопки

- **Кнопка 4**: Display toggle (Ctrl+Alt+D) - переключение eDP-1
- **Кнопка 6**: HyperHDR toggle (Super+H) - запуск/остановка HyperHDR

## Установка

### 1. Загрузить маппинг на клавиатуру

```bash
ch57x-keyboard-tool upload mapping-media.yaml
```

Кнопка 4 теперь отправляет **Ctrl+Alt+D**.

### 2. Настроить глобальные shortcuts в KDE

**System Settings → Shortcuts → Custom Shortcuts:**

#### Кнопка 4 - Display Toggle

1. **Edit → New → Global Shortcut → Command/URL**
2. Trigger tab: `Ctrl+Alt+D`
3. Action tab: `/home/hive/Projects/minikb-gui/toggle-display.sh`

#### Кнопка 6 - HyperHDR Toggle

1. **Edit → New → Global Shortcut → Command/URL**
2. Trigger tab: `Meta+H` (Super+H)
3. Action tab: `/home/hive/Projects/minikb-gui/hyperhdr-toggle.sh`

Готово!

## Как работает

### Display Toggle (кнопка 4)
- **eDP-1** (встроенный экран) - включается слева, выключается
- **HDMI-A-1** (внешний монитор) - всегда включен, справа от eDP-1
- Показывает уведомление при переключении

### HyperHDR Toggle (кнопка 6)
- Проверяет процесс `hyperhdr`
- Если запущен → убивает процесс
- Если не запущен → запускает процесс
- Показывает уведомление при переключении

## Тестирование

### Display Toggle
```bash
# Проверить текущее состояние
kscreen-doctor -o

# Запустить скрипт вручную
./toggle-display.sh
```

### HyperHDR Toggle
```bash
# Проверить запущен ли HyperHDR
pgrep hyperhdr

# Запустить toggler вручную
./hyperhdr-toggle.sh
```

## Настройка скрипта

Файл `toggle-display.sh`:
- Автоматически находит eDP-1 / LVDS-1
- Переключает состояние (enabled/disabled)
- Показывает notification
