# rapid_fts_spectra_qc
A script to produce an overview plot of a set of FTS spectra including the corresponding interferogram and header information.

**Requires** the script: [ftsreader.py](https://github.com/mbuschmann/ftsreader) to be present on the system

Intended usage:
  - Setup config.yaml to your specifics
  - Using qc_spectra_plots.py, create a set of images based on the spectra and slices selection specified
  - Check QC images and delete the bad ones with your favourite image viewer
  - Run whitelist_spectra.py to create two lists, containing stil available (whitelist) all deleted (blacklist) spectra names


