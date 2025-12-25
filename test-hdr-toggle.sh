#!/bin/bash
# Автоматический тест HyperHDR toggle

echo "=== Тест HyperHDR Toggle ==="
echo

# Начальная очистка
echo "1. Останавливаем все процессы hyperhdr..."
systemctl --user stop hyperhdr.service 2>/dev/null
pkill -9 hyperhdr 2>/dev/null
sleep 1

# Проверка начального состояния
STATUS=$(systemctl --user is-active hyperhdr.service 2>/dev/null)
echo "Начальное состояние: $STATUS"
echo

# Тест 1: Запуск
echo "2. Эмуляция нажатия кнопки (должен запустить)..."
./hyperhdr-toggle.sh
sleep 1
STATUS=$(systemctl --user is-active hyperhdr.service 2>/dev/null)
echo "Состояние после 1 нажатия: $STATUS"
if [ "$STATUS" = "active" ]; then
    echo "✓ OK: Запустился"
else
    echo "✗ FAIL: Не запустился (ожидалось active, получено $STATUS)"
fi
echo

# Тест 2: Остановка
echo "3. Эмуляция нажатия кнопки (должен остановить)..."
./hyperhdr-toggle.sh
sleep 1
STATUS=$(systemctl --user is-active hyperhdr.service 2>/dev/null)
echo "Состояние после 2 нажатия: $STATUS"
if [ "$STATUS" = "inactive" ] || [ "$STATUS" = "failed" ]; then
    echo "✓ OK: Остановился"
else
    echo "✗ FAIL: Не остановился (ожидалось inactive, получено $STATUS)"
fi
echo

# Тест 3: Повторный запуск
echo "4. Эмуляция нажатия кнопки (должен запустить снова)..."
./hyperhdr-toggle.sh
sleep 1
STATUS=$(systemctl --user is-active hyperhdr.service 2>/dev/null)
echo "Состояние после 3 нажатия: $STATUS"
if [ "$STATUS" = "active" ]; then
    echo "✓ OK: Запустился снова"
else
    echo "✗ FAIL: Не запустился (ожидалось active, получено $STATUS)"
fi
echo

# Тест 4: Повторная остановка
echo "5. Эмуляция нажатия кнопки (должен остановить снова)..."
./hyperhdr-toggle.sh
sleep 1
STATUS=$(systemctl --user is-active hyperhdr.service 2>/dev/null)
echo "Состояние после 4 нажатия: $STATUS"
if [ "$STATUS" = "inactive" ] || [ "$STATUS" = "failed" ]; then
    echo "✓ OK: Остановился снова"
else
    echo "✗ FAIL: Не остановился (ожидалось inactive, получено $STATUS)"
fi
echo

echo "=== Тест завершён ==="
