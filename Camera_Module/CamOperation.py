# -- coding: utf-8 --
import threading
import numpy as np
import time
import inspect
from ctypes import *
from Camera_Module.utils import *
from Camera_Module.CameraParams_header import *
from Camera_Module.MvCameraControl_class import *
from PySide6.QtCore import QObject, Signal

# Force close a thread
def Async_raise(tid, exctype):
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

# Stop thread
def Stop_thread(thread):
    Async_raise(thread.ident, SystemExit)

# Convert to hexadecimal string
def To_hex_str(num):
    chaDic = {10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}
    hexStr = ""
    if num < 0:
        num = num + 2 ** 32
    while num >= 16:
        digit = num % 16
        hexStr = chaDic.get(digit, str(digit)) + hexStr
        num //= 16
    hexStr = chaDic.get(num, str(num)) + hexStr
    return hexStr

# Whether it is a Mono image
def Is_mono_data(enGvspPixelType):
    if PixelType_Gvsp_Mono8 == enGvspPixelType or PixelType_Gvsp_Mono10 == enGvspPixelType \
            or PixelType_Gvsp_Mono10_Packed == enGvspPixelType or PixelType_Gvsp_Mono12 == enGvspPixelType \
            or PixelType_Gvsp_Mono12_Packed == enGvspPixelType:
        return True
    else:
        return False

# Is it a color image?
def Is_color_data(enGvspPixelType):
    if PixelType_Gvsp_BayerGR8 == enGvspPixelType or PixelType_Gvsp_BayerRG8 == enGvspPixelType \
            or PixelType_Gvsp_BayerGB8 == enGvspPixelType or PixelType_Gvsp_BayerBG8 == enGvspPixelType \
            or PixelType_Gvsp_BayerGR10 == enGvspPixelType or PixelType_Gvsp_BayerRG10 == enGvspPixelType \
            or PixelType_Gvsp_BayerGB10 == enGvspPixelType or PixelType_Gvsp_BayerBG10 == enGvspPixelType \
            or PixelType_Gvsp_BayerGR12 == enGvspPixelType or PixelType_Gvsp_BayerRG12 == enGvspPixelType \
            or PixelType_Gvsp_BayerGB12 == enGvspPixelType or PixelType_Gvsp_BayerBG12 == enGvspPixelType \
            or PixelType_Gvsp_BayerGR10_Packed == enGvspPixelType or PixelType_Gvsp_BayerRG10_Packed == enGvspPixelType \
            or PixelType_Gvsp_BayerGB10_Packed == enGvspPixelType or PixelType_Gvsp_BayerBG10_Packed == enGvspPixelType \
            or PixelType_Gvsp_BayerGR12_Packed == enGvspPixelType or PixelType_Gvsp_BayerRG12_Packed == enGvspPixelType \
            or PixelType_Gvsp_BayerGB12_Packed == enGvspPixelType or PixelType_Gvsp_BayerBG12_Packed == enGvspPixelType \
            or PixelType_Gvsp_YUV422_Packed == enGvspPixelType or PixelType_Gvsp_YUV422_YUYV_Packed == enGvspPixelType:     
        return True
    else:
        return False


# Mono image converted to python array
def Mono_numpy(data, nWidth, nHeight):
    data_ = np.frombuffer(data, count=int(nWidth * nHeight), dtype=np.uint8, offset=0)
    data_mono_arr = data_.reshape(nHeight, nWidth)
    numArray = np.zeros([nHeight, nWidth, 1], "uint8")
    numArray[:, :, 0] = data_mono_arr
    return numArray

# Convert color image to python array
def Color_numpy(data, nWidth, nHeight):
    data_ = np.frombuffer(data, count=int(nWidth * nHeight * 3), dtype=np.uint8, offset=0)
    data_r = data_[0:nWidth * nHeight * 3:3]
    data_g = data_[1:nWidth * nHeight * 3:3]
    data_b = data_[2:nWidth * nHeight * 3:3]

    data_r_arr = data_r.reshape(nHeight, nWidth)
    data_g_arr = data_g.reshape(nHeight, nWidth)
    data_b_arr = data_b.reshape(nHeight, nWidth)
    numArray = np.zeros([nHeight, nWidth, 3], "uint8")

    numArray[:, :, 0] = data_r_arr
    numArray[:, :, 1] = data_g_arr
    numArray[:, :, 2] = data_b_arr
    return numArray

