# NSFW Content Filter

A script for automatically hiding detected objects on the user's screen.

## Installation

1. **Install Python**
    - Download and install [Python](https://www.python.org/downloads/).
2. **Clone or download the repository**:
    - ``git clone https://github.com/Serfetto/NSFW-Classification ``
3. **Create and activate a virtual environment**(You can skip this point):
    1. ```cd NsfwPlugin```
    2. ```python -m venv.venv```
    3. ```.venv\Scripts\activate```
4. **Install dependencies**
    - On the processor (CPU): ```pip install dxcam screeninfo pyqt5 ultralytics```
    - On the graphics card (GPU):
      1. ```pip install dxcam screeninfo pyqt5 ultralytics```
      2. Make sure that you have the [CUDA Toolkit] installed](https://developer.nvidia.com/cuda-toolkit), [cuDNN](https://developer.nvidia.com/cudnn), [Visual Studio](https://visualstudio.microsoft.com), [PyTorch](https://pytorch.org/get-started/locally/).
## Launch
- ```python NsfwBlur.py```

Upd: This script does not work on the Linux operating system


