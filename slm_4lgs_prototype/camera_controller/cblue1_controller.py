import numpy as np
from slm_4lgs_prototype.camera_controller import FliSdk

#TODO: check units in exposure time
#TODO: erase exit() use riseError
#TODO: implement acquisition functions
#TODO: add documentation to functions
#TODO: implement test unit?

def detect_cameras():
    FliSdk.Init()
    #need to detect grabbers first otherwise camera cannot
    #be detected
    print("Detection of grabbers...")
    listOfGrabbers, nbGrabbers = FliSdk.DetectGrabbers()

    if nbGrabbers == 0:
        print("No grabber detected, exit.")
        exit()

        print("Done.")
        print("List of detected grabber(s):")

    for i in range(nbGrabbers):
        print("- " + listOfGrabbers[i])
        
    print("Detection of cameras...")
    listOfCameras, nbCameras = FliSdk.DetectCameras()
    if nbCameras == 0:
        print("No camera detected, exit.")
        exit()

    print("Done.")
    print("List of detected camera(s):")
    
    for i in range(nbCameras):
        print("- " + str(i) + " -> " + listOfCameras[i])

    FliSdk.Exit()
    
class CBlueOneCamera():
    
    def __init__(self, camera_name = 'CBLUE1:MatroxCXP-Dev_0'):
        self._cname =  camera_name
        FliSdk.Init()
        self._detect_and_set_camera(camera_name)
        self._set_camera_mode()
        self._updateSDK()
        self._check_if_is_cblue()
        self._status = None
    
    def _detect_and_set_camera(self, camera_name):
        #need to detect grabbers first otherwise camera cannot
        #be detected
        listOfGrabbers, nbGrabbers = FliSdk.DetectGrabbers()
        listOfCameras, nbCameras = FliSdk.DetectCameras()
        if nbCameras == 0:
            print("No camera detected, exit.")
            exit()
        #cameraIndex = 0
        ok = FliSdk.SetCamera(camera_name)
        if not ok:
            print("Error while setting camera.")
            exit()
    
    def _set_camera_mode(self):
        FliSdk.SetMode(FliSdk.Mode.Full)
        
    def _updateSDK(self):
        ok = FliSdk.Update()
        if not ok:
            print("Error while updating SDK.")
            exit()
            
    def _check_if_is_cblue(self):
        check1 = FliSdk.IsCblueSfnc()
        check2 = FliSdk.IsCblueOne()
        if not check1:
            print("Error: Camera is not CBLUE.")
            exit()
        if not check2:
            print("Error: Camera is not CBLUE.")
            exit()
            
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
        self._status = FliSdk.CblueSfnc_setExposureTime(texp_in_ms)
    
    def get_exposure_time(self):
        self._status, texp = FliSdk.CblueSfnc_getExposureTime()
        texp_in_ms = texp #/1000
        return texp_in_ms
    
    def get_max_exposure_time(self):
        self._status, texp_max = FliSdk.CblueSfnc_getExposureTimeMax()
        return texp_max
    
    def get_min_exposure_time(self):
        self._status, texp_min = FliSdk.CblueSfnc_getExposureTimeMin()
        return texp_min
    
    def close_camera(self):
        FliSdk.Stop()
        FliSdk.Exit()
    
    def _check_last_opertion_status(self):
        return self._status
        