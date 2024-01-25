import numpy as np
from plico_dm import deformableMirror
from slm_4lgs_prototype.diffractive_spots.spots_due_tilt import SpotPositionMeasurer
from slm_4lgs_prototype.camera_controller.cblue1_controller import CBlueOneCamera


def main(lambda_vector, texp, gain, Nframes, file_name):
    #creating devices
    slm = deformableMirror('localhost', 7000)
    camera = CBlueOneCamera("CBLUE1:MatroxCXP-Dev_0")
    
    fdir = "D:\\06 SLM\\tilt_fullsize_bmp_lambda_v2\\"
    Nmaps = len(lambda_vector)
    wl = 589e-9
    spm = SpotPositionMeasurer(slm, camera, lambda_vector, fdir, wl)
    
    dark_fname = 'dark.fits'
    dark = 0
    
    spm.acquire_measures(texp, Nframes, gain, dark)
    fname_meas = "D:\\06 SLM\\diffractive_spots_res\\" + file_name
    spm.save_measures(fname_meas)
    
    #The camera MUST be closed
    camera.close_camera()
    
    #test_acquired = spm.get_acquired_measures()
    #test_loaded = SpotPositionMeasurer.load_measures(fname_meas)
    #check = (test_acquired == test_loaded[0]).all()
    #print(check)
    
    
    
def show_images(file_name):
    import matplotlib.pyplot as plt
    
    cube_images, ptv_vector, texp, gain, Nframes, wl = SpotPositionMeasurer.load_measures(file_name)
    
    Nima = cube_images.shape[0]
    
    for i in range(Nima):
        plt.figure()
        plt.clf()
        plt.imshow(np.log(cube_images[i]), cmap = 'jet')
        print(cube_images[i].max())
        plt.colorbar()
        plt.title("lambda = %g"%ptv_vector[i])
        plt.figure()
        plt.clf()
        plt.plot(cube_images[i].sum(axis=0))
        plt.title("lambda = %g"%ptv_vector[i])