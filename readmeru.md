# NSFW Content Filter

Скрипт для автоматического скрытия обнаруженых объектов на экране пользователя.

## Установка

1. **Установите Python**
   - Скачайте и установите [Python](https://www.python.org/downloads/).
2. **Клонируйте или скачайте репозиторий**:
   - ```git clone https://github.com/Serfetto/NsfwPlugin```
3. **Создайте и активируйте виртуальное окружение**(Можете пропустить этот пункт):
   1) ```cd NsfwPlugin```
   2) ```python -m venv .venv```
   3) ```.venv\Scripts\activate```
3. **Установите зависимости**
   - Скачайте [модель](https://drive.google.com/file/d/1Ne74BR39pZfNcK_60Iljd9h5bT5j-YcQ)
   - На процессоре (CPU):
      ```pip install dxcam screeninfo pyqt5 ultralytics```
   - На видеокарте (GPU):
      1. ```pip install dxcam screeninfo pyqt5 ultralytics```
      2. Убедитесь, что у вас установлены [CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit), [cuDNN](https://developer.nvidia.com/cudnn), [Visual Studio](https://visualstudio.microsoft.com), [PyTorch](https://pytorch.org/get-started/locally/).
## Запуск
   - ```python NsfwBlur.py```

Upd: Этот скрипт не работает в операционной системе Linux


   
