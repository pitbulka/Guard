@echo off
chcp 65001
title Голосовой помощник

rem Переходим в папку проекта
cd /d "C:\Users\SystemX\PycharmProjects\PythonProject4"

rem Показываем что есть в папке
echo Содержимое папки:
dir *.py

rem Запускаем программу
echo.
echo Запуск голосового помощника...
python job.py

rem Пауза в конце
echo.
echo Программа завершена. Нажмите любую клавишу...
pause >nul