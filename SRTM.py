def SRTM_Zhou2003(timeSeriesImgFile, refRegionMaskFile, frameTimingCsvFile,
                  startTime, endTime, proportiontocut=0, fwhm):
    import numpy.matlib as mat
    from scipy import stats, ndimage, integrate, linalg
    import math

    # load 4D image
    img = TemporalImage(timeSeriesImgFile, frameTimingCsvFile,
                        startTime, endTime)
    img_dat = img.get_data()
    t = img.get_midTime()
    delta = img.get_frameDuration()


    [rows,cols,slices,comps] = img_dat.shape
    voxSize = img.header.get_zooms()[0:3]
    sigma_mm = fwhm / (2*math.sqrt(2*math.log(2)))
    sigma = [sigma_mm / v for v in voxSize]

    mip = np.amax(img_dat,axis=3)
    mask = mip>=1 # don't process voxels that don't have at least one count
    numVox = np.sum(mask)

    # load reference region mask
    ref = nib.load(refRegionMaskFile)
    ref_dat = ref.get_data().astype(bool)

    # make sure that the reference region mask is in alignment with PET
    Cref = np.zeros(comps) # Time activity curve (TAC) of reference region
    Ctfilt = np.zeros(img_dat.shape) # Spatially smoothed image
    for l in range(comps):
        timeframe = img_dat[:,:,:,l]
        tmp = timeframe[ref_dat]
        Cref[l] = stats.trim_mean(tmp[np.isfinite(tmp)], proportiontocut)
        Ctfilt[:,:,:,l] = ndimage.gaussian_filter(img_dat[:,:,:,l],sigma=sigma,order=0)

    # Integrals etc.
    # Numerical integration of TAC
    intCref = integrate.cumtrapz(Cref,t,initial=0)
    # account for ignored frames at the beginning:
    #   assume signal increased linearly with time until first included frame,
    #   starting at 0 at time 0.
    #   So we compute the are of this right triangle and add to the trapezoid integral
    intCref = intCref + t[0] * Cref[0] / 2

    # Numerical integration of Ct
    intCt_ = integrate.cumtrapz(img_dat,t,axis=3,initial=0)
    # account for ignored frames at the beginning:
    #   assume signal increased linearly with time until first included frame,
    #   starting at 0 at time 0.
    #   So we compute the are of this right triangle and add to the trapezoid integral
    intCt_ = intCt_ + t[0] * img_dat[:,:,:,:1] / 2

    # STEP 1: weighted linear regression (wlr) [Zhou 2003 p. 978]
    m = 3
    W = mat.diag(delta)
    B0_wlr = np.zeros((rows,cols,slices,m))
    var_B0_wlr = np.zeros((rows,cols,slices))
    B1_wlr = np.zeros((rows,cols,slices,m))
    var_B1_wlr = np.zeros((rows,cols,slices))

    # This for-loop will be more efficient if iteration is performed only
    # over voxels within mask
    for i in range(rows):
        for j in range(cols):
            for k in range(slices):
                if mask[i,j,k]:
                    Ct = Ctfilt[i,j,k,:]
                    intCt = intCt_[i,j,k,:]

                    # Compute DVR using eq. 9
                    X = np.mat(np.column_stack((intCref, Cref, -Ct)))
                    y = np.mat(intCt).T
                    b0 = linalg.solve(X.T * W * X, X.T * W * y)
                    residual = y - X * b0
                    var_b0 = residual.T * W * residual / (comps-m)
                    B0_wlr[i,j,k,:] = b0.T
                    var_B0_wlr[i,j,k] = var_b0

                    # Compute R1 using eq. 8
                    XR1 = np.mat(np.column_stack((Cref, intCref, -intCt)))
                    yR1 = np.mat(Ct).T
                    b1 = linalg.solve(XR1.T * W * XR1, XR1.T * W * yR1)
                    residual = yR1 - XR1 * b1
                    var_b1 = residual.T * W * residual / (comps-m)
                    B1_wlr[i,j,k,:] = b1.T
                    var_B1_wlr[i,j,k] = var_b1

    dvr_wlr = B0_wlr[:,:,:,0]
    r1_wlr = B1_wlr[:,:,:,0]

    # Preparation for Step 2
    # Apply spatially smooth initial parameter estimates
    B1_sc = np.zeros(B1_wlr.shape)
    for l in range(m):
        B1_sc[:,:,:,l] = ndimage.gaussian_filter(B1_wlr[:,:,:,l],sigma=sigma,order=0)

    H1 = np.zeros(B1_wlr.shape)
    for i in range(rows):
        for j in range(cols):
            for k in range(slices):
                if mask[i,j,k]:
                    H1[i,j,k,:] = m * var_B1_wlr[i,j,k] / np.square(B1_wlr[i,j,k,:] - B1_sc[i,j,k,:])

    # Apply spatial smoothing to H0 and H1
    HH1 = np.zeros(H1.shape)
    for l in range(m):
        HH1[:,:,:,l] = ndimage.gaussian_filter(H1[:,:,:,l],sigma=sigma,order=0)

    # STEP 2: ridge regression [Zhou 2003 p. 978]
    B1_lrsc = np.zeros((rows,cols,slices,m))

    # This for-loop will be more efficient if iteration is performed only
    # over voxels within mask
    for i in range(rows):
        for j in range(cols):
            for k in range(slices):
                if mask[i,j,k]:
                    intCt = intCt_[i,j,k,:]

                    XR1 = np.mat(np.column_stack((Cref, intCref, -intCt)))
                    yR1 = np.mat(Ct).T
                    b1 = linalg.solve(XR1.T * W * XR1 + mat.diag(HH1[i,j,k,:]),
                                      XR1.T * W * yR1 + mat.diag(HH1[i,j,k,:]) * np.mat(B1_sc[i,j,k,:]).T)
                    B1_lrsc[i,j,k,:] = b1.T

    r1_lrsc = B1_lrsc[:,:,:,0]
