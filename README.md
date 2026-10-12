# PerformanceDegradation

A modular, automated infrastructure designed for the **study of Software Aging** across multiple hypervisors and virtualization environments (**VirtualBox, KVM, Xen, and LXD**).

## 📌 Table of Contents

* [Overview](#-overview)
* [Architecture and Features](#-architecture-and-features)
* [Repository Structure](#-repository-structure)
* [Prerequisites](#-prerequisites)
* [Installation & Setup](#-installation--setup)
* [How to Run Tests](#-how-to-run-tests)
  * [Command Line Options](#command-line-options)
  * [Usage Examples](#usage-examples)
* [Resource Monitoring](#-resource-monitoring)
* [Statistical Aging Analysis (`AgingAnalisys`)](#-statistical-aging-analysis-aginganalisys)
* [License & Credits](#-license--credits)

## 🎯 Overview

Long-running software systems suffer from progressive performance degradation (*Software Aging*) due to error state accumulation over time—such as memory leaks, RAM fragmentation, process table exhaustion (zombies), and disk I/O degradation.

This framework provides:

1. **Controlled Workload Injection**: Continuous I/O stress and dynamic virtual disk attach/detach cycles to accelerate aging in the hypervisor and host system.
2. **Low-Level Telemetry**: Real-time metric capture covering OS stats, internal hypervisor process tracking, and kernel memory fragmentation via **SystemTap**.
3. **Scientific Data Analysis**: Non-parametric trend analysis (**Mann-Kendall**), degradation rate calculation (**Theil-Sen Estimator**), and **Euclidean Aging Index** scoring.

## 🛠️ Architecture and Features

```
                             +-----------------------------------+
                             |       Main Script (run)           |
                             +-----------------+-----------------+
                                               |
         +--------------------+----------------+--------------------+--------------------+
         |                    |                                     |                    |
  +------v-------+     +------v-------+                      +------v-------+     +------v-------+
  |  VirtualBox  |     |     KVM      |                      |     Xen      |     |     LXD      |
  +--------------+     +--------------+                      +--------------+     +--------------+
         |                    |                                     |                    |
         +--------------------+----------------+--------------------+--------------------+
                                               |
                                    +----------v----------+
                                    | Workload Injector   |
                                    | (Disk Attach/Detach)|
                                    +----------+----------+
                                               |
                                    +----------v----------+
                                    | Monitoring Daemon   |
                                    | SystemTap + procfs  |
                                    +----------+----------+
                                               |
                                    +----------v----------+
                                    |  AgingAnalisys      |
                                    | (Theil-Sen / MK)    |
                                    +---------------------+
```

### Supported Hypervisors

* **VirtualBox (`vbox`)**: Managed via `VBoxManage` (tracks `VBoxHeadless`, `VBoxSVC`, `VBoxXPCOMIPCD`).
* **KVM / QEMU (`kvm`)**: Managed via `virsh` and `libvirt` (tracks `qemu-system-x86` and `libvirtd`).
* **Xen Hypervisor (`xen`)**: Managed via `xl` and `xen-tools` (tracks `oxenstored`, `xen-balloon`, `xenbus`, `xenconsoled`, `Domain-0`).
* **LXD Containers/VMs (`lxd`)**: Managed via `lxc` CLI and LVM pools.

## 📂 Repository Structure

```
├── run                                  # Master orchestrator script for experiments
├── setup/                               # Provisioning scripts per hypervisor
│   ├── virtualbox/                      # Setup and VM creation for VirtualBox
│   ├── kvm/                             # Dependencies, XML templates, and hooks for KVM
│   ├── xen/                             # Dom0, LVM, and DomU image setup for Xen
│   └── lxd/                             # LXD initialization and LVM pool scripts
├── virtualizer_functions/               # Abstraction layer for hypervisor commands
│   ├── vbox_functions.sh
│   ├── kvm_functions.sh
│   ├── xen_functions.sh
│   └── lxc_functions.sh
├── workloads/                           # Continuous stress and workload injection scripts
│   ├── vbox_workload.sh
│   ├── kvm_workload.sh
│   ├── xen_workload.sh
│   └── lxc_workload.sh
├── machine_resources_monitoring/        # Metrics collection daemon
│   ├── run                              # Main entrypoint to start monitoring workers
│   ├── general_dependencies.sh          # SystemTap compilation and Kernel symbol setup
│   ├── memory_fragmentation/            # SystemTap probes (mm_page_alloc_extfrag)
│   ├── processes/                       # Hypervisor-specific process monitors
│   └── general_resources/               # Global host monitors (CPU, RAM, Disk, Zombies)
├── AgingAnalisys/                       # Post-experiment statistical analysis package
│   ├── Main.py                          # Interactive CLI for plots and summaries
│   ├── theilsen.py                      # Theil-Sen slope calculation and aging index
│   ├── requirements.txt                 # Python dependencies (scipy, pymannkendall, matplotlib)
│   └── classes/                         # Data processing and IEEE-styled plot generators
└── utils/                               # Helper scripts for logging, errors, and formatting
```

## 📋 Prerequisites

* **Host Operating System**: Debian 12 (Bookworm).
* **Privileges**: `root` access or passwordless `sudo`.
* **System Packages**:
  * `bash`, `curl`, `wget`, `sysstat`, `gawk`, `make`, `gcc`, `git`.
  * `systemtap` compiled with matching kernel headers and debug symbols (`linux-image-$(uname -r)-dbg`).
* **Python**: Version 3.10+ (for data analysis).

## 📥 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-repository.git
cd your-repository
chmod +x run machine_resources_monitoring/run setup/*/*.sh
```

### 2. Install General Dependencies & Compile SystemTap

Run the global dependency installer (required for memory fragmentation probes):

```bash
sudo bash machine_resources_monitoring/general_dependencies.sh
```

### 3. Provision the Selected Hypervisor

Configure your target environment prior to running test benchmarks:

* **VirtualBox**:
  ```bash
  cd setup/virtualbox
  sudo bash dependencies.sh
  sudo bash setupVm.sh
  ```

* **KVM / Libvirt**:
  ```bash
  cd setup/kvm
  sudo bash dependencies.sh
  sudo bash setupVm.sh
  ```

* **Xen Hypervisor**:
  ```bash
  cd setup/xen
  sudo bash dependencies.sh
  sudo bash setupVm.sh
  ```

* **LXD**:
  ```bash
  cd setup/lxd
  sudo bash dependencies.sh
  sudo bash setupVm.sh
  ```

## 🚀 How to Run Tests

The primary orchestrator script `./run` handles:

1. Target hypervisor selection.
2. Initializing telemetry and monitoring daemons.
3. Launching workload injectors.
4. Triggering rejuvenation reboots at specified intervals.

### Command Line Options

```text
Usage: bash ./run [PARAMETERS]

Parameters:
  -t, --time <int>           Interval (in minutes or hours) between rejuvenation reboots.
  -f, --force                Use forced hardware reset (Reset hardware / xl destroy).
  -s, --soft                 Use graceful shutdown via ACPI power button event.
  -ssh, --ssh                Use direct SSH reboot command inside the guest VM.
  -e, --enable               Enable advanced workload lifecycle mode.
  -w=<val>, --work_cycle=<val> Define the number of workload stress cycles.
  -h, --help                 Display usage information.
```

> **Note**: The active hypervisor type is set via the `VIRTUALIZER_TYPE` variable at the top of the `run` script (`vbox`, `kvm`, `xen`, or `lxd`).

### Usage Examples

1. **Run experiment on VirtualBox with soft reboot every 120 minutes**:
   ```bash
   sudo ./run -t 120 -s
   ```

2. **Run experiment on KVM with SSH reboot every 60 minutes**:
   ```bash
   sudo ./run -t 60 -ssh
   ```

3. **Run experiment with advanced workload cycles enabled (-e) and 4 stress cycles**:
   ```bash
   sudo ./run -e -w=4 -s
   ```

## 📊 Resource Monitoring

During experiments, telemetry metrics are continuously logged to `machine_resources_monitoring/logs/`:

| Log File | Captured Metric |
| :--- | :--- |
| `cpu_monitoring_sumAllCores.csv` | CPU usage breakdown (%usr, %sys, %iowait, %soft) across cores |
| `machine_monitoring-cpu.csv` | Average overall host CPU utilization |
| `machine_monitoring-mem.csv` | Host memory stats (Used, Buffers, Cached, Free Swap) |
| `machine_monitoring-disk.csv` | Disk space usage on root partition (`/`) |
| `machine_monitoring-zombies.csv` | Host zombie process count |
| `fragmentation.csv` | Kernel memory allocation fragmentation (`mm_page_alloc_extfrag`) via SystemTap |
| `nginx_response.csv` | HTTP service response time (ms) from inside the guest |
| `*monitoring-*.csv` | Individual hypervisor process metrics (CPU, RAM, VSZ, RSS, Threads, Swap) |

## 📈 Statistical Aging Analysis (`AgingAnalisys`)

The **`AgingAnalisys`** module processes collected CSV logs after an experiment finishes to detect statistically significant aging trends.

### Setting Up the Python Environment

```bash
cd AgingAnalisys
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running the Analysis

1. **Interactive Plotting CLI**:
   ```bash
   python Main.py
   ```
   Select your target scenario (`1` for VirtualBox, `2` for KVM, `3` for Xen, `4` for LXD, etc.).

2. **Calculate Theil-Sen Slopes and Aging Index**:
   ```bash
   python theilsen.py
   ```

   Calculated metrics include:
   * **Theil-Sen Slope (**$\beta$**)**: Rate of resource degradation per day.
   * **Mann-Kendall Test**: Non-parametric trend significance ($p$-value, $z$-score).
   * **Euclidean Aging Index**:
     
     **Aging Index**ⱼ = (1/M) ∑ᵢ₌₁ᴹ Sₙₒᵣₘ,ᵢ⁽ʲ⁾

   * Automated generation of publication-ready figures (**IEEE/SciencePlots** formatting in `.svg` and `.pdf`).

## 📄 License & Credits

This project is open-source under the **MIT License**. See the [LICENSE](LICENSE) file for details.
