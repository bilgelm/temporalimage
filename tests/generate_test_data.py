def generate_fake4D():
    # generate fake 4D image

    import numpy as np
    import nibabel as nib
    import pandas as pd
    import os

    dims = (10,11,12,7)
    img_dat = np.zeros(dims)

    frameStart = np.array([0, 5, 10, 20, 30, 40, 50])
    frameEnd = np.append(frameStart[1:], frameStart[-1]+10)
    frameDuration = frameEnd - frameStart
    timingData = pd.DataFrame(data={'Duration of time frame (min)': frameDuration,
                                    'Elapsed time (min)': frameEnd})
    csvfilename = os.path.join(os.pardir,'data','timingData.csv')
    timingData.to_csv(csvfilename, index=False)

    R1 = 1.0
    DVR = 1.2
    k2 = 1.1

    Cref = np.array([0, 100, 200, 160, 140, 120, 120], dtype=np.float64)
    t = 0.5*(frameStart + frameEnd)
    Ct = R1 * Cref + np.convolve((k2 - R1*k2/DVR) * Cref, np.exp(-k2*t / DVR), 'same')

    for i in range(dims[0]):
        for j in range(dims[1]):
            for k in range(dims[2]):
                if k<(dims[2]//2):
                    img_dat[i,j,k,:] = Cref
                else:
                    img_dat[i,j,k,:] = Ct

    # save 4D image
    img = nib.Nifti1Image(img_dat, np.eye(4))
    imgfilename = os.path.join(os.pardir,'data','img.nii.gz')
    nib.save(img, imgfilename)

    return (imgfilename, csvfilename)
