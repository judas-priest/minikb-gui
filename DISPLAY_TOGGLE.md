# MiniKB Toggle Scripts Setup

Переключение встроенного экрана и HyperHDR через кнопки на MiniKB.

## Кнопки

- **Кнопка 4**: Display toggle (Ctrl+Alt+D) - переключение eDP-1
- **Кнопка 6**: HyperHDR toggle (Super+H) - запуск/остановка HyperHDR

## Установка

### 0. Установить HyperHDR systemd service (только для кнопки 6)

```bash
# Скопировать service файл
mkdir -p ~/.config/systemd/user
cp hyperhdr.service ~/.config/systemd/user/

# Перезагрузить systemd
systemctl --user daemon-reload
```

**Примечание:** Service НЕ нужно включать (enable)! Кнопка будет запускать/останавливать вручную.

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
- Проверяет статус `hyperhdr.service` через systemd
- Если запущен → останавливает service (`systemctl --user stop`)
- Если не запущен → запускает service (`systemctl --user start`)
- Показывает уведомление при переключении
- Надёжнее чем pkill/pgrep

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
# Проверить статус service
systemctl --user status hyperhdr.service

# Запустить toggler вручную
./hyperhdr-toggle.sh

# Логи (если не работает)
journalctl --user -u hyperhdr.service -f
```

## Настройка скрипта

Файл `toggle-display.sh`:
- Автоматически находит eDP-1 / LVDS-1
- Переключает состояние (enabled/disabled)
- Показывает notification
