import numpy as np 
from plico_dm import deformableMirror
from slm_4lgs_prototype.camera_controller.cblue1_controller import CBlueOneCamera
from astropy.io import fits
def create_devices():
    
    slm = deformableMirror('localhost', 7000)
    camera = CBlueOneCamera("CBLUE1:MatroxCXP-Dev_0")
    
    return slm, camera

class FlatSpotPositionMeasurer():
    
    def __init__(self):
        
        self._Nframes = 100
        self._texp = 99
        self._fps = 10
        self._gain = 0
        self._convEff = 1 #high
        self._wl = 589e-9 
    
    def acquire_measures(self):
        slm, cam = create_devices()
        
        cam.set_fps(self._fps)
        cam.set_exposure_time(self._texp)
        #cam.set_convertion_efficiency(self._convEff)
        cam.set_gain(self._gain)
        
        self._raw_ima = cam.get_cube_of_raw_images(self._Nframes)
        cam.close_camera()
        
    def save_data(self, fname):
        hdr = fits.Header()
        hdr['T_EX_MS'] = self._texp
        hdr['N_AV_FR'] = self._Nframes
        hdr['G_DB'] = self._gain
        hdr['WL_M'] = self._wl
        hdr['FPS'] = self._fps
        fits.writeto(fname, self._raw_ima, hdr, overwrite=True)
    
    @staticmethod
    def load_data(fname):
        header = fits.getheader(fname)
        hduList = fits.open(fname)
        
        cube_images = hduList[0].data 
        
        Nframes = header['N_AV_FR']
        texp = header['T_EX_MS']
        gain = header['G_DB']
        wl = header['WL_M']
        fps = header['FPS']
        return cube_images, texp, gain,fps, Nframes, wl