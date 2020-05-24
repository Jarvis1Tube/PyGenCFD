## About (О чем)
Этот проект призван облегчить участь Fortran программистов, занимающихся вычислительной гидродинамикой (*CFD*).

Идея в том, чтобы вводить условия задачи аналитически через графический интерфейс (*GUI*), а на выходе уже получать высокопроизводительный код на Fortran, который можно будет запустить как локально, так и на большом кластере.

## Installation (Установка)
Прежде всего нужен установленный [Python3.7+](https://www.python.org/)  
Для Windows можно просто скачать архив с исходниками и распаковать его.  
В этом случае *git clone* вам не нужен.

```bash
git clone https://github.com/Jarvis1Tube/PyGenCFD
cd PyGenCFD
pip3 install -r requirements.txt

make
```

<details>
    <summary>Вариант с виртуальным пространством (*virtualenv*)</summary>

```
git clone https://github.com/Jarvis1Tube/PyGenCFD
cd PyGenCFD

pip3 install virtualenv
virtualenv ./env -p 3.7
pip3 install -r requirements.txt

make
```
</details>

## Running (Запуск)
```
python3 ./src/start_ui.py
```