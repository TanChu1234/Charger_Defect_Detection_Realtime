import os
import time
import cv2
import numpy as np
from datetime import datetime
from PySide6.QtWidgets import QMainWindow, QMessageBox, QFileDialog
from PySide6.QtGui import QPixmap, QImage, QCloseEvent
from PySide6.QtCore import Qt, QSettings

from UI.Home import Ui_MainWindow
from Camera_Module.MvCameraControl_class import cast, POINTER, MvCamera, MV_CC_DEVICE_INFO_LIST, MV_CC_DEVICE_INFO, MV_GIGE_DEVICE, MV_USB_DEVICE
from Camera_Module.MvErrorDefine_const import *
from Camera_Module.CamOperation import CameraOperation
from Camera_Module.utils import decoding_char, is_float
from Image_Processing.process_image import ImageFunction
from Image_Processing.model import DetectionModel, PositionOffset, AdapterDetectionModel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Vision Inspection System")

        self.deviceList = MV_CC_DEVICE_INFO_LIST()
        self.cam = MvCamera()
        self.obj_cam_operation = None
        self.isOpen = False
        
        self.image_function = ImageFunction()
        self.model_detection = DetectionModel()
        self.adapter_model = AdapterDetectionModel()
        self.model_cls = PositionOffset()
        # self.find_pattern = MatchTemplate()
        self.setup_ui()
        self.load_initial_settings()
        self.enable_controls()

    def setup_ui(self):
        self.ui.bnStart.setCheckable(True)
        self.ui.bnStart.setText("Start Camera")
        self.ui.bnStart.clicked.connect(self.toggle_camera)
        self.ui.bnTrigger.clicked.connect(self.trigger)
        self.ui.bnEnum.clicked.connect(self.enum_devices)
        self.ui.bnSet.clicked.connect(self.save_settings)
        self.ui.bnFolder.clicked.connect(self.choose_folder)

    def load_initial_settings(self):
        self.settings = QSettings("config.ini", QSettings.IniFormat)
        base_output_dir = self.settings.value("Paths/output_dir")
        if base_output_dir:
            self._initialize_output_directories(base_output_dir)
        else:
            self.ui.dir.setText("No base folder selected in settings")

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.settings.setValue("Paths/output_dir", folder)
            self._initialize_output_directories(folder)
        else:
            self.ui.dir.setText("No folder selected")

    def _initialize_output_directories(self, base_output_dir):
        today = datetime.now().strftime("%Y-%m-%d")
        self.output_dir = os.path.join(base_output_dir, today)
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.subfolders = {
            "ok_raw": os.path.join(self.output_dir, "OK", "raw_image"),
            "ok": os.path.join(self.output_dir, "OK", "raw"),
            "ok_annotated": os.path.join(self.output_dir, "OK", "annotated_image"),
            "ng_raw": os.path.join(self.output_dir, "NG", "raw_image"),
            "ng": os.path.join(self.output_dir, "NG", "raw"),
            "ng_annotated": os.path.join(self.output_dir, "NG", "annotated_image"),
        }

        for path in self.subfolders.values():
            os.makedirs(path, exist_ok=True)

        self.ui.dir.setText(base_output_dir)

    def toggle_camera(self):
        if self.ui.bnStart.isChecked():
            self.start_camera()
        else:
            self.stop_camera()

    def enum_devices(self):
        self.deviceList = MV_CC_DEVICE_INFO_LIST()
        ret = MvCamera.MV_CC_EnumDevices(MV_GIGE_DEVICE | MV_USB_DEVICE, self.deviceList)
        if ret != 0 or self.deviceList.nDeviceNum == 0:
            QMessageBox.warning(self, "Error", "No camera found", QMessageBox.Ok)
            return

        self.ui.ComboDevices.clear()
        devList = []

        for i in range(self.deviceList.nDeviceNum):
            info = cast(self.deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
            if info.nTLayerType == MV_GIGE_DEVICE:
                name = decoding_char(info.SpecialInfo.stGigEInfo.chUserDefinedName)
                model = decoding_char(info.SpecialInfo.stGigEInfo.chModelName)
                ip = info.SpecialInfo.stGigEInfo.nCurrentIp
                ip_str = '.'.join([str((ip >> (8 * i)) & 0xFF) for i in reversed(range(4))])
                devList.append(f"[{i}] GigE: {name} {model} ({ip_str})")
            elif info.nTLayerType == MV_USB_DEVICE:
                name = decoding_char(info.SpecialInfo.stUsb3VInfo.chUserDefinedName)
                model = decoding_char(info.SpecialInfo.stUsb3VInfo.chModelName)
                sn = ''.join([chr(c) for c in info.SpecialInfo.stUsb3VInfo.chSerialNumber if c != 0])
                devList.append(f"[{i}] USB: {name} {model} ({sn})")

        self.ui.ComboDevices.addItems(devList)

    def start_camera(self):
        idx = self.ui.ComboDevices.currentIndex()
        if idx < 0:
            QMessageBox.warning(self, "Error", "Please select a camera!", QMessageBox.Ok)
            self.ui.bnStart.setChecked(False)
            return

        self.obj_cam_operation = CameraOperation(self.cam, self.deviceList, idx)
        if self.obj_cam_operation.Open_device() != MV_OK:
            QMessageBox.warning(self, "Error", "Failed to open camera", QMessageBox.Ok)
            self.ui.bnStart.setChecked(False)
            return

        self.get_param()

        if not self.obj_cam_operation.Set_trigger_external(trigger_source=0, trigger_activation=1,trigger_delay_us= 0) == MV_OK:
        # if not self.obj_cam_operation.Set_trigger_mode(True) == MV_OK:
            QMessageBox.warning(self, "Error", "Failed to set external trigger", QMessageBox.Ok)
            self.ui.bnStart.setChecked(False)
            return

        if self.obj_cam_operation.Start_grabbing() != MV_OK:
            QMessageBox.warning(self, "Error", "Failed to start grabbing", QMessageBox.Ok)
            self.ui.bnStart.setChecked(False)
            return

        self.isOpen = True
        self.enable_controls()
        self.obj_cam_operation.image_signal.connect(self.process_with_yolo)
        self.ui.bnStart.setText("Stop Camera")

    def trigger(self):
        ret = self.obj_cam_operation.Set_trigger_mode(True)
        if ret != 0:
            strError = "Set trigger mode failed "
            QMessageBox.warning(self, "Error", strError, QMessageBox.StandardButton.Ok)
            return False
        # Disconnect any previous connections
        try:
            self.obj_cam_operation.image_signal.disconnect()
        except (TypeError, RuntimeError):
            pass  # Already disconnected or never connected
         # Trigger once
        ret = self.obj_cam_operation.Trigger_once()
        if ret != MV_OK:
            QMessageBox.warning(self, "Error", f"Trigger failed", QMessageBox.Ok)
            # Clean up if trigger fails
            return
        # Connect signal to receive one image
        self.obj_cam_operation.image_signal.connect(self.process_with_yolo)
        # self.obj_cam_operation.Set_trigger_external(trigger_source=0, trigger_activation=1,trigger_delay_us= 0)
        
        
    def stop_camera(self):
        if not self.isOpen:
            return
        try:
            self.obj_cam_operation.image_signal.disconnect()
        except Exception:
            pass

        self.obj_cam_operation.Stop_grabbing()
        self.obj_cam_operation.Close_device()
        self.isOpen = False
        self.enable_controls()
        self.ui.bnStart.setText("Start Camera")
        self.ui.bnStart.setChecked(False)
        # print("Closed successfully!")

    def get_param(self):
        if self.obj_cam_operation.Get_parameter() == MV_OK:
            self.ui.edtExposureTime.setText(f"{self.obj_cam_operation.exposure_time:.2f}")
            self.ui.edtGain.setText(f"{self.obj_cam_operation.gain:.2f}")
            self.ui.edtFrameRate.setText(f"{self.obj_cam_operation.frame_rate:.2f}")

    def save_settings(self):
        if not self.isOpen:
            QMessageBox.warning(self, "Error", "Camera not open", QMessageBox.Ok)
            return MV_E_CALLORDER

        frame_rate = self.ui.edtFrameRate.text()
        exposure = self.ui.edtExposureTime.text()
        gain = self.ui.edtGain.text()

        if not all(map(is_float, [frame_rate, exposure, gain])):
            QMessageBox.warning(self, "Error", "Invalid parameters", QMessageBox.Ok)
            return MV_E_PARAMETER

        return self.obj_cam_operation.Set_parameter(frame_rate, exposure, gain)

    def enable_controls(self):
        for field in [self.ui.edtExposureTime, self.ui.edtGain, self.ui.edtFrameRate]:
            field.setEnabled(self.isOpen)
        
    def Display_frame(self, np_arr):
        np_arr = np.ascontiguousarray(np_arr)
        if np_arr is None or np_arr.size == 0:
            return

        if len(np_arr.shape) == 2:
            height, width = np_arr.shape
            q_image = QImage(np_arr.data, width, height, width, QImage.Format_Grayscale8)
        elif len(np_arr.shape) == 3 and np_arr.shape[2] == 3:
            height, width, channels = np_arr.shape
            q_image = QImage(np_arr.data, width, height, width * channels, QImage.Format_BGR888)
        else:
            return

        pixmap = QPixmap.fromImage(q_image).scaled(self.ui.label_img_out.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ui.label_img_out.setImage(pixmap)

    

    def process_with_yolo(self, img_np):
        start = time.time()
        self.ui.position.clear()
        self.ui.qr_code.clear()
        self.ui.serial.clear()

        # crop_img = self.image_function.processing_image(img_np)
        # crop_size = (1100, 720)   # width, height
        # start_point = (1550, 1380)  # (x, y) where cropping starts
        # crop_size = (1300, 1300)   # width, height
        # start_point = (1450, 1050) # (x, y) where cropping starts
        # crop_img = self.image_function.crop_image(img_np, start_point, crop_size)
        # crop_img = self.image_function.crop_image(img_np)
        # print(img_np.shape)
        # crop_img = self.image_function.processing_image(img_np)
        # crop_img = self.adapter_model.crop_adapter(img_np)
        

        adapter_result, rgb_image = self.adapter_model.detecting(img_np)
        crop_img = self.adapter_model.crop_adapter(adapter_result, rgb_image)
        copy_crop_img = crop_img.copy()
        img1, defect, qr, sn = self.model_detection.detection(copy_crop_img)
        # crop_img, rgb_image = self.find_pattern.run(img_np)
        # copy_crop_img = crop_img.copy()
        # img1, defect, qr, sn = self.model_detection.detection(rgb_image)
        
        # img1 = self.adapter_model.find_offset(adapter_result, img1.copy())
        
        
        if sn or qr:
            # img2, offset = self.model_cls.classify(crop_img)
            # result_img = cv2.add(img1, img2)
            # result_img = cv2.add(result_img, img3)      
            result_img = img1
            # _ = self.check_quality(defect, qr == sn, offset)
            
            # self.ui.position.setText(f"{offset}")
            # if offset == "standard":
            #     self.ui.position.setText(f"{offset}")
            # else:
            #     self.ui.position.setText(f"{offset} Offset")
            self.ui.position.setText(f"standard")
            self.ui.qr_code.setText(qr)
            self.ui.serial.setText(sn)
            _ = self.check_defect(defect)  
        else:
            result_img = img1
            _ = self.check_defect(defect)

        save_name = datetime.now().strftime("%Y%m%d_%H%M%S") + ".bmp"
        cv2.imwrite(os.path.join(self.subfolders['ok_raw'], save_name), crop_img)
        cv2.imwrite(os.path.join(self.subfolders['ok_annotated'], save_name), result_img)
        cv2.imwrite(os.path.join(self.subfolders['ok'], save_name), img_np)
        self.Display_frame(result_img)
        elapsed_ms = (time.time() - start) * 1000
        self.ui.label_time.setText(f"{elapsed_ms:.0f} ms")

    def check_quality(self, defect, match, offset):
        if defect or not match or offset != "standard":
            self.ui.label_check.setText("NG")
            self.ui.label_check.setStyleSheet("background-color: red; color: black;")
            return False
        else:
            self.ui.label_check.setText("OK")
            self.ui.label_check.setStyleSheet("background-color: green; color: rgb(85, 170, 0);")
            return True

    def check_defect(self, defect):
        if defect:
            self.ui.label_check.setText("NG")
            self.ui.label_check.setStyleSheet("background-color: red; color: black;")
            return False
        else:
            self.ui.label_check.setText("OK")
            self.ui.label_check.setStyleSheet("background-color: green; color: rgb(85, 170, 0);")
            return True

    def closeEvent(self, event: QCloseEvent):
        if self.obj_cam_operation:
            self.stop_camera()
            event.accept()
        return