import os
from datetime import datetime
import time
import cv2
import numpy as np
from PySide6.QtWidgets import QMainWindow, QMessageBox, QFileDialog
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QSettings
from UI.Home import Ui_MainWindow  # Import your generated class
from Camera_Module.MvCameraControl_class import cast, POINTER, MvCamera, MV_CC_DEVICE_INFO_LIST,MV_CC_DEVICE_INFO, MV_GIGE_DEVICE, MV_USB_DEVICE
from Camera_Module.MvErrorDefine_const import *
from Camera_Module.CamOperation import CameraOperation
from Camera_Module.utils import decoding_char, ToHexStr, is_float
from Image_Processing.process_image import ImageFunction
from Image_Processing.model import DetectionModel, PositionOffset

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("My Application")

        self.deviceList = MV_CC_DEVICE_INFO_LIST()
        self.cam = MvCamera()
        self.image_function = ImageFunction()
        self.model_detection = DetectionModel()
        self.model_cls = PositionOffset()
        self.nSelCamIndex = 0
        self.obj_cam_operation = 0
        
        self.image_arr = None
        self.isOpen = False
        self.isGrabbing = False

        # Event bindings
        self.ui.bnEnum.clicked.connect(self.enum_devices)
        self.ui.bnOpen.clicked.connect(self.open_devices)
        self.ui.bnClose.clicked.connect(self.close_devices)
        self.ui.bnStart.clicked.connect(self.start_camera)
        self.ui.bnStop.clicked.connect(self.stop_camera)
        self.ui.bnSet.clicked.connect(self.save_settings)
        self.ui.bnFolder.clicked.connect(self.choose_folder)
        
        self.load_initial_settings()
        self.enable_controls() 

    def load_initial_settings(self):
        # Load settings from config.ini
        self.settings = QSettings("config.ini", QSettings.IniFormat)
        base_output_dir = self.settings.value("Paths/output_dir")

        if not base_output_dir:
            self.ui.dir.setText("No base folder selected in settings")
            return

        self._initialize_output_directories(base_output_dir)

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if not folder:
            self.ui.dir.setText("No folder selected")
            return

        # Store selected folder as base output directory
        self.settings.setValue("Paths/output_dir", folder)
        self._initialize_output_directories(folder)
    
    def _initialize_output_directories(self, base_output_dir):
        """Create date-based OK/NG folder structure under the given base path."""
        today = datetime.now().strftime("%Y-%m-%d")
        self.output_dir = os.path.join(base_output_dir, today)
        os.makedirs(self.output_dir, exist_ok=True)

        # Define subfolder structure
        subfolders = {
            "output_dir_ok_raw": os.path.join(self.output_dir, "OK", "raw_image"),
            "output_dir_ok_annotated": os.path.join(self.output_dir, "OK", "annotated_image"),
            "output_dir_ok_label": os.path.join(self.output_dir, "OK", "label"),
            "output_dir_ng_raw": os.path.join(self.output_dir, "NG", "raw_image"),
            "output_dir_ng_annotated": os.path.join(self.output_dir, "NG", "annotated_image"),
            "output_dir_ng_label": os.path.join(self.output_dir, "NG", "label"),
        }

        # Create folders and store paths in self
        for attr, path in subfolders.items():
            os.makedirs(path, exist_ok=True)
            setattr(self, attr, path)

        # Update UI
        self.ui.dir.setText(base_output_dir)

    ## Connect Camera
    def enum_devices(self):
        self.deviceList = MV_CC_DEVICE_INFO_LIST()
        ret = MvCamera.MV_CC_EnumDevices(MV_GIGE_DEVICE | MV_USB_DEVICE, self.deviceList)
        if ret != 0:
            strError = "Enum devices fail! ret = :" + ToHexStr(ret)
            QMessageBox.warning(self, "Error", strError, QMessageBox.Ok)
            return ret

        if self.deviceList.nDeviceNum == 0:
            QMessageBox.warning(self, "Info", "Find no device", QMessageBox.Ok)
            return ret
        print("Find %d devices!" % self.deviceList.nDeviceNum)
        devList = []
        for i in range(0, self.deviceList.nDeviceNum):
            mvcc_dev_info = cast(self.deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
            if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
                print("gige device: [%d]" % i)
                user_defined_name = decoding_char(mvcc_dev_info.SpecialInfo.stGigEInfo.chUserDefinedName)
                model_name = decoding_char(mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName)
                print("device user define name: " + user_defined_name)
                print("device model name: " + model_name)

                nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
                nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
                nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
                nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
                print("current ip: %d.%d.%d.%d " % (nip1, nip2, nip3, nip4))
                devList.append(
                    "[" + str(i) + "]GigE: " + user_defined_name + " " + model_name + "(" + str(nip1) + "." + str(
                        nip2) + "." + str(nip3) + "." + str(nip4) + ")")
            elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
                print("\nu3v device: [%d]" % i)
                user_defined_name = decoding_char(mvcc_dev_info.SpecialInfo.stUsb3VInfo.chUserDefinedName)
                model_name = decoding_char(mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName)
                print("device user define name: " + user_defined_name)
                print("device model name: " + model_name)

                strSerialNumber = ""
                for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                    if per == 0:
                        break
                    strSerialNumber = strSerialNumber + chr(per)
                print("user serial number: " + strSerialNumber)
                devList.append("[" + str(i) + "]USB: " + user_defined_name + " " + model_name
                               + "(" + str(strSerialNumber) + ")")

        self.ui.ComboDevices.clear()
        self.ui.ComboDevices.addItems(devList)
        self.ui.ComboDevices.setCurrentIndex(0)

    def set_external_trigger_mode(self):
        if not self.isOpen or not self.obj_cam_operation:
            return False    
        ret = self.obj_cam_operation.Set_trigger_external(trigger_source=0, trigger_activation=0, trigger_delay_us=2000)
        # breakpoint()
        if ret != 0:
            strError = "Set trigger mode failed " + ToHexStr(ret)
            QMessageBox.warning(self, "Error", strError, QMessageBox.StandardButton.Ok)
            return False
        return True
    
    def get_param(self):
        ret = self.obj_cam_operation.Get_parameter()
        if ret != MV_OK:
            strError = "Get param failed ret:" + ToHexStr(ret)
            QMessageBox.warning(self, "Error", strError, QMessageBox.Ok)
        else:
            self.ui.edtExposureTime.setText("{0:.2f}".format(self.obj_cam_operation.exposure_time))
            self.ui.edtGain.setText("{0:.2f}".format(self.obj_cam_operation.gain))
            self.ui.edtFrameRate.setText("{0:.2f}".format(self.obj_cam_operation.frame_rate))

    def save_settings(self):
        if not self.isOpen or not self.obj_cam_operation:
            QMessageBox.warning(self, "Error", "Camera not open", QMessageBox.StandardButton.Ok)
            return MV_E_CALLORDER   
        frame_rate = self.ui.edtFrameRate.text()
        exposure = self.ui.edtExposureTime.text()
        gain = self.ui.edtGain.text()
        if is_float(frame_rate)!=True or is_float(exposure)!=True or is_float(gain)!=True:
            strError = "Set param failed ret:" + ToHexStr(MV_E_PARAMETER)
            QMessageBox.warning(self, "Error", strError, QMessageBox.StandardButton.Ok)
            return MV_E_PARAMETER
        ret = self.obj_cam_operation.Set_parameter(frame_rate, exposure, gain)
        if ret != MV_OK:
            strError = "Set param failed ret:" + ToHexStr(ret)
            QMessageBox.warning(self, "Error", strError, QMessageBox.StandardButton.Ok)
        print("set ok")
        return MV_OK

    def open_devices(self):
        # if self.isOpen:
        #     QMessageBox.warning(self, "Error", 'Camera is Running!', QMessageBox.Ok)
        #     return MV_E_CALLORDER
        nSelCamIndex = self.ui.ComboDevices.currentIndex()
        if nSelCamIndex < 0:
            QMessageBox.warning(self, "Error", 'Please select a camera!', QMessageBox.Ok)
            return MV_E_CALLORDER

        # Create camera operation object
        self.obj_cam_operation = CameraOperation(self.cam, self.deviceList, nSelCamIndex)

        ret = self.obj_cam_operation.Open_device()
        if 0 != ret:
            strError = "Open device failed ret:" + ToHexStr(ret)
            QMessageBox.warning(self, "Error", strError, QMessageBox.Ok)
            self.isOpen = False
        else:
            self.get_param()
            self.isOpen = True
            self.enable_controls()
            

    # Enable camera controls
    def enable_controls(self):
        # Basic camera state
        self.ui.bnClose.setEnabled(self.isOpen)
        self.ui.bnEnum.setEnabled(not self.isOpen)
        self.ui.bnOpen.setEnabled(not self.isOpen)

        # Start/Stop buttons
        self.ui.bnStart.setEnabled(self.isOpen and not self.isGrabbing)
        self.ui.bnStop.setEnabled(self.isOpen and self.isGrabbing)

        # Parameter controls
        self.ui.edtExposureTime.setEnabled(self.isOpen and not self.isGrabbing)
        self.ui.edtGain.setEnabled(self.isOpen and not self.isGrabbing)
        self.ui.edtFrameRate.setEnabled(self.isOpen and not self.isGrabbing)

    def close_devices(self):
        if self.isOpen:
            # Disconnect any connected signals to prevent callbacks after close
            # Stop grabbing first if needed
            if self.isGrabbing:
                self.stop_camera()
                
            # Close the device
            self.obj_cam_operation.Close_device()
            self.isOpen = False
            self.isGrabbing = False
            self.enable_controls()
 
    def start_camera(self):
        if not self.isOpen:
            QMessageBox.warning(self, "Error", "Camera not open", QMessageBox.Ok)
            return
        
        # Set software trigger mode ON
        if not self.set_external_trigger_mode():
            return

        # Start grabbing
        ret = self.obj_cam_operation.Start_grabbing()
        if ret != MV_OK:
            QMessageBox.warning(self, "Error", f"Start grabbing in trigger mode failed: {ToHexStr(ret)}", QMessageBox.Ok)
            return

        self.isGrabbing = True
        self.enable_controls()
        
        self.obj_cam_operation.image_signal.connect(self.process_with_yolo)

    def Display_frame(self, np_arr):
        if np_arr is None or np_arr.size == 0:
            print("Error: Empty image array received")
            return
        if np_arr.dtype != np.uint8:
            raise ValueError("The input NumPy array must be of type uint8")
        if len(np_arr.shape) == 2:  # If the image is grayscale (1 channel)
            height, width = np_arr.shape
            channels = 1
            bytes_per_line = width
            q_image = QImage(np_arr.data, width, height, bytes_per_line, QImage.Format.Format_Grayscale8)
        elif len(np_arr.shape) == 3 and np_arr.shape[2] == 3:  # If the image has 3 channels (BGR)
            height, width, channels = np_arr.shape
            bytes_per_line = channels * width
            q_image = QImage(np_arr.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)
        elif len(np_arr.shape) == 3 and np_arr.shape[2] == 1:  # If it's grayscale with 1 channel (shape: [height, width, 1])
            height, width, channels = np_arr.shape
            bytes_per_line = width
            q_image = QImage(np_arr.data, width, height, bytes_per_line, QImage.Format.Format_Grayscale8)
        else:
            raise ValueError("The input NumPy array must be a grayscale or BGR image")
        # Convert QImage to QPixmap and scale it to fit in the label
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(self.ui.label_img_out.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        # Set the scaled pixmap to the label
        self.ui.label_img_out.setPixmap(scaled_pixmap)

    def stop_camera(self):
        if not self.isGrabbing:
            return

        # Disconnect signal first to prevent callbacks during stop
        try:
            self.obj_cam_operation.image_signal.disconnect()
        except (TypeError, RuntimeError):
            pass  # Already disconnected or never connected
            
        ret = self.obj_cam_operation.Stop_grabbing()
        if ret != 0:
            strError = "Stop grabbing failed " + ToHexStr(ret)
            QMessageBox.warning(self, "Error", strError, QMessageBox.Ok)
            return
        self.isGrabbing = False
        self.enable_controls()

    def process_with_yolo(self, img_np):
        start = time.time()
        self.ui.qr_code.clear()
        self.ui.serial.clear()
        # Crop and prepare images
        qr_match_sn = False
        crop_img = ImageFunction.processing_image(img_np)
        img1, found_deffect, qr, sn = self.model_detection.detection(crop_img)
        img2, position_fail = self.model_cls.classify(crop_img)
        if qr == sn:
            qr_match_sn = True
        img = cv2.add(img1, img2)
        self.Display_frame(img)  # Display the original image
        result = self.check_quality(found_deffect, position_fail, qr_match_sn)
        stop = time.time()
        elapsed_ms = (stop - start) * 1000
        self.ui.label_time.setText(f"{elapsed_ms:.0f} ms")
        self.ui.qr_code.setText(f"{qr}")
        self.ui.serial.setText(f"{sn}")
        
    def check_quality(self, found_deffect, position_fail, qr_match_sn):
        if (found_deffect or position_fail) or not (qr_match_sn):
            self.ui.label_check.setText("NG")
            self.ui.label_check.setStyleSheet("background-color: red; color: black;")
            return False
        else:
            self.ui.label_check.setText("OK")
            self.ui.label_check.setStyleSheet("background-color: green; color: rgb(85, 170, 0);")
        return True
