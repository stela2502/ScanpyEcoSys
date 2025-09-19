# ScanpyEcoSys

The **ScanpyEcoSys** Apptainer image provides a ready-to-use, full **Scanpy ecosystem** for single-cell analysis, including a wide selection of popular Python tools for transcriptomics, spatial data, trajectory inference, and more.

If you notice a useful package missing, please [open an issue](https://github.com/stela2502/ScanpyEcoSys/issues) or submit a pull request.

---

## Using on COSMOS-SENS

This container is published as a COSMOS-SENS module.

To make it available in your environment:

```bash
module use /scale/gr01/shared/common/modules
module load ScanpyEcoSys/1.5
```

> **Tip:** Any future versions will follow the naming convention  
> `ScanpyEcoSys/<version>` (currently **1.5**).

---

## Included Software Highlights

The image bundles most of the Scanpy single-cell ecosystem:

* **Core analysis**: `scanpy`, `muon`, `scvi-tools`
* **Specialized tools**: `scirpy`, `squidpy`, `scVelo`, `velocyto`
* **Data integration & metrics**: `harmony`, `scanorama`, `pymde`, `scib_metrics`, `spatialdata`
* **Manifold/embedding algorithms**: `phate`, `trimap`, `sam`, `phenograph`
* **Visualization & utilities**: `seaborn`, `jupyterlab`, `papermill`, `nbconvert`, `ipywidgets`
* **Monitoring**: `psutil`, `pynvml`, `autotime`
* **Special environment**: `cellphonedb` with a dedicated Micromamba env

---

## Definition File (for reference)

The [current Apptainer/Singularity recipe](./ScanpyEcoSys.def) is part of this Github repo.

---

## Build the Apptainer Image

You can build the container yourself if you have:

* **git**
* **make**
* **Apptainer/Singularity**
* **super-user (root) privileges** – Apptainer needs these for building images

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/stela2502/ScanpyEcoSys.git
cd ScanpyEcoSys
```

### 2️⃣ Build
The provided `Makefile` handles both a sandbox (writable directory) and a final `.sif` image.

```bash
sudo make restart build
```

* `make restart` – creates the sanbox from the definition file  
* `make build`   – creates the `.sif` image from `ScanpyEcoSys.def`

After completion you will have:

* `ScanpyEcoSys_v<version>.sif` – the Apptainer image  
* a `sandbox/` directory – a writable build directory

### 3️⃣ Test the Image
```bash
apptainer run ScanpyEcoSys.sif
```

> **Tip:** If you don’t have root access, you can only run an already-built `.sif` image.  
> Building requires root because Apptainer needs to set file ownership and namespaces.

## Getting Started

After building the image:
```bash
apptainer run ScanpyEcoSys_1.5.sif
```

This will start a JupyterLab server on port `9734` listening on all interfaces (`0.0.0.0`).
---

## Contributing

Pull requests and issues are welcome!  
Please describe any additional tools you would like included.

---

© 2025 ScanpyEcoSys Maintainers
