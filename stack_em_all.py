import numpy as np
import matplotlib.pyplot as plt
import pyFAI, fabio
import os
from nexusformat.nexus import *
from spec2nexus.spec import SpecDataFile
import sys
import inspect

# command line inputs: spec file name, sample, scan number, temperature
specfile = sys.argv[1]
calibfile = sys.argv[2]
maskfile = sys.argv[3]
sample_name = sys.argv[4]
scan_num = int(sys.argv[5])
temperature = int(sys.argv[6])
temperdir = sys.argv[6]
raw_dir = sys.argv[7]
outpath = sys.argv[8]

# load the geometry calibration for the instrument and bad-pixel-mask for the detector
ai = pyFAI.load(calibfile)
imgmask = fabio.open(maskfile)

# Where to write the stacks
outfile = "stack1.nxs"

if not os.path.exists(outpath):
    os.makedirs(outpath)

while os.path.exists(outpath + outfile):
    stacknum = int(outfile[-5:-4])
    outfile = outfile[:-5] + str(stacknum + 1) + ".nxs"

print("Will save stacked frames to " + outpath + outfile)

## Read in spec file data (psic/temp/ic)
spexus = SpecDataFile(specfile)
scanexus = spexus.getScan(scan_num)

## Where are those detector images?
scan_dir = raw_dir
print('Scan directory: ' + scan_dir)

## Grab all the angles / info needed from the spec file
phi = np.asarray(scanexus.data['phi'])
chi = float(scanexus.positioner['chi'])
mu = float(scanexus.positioner['mu'])
eta = float(scanexus.positioner['th'])
print('chi=' + str(chi), 'eta=' + str(eta), 'mu=' + str(mu))
print('positioner=' + str(scanexus.positioner))

# Can either take the wavelength from spec or calibration, spec is more robust. Note units are different
if scanexus.diffractometer.wavelength:
    wl = float(scanexus.diffractometer.wavelength)
else:
    with open(specfile, "r") as file:
        for line in file:
            if line.startswith("#G4"):
                parts = line.split()
                wl = float(parts[4])  # The wavelength is the 5th element (index 4)
                break  # Stop reading after finding the line
    # Add method for getting new wavelength format
print("Spec wavelength=", wl)
Energy = 12.3984 / wl
print("Spec Energy=", Energy)
wl = ai.wavelength * 1e10
print("pyFAI wavelength=", wl)
Energy = 12.3984 / wl
print("pyFAI Energy=", Energy)

n = np.size(phi)

# signal to normalize frames - ion chamber 2 during flyscan- flyc2
icnorm = np.asarray(scanexus.data['ic2'])
# rescale icnorm to approx signal per one second, to keep units ~ photons / sec. Change for different instrument setups.
icnorm = icnorm / (1.25e4)

print('icnorm=' + str(icnorm))

# read in geometry info from pyFAI
pol = ai.twoThetaArray() * np.cos(ai.chiArray() + (np.pi * 0.5))
az = -ai.twoThetaArray() * np.sin(ai.chiArray() + (np.pi * 0.5))
psi = ai.chiArray()
qmag = ai.qArray()

solidangle = ai.solidAngleArray()

#####

# load the first data frame, define arrays
imgfiles = [filename for filename in sorted(os.listdir(scan_dir)) if filename.endswith('cbf')]

print('imgfiles size=' + str(np.size(imgfiles)))
if (np.size(imgfiles) == n):
    print("Size matches - good")

print("Loading raw frames...")

imgcurr = fabio.open(scan_dir + imgfiles[0])
imgshape = np.shape(imgcurr.data)

##Define the nexus fields and object to be created

phi = NXfield(phi, name='phi')
xpixel = NXfield(range(0, imgshape[0]), name='x')
ypixel = NXfield(range(0, imgshape[1]), name='y')
pol = NXfield(pol, name='pol')
az = NXfield(az, name='az')
qmag = NXfield(qmag, name='qmag')
psi = NXfield(psi, name='psi')
icnorm = NXfield(icnorm, name='icnorm')
solidangle = NXfield(solidangle, name='solidangle')

W = NXroot()

W.psic = NXentry()  # psi-circle angles from spec
W.psic.eta = eta
W.psic.mu = mu
W.psic.chi = chi

W.spec = NXentry()  # preserve link to spec scan for metadata
W.spec.scannum = NXfield(scanexus.scanNum, name="spec_scan_number")
W.spec.scancom = NXfield(scanexus.scanCmd, name="spec_command")
W.spec.filename = NXfield(raw_dir + specfile, name="spec_file")

W.meta = NXentry()  # other processing and source metadata
W.meta.calibrationfile = NXfield(calibfile, name="calibrationFile")
W.meta.maskfile = NXfield(maskfile, name="maskFile")
W.meta.imagespath = NXfield(scan_dir, name="detectorImagesPath")
sourcepy = os.getcwd() + "/" + inspect.stack()[0][1]
W.meta.sourceCode = NXfield(sourcepy, name="pythonSource")

W.sample = NXentry()  # sample info, read from spec / meta / command line
W.sample.compound = NXfield(specfile, name="compound")
W.sample.id = NXfield(sample_name, name="sampleid")
W.sample.temperature = NXfield(temperature, name="temperature")

W.geo = NXentry()  # area detector geometry
W.geo.pol = pol
W.geo.az = az
W.geo.psi = psi
W.geo.qmag = qmag
W.geo.wl = NXfield(wl, name='wavelength')

W.energy = NXentry()  # area detector geometry
W.energy.energy = NXfield(Energy, name='energy')

W.norm = NXentry()
W.norm.icnorm = icnorm
W.norm.solidangle = solidangle

W.powder = NXentry()  # mimic powder pattern

W.data = NXentry()  # data from the area detector

# W.mask = NXentry()
# W.mask.data = imgmask.data
# Read in the frames from the area detector

imgstack = np.repeat(imgcurr.data[:, :, np.newaxis], n, axis=2)

for i in range(0, n):  # change back to n
    imgcurrent = fabio.open(scan_dir + imgfiles[i]).data  # open file
    imgcurrent[imgmask.data > 0.5] = -2
    imgstack[:, :, i] = imgcurrent  # put the masked image into the stack
    print('T=' + str(temperature) + ' ' + str(imgfiles[i]) + ' to ' + outfile)

counts = NXfield(imgstack, name='counts', long_name='counts')
W.data = NXdata(counts, (xpixel, ypixel, phi))

stacked = W.data.sum(2)
print(stacked.tree)
powderized = ai.integrate1d(stacked.counts, 8000, unit='q_A^-1', mask=imgmask.data)
powderized = ai.integrate1d(stacked.counts, 8000, unit='q_A^-1', mask=imgmask.data, azimuth_range=(-155, -25))

# plt.figure()
# plt.plot(powderized[0],powderized[1],label="XPD")
# plt.show()

powQ = NXfield(powderized[0], name='Q_powder')
powI = NXfield(powderized[1], name='I_powder')

W.powder = NXdata(powI, (powQ))
# W.powder.save(outpath+"testpowder.nxs")

print(W.tree)
print("Saving stacked frames to " + outpath + outfile)

W.save(outpath + outfile)
