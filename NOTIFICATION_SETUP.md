# KDE Plasma Notification LED Setup

Автоматическое мигание RGB подсветки MiniKB при уведомлениях KDE Plasma 6.

## Быстрый старт

### Вариант 1: Ручной запуск (для тестирования)

```bash
./notification-blink.sh
```

Скрипт будет мониторить уведомления. Протестируйте отправив уведомление:
```bash
notify-send "Test" "Notification test"
```

RGB должна мигнуть (режим 2 → режим 0).

### Вариант 2: Автозапуск через systemd

**Установка:**
```bash
# Скопировать service файл
mkdir -p ~/.config/systemd/user
cp minikb-notify.service ~/.config/systemd/user/

# Включить и запустить
systemctl --user enable minikb-notify.service
systemctl --user start minikb-notify.service

# Проверить статус
systemctl --user status minikb-notify.service
```

**Остановить:**
```bash
systemctl --user stop minikb-notify.service
systemctl --user disable minikb-notify.service
```

**Логи:**
```bash
journalctl --user -u minikb-notify.service -f
```

## Настройка

### Изменить LED режимы

Отредактируйте `notification-blink.sh`:
```bash
ch57x-keyboard-tool led 2  # Режим 2 (rainbow)
sleep 1                     # Длительность
ch57x-keyboard-tool led 0  # Режим 0 (off)
```

**Доступные режимы:**
- `0` - выключен
- `1` - cyan/steady
- `2` - rainbow
- `3` - freeze

### Изменить длительность

Измените `sleep 1` на нужное значение (в секундах).

## Требования

- KDE Plasma 6
- `ch57x-keyboard-tool` в PATH
- `dbus-monitor` (обычно уже установлен)

## Устранение проблем

**LED не мигает:**
1. Проверьте что `ch57x-keyboard-tool` работает:
   ```bash
   ch57x-keyboard-tool led 2
   ```

2. Проверьте что уведомления работают:
   ```bash
   notify-send "Test" "Message"
   ```

3. Проверьте логи systemd:
   ```bash
   journalctl --user -u minikb-notify.service -f
   ```

**Скрипт не запускается:**
- Убедитесь что `notification-blink.sh` исполняемый:
  ```bash
  chmod +x notification-blink.sh
  ```

- Проверьте путь в `minikb-notify.service` (строка `ExecStart`)

## Альтернатива: KDE Event Actions

Можно настроить через KDE System Settings:
1. Settings → Notifications
2. Configure Events → выбрать приложение
3. Event Actions → добавить команду:
   ```bash
   /path/to/notification-blink.sh &
   ```

Но systemd вариант надежнее!
