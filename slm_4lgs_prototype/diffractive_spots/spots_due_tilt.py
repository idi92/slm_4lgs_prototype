import numpy as np 
from PIL import Image
from time import sleep
from astropy.io import fits
from scipy.signal import find_peaks
from slm_4lgs_prototype.utils import whittaker_smooth



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
    
    def acquire_measures(self, texp, Nframes, fps, gain = 1, dark = None):
        if dark is None:
            dark = 0
        self._fps = fps
        self._texp = texp
        self._Nframes = Nframes #of each applied tilt
        self._gain = gain
        self._cube_ima = []
        flat_cmd = np.zeros(self._Nact)
        
        self._cam.set_fps(fps)
        print("fps: %g"%self._cam.get_fps())
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
        hdr['FPS'] = self._fps
        
        
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
        fps = header['FPS']
        return cube_images, ptv_vector, texp, gain,fps, Nframes, wl
    
class SpotPositionAnalyser():
    
    FDIR = "D:\\06 SLM\\diffractive_spots_res\\"
    #FDIR = "C:\\Users\\labot\\Desktop\\misure_tesi_slm\\misure_temp\\"
    
    def __init__(self, file_name_data, dark = None):
        self._cube_images,  self._lambda_vector,\
         self._texp, self._gain, self._fps,\
          self._Nframes, self._wl = SpotPositionMeasurer.load_measures(self.FDIR + file_name_data)
        if dark is None:
            self._dark = 0
        else:
            self._dark = dark
            self._reduce_raw_cube()
        self._detect_spots()
            
    def get_cube_images(self):
        return self._cube_images
    
    def get_ptv_vector(self):
        return self._lambda_vector
    
    def get_exposure_time(self):
        return self._texp
    
    def get_gain(self):
        return self._gain
        
        
    def _reduce_raw_cube(self):
        self._N_of_tilts = len(self._lambda_vector)
        
        for idx in range(self._N_of_tilts):
            self._cube_images[idx] -= self._dark
    
    
    def show_image(self, ptv_in_lambda):
        import matplotlib.pyplot as plt
        
        idx = np.where(self._lambda_vector == ptv_in_lambda)[0][0]
        
        ptv = self._lambda_vector[idx]
        image = self._cube_images[idx]
        
        plt.subplots(2,1, sharex=True, sharey=True)
        plt.subplot(2,1,1)
        plt.title(r"$%g \lambda$"%ptv)
        plt.imshow(np.log(image), cmap='jet')
        plt.colorbar()
        plt.subplot(2,1,2)
        plt.imshow(image, cmap='jet')
        plt.colorbar()
        
    def show_profile(self, ptv_in_lambda):
        import matplotlib.pyplot as plt
        idx = np.where(self._lambda_vector == ptv_in_lambda)[0][0]
        ptv = self._lambda_vector[idx]
        image = self._cube_images[idx]
        
        
        #xc = np.where(image.mean(axis = 0) == (image.mean(axis = 0)).max())[0][0]
        Iprofile = image.sum(axis = 0)
        
        plt.figure()
        plt.clf()
        plt.title(r"$%g \lambda$"%ptv)
        plt.plot(np.log(Iprofile))
        
        plt.figure()
        plt.clf()
        plt.title(r"$%g \lambda$"%ptv)
        plt.plot(Iprofile)
        
    def _show_detected_orders(self, Iprofile, height = None, threshold = 0, distance = 80):
        import matplotlib.pyplot as plt
        #from slm_4lgs_prototype.utils import whittaker_smooth
        
        #Isoothed =  whittaker_smooth.whittaker_smooth(Iprofile, 10, 2)
        
        peaks_idx, dct_peaks = find_peaks(Iprofile, height, threshold, distance)
        Ipeaks = Iprofile[peaks_idx]
        
        plt.subplots(2,1,sharex=True)
        plt.subplot(2,1,1)
        #plt.title("h = %g"%height+" thsld = %g"%threshold+"dist = %g"%distance)
        plt.plot(np.log(Iprofile),'k-', label='Sum I')
        plt.plot(peaks_idx, np.log(Ipeaks),'ro', label = 'peaks/orders')
        plt.legend(loc='best')
        plt.subplot(2,1,2)
        plt.plot(Iprofile,'k-')
        plt.plot(peaks_idx, Ipeaks,'ro')
    
    def _detect_spots(self, height = None, threshold = 0, distance = 80):
        #TODO: Find a proper way to detect the spots 
        #height = None
        #threshold = 0
        #distance = 80 # FWHM in pixels
        self._Ispot_list = []
        self._spot_position_list = []
        
        for k in range(self._N_of_tilts):
            Iprofile = self._cube_images[k].mean(axis=0)
            Iprofile = whittaker_smooth.whittaker_smooth(Iprofile, 10, 2)
            peaks_idx, dct_peaks = find_peaks(Iprofile, height, threshold, distance)
            Ipeaks = Iprofile[peaks_idx]
            self._Ispot_list.append(Ipeaks)
            self._spot_position_list.append(peaks_idx)
    
    def show_detected_spots_vs_tilt(self):
        import matplotlib.pyplot as plt
        
        x0 = self._get_specular_refection_position()
        Imax, Imin = self._get_Intensity_min_max_when_flat()
        
        plt.figure()
        plt.clf()
        
        for idx in range(self._N_of_tilts):
            spot_pos = self._spot_position_list[idx] - x0
            ptv = self._lambda_vector[idx]
            Ispot = (self._Ispot_list[idx] -Imin)/(Imax - Imin)
            
            plt.scatter(ptv*np.ones(len(spot_pos)), spot_pos, c=np.log(Ispot), cmap='jet')
        
        plt.colorbar(label="Normalised Intensity", orientation="vertical") 
    
    def _get_specular_refection_position(self):
        idx = np.where(self._lambda_vector == 0)[0][0]
        origin = np.where(self._Ispot_list[idx] == self._Ispot_list[idx].max())
        return self._spot_position_list[idx][origin][0] 
    
    def _get_Intensity_min_max_when_flat(self):
        idx = np.where(self._lambda_vector == 0)[0][0]
        Imax = self._Ispot_list[idx].max()
        Imin = self._Ispot_list[idx].min()
        return Imax, Imin
        
    def get_tilted_position(self, ptv, f, D = 1100*9.2e-6 ):    
        return ptv*f/D

        