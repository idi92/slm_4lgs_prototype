import numpy as np
from slm_4lgs_prototype.camera_controller import FliSdk

#TODO: check units in exposure time
#TODO: erase exit() use riseError
#TODO: implement acquisition functions
#TODO: add documentation to functions
#TODO: implement test unit?

class FliError(Exception):
    """Exception raised for FirstLightImager SDK error.
    
    ...
    
    Attributes:
        errorCode -- First Light error code
        message -- error explanation    
    """
    def __init__(self, message, errorCode = None):
        self.message = message
        self.errorCode = errorCode
        
        
def detect_cameras():
    FliSdk.Init()
    #need to detect grabbers first otherwise camera cannot
    #be detected
    print("Detection of grabbers...")
    listOfGrabbers, nbGrabbers = FliSdk.DetectGrabbers()

    if nbGrabbers == 0:
        raise FliError("No grabber detected, exit.")
        

    print("Done.")
    print("List of detected grabber(s):")

    for i in range(nbGrabbers):
        print("- " + listOfGrabbers[i])
        
    print("Detection of cameras...")
    listOfCameras, nbCameras = FliSdk.DetectCameras()
    if nbCameras == 0:
        raise FliError("No camera detected, exit.")

    print("Done.")
    print("List of detected camera(s):")
    
    for i in range(nbCameras):
        print("- " + str(i) + " -> " + listOfCameras[i])

    FliSdk.Exit()
    
class CBlueOneCamera():
    
    def __init__(self, camera_name = "CBLUE1:MatroxCXP-Dev_0"):
        self._cname =  camera_name
        FliSdk.Init()
        self._detect_and_set_camera(camera_name)
        self._set_camera_mode()
        #need to update to use CblueSfnc and  CblueOne functions
        self._updateSDK()
        self._check_if_is_cblue()
        self._status = None
        FliSdk.Start()
    
    def _detect_and_set_camera(self, camera_name):
        #need to detect grabbers first otherwise camera cannot
        #be detected
        listOfGrabbers, nbGrabbers = FliSdk.DetectGrabbers()
        if nbGrabbers == 0:
            raise FliError("No grabber detected, exit.")
        
        listOfCameras, nbCameras = FliSdk.DetectCameras()
        if nbCameras == 0:
            raise FliError("No camera detected, exit.")

        ok = FliSdk.SetCamera(camera_name)
        if not ok:
            raise FliError("Error while setting camera.")
    
    def _set_camera_mode(self):
        FliSdk.SetMode(FliSdk.Mode.Full)
        
    def _updateSDK(self):
        ok = FliSdk.Update()
        if not ok:
            raise FliError("Error while updating SDK.")
            
    def _check_if_is_cblue(self):
        check1 = FliSdk.IsCblueSfnc()
        check2 = FliSdk.IsCblueOne()
        check3 = FliSdk.IsSerialCamera()
        check4 = FliSdk.IsCred()
        
        if check4:
            raise FliError("Error: This is a CRED Camera. Only CBlueOne supported.")
        
        if check3:
            raise FliError("Error: This is a SerialCamera. Only CBlueOne supported.")
        
        if not check2:
            raise FliError("Error: Camera is not CBLUE.  CblueOne functions not available.")
        
        if not check1:
            raise FliError("Error: Camera is not CBLUE. CblueSfnc functions not available.")
            
    def set_fps(self, fps):
        self._status = FliSdk.CblueSfnc_setAcquisitionFrameRate(fps)
    
    def get_fps(self):
        self._status, fps = FliSdk.CblueSfnc_getAcquisitionFrameRate()
        return fps
    
    def get_max_fps(self):
        self._status, fps_max = FliSdk.CblueSfnc_getAcquisitionFrameRateMax()
        return fps_max
    
    def get_min_fps(self):
        self._status, fps_min = FliSdk.CblueSfnc_getAcquisitionFrameRateMin()
        return fps_min
    
    def set_exposure_time(self, texp_in_ms):
        texp_in_us = texp_in_ms * 1000
        self._status = FliSdk.CblueSfnc_setExposureTime(texp_in_us)
    
    def get_exposure_time(self):
        self._status, texp_in_us = FliSdk.CblueSfnc_getExposureTime()
        texp_in_ms = texp_in_us * 1e-3
        return texp_in_ms
    
    def get_max_exposure_time(self):
        self._status, texp_max_in_us = FliSdk.CblueSfnc_getExposureTimeMax()
        texp_max_in_ms = texp_max_in_us * 1e-3
        return texp_max_in_ms
    
    def get_min_exposure_time(self):
        self._status, texp_min_in_us = FliSdk.CblueSfnc_getExposureTimeMin()
        texp_min_in_ms = texp_min_in_us * 1e-3
        return texp_min_in_ms
    
    def get_gain(self):
        self._status, gain_in_dB = FliSdk.CblueSfnc_getGain()
        return gain_in_dB
    
    def set_gain(self, gain_in_dB):
        self._status = FliSdk.CblueSfnc_setGain(gain_in_dB)
        
    def get_max_gain(self):
        self._status, max_gain_in_dB = FliSdk.CblueSfnc_getGainMax()
        return max_gain_in_dB
    
    def get_min_gain(self):
        self._status, min_gain_in_dB = FliSdk.CblueSfnc_getGainMin()
        return min_gain_in_dB
    
    def get_convertion_efficiency(self):
        #eff = 0 -> low
        #eff = 1 -> high
        self._status, eff = FliSdk.Cblue1_getConversionEfficiency()
        return eff
    
    def set_convertion_efficiency(self, eff = 1):
        #eff = 0 -> low
        #eff = 1 -> high
        self._status = FliSdk.Cblue1_setConversionEfficiency(eff)
        
    def get_raw_image(self):
        raw_image= FliSdk.GetRawImageAsNumpyArray(-1)
        #raw_image[0] -> numpy array uint 16
        #raw_image[1], raw_image[2] -> image frame shape
        return raw_image[0]
    
    def get_frame_shape(self):
        self._status, height = FliSdk.CblueSfnc_getHeightMax()
        self._status, width = FliSdk.CblueSfnc_getWidthMax()
        return height, width
    
    def close_camera(self):
        FliSdk.Stop()
        FliSdk.Exit()
    
    def get_device_stastus(self):
        self._status, message = FliSdk.Cblue1_getDeviceStatus()
        val = FliSdk.IsStarted()
        print("Device Status:\t" + message)
        print("Grabber Started:\t"+ val)
    
    def get_device_info(self):
        self._status, model_name = FliSdk.CblueSfnc_getDeviceModelName()
        self._status, version_name = FliSdk.CblueSfnc_getDeviceVersion()
        self._status, serial_number = FliSdk.CblueSfnc_getDeviceSerialNumber()
        print("Device Model Name:\t" + model_name)
        print("Device Version Name:\t" + version_name)
        print("Device Serial Number:\t" + serial_number)
        
    def _check_last_opertion_status(self):
        return self._status
        