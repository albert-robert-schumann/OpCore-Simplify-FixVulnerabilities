<br/>
<div align="center">
  <h3 align="center">OpCore Simplify</h3>

  <p align="center">
    A specialized tool that streamlines <a href="https://github.com/acidanthera/OpenCorePkg">OpenCore</a> EFI creation by automating the essential setup process and providing standardized configurations. Designed to reduce manual effort while ensuring accuracy in your Hackintosh journey.
    <br />
    <br />
    <a href="#-features">Features</a> •
    <a href="#-how-to-use">How To Use</a> •
    <a href="#-contributing">Contributing</a> •
    <a href="#-license">License</a> •
    <a href="#-credits">Credits</a> •
  </p>

</div>

> [!CAUTION]
> **DO NOT RELY SOLELY ON AI/LLM SOURCES FOR BUILDING HACKINTOSHES**
> 
> They often provide incorrect information about Hackintosh, except Copilot https://copilot.microsoft.com/ which tends to give more acurrate info about hackintoshing. Always rely on official sources like the [Dortania Guide](https://dortania.github.io/OpenCore-Install-Guide/) and the Hackintosh community for accurate information. If you use AI (including Copilot) for Hackintoshing, always test it and if it fails, report it back to the AI chatbot so it can give instructions how to fix this. Here's a proof that actually AI can be right about Hackintoshing stuff:
> [AI answer from Copilot](https://youtu.be/v1abbD6tdBg)

> [!NOTE]
> While OpCore Simplify significantly reduces setup time, the Hackintosh journey still requires:
> - Understanding basic concepts from the [Dortania Guide](https://dortania.github.io/OpenCore-Install-Guide/)
> - Testing and troubleshooting during the installation process, especially if AI is being used for hackintoshing.
> - Patience and persistence in resolving any issues that arise
>
> Our tool doesn't eliminate these steps, but it ensures you start with a solid foundation.
>
## **Security & Maintenance**
> This project doesn't rely just on people to find vulnerabilities - it also uses CodeQL to increase accuracy and find vulnerabilities on time.

## **Vulnerabilities that have been successfully mitigated:**
> Outdated UA string - it was using an outdated Chrome 131 UA which exposed users to unpatched Google Chrome flaws that Google has already patched - or even worse - redirect to less secure servers. This is mitigated by using the latest UA for Safari - 26.1.

> WiFi passwords in wifi_extractor.py were stored in plain text. This could lead to attackers brute forcing the passowrd and gain unauthorized access to the internet - or worse - search the router for vulnerabilities to hijack the router and do whatever they want, including redirecting victims to malicious DNS servers. This is mitigated by encrypting the passwords and decrypt them only if needed.

> Previously, random MAC addresses generated in `add_null_ethernet_device()` were stored in plain text. This exposed sensitive identifiers that could be used by attackers to fingerprint or track devices. An attacker could obtain the MAC address to identify the device or other devices in the network to launch targeted cyberattacks against the device or even the entire network. This vulnerability is mitigated by obfuscating MAC addresses using SHA-256 hashing. 

## **Other changes and bug fixes:**
> The updater in the main branch downloads updates from this repository instead from the official one to avoid the vulnerabilities that have been patched before to be reintroduced.

> Adding init.py as a placeholder to improve OpCore-Simplify's reliability, it will apply this only for this project in the near future as the maintainer denied to apply this fix.

> Deleting the funding.yml file as it is only for the official repository, not this one.

## **Minimum OS requirements to even run OpCore-Simplify at all**
> The minimum OS requirements to run even OpCore-Simplify in the first place are:
> -	Windows 10 22H2 with all updates installed
> -	macOS
> -	Linux

## **Recommended OS versions:**
> -	Windows 11 24H2 or newer
> -	macOS 12.7.6 Monterey or newer
> -	a supported Linux distro with all updates installed

## ✨ **Features**

1. **Comprehensive Hardware and macOS Support**  
   Fully supports modern hardware. Use `Compatibility Checker` to check supported/unsupported devices and macOS version supported.

   | **Component**  | **Supported**                                                                                       |
   |----------------|-----------------------------------------------------------------------------------------------------|
   | **CPU**        | Intel: Nehalem and Westmere (1st Gen) (for first gens there are some caveats: on legacy BIOS systems with Nehalem or Westmere architectures, only Clover can run - I tested this) → Arrow Lake (15th Gen/Core Ultra Series 2) <br> AMD: Ryzen and Threadripper with [AMD Vanilla](https://github.com/AMD-OSX/AMD_Vanilla) |
   | **GPU**        | Intel iGPU: Iron Lake (1st Gen) → Ice Lake (10th Gen) <br> AMD APU: The entire Vega Raven ASIC family (Ryzen 1xxx → 5xxx, 7x30 series) <br> AMD dGPU: Navi 23, Navi 22, Navi 21 generations, and older series <br> NVIDIA: Kepler, Pascal, Maxwell, Fermi, Tesla generations |
   | **macOS**      | macOS High Sierra → macOS Tahoe |

2. **ACPI Patches and Kexts**  
   Automatically detects and adds ACPI patches and kexts based on hardware configuration.
   
   - Integrated with [SSDTTime](https://github.com/corpnewt/SSDTTime) for common patches (e.g., FakeEC, FixHPET, PLUG, RTCAWAC).
   - Includes custom patches:
      - Prevent kernel panics by directing the first CPU entry to an active CPU, disabling the UNC0 device, and creating a new RTC device for HEDT systems.
      - Disable unsupported or unused PCI devices, such as the GPU (using Optimus and Bumblebee methods or adding the disable-gpu property), Wi-Fi card, and NVMe storage controller.
      - Fix sleep state values in _PRW methods (GPRW, UPRW, HP special) to prevent immediate wake.
      - Add devices including ALS0, BUS0, MCHC, PMCR, PNLF, RMNE, IMEI, USBX, XOSI, along with a Surface Patch.
      - Enable ALSD and GPI0 devices.

3. **Automatic Updates**  
    Automatically checks for and updates OpenCorePkg and kexts from [Dortania Builds](https://dortania.github.io/builds/) and GitHub releases before each EFI build.
            
4. **EFI Configuration**  
   Apply additional customization based on both widely used sources and personal experience.

   - Spoof GPU IDs for certain AMD GPUs not recognized in macOS.
   - Use CpuTopologyRebuild kext for Intel CPUs with P-cores and E-cores to enhance performance.
   - Disable System Integrity Protection (SIP).
   - Spoof CPU IDs for Intel Pentium, Celeron, Core, and Xeon processors.
   - Add custom CPU names for AMD CPUs, as well as Intel Pentium, Celeron, Xeon, and Core lines from the Rocket Lake (11th) generation and newer.
   - Add a patch to allow booting macOS with unsupported SMBIOS.
   - Add NVRAM entries to bypass checking the internal Bluetooth controller.
   - Properly configure ResizeAppleGpuBars based on specific Resizable BAR information.
   - Allow flexible iGPU configuration between headless and driving a display when a supported discrete GPU is present.
   - Force Intel GPUs into VESA mode with HDMI and DVI connectors to simplify installation process.
   - Provide configuration required for using OpenCore Legacy Patcher.
   - Add built-in device property for network devices (fix 'Could not communicate with the server' when using iServices) and storage controllers (fix internal drives shown as external).
   - Prioritize SMBIOS optimized for both power management and performance.
   - Re-enable CPU power management on legacy Intel CPUs in macOS Ventura 13 and newer.
   - Apply WiFi profiles for itlwm kext to enable auto WiFi connections at boot time.

   and more...

5. **Easy Customization**  
   In addition to the default settings applied, users can easily make further customizations if desired.

   - Custom ACPI patches, kexts, and SMBIOS adjustments (**not recommended**).
   - Force load kexts on unsupported macOS versions.

## 🚀 **How To Use**
For a tutorial on how to use OpCore-Simplify, please go to https://lzhoang2801-github-io.translate.goog/gathering-files/opencore-efi?_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=en&_x_tr_pto=wapp .

## 🤝 **Contributing**

Contributions are **highly appreciated**! If you have ideas to improve this project, feel free to fork the repo and create a pull request, or open an issue with the "enhancement" tag.

Don't forget to ⭐ star the project! Thank you for your support! 🌟

## 📜 **License**

Distributed under the BSD 3-Clause License. See `LICENSE` for more information.

## 🙌 **Credits**

- [OpenCorePkg](https://github.com/acidanthera/OpenCorePkg) and [kexts](https://github.com/lzhoang2801/OpCore-Simplify/blob/main/Scripts/datasets/kext_data.py) – The backbone of this project.
- [SSDTTime](https://github.com/corpnewt/SSDTTime) – SSDT patching utilities.

## 📞 **Contact the owner of the official project**

**Hoang Hong Quan (the maintainer of the official project)**
> Facebook [@macforce2601](https://facebook.com/macforce2601) &nbsp;&middot;&nbsp;
> Telegram [@lzhoang2601](https://t.me/lzhoang2601) &nbsp;&middot;&nbsp;
> Email: lzhoang2601@gmail.com
