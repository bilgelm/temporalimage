def generate_fake4D():
    # generate fake 4D image

    import numpy as np
    import nibabel as nib
    import pandas as pd
    import os

    from temporalimage import Quantity

    dims = (10,11,12,7)
    img_dat = np.zeros(dims)

    frameStart = Quantity(np.array([0,  5, 10, 20, 30, 40, 50]), 'minute')
    frameEnd = Quantity(np.array([5, 10, 20, 30, 40, 50, 60]), 'minute')
    frameDuration = frameEnd - frameStart
    timingData_min = pd.DataFrame(data={
                        'Duration of time frame (min)': frameDuration.magnitude,
                        'Elapsed time (min)': frameEnd.magnitude})
    csvfilename_min = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                   os.pardir,'data',
                                                   'timingData_min.csv'))
    timingData_min.to_csv(csvfilename_min, index=False)

    timingData_s = pd.DataFrame(data={
                'Duration of time frame (s)': frameDuration.to('sec').magnitude,
                'Elapsed time (s)': frameEnd.to('sec').magnitude})
    csvfilename_s = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 os.pardir,'data',
                                                 'timingData_s.csv'))
    timingData_s.to_csv(csvfilename_s, index=False)

    siffilename = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir,'data','timingData.sif'))
    timingData_sif = pd.DataFrame(data={
        'Start of time frame (s)': [' '] + (frameStart.to('sec').magnitude).tolist(),
        'Elapsed time (s)': [' '] + (frameEnd.to('sec').magnitude).tolist()})
    timingData_sif.to_csv(siffilename, header=None, index=None, sep=' ',
                          columns=['Start of time frame (s)','Elapsed time (s)'])

    R1 = 1.0
    DVR = 1.2
    k2 = 1.1 # 1/minute

    Cref = np.array([0, 100, 200, 160, 140, 120, 120], dtype=np.float64)
    t = 0.5*(frameStart + frameEnd).magnitude
    Ct = R1 * Cref + \
         np.convolve((k2 - R1*k2/DVR) * Cref, np.exp(-k2*t / DVR), 'same')

    for i in range(dims[0]):
        for j in range(dims[1]):
            for k in range(dims[2]):
                if k<(dims[2]//2):
                    img_dat[i,j,k,:] = Cref
                else:
                    img_dat[i,j,k,:] = Ct



    # save 4D image
    img = nib.Nifti1Image(img_dat, np.eye(4))
    imgfilename = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir,'data','img.nii.gz'))
    nib.save(img, imgfilename)

    return (imgfilename, csvfilename_min, csvfilename_s, siffilename)
