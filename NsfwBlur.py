import sys
import screeninfo
import dxcam
import cv2
import torch
from pathlib import Path
from ultralytics import YOLO
from PyQt5.QtCore import QThread, pyqtSignal, QSettings
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (QApplication, QLabel, QMainWindow, QVBoxLayout,
                             QDialog, QPushButton, QFileDialog, QFormLayout,
                             QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки модели")
        self.setFixedSize(500, 210)
        self.settings = QSettings("MyApp", "ScreenBlur")
        self.model_path = ""
        self.init_ui()
        self.load_last_settings()

    def init_ui(self):
        layout = QVBoxLayout()

        self.model_btn = QPushButton("Выберите модель YOLO (.pt)", self)
        self.model_btn.clicked.connect(self.select_model)

        self.conf_spin = QDoubleSpinBox()
        self.conf_spin.setRange(0.0, 1.0)
        self.conf_spin.setSingleStep(0.1)

        self.blur_size = QSpinBox()
        self.blur_size.setRange(1, 100)
        self.blur_size.setSingleStep(1)

        self.checkboxblur = QCheckBox(text="Размытие")
        self.checkboxblur.clicked.connect(self.on_checkboxblur_toggled)

        self.checkboxrectangles = QCheckBox(text="Прямоугольники")

        self.start_btn = QPushButton("Старт", self)
        self.start_btn.clicked.connect(self.accept)
        self.start_btn.setEnabled(False)

        self.monitors = QComboBox()
        self.generate_monitor()

        self.form_layout = QFormLayout()
        self.form_layout.addRow("Модель YOLO:", self.model_btn)
        self.form_layout.addRow("Монитор:", self.monitors)
        self.form_layout.addRow("Уверенность (conf):", self.conf_spin)
        self.form_layout.addRow("", self.checkboxblur)
        self.form_layout.addRow("Степень размытия\n(проценты):", self.blur_size)
        self.form_layout.addRow("", self.checkboxrectangles)

        layout.addLayout(self.form_layout)
        layout.addWidget(self.start_btn)
        self.setLayout(layout)

        self.on_checkboxblur_toggled(self.checkboxblur.isChecked())

    def generate_monitor(self):
        monitors_iter = screeninfo.get_monitors()
        for monitor in monitors_iter:
            name = monitor.name
            width, height = monitor.width, monitor.height
            is_primary = monitor.is_primary
            self.monitors.addItem(f"{name}, {width}x{height}, главный монитор: {is_primary}")

    def on_checkboxblur_toggled(self, checked):
        self.blur_size.setVisible(checked)
        if hasattr(self, 'form_layout'):
            self.form_layout.labelForField(self.blur_size).setVisible(checked)

    def select_model(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл модели", 
            "",
            "YOLO Models (*.pt)"
        )

        if path:
            self.model_path = path
            self.model_btn.setText(Path(path).name)
            self.start_btn.setEnabled(True)

    def load_last_settings(self):
        self.model_path = self.settings.value("model_path", "")
        if self.model_path and Path(self.model_path).exists():
            self.model_btn.setText(Path(self.model_path).name)
            self.start_btn.setEnabled(True)

        self.conf_spin.setValue(self.settings.value("conf", 0.32, type=float))
        self.blur_size.setValue(self.settings.value("blur_size", 89, type=int))
        self.checkboxblur.setChecked(self.settings.value("checkboxblur", False, type=bool))
        self.checkboxrectangles.setChecked(self.settings.value("checkboxrectangles", False, type=bool))
        index_monitor = self.settings.value("index_monitor", 0, type=int)
        if 0 <= index_monitor < self.monitors.count():
            self.monitors.setCurrentIndex(index_monitor)
        else:
            self.monitors.setCurrentIndex(0)

    def save_settings(self):
        self.settings.setValue("model_path", self.model_path)
        self.settings.setValue("conf", self.conf_spin.value())
        self.settings.setValue("blur_size", self.blur_size.value())
        self.settings.setValue("checkboxblur", self.checkboxblur.isChecked())
        self.settings.setValue("checkboxrectangles", self.checkboxrectangles.isChecked())
        self.settings.setValue("index_monitor", self.monitors.currentIndex())

    def accept(self):
        self.save_settings()
        super().accept()

    def get_settings(self):
        return {
            "model_path": self.model_path,
            "conf": self.conf_spin.value(),
            "blur_size": self.blur_size.value(),
            "checkboxblur": self.checkboxblur.isChecked(),
            "checkboxrectangles": self.checkboxrectangles.isChecked(),
            "index_monitor": self.monitors.currentIndex()
        }

class YOLOThread(QThread):
    frame_processed = pyqtSignal(object)

    def __init__(self, camera, settings):
        super().__init__()
        self.camera = camera
        self.settings = settings
        self.model = YOLO(settings["model_path"])
        self.model.to("cuda" if torch.cuda.is_available() else "cpu")
        self.running = True

    def run(self):
        while self.running:
            frame = self.camera.grab()
            if frame is not None:
                results = self.model.predict(frame, conf=self.settings["conf"], verbose=False)
                frame = self.blur(frame, results)
                self.frame_processed.emit(frame)

                classes = list(map(lambda x: int(x), results[0].boxes.cls.tolist()))
                dict_names_count = {results[0].names[i]: classes.count(i) for i in classes}
                print(dict_names_count if len(dict_names_count) > 0 else None)

    def blur(self, frame, results):
        if self.settings["checkboxblur"]:
            blur_size = self.settings["blur_size"]
            for box in results[0].boxes.xyxy.cpu().tolist():
                obj = frame[int(box[1]):int(box[3]), int(box[0]):int(box[2])]
                frame[int(box[1]):int(box[3]), int(box[0]):int(box[2])] = cv2.blur(obj, (blur_size, blur_size))

        if self.settings["checkboxrectangles"]:
            for result in results[0].boxes:
                x1, y1, x2, y2 = map(int, result.xyxy[0].tolist())
                class_id = int(result.cls[0])
                label = f"{results[0].names[class_id]} {result.conf[0]:.2f}"

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        return frame
    
    def stop(self):
        self.running = False
        self.wait()

class ScreenCaptureApp(QMainWindow):
    def __init__(self, settings):
        super().__init__()
        self.camera = dxcam.create(device_idx=0, output_idx=settings['index_monitor'], output_color="BGR")
        self.settings = settings
        self.init_ui()
        self.start_processing()

    def init_ui(self):
        self.setWindowTitle(f"Screen Blur - {Path(self.settings['model_path']).name}")
        self.setGeometry(0, 0, 800, 600)

        self.video_label = QLabel(self)
        self.setCentralWidget(self.video_label)
        self.setMinimumSize(300, 200)

    def start_processing(self):
        self.yolo_thread = YOLOThread(self.camera, self.settings)
        self.yolo_thread.frame_processed.connect(self.update_frame)
        self.yolo_thread.start()

    def update_frame(self, frame):
        label_width = self.video_label.width()
        label_height = self.video_label.height()
        resized_frame = cv2.resize(frame, (label_width, label_height), interpolation=cv2.INTER_AREA)
        height, width, channel = resized_frame.shape
        bytes_per_line = channel * width
        q_image = QImage(resized_frame.data, width, height, bytes_per_line, QImage.Format_BGR888)
        self.video_label.setPixmap(QPixmap.fromImage(q_image))

    def closeEvent(self, event):
        self.yolo_thread.stop()
        self.camera.stop()
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    while True:
        settings_dialog = SettingsDialog()
        if settings_dialog.exec_() != QDialog.Accepted:
            break
        
        settings = settings_dialog.get_settings()

        window = ScreenCaptureApp(settings)
        window.show()
        
        app.exec_()
        window.close()

if __name__ == "__main__":
    main()