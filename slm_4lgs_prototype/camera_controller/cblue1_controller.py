import numpy as np
from slm_4lgs_prototype.camera_controller import FliSdk

#TODO: check units in exposure time
#TODO: erase exit() use riseError
#TODO: implement acquisition functions
#TODO: add start and stop only for get image
# and verify all parameters can be changed
# if it works change set func
#TODO: add control on range of aviliable values on set cmdsf
#TODO: add documentation to functions
#TODO: implement test unit?

class FliError(Exception):
    """Exception raised for FirstLightImaging SDK error.
    
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
        self._update_parameters_limits()
        
    
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
        #FliSdk.Start()
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
        
    def _update_parameters_limits(self):
        
        self._fpsMax = self.get_max_fps()
        self._fpsMin = self.get_min_fps()
        self._tMax = self.get_max_exposure_time()
        self._tMin = self.get_min_exposure_time()
        self._gainMax = self.get_max_gain()
        self._gainMin = self.get_min_gain()
        self._convEffStat = self.get_convertion_efficiency()
        
            
    def set_fps(self, fps):
        if self._fpsMin <= fps <= self._fpsMax :
            FliSdk.Stop()
            self._status = FliSdk.CblueSfnc_setAcquisitionFrameRate(fps)
            self._update_parameters_limits()
            FliSdk.Start()
        else:
            raise FliError("Error! Input fps value out of limits: Min fps = %g"%self._fpsMin +", Max fps = %g"%self._fpsMax)
         
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
        if self._tMin <= texp_in_ms <= self._tMax:
            FliSdk.Stop()
            texp_in_us = texp_in_ms * 1000
            self._status = FliSdk.CblueSfnc_setExposureTime(texp_in_us)
            self._update_parameters_limits()
            FliSdk.Start()
        else:
            raise FliError("Error! Input exposure time out of limits: tMin = %g"%self._tMin +" ms, tMax = %g ms"%self._tMax)
    
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
        if self._gainMin <= gain_in_dB <= self._gainMax:
            FliSdk.Stop()
            self._status = FliSdk.CblueSfnc_setGain(gain_in_dB)
            FliSdk.Start()
        else:
            raise FliError("Error! Input gain out of limits: Min = %g dB"%self._gainMin + " Max = %g dB"%self._gainMax)
        
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
        if eff == 0 or eff == 1:
            FliSdk.Stop()
            #eff = 0 -> low
            #eff = 1 -> high
            self._status = FliSdk.Cblue1_setConversionEfficiency(eff)
            FliSdk.Start()
        else:
            raise FliError("Error!Wrong Input: set 0 or 1 for Low or High Convertion Gain, rispectively.")
        
    def get_raw_image(self):
        #FliSdk.Start()
        raw_image= FliSdk.GetRawImageAsNumpyArray(-1)
        #raw_image[0] -> numpy array uint 16
        #raw_image[1], raw_image[2] -> image frame shape
        #FliSdk.Stop()
        return raw_image[0]
    
    def get_cube_of_raw_images(self, Nframes):
        cube = []
        for idx in range(Nframes):
            cube.append(self.get_raw_image())
        return np.array(cube)
    
    def get_frame_shape(self):
        self._status, height = FliSdk.CblueSfnc_getHeightMax()
        self._status, width = FliSdk.CblueSfnc_getWidthMax()
        return height, width
    
    def get_pixel_pitch(self):
        self._status, pitch_y_in_um = FliSdk.CblueSfnc_getSensorPixelHeight()
        self._status, pitch_x_in_um = FliSdk.CblueSfnc_getSensorPixelWidth()
        if pitch_y_in_um == pitch_x_in_um :
            pixel_pitch = pitch_x_in_um
        else:
            pixel_pitch = (pitch_y_in_um, pitch_x_in_um)
            
        return pixel_pitch
    
    def close_camera(self):
        FliSdk.Stop()
        FliSdk.Exit()
    
    def show_device_status(self):
        self._status, message1 = FliSdk.Cblue1_getDeviceStatus()
        self._status, message2 = FliSdk.Cblue1_getDeviceStatusDetailed()
        val = FliSdk.IsStarted()
        print("Device Status:\t" + message1 + ',\t' + message2)
        print("Grabber Started:\t"+ str(val))
    
    def show_device_info(self):
        self._status, vendor_name = FliSdk.CblueSfnc_getDeviceVendorName()
        self._status, device_name = FliSdk.CblueSfnc_getDeviceManufacturerInfo()
        self._status, model_name = FliSdk.CblueSfnc_getDeviceModelName()
        self._status, version_name = FliSdk.CblueSfnc_getDeviceVersion()
        self._status, serial_number = FliSdk.CblueSfnc_getDeviceSerialNumber()
        print(vendor_name + ":\t" + device_name)
        print("Device Model Name:\t" + model_name)
        print("Device Version Name:\t" + version_name)
        print("Device Serial Number:\t" + serial_number)
        
    def _check_last_opertion_status(self):
        return self._status
        