#!/bin/bash
# Автоматический тест HyperHDR toggle

echo "=== Тест HyperHDR Toggle ==="
echo

# Начальная очистка
echo "1. Останавливаем все процессы hyperhdr..."
pkill -9 hyperhdr 2>/dev/null
rm -f /tmp/hyperhdr-domain 2>/dev/null
sleep 1

# Проверка начального состояния
if pgrep hyperhdr > /dev/null 2>&1; then
    STATUS="running"
else
    STATUS="stopped"
fi
echo "Начальное состояние: $STATUS"
echo

# Тест 1: Запуск
echo "2. Эмуляция нажатия кнопки (должен запустить)..."
./hyperhdr-toggle.sh
sleep 1
if pgrep hyperhdr > /dev/null 2>&1; then
    echo "Состояние после 1 нажатия: running"
    echo "✓ OK: Запустился"
else
    echo "Состояние после 1 нажатия: stopped"
    echo "✗ FAIL: Не запустился"
fi
echo

# Тест 2: Остановка
echo "3. Эмуляция нажатия кнопки (должен остановить)..."
./hyperhdr-toggle.sh
sleep 1
if pgrep hyperhdr > /dev/null 2>&1; then
    echo "Состояние после 2 нажатия: running"
    echo "✗ FAIL: Не остановился"
else
    echo "Состояние после 2 нажатия: stopped"
    echo "✓ OK: Остановился"
fi
echo

# Тест 3: Повторный запуск
echo "4. Эмуляция нажатия кнопки (должен запустить снова)..."
./hyperhdr-toggle.sh
sleep 1
if pgrep hyperhdr > /dev/null 2>&1; then
    echo "Состояние после 3 нажатия: running"
    echo "✓ OK: Запустился снова"
else
    echo "Состояние после 3 нажатия: stopped"
    echo "✗ FAIL: Не запустился"
fi
echo

# Тест 4: Повторная остановка
echo "5. Эмуляция нажатия кнопки (должен остановить снова)..."
./hyperhdr-toggle.sh
sleep 1
if pgrep hyperhdr > /dev/null 2>&1; then
    echo "Состояние после 4 нажатия: running"
    echo "✗ FAIL: Не остановился"
else
    echo "Состояние после 4 нажатия: stopped"
    echo "✓ OK: Остановился снова"
fi
echo

echo "=== Тест завершён ==="
