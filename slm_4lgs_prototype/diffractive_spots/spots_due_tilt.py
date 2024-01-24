import numpy as np 
#import matplotlib.pyplot as plt
from PIL import Image
from time import sleep
from astropy.io import fits



#im = Image.open(self._wfc_filename)
#wfc = np.array(im, dtype=np.uint8)
#☺wfc = np.reshape(wfc, (self.getNumberOfActuators(),))


class SpotPositionMeasurer():
    
    def __init__(self, slm, camera, lamda_vector = np.arange(0, 560, 10), fdir = "D:\\06 SLM\\tilt_fullsize_bmp_lambda_v2\\", wl = 589e-9):
        self._slm = slm
        self._cam = camera
        self._fdir = fdir
        self._Ntilt = len(lamda_vector)
        self._Nact = slm.get_number_of_actuators()
        self._wl = wl
        
        self._ptv_vector = lamda_vector
        self._load_bmp_tilt()
    
    def _load_bmp_tilt(self):
        
        self._tilt_matrix = np.zeros((self._Ntilt, self._Nact))
        
        for idx in range(self._Ntilt):
            
            if self._ptv_vector[idx] == 0:
                fmap = '0000.bmp'
            else:
                if  self._ptv_vector[idx] <100:
                    fmap ='00'+str(self._ptv_vector[idx])+".bmp"
                else:
                        fmap ='0'+str(self._ptv_vector[idx])+".bmp"
                
            self._fname = self._fdir + fmap
            #print(self._fname)
            bmp_image = Image.open(self._fname)
            gray_map = np.array(bmp_image, dtype=np.uint8)
            lamda_map = self._wl/256 * gray_map
            lambda_vector = np.reshape(lamda_map, (self._Nact))
            self._tilt_matrix[idx] = lambda_vector
            
    def _clean_raw_image(self, raw_image, dark):
        return raw_image - dark
    
    def _clean_raw_cube(self, raw_cube, dark):
        Nframes = raw_cube.shape[0]
        clean_cube = np.zeros(raw_cube.shape)
        for n in range(Nframes):
            raw_image = raw_cube[n]
            clean_cube[n] = self._clean_raw_image(raw_image, dark)
        return clean_cube
    
    def acquire_measures(self, texp, Nframes, gain = 1, dark = None):
        if dark is None:
            dark = 0
        self._texp = texp
        self._Nframes = Nframes #of each applied tilt
        self._gain = gain
        self._cube_ima = []
        flat_cmd = np.zeros(self._Nact)
        
        self._cam.set_exposure_time(texp)
        print("texp:%g"%self._cam.get_exposure_time())
        self._cam.set_gain(gain)
        print("gain: %g"%self._cam.get_gain())
        
        for idx in range(self._Ntilt):
            cmd = self._tilt_matrix[idx]
            self._slm.set_shape(cmd)
            sleep(0.01) #seconds
            raw_cube = self._cam.get_cube_of_raw_images(self._Nframes)
            clean_cube = self._clean_raw_cube(raw_cube, dark)
            self._cube_ima.append(np.median(clean_cube, axis=0))
        self._cube_ima = np.array(self._cube_ima)
        self._slm.set_shape(flat_cmd)
        
    def get_acquired_measures(self):
        return self._cube_ima
    
    def save_measures(self, fname):
        hdr = fits.Header()
        hdr['T_EX_MS'] = self._texp
        hdr['N_AV_FR'] = self._Nframes
        hdr['G_DB'] = self._gain
        hdr['WL_M'] = self._wl
        
        
        fits.writeto(fname, self._cube_ima, hdr, overwrite=True)
        fits.append(fname, self._ptv_vector)
        
    @staticmethod
    def load_measures(fname):
        header = fits.getheader(fname)
        hduList = fits.open(fname)
        
        cube_images = hduList[0].data 
        ptv_vector = hduList[1].data
        
        Nframes = header['N_AV_FR']
        texp = header['T_EX_MS']
        gain = header['G_DB']
        wl = header['WL_M']
        return cube_images, ptv_vector, texp, gain, Nframes, wl