# Camera operation class
class CameraOperation(QObject):
    image_signal = Signal(object)

    def __init__(self, obj_cam, st_device_list, n_connect_num=0, b_open_device=False, b_start_grabbing=False,
                 h_thread_handle = None, np_arr = None, 
                 b_thread_closed = False, st_frame_info = None, b_exit=False, b_save_bmp=False,
                 buf_save_image = None, 
                 n_save_image_size = 0, frame_rate = 0, exposure_time = 0, gain = 0):
        super().__init__()
        self.obj_cam = obj_cam
        self.st_device_list = st_device_list
        self.n_connect_num = n_connect_num
        self.b_open_device = b_open_device
        self.b_start_grabbing = b_start_grabbing
        self.b_thread_closed = b_thread_closed
        self.st_frame_info = st_frame_info

        self.np_arr = np_arr
        self.b_exit = b_exit
        self.b_save_bmp = b_save_bmp
        self.buf_save_image = buf_save_image
        self.n_save_image_size = n_save_image_size

        self.h_thread_handle = h_thread_handle

        self.frame_rate = frame_rate
        self.exposure_time = exposure_time
        self.gain = gain
        self.buf_lock = threading.Lock()  # 取图和存图的buffer锁
        self.order = 0

    def Open_device(self):
        if not self.b_open_device:
            if self.n_connect_num < 0:
                return MV_E_CALLORDER

            # ch:选择设备并创建句柄 | en:Select device and create handle
            nConnectionNum = int(self.n_connect_num)
            stDeviceList = cast(self.st_device_list.pDeviceInfo[int(nConnectionNum)],
                                POINTER(MV_CC_DEVICE_INFO)).contents
            self.obj_cam = MvCamera()
            ret = self.obj_cam.MV_CC_CreateHandle(stDeviceList)
            if ret != 0:
                self.obj_cam.MV_CC_DestroyHandle()
                return ret

            ret = self.obj_cam.MV_CC_OpenDevice()
            if ret != 0:
                return ret
            print("open device successfully!")
            self.b_open_device = True
            self.b_thread_closed = False

            # Detection network optimal package size(It only works for the GigE camera)
            if stDeviceList.nTLayerType == MV_GIGE_DEVICE:
                nPacketSize = self.obj_cam.MV_CC_GetOptimalPacketSize()
                if int(nPacketSize) > 0:
                    ret = self.obj_cam.MV_CC_SetIntValue("GevSCPSPacketSize", nPacketSize)
                    if ret != 0:
                        print("warning: set packet size fail! ret[0x%x]" % ret)
                else:
                    print("warning: set packet size fail! ret[0x%x]" % nPacketSize)

            stBool = c_bool(False)
            ret = self.obj_cam.MV_CC_GetBoolValue("AcquisitionFrameRateEnable", stBool)
            if ret != 0:
                print("get acquisition frame rate enable fail! ret[0x%x]" % ret)

            # ch:设置触发模式为off | en:Set trigger mode as off
            ret = self.obj_cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
            if ret != 0:
                print("set trigger mode fail! ret[0x%x]" % ret)
            return MV_OK

    def Start_grabbing(self):
        if not self.b_start_grabbing and self.b_open_device:
            self.b_exit = False
            ret = self.obj_cam.MV_CC_StartGrabbing()
            if ret != 0:
                return ret
            self.b_start_grabbing = True
            # print("start grabbing successfully!")
            try:
                # thread_id = random.randint(1, 10000)
                self.h_thread_handle = threading.Thread(target=CameraOperation.Work_thread, args=(self,))
                self.h_thread_handle.start()
                # self.h_thread_handle.join()
                self.b_thread_closed = True
            finally:
                pass
            return MV_OK
        return MV_E_CALLORDER

    
    def Stop_grabbing(self):
        if self.b_start_grabbing and self.b_open_device:
            if self.b_thread_closed:
                Stop_thread(self.h_thread_handle)
                self.b_thread_closed = False
            ret = self.obj_cam.MV_CC_StopGrabbing()
            if ret != 0:
                return ret
            # print("stop grabbing successfully!")
            self.b_start_grabbing = False
            self.b_exit = True
            return MV_OK
        else:
            return MV_E_CALLORDER

    def Close_device(self):
        if self.b_open_device:
            if self.b_thread_closed:
                Stop_thread(self.h_thread_handle)
                self.b_thread_closed = False
            ret = self.obj_cam.MV_CC_CloseDevice()
            if ret != 0:
                return ret

        # Destroy handle
        self.obj_cam.MV_CC_DestroyHandle()
        self.b_open_device = False
        self.b_start_grabbing = False
        self.b_exit = True
        print("close device successfully!")

        return MV_OK

    def Set_trigger_mode(self, is_trigger_mode):
        if not self.b_open_device:
            return MV_E_CALLORDER

        if not is_trigger_mode:
            ret = self.obj_cam.MV_CC_SetEnumValue("TriggerMode", 0)
            if ret != 0:
                return ret
        else:
            ret = self.obj_cam.MV_CC_SetEnumValue("TriggerMode", 1)
            if ret != 0:
                return ret
            ret = self.obj_cam.MV_CC_SetEnumValue("TriggerSource", 7)
            if ret != 0:
                return ret

        return MV_OK

    def Set_trigger_external(self, trigger_source=0, trigger_activation=0, trigger_delay_us=0):
        """
        Set the camera to external trigger mode.
        :param trigger_source: 0 for Line0, 1 for Line1, etc.
        :param trigger_activation: 0 for Rising Edge, 1 for Falling Edge, etc.
        :param trigger_delay_us: Trigger delay in microseconds.
        :return: status code
        """
        if not self.b_open_device:
            return MV_E_CALLORDER
        # Set Trigger Mode to On
        ret = self.obj_cam.MV_CC_SetEnumValue("TriggerMode", 1)
        if ret != 0:
            return ret
        # Set Trigger Source
        ret = self.obj_cam.MV_CC_SetEnumValue("TriggerSource", trigger_source)
        if ret != 0:
            return ret
        # Set Trigger Activation
        ret = self.obj_cam.MV_CC_SetEnumValue("TriggerActivation", trigger_activation)
        if ret != 0:
            return ret       
        # Set Trigger Delay
        if trigger_delay_us > 0:
            ret = self.obj_cam.MV_CC_SetFloatValue("TriggerDelay", float(trigger_delay_us))
            if ret != 0:
                return ret
        return MV_OK

    # Soft trigger once
    def Trigger_once(self):
        self.order +=1
        if self.b_open_device:
            # self.b_save_bmp = True 
            return self.obj_cam.MV_CC_SetCommandValue("TriggerSoftware")

    # Get parameters
    def Get_parameter(self):
        if self.b_open_device:
            stFloatParam_FrameRate = MVCC_FLOATVALUE()
            memset(byref(stFloatParam_FrameRate), 0, sizeof(MVCC_FLOATVALUE))
            stFloatParam_exposureTime = MVCC_FLOATVALUE()
            memset(byref(stFloatParam_exposureTime), 0, sizeof(MVCC_FLOATVALUE))
            stFloatParam_gain = MVCC_FLOATVALUE()
            memset(byref(stFloatParam_gain), 0, sizeof(MVCC_FLOATVALUE))
            ret = self.obj_cam.MV_CC_GetFloatValue("AcquisitionFrameRate", stFloatParam_FrameRate)
            if ret != 0:
                return ret
            self.frame_rate = stFloatParam_FrameRate.fCurValue

            ret = self.obj_cam.MV_CC_GetFloatValue("ExposureTime", stFloatParam_exposureTime)
            if ret != 0:
                return ret
            self.exposure_time = stFloatParam_exposureTime.fCurValue

            ret = self.obj_cam.MV_CC_GetFloatValue("Gain", stFloatParam_gain)
            if ret != 0:
                return ret
            self.gain = stFloatParam_gain.fCurValue

            return MV_OK

    def Set_parameter(self, frameRate, exposureTime, gain):
        if '' == frameRate or '' == exposureTime or '' == gain:
            print('show info', 'please type in the text box !')
            return MV_E_PARAMETER
        if self.b_open_device:
            ret = self.obj_cam.MV_CC_SetEnumValue("ExposureAuto", 0)
            time.sleep(0.2)
            ret = self.obj_cam.MV_CC_SetFloatValue("ExposureTime", float(exposureTime))
            if ret != 0:
                print('show error', 'set exposure time fail! ret = ' + To_hex_str(ret))
                return ret

            ret = self.obj_cam.MV_CC_SetFloatValue("Gain", float(gain))
            if ret != 0:
                print('show error', 'set gain fail! ret = ' + To_hex_str(ret))
                return ret

            ret = self.obj_cam.MV_CC_SetFloatValue("AcquisitionFrameRate", float(frameRate))
            if ret != 0:
                print('show error', 'set acquistion frame rate fail! ret = ' + To_hex_str(ret))
                return ret

            print('show info', 'set parameter success!')

            return MV_OK

    def Work_thread(self):
        stOutFrame = MV_FRAME_OUT()
        memset(byref(stOutFrame), 0, sizeof(stOutFrame))
        while True:
            # 200 
            ret = self.obj_cam.MV_CC_GetImageBuffer(stOutFrame, 200)
            if 0 == ret:
                self.order += 1 
                # Copy images and image information
                if self.buf_save_image is None:
                    self.buf_save_image = (c_ubyte * stOutFrame.stFrameInfo.nFrameLen)()
                self.st_frame_info = stOutFrame.stFrameInfo
                # Get cache lock
                self.buf_lock.acquire()
                cdll.msvcrt.memcpy(byref(self.buf_save_image), stOutFrame.pBufAddr, self.st_frame_info.nFrameLen)
                self.np_arr = Mono_numpy(self.buf_save_image, self.st_frame_info.nWidth, self.st_frame_info.nHeight)  
                self.buf_lock.release()
                if self.order == 1:
                    self.image_signal.emit(self.np_arr)
                    # self.Save_Bmp()
                    # self.b_save_bmp = False  # Reset trigger flag after saving the image
                # Free cache
                self.obj_cam.MV_CC_FreeImageBuffer(stOutFrame)
            else:
                self.order = 0
                # print("no data, ret = " + To_hex_str(ret))
                continue

            if self.b_exit:
                
                if self.buf_save_image is not None:
                    del self.buf_save_image
                break
    
    # 存BMP图像
    def Save_Bmp(self):

        if 0 == self.buf_save_image:
            return

        # Get buffer_lock
        self.buf_lock.acquire()
        file_path = str(self.st_frame_info.nFrameNum) + ".bmp"
        c_file_path = file_path.encode('ascii')
        stSaveParam = MV_SAVE_IMAGE_TO_FILE_PARAM_EX()
        stSaveParam.enPixelType = self.st_frame_info.enPixelType
        stSaveParam.nWidth = self.st_frame_info.nWidth  # ch:相机对应的宽 | en:Width
        stSaveParam.nHeight = self.st_frame_info.nHeight  # ch:相机对应的高 | en:Height
        stSaveParam.nDataLen = self.st_frame_info.nFrameLen
        stSaveParam.pData = cast(self.buf_save_image, POINTER(c_ubyte))
        stSaveParam.enImageType = MV_Image_Bmp  # ch:需要保存的图像类型 | en:Image format to save
        stSaveParam.nQuality = 8
        stSaveParam.pcImagePath = ctypes.create_string_buffer(c_file_path)
        stSaveParam.iMethodValue = 2
        ret = self.obj_cam.MV_CC_SaveImageToFileEx(stSaveParam)
        self.buf_lock.release()
        return ret
        
    def Save_Png(self):
        if 0 == self.buf_save_image:
            return
        # Get buffer_lock
        self.buf_lock.acquire()
        file_path = str(self.st_frame_info.nFrameNum) + ".png"
        c_file_path = file_path.encode('ascii')
        stSaveParam = MV_SAVE_IMAGE_TO_FILE_PARAM_EX()
        stSaveParam.enPixelType = self.st_frame_info.enPixelType  # ch:相机对应的像素格式 | en:Camera pixel type
        stSaveParam.nWidth = self.st_frame_info.nWidth  # ch:相机对应的宽 | en:Width
        stSaveParam.nHeight = self.st_frame_info.nHeight  # ch:相机对应的高 | en:Height
        stSaveParam.nDataLen = self.st_frame_info.nFrameLen
        stSaveParam.pData = cast(self.buf_save_image, POINTER(c_ubyte))
        stSaveParam.enImageType = MV_Image_Png  # ch:需要保存的图像类型 | en:Image format to save
        stSaveParam.nQuality = 8
        stSaveParam.pcImagePath = ctypes.create_string_buffer(c_file_path)
        stSaveParam.iMethodValue = 2
        ret = self.obj_cam.MV_CC_SaveImageToFileEx(stSaveParam)
        self.buf_lock.release()
        return ret
    
    def save_mono_image(self):
        if self.buf_save_image == 0:
            print("No image buffer available.")
            return

        self.buf_lock.acquire()
        try:
            # Assume you need to convert the buffer from color to Mono8
            convert_params = MV_CC_PIXEL_CONVERT_PARAM()  # Assuming you have this structure defined
            convert_params.nWidth = self.st_frame_info.nWidth
            convert_params.nHeight = self.st_frame_info.nHeight
            convert_params.enSrcPixelType = self.st_frame_info.enPixelType  # Current pixel type
            convert_params.pSrcData = self.buf_save_image  # Source buffer
            convert_params.nSrcDataLen = self.st_frame_info.nFrameLen
            convert_params.enDstPixelType = PixelType_Gvsp_Mono8  # Destination pixel type
            convert_params.pDstBuffer = ctypes.cast(ctypes.create_string_buffer(self.st_frame_info.nWidth * self.st_frame_info.nHeight + 2048), POINTER(c_ubyte)) # Assuming frame len is sufficient
            convert_params.nDstBufferSize = self.st_frame_info.nWidth * self.st_frame_info.nHeight + 2048

            # Perform the conversion
            ret = self.obj_cam.MV_CC_ConvertPixelType(convert_params)
            if ret != 0:
                print(f"Failed to convert image, error code: {ret}")
                return ret

            file_path = r"D:\Pharma2\new\1.bmp"
            c_file_path = file_path.encode('ascii')

            stSaveParam = MV_SAVE_IMAGE_TO_FILE_PARAM_EX()
            stSaveParam.enPixelType = PixelType_Gvsp_Mono8
            stSaveParam.nWidth = self.st_frame_info.nWidth
            stSaveParam.nHeight = self.st_frame_info.nHeight
            stSaveParam.nDataLen = self.st_frame_info.nFrameLen  # Updated to use the size of the converted image
            stSaveParam.pData = cast(convert_params.pDstBuffer, POINTER(c_ubyte))
            stSaveParam.enImageType = MV_Image_Bmp
            stSaveParam.nQuality = 8
            stSaveParam.pcImagePath = ctypes.create_string_buffer(c_file_path)
            stSaveParam.iMethodValue = 2

            ret = self.obj_cam.MV_CC_SaveImageToFileEx(stSaveParam)
            if ret != 0:
                print(f"Failed to save image, error code: {ret}")
        finally:
            self.buf_lock.release()

        return ret
