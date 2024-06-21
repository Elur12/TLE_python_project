## Содержание:
1. [Требования к среде](#reqirements)
2. [Архитектура программного обеспечения](#architecture)
3. [Структура каталогов](#structure)
4. [Внешние источники данных](#sources)
5. [Описание классов и методов](#documentation)

<h3 id="requirements">Требования к системе</h3>

1. Операционная система: Windows 10 и позднее / MacOS X BigSure и позднее
2. Наличие интернет-подключения
2. Наличие установленного Python 3.12
3. Наличие установленных библиотек

<h3 id="architecture">Архитектура программного обеспечения</h3>

<h3 id="structure">Структура каталогов</h3>

* /data
  * data.pk
  * data.csv
* /documentation
  * Developer guide.md
  * User guide.md
* /interface
  * window.py
    * class `MainWindow`
    * class `TabTracking`
    * class `TabWorldMap`
    * class `TabSchedule`
* /tle
* README.md
* requirements.txt
* satelite.py
  * class `place`
  * class `Satelite`

<h3 id="sources">Внешние источники данных</h3>

Программа получает TLE-данные по заданным в настройках (вкладка `Settings`) ссылкам.
По умолчанию набор ссылок выглядит следующим образом:
```
http://www.celestrak.com/NORAD/elements/active.txt
http://celestrak.com/NORAD/elements/weather.txt
http://celestrak.com/NORAD/elements/resource.txt
https://www.celestrak.com/NORAD/elements/cubesat.txt
http://celestrak.com/NORAD/elements/stations.txt
https://www.celestrak.com/NORAD/elements/sarsat.txt
https://www.celestrak.com/NORAD/elements/noaa.txt
https://www.celestrak.com/NORAD/elements/amateur.txt
https://www.celestrak.com/NORAD/elements/engineering.txt
```

<h2 id="documentation">Описание классов и методов</h3>

### Содержание:
1. [Функции](#functions)
   1. [Функции файла `satelites.py`](#functions_satelites)
   2. [Функции файла `window.py`](#functions_window)
2. [Класс `place`](#class_place)
2. [Класс `Satelite`](#class_satelite)
3. [Методы класса `Satelite`](#methods_satelite)
4. [Классы интерфейса](#class_satelite)

<h3 id="functions">Функции</h3>

<h4 id="functions_satelites">Функции файла `satelites.py`</h3>

`timenow(start_time, use_speed) -> datetime` возвращает время в программе,
учитывая скорость течения времени в программе.

```
Параметры:
– start_time: datetime
  Значение по умолчанию: datetime.datetime.now(UTC)
– use_speed: bool
  Значение по умолчанию: False
```

---

`save_to_json(**kwargs)` сохраняет кэш `**kwargs` в файл по заданным параметрам.

---

`load_from_json(*args) -> ` возвращает сохраненный кэш из файла.

---

Декоратор `TLE(func)` при вызове функций, связанных с TLE-данными,
проверяет актуальность данных и обновляет их.

---
Декоратор `csv_info(func)` при вызове функций, связанных с SHEET - обновляет файл data.csv согласно новым данным

---

`update_tle(urls, all_update) -> datetime` обновляет TLE данные, загружая по ссылкам,
и возвращает время обновления `update`.

```
Параметры:
– urls: str
– all_update: bool
  Значение по умолчанию: False
```

---

`create_folder(workspace, folder)` создает технические папки
для работы программы и выводит результат выполнения.

```
Параметры:
– workspace: str
– folder: str
```

---

`update_settings()` обновляет настройки в приложении, загружая их из `data.json`.

---

<h4 id="functions_window">Функции файла `window.py`</h3>

`draw_map(m, scale)` рисует линии широт и медиан на карте.

```
Параметры:
– m: Basemap()
– scale: float
  Значение по умолчанию: 0.2
```

---

`rasdel(l) -> []` считает, когда график подходит к концу траектории и делит общий график на два графика: левый и правый.

```
Параметры:
– l: int
```

---

`rainbow(iter, speed, brightness, unbrightness) -> float` подбирает новый цвет для визуализации траектории спутника.

```
Параметры:
– iter: насколько далеко от радуги ушли
– speed: длина радуги
– brightness: максимальное значение у цвета радуги
– unbrightness: когда iter > speed, делает цвет более пастельным
```

---

`window(sattelite, timenow, load_from_json, save_to_json, place, selected_items, color, color_iter)` открывает окно с программой.

```
Параметры:
– sattelite: [Satelite()]
– timenow: timenow()
– load_from_json: load_from_json()
– save_to_json: save_to_json()
– place: place()
– selected_items: {str} – выбранные спутники
– color: dict(название_спутника: цвет)
– color_iter: int – количество занятых цветов
```

---

<h3 id="class_place">Класс `place`</h3>

Хранит в себе координаты наблюдателя.

```
Значения по умолчанию:
– lon: float = 0
– lat: float = 0
– alt: float = 0
```

---

<h3 id="class_satelite">Класс `Satelite`</h3>

```
Инициализируется параметрами:
– name: str
– place: place()
```

---

<h3 id="methods_satelite">Методы класса `Satelite`</h3>

`Satelite.get_location() -> tuple[None, None, float]` возвращает координаты спутника.

---

`Satelite.get_while_loc(deltaseconds) -> list[list | list[None]]` возвращает массив широт для matplotlib.

```
Параметры:
– deltaseconds: float
  Значение по умолчанию: 10
```

---

`Satelite.get_orbit_number() -> int` возвращает номер орбиты спутника.

---

`Satelite.get_observer(time) -> tuple[float, None]` возвращает координаты в небесной сфере относительно точки наблюдателя.

```
Параметры:
– time: datetime
  Значение по умолчанию: timenow(use_speed=True)
```

---

`Satelite.get_next_observers(horizon, max_angle, delta_seconds) -> list[list | datetime]` возвращает список координат
в угловой форме для отображение в TabTracking.

```
Параметры:
– horizon: float
  Значение по умолчанию: 0
– max_angle: float
  Значение по умолчанию: 60
– delta_seconds: float
  Значение по умолчанию: 0.5
```

---

`Satelite.get_next_passes(horizon, max_angle) -> list` возвращает
рассчитанные проходы на следующие часы для заданного времени начала и данного наблюдателя.

```
Параметры:
– horizon: float
  Значение по умолчанию: 0
– max_angle: float
  Значение по умолчанию: 30
```

---

`Satelite.get_positions() -> tuple[ndarray, ndarray]` возвращает декартово положение и скорость со спутника.

---

`Satelite.update_place(my_place)` обновляет позицию наблюдателя.

```
Параметры:
– my_place: place()
```

---

`Satelite.update()` обновляет [Satelite()] в соответствии с новыми данными из внешнего сервера.

---

<h3 id="class_satelite">Классы интерфейса</h3>

#### Класс `MainWindow`

Наследует класс `PyQt5.QtWidgets.QDialog` определяет главное
окно программы, содержащее в себе вкладки.

```
Инициализируется значениями:
– sattelites: [Satelite()]
– timenow: timenow()
– save_to_json: save_to_json()
– place: place()
– selected_items:  {str} – выбранные спутники
– color
– color_iter
– load_from_json: load_from_json()
```

##### Методы

`MainWindow.message(item: PyQt5.QWidgets.QTableWidgetItem)` сохраняет выбранные спутники в `data.json`.

`MainWindow.search(s: str)` выполняет поиск в таблице спутников по запросу `s`.

`MainWindow.update_time(label_time: QLabel, timenow: timenow())` устанавливает время
у текстового блока в нормализированном формате.

`MainWindow.update_place(value: float, i: int)` сохраняет координаты наблюдателя в кэш.

---

#### Класс `TabTracking`

Наследует класс `PyQt5.QtWidgets.QWidget` и хранит вкладку Tracking.

```
Инициализируется значениями:
– sattelites: [Satelite()]
– timenow: timenow()
– place: place()
– selected_items: {str} – выбранные спутники
– color
```

##### Методы

`TabTracking.update_plot()` обновляет картинку карту.

`TabTracking.clear_all()` стирает картинку карту.

---

#### Класс `TabWorldMap`

Наследует класс `PyQt5.QtWidgets.QWidget` и хранит вкладку World map.

```
Инициализируется значениями:
– sattelites: [Satelite()]
– place: place()
– selected_items: {str} – выбранные спутники
– color
– save_to_json: save_to_json()
– color_iter
```

##### Методы

`TabWorldMap.update_plot()` обновляет картинку карты.

`TabWorldMap.clear_all()` стирает картинку карты.

`TabWorldMap.update_color()` обновляет цвета траекторий движения спутников.

---

#### Класс `TabSchedule`

Наследует класс `PyQt5.QtWidgets.QWidget` и хранит вкладку Schedule.

```
Инициализируется значениями:
– sattelites: [Satelite()]
– selected_items: {str} – выбранные спутники
```

##### Методы

`TabSchedule.update_plot()` обновляет данные в таблице.

---

#### Класс `TabSettings`

Наследует класс `PyQt5.QtWidgets.QWidget` и хранит вкладку Settings.

```
Инициализируется значениями:
– load_from_json: load_from_json()
– save_to_json: save_to_json()
– worldmap: TabWorldMap()
– tracking: TabTracking()
```

##### Методы

`TabSettings.save_settings()` обновляет программу исходя из настроек.

`TabSettings.update_settings()` загружает настройки из `data.json`.