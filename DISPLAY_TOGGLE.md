# KDE Plasma Display Toggle Setup

Переключение встроенного экрана (eDP-1) через кнопку 4 на MiniKB.

## Установка

### 1. Загрузить маппинг на клавиатуру

```bash
ch57x-keyboard-tool upload mapping-media.yaml
```

Кнопка 4 теперь отправляет **Ctrl+Alt+D**.

### 2. Настроить глобальный shortcut в KDE

**System Settings → Shortcuts → Custom Shortcuts:**

1. Нажать **Edit → New → Global Shortcut → Command/URL**
2. Trigger tab:
   - Нажать кнопку для Shortcut
   - Нажать `Ctrl+Alt+D`
3. Action tab:
   - Command/URL: `/home/hive/Projects/minikb-gui/toggle-display.sh`

Готово! Теперь кнопка 4 переключает встроенный экран.

## Как работает

- **eDP-1** (встроенный экран) - включается/выключается
- **HDMI-A-1** (внешний монитор) - всегда включен
- Показывает уведомление при переключении

## Тестирование

```bash
# Проверить текущее состояние
kscreen-doctor -o

# Запустить скрипт вручную
./toggle-display.sh
```

## Настройка скрипта

Файл `toggle-display.sh`:
- Автоматически находит eDP-1 / LVDS-1
- Переключает состояние (enabled/disabled)
- Показывает notification
