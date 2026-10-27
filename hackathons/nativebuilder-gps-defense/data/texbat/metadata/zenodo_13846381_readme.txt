# IQ Samples and Model Information

## Dataset Overview

This is a dataset of raw IQ GNSS measurements, with and without spoofing. Each scenario contains two sub-scenarios:
a clean data (with only GNSS PRNs from the shy satellites) and a spoofed data (with a mixture of shy PRNs and 
two spoofing PRNs) 
The raw IQ samples for the GNSS signal analysis were collected over two days: October 18 and October 19. 
These samples are stored in the /data/ directory. 

There is a subset of 1000 samples, randomly selected from the original dataset for each scenario to keep the
open-access data to a reasonable size.
Detailed  description of the setup will be available in our publication
J. Sankari, W. Wang, E.S. Lohan and M. Valkama, "Data-quality and cross-training aspects in GNSS RF 
fingerprinting with raw I/Q measurement data", to come.


## How to cite this Zenodo data
W. Wang, J. Sankari, E.S. Lohan, and M. Valkama, "Raw I/Q measurement data and software for GNSS RFF fingerprinting", 
open-access data set, 10.5281/zenodo.13846381, Sep 2024.
---

## File Naming Convention

Each file in the dataset follows a specific naming structure for easy identification:

- Files starting with 'S' are clean GNSS samples.
- Files starting with 'SS' are spoofed GNSS samples.

The naming convention is as follows:
<Prefix><Category>_<Sample Sequence>.mat

### File Prefixes:
- 'S': Clean GNSS samples
- 'SS': Spoofer samples

### Categories:
- 1: Baseline; sampling rate 25 MHz, 16-bit per real (I/Q) sample quantization (i.e., 32-bit complex quantization) 
- 2: Multipath; sampling rate 25 MHz, 16-bit per real (I/Q) sample quantization
- 3: High Sampling Rate; sampling rate 50 MHz, 16-bit per real (I/Q) sample quantization
- 4: Low Quantization; sampling rate 25 MHz, 8-bit per real (I/Q) sample quantization

### Sample Sequence: 
- This is a unique sequence number for each file, indicating its order in the original dataset.

#### Examples:
- data/oct_18/S1_50.mat: 50th Baseline clean GNSS sample recorded on Oct 18.
- data/oct_19/SS3_120.mat: 120th High-Sampling-Rate spoofer sample recorded on Oct 19.

---

## Pretrained Models

Pretrained models used for analysis and classification are located in the /models/ directory. 

---

## Model testing

Testing the pre-trained models can be done in demo.py file.

Note: until the publication of the journal paper describing the data in detail, the password
to unzip the data is available in request, by contacting elena-simona.lohan @  tuni.fi