from datetime import datetime
import numpy as np
from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QMessageBox
from Camera_Module.MvCameraControl_class import *
from Camera_Module.CamOperation import CameraOperation
from Camera_Module.utils import ToHexStr, decoding_char

class CameraController(QObject):
    image_received = Signal(np.ndarray)
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.deviceList = MV_CC_DEVICE_INFO_LIST()
        self.cam = MvCamera()
        self.obj_cam_operation = None
        self.is_open = False
        self.is_grabbing = False
        self.nSelCamIndex = 0

    def get_state(self):
        return {
            'is_open': self.is_open,
            'is_grabbing': self.is_grabbing
        }

    def enum_devices(self):
        self.deviceList = MV_CC_DEVICE_INFO_LIST()
        ret = MvCamera.MV_CC_EnumDevices(MV_GIGE_DEVICE | MV_USB_DEVICE, self.deviceList)
        if ret != 0:
            strError = "Enum devices fail! ret = :" + ToHexStr(ret)
            QMessageBox.warning(self.main_window, "Error", strError, QMessageBox.Ok)
            return ret

        if self.deviceList.nDeviceNum == 0:
            QMessageBox.warning(self.main_window, "Info", "Find no device", QMessageBox.Ok)
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

        self.main_window.ui.ComboDevices.clear()
        self.main_window.ui.ComboDevices.addItems(devList)
        self.main_window.ui.ComboDevices.setCurrentIndex(0)

    def open_device(self):
        if self.is_open:
            QMessageBox.warning(self.main_window, "Error", 'Camera is Running!', QMessageBox.Ok)
            return MV_E_CALLORDER

        self.nSelCamIndex = self.main_window.ui.ComboDevices.currentIndex()
        if self.nSelCamIndex < 0:
            QMessageBox.warning(self.main_window, "Error", 'Please select a camera!', QMessageBox.Ok)
            return MV_E_CALLORDER

        # Create camera operation object
        self.obj_cam_operation = CameraOperation(self.cam, self.deviceList, self.nSelCamIndex)

        ret = self.obj_cam_operation.Open_device()
        if 0 != ret:
            strError = "Open device failed ret:" + ToHexStr(ret)
            QMessageBox.warning(self.main_window, "Error", strError, QMessageBox.Ok)
            self.is_open = False
        else:
            self.get_param()
            self.is_open = True
            self.set_software_trigger_mode_on()
            self.main_window.enable_controls()

    def close_device(self):
        if self.is_open:
            # Disconnect any connected signals to prevent callbacks after close
            try:
                self.obj_cam_operation.image_signal.disconnect()
            except (TypeError, RuntimeError):
                pass  # Already disconnected or never connected
                
            # Stop grabbing first if needed
            if self.is_grabbing:
                self.stop_capture(reset_trigger_mode=False)
                
            # Close the device
            self.obj_cam_operation.Close_device()
            self.is_open = False
            self.is_grabbing = False
            self.main_window.enable_controls()

    def start_continuous_capture(self):
        if not self.is_open:
            QMessageBox.warning(self.main_window, "Error", "Camera not open", QMessageBox.Ok)
            return
            
        # Set continuous (non-trigger) mode
        if not self.set_software_trigger_mode_off():
            return
            
        # Start grabbing
        ret = self.obj_cam_operation.Start_grabbing()
        if ret != 0:
            strError = "Start grabbing failed " + ToHexStr(ret)
            QMessageBox.warning(self.main_window, "Error", strError, QMessageBox.Ok)
            return

        self.is_grabbing = True
        self.main_window.enable_controls()
        
        # Disconnect any previous connections to avoid multiple callbacks
        try:
            self.obj_cam_operation.image_signal.disconnect()
        except (TypeError, RuntimeError):
            pass  # Already disconnected or never connected
            
        # Connect signal for continuous display
        self.obj_cam_operation.image_signal.connect(self._display_frame)

    def stop_capture(self, reset_trigger_mode=True):
        if not self.is_grabbing:
            return
            
        # Disconnect signal first to prevent callbacks during stop
        try:
            self.obj_cam_operation.image_signal.disconnect()
        except (TypeError, RuntimeError):
            pass  # Already disconnected or never connected
            
        ret = self.obj_cam_operation.Stop_grabbing()
        if ret != 0:
            strError = "Stop grabbing failed " + ToHexStr(ret)
            QMessageBox.warning(self.main_window, "Error", strError, QMessageBox.Ok)
            return
            
        self.is_grabbing = False
        
        if reset_trigger_mode:
            self.set_software_trigger_mode_on()
            
        self.main_window.enable_controls()

    def trigger_single_capture(self):
        if not self.is_open or not self.obj_cam_operation:
            QMessageBox.warning(self.main_window, "Error", "Camera is not open!", QMessageBox.Ok)
            return

        # Ensure camera is not already grabbing continuously
        if self.is_grabbing:
            self.stop_capture(reset_trigger_mode=False)

        # Set software trigger mode
        if not self.set_software_trigger_mode_on():
            return

        # Start grabbing in trigger mode
        ret = self.obj_cam_operation.Start_grabbing()
        if ret != MV_OK:
            QMessageBox.warning(self.main_window, "Error", f"Start grabbing failed: {ToHexStr(ret)}", QMessageBox.Ok)
            return
            
        self.is_grabbing = True
        self.main_window.enable_controls()

        # Disconnect any previous connections
        try:
            self.obj_cam_operation.image_signal.disconnect()
        except (TypeError, RuntimeError):
            pass  # Already disconnected or never connected
            
        # Connect signal to receive one image
        self.obj_cam_operation.image_signal.connect(self._handle_triggered_image)

        # Trigger once
        ret = self.obj_cam_operation.Trigger_once()
        if ret != MV_OK:
            QMessageBox.warning(self.main_window, "Error", f"Trigger failed: {ToHexStr(ret)}", QMessageBox.Ok)
            # Clean up if trigger fails
            self.stop_capture(reset_trigger_mode=True)
            return

    def save_settings(self):
        if not self.is_open or not self.obj_cam_operation:
            QMessageBox.warning(self.main_window, "Error", "Camera not open", QMessageBox.StandardButton.Ok)
            return MV_E_CALLORDER
            
        frame_rate = self.main_window.ui.edtFrameRate.text()
        exposure = self.main_window.ui.edtExposureTime.text()
        gain = self.main_window.ui.edtGain.text()

        if not (frame_rate.replace('.', '', 1).isdigit() and 
                exposure.replace('.', '', 1).isdigit() and 
                gain.replace('.', '', 1).isdigit()):
            strError = "Set param failed ret:" + ToHexStr(MV_E_PARAMETER)
            QMessageBox.warning(self.main_window, "Error", strError, QMessageBox.StandardButton.Ok)
            return MV_E_PARAMETER

        ret = self.obj_cam_operation.Set_parameter(frame_rate, exposure, gain)
        if ret != MV_OK:
            strError = "Set param failed ret:" + ToHexStr(ret)
            QMessageBox.warning(self.main_window, "Error", strError, QMessageBox.StandardButton.Ok)
        print("set ok")
        return MV_OK

    def get_param(self):
        ret = self.obj_cam_operation.Get_parameter()
        if ret != MV_OK:
            strError = "Get param failed ret:" + ToHexStr(ret)
            QMessageBox.warning(self.main_window, "Error", strError, QMessageBox.Ok)
        else:
            self.main_window.ui.edtExposureTime.setText("{0:.2f}".format(self.obj_cam_operation.exposure_time))
            self.main_window.ui.edtGain.setText("{0:.2f}".format(self.obj_cam_operation.gain))
            self.main_window.ui.edtFrameRate.setText("{0:.2f}".format(self.obj_cam_operation.frame_rate))

    def set_software_trigger_mode_on(self):
        if not self.is_open or not self.obj_cam_operation:
            return False
            
        ret = self.obj_cam_operation.Set_trigger_mode(True)
        if ret != 0:
            strError = "Set trigger mode failed " + ToHexStr(ret)
            QMessageBox.warning(self.main_window, "Error", strError, QMessageBox.StandardButton.Ok)
            return False
        return True

    def set_software_trigger_mode_off(self):
        if not self.is_open or not self.obj_cam_operation:
            return False
            
        ret = self.obj_cam_operation.Set_trigger_mode(False)
        if ret != 0:
            strError = "Set trigger mode failed " + ToHexStr(ret)
            QMessageBox.warning(self.main_window, "Error", strError, QMessageBox.StandardButton.Ok)
            return False
        return True

    def _display_frame(self, np_arr):
        """Emit the image for display"""
        self.image_received.emit(np_arr)

    def _handle_triggered_image(self, np_arr):
        """Handle a single triggered image"""
        # Disconnect the signal first to avoid multiple triggers
        try:
            self.obj_cam_operation.image_signal.disconnect(self._handle_triggered_image)
        except (TypeError, RuntimeError):
            pass  # Already disconnected or never connected
        
        # Emit the image for processing
        self._display_frame(np_arr)
        
        # Stop grabbing but keep trigger mode on
        self.stop_capture(reset_trigger_mode=False)
        
        # Update controls
        self.main_window.enable_controls()