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

## **Security & Maintenance**
> This project doesn't rely just on people to find vulnerabilities - it also uses CodeQL to increase accuracy and find vulnerabilities on time.

## **Vulnerabilities that have been successfully mitigated:**
> Outdated UA string - it was using an outdated Chrome 131 UA which exposed users to unpatched Google Chrome flaws that Google has already patched - or even worse - redirect to less secure servers. This is mitigated by using the latest UA for Safari - 26.1.

> WiFi passwords in wifi_extractor.py were stored in plain text. This could lead to attackers brute forcing the passowrd and gain unauthorized access to the internet - or worse - search the router for vulnerabilities to hijack the router and do whatever they want, including redirecting victims to malicious DNS servers. This is mitigated by encrypting the passwords and decrypt them only if needed.

> Previously, random MAC addresses generated in `add_null_ethernet_device()` were stored in plain text. This exposed sensitive identifiers that could be used by attackers to fingerprint or track devices. An attacker could obtain the MAC address to identify the device or other devices in the network to launch targeted cyberattacks against the device or even the entire network. This vulnerability is mitigated by obfuscating MAC addresses using SHA-256 hashing.

> An invalid user agent in dsdt.py of Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 could lead to servers treating the project as bot or worse - redirect downloads to legacy servers. This is mitigated by updating the user agent to a valid and latest Safari user agent.

## **Other changes and bug fixes:**
> The updater in the main branch downloads updates from this repository instead from the official one to avoid the vulnerabilities that have been patched before to be reintroduced.

> Adding init.py as a placeholder to improve OpCore-Simplify's reliability, it will apply this only for this project in the near future as the maintainer denied to apply this fix.

> Deleting the funding.yml file as it is only for the official repository, not this one.

> The updater in the release-preview branch was the last one that still pulled updates from the official repository. Now even that one is pulling updates from this repository instead.

> Disabling TPM via SSDTs if for example the motherboard doesn't offer disabling TPM at all (currently in beta)

### **What is Hackintosh?**
> A Hackintosh is macOS running on non‑Apple hardware.

**Early era (2006–2012):**  
> Running Mac OS X on PCs required modifying the operating system’s core kernel image.  
> Updates often broke compatibility, sometimes bricking entire Hackintosh setups.  
> This was true “hacking” of the OS image — builders literally exploited vulnerabilities in Mac OS X to force it to run on unsupported hardware.

**Modern era (2012–present):**  
> With Clover and OpenCore's existance, hacking the kernel is no longer required.  
> Users simply download the official macOS image, flash it to a USB drive, and build an EFI configuration.  
> The EFI layer handles hardware compatibility, making Hackintosh setups more stable and reproducible.
> Today, installing macOS updates is safe, provided OpenCore is updated before each system update.

## **What is a boot manager?**
> A boot manager is a program that controls how your computer starts up, deciding which operating system or boot option to load. It sits between the firmware (BIOS/UEFI) and the operating system, and is especially important when multiple operating systems are installed.

## **What is OpenCore?**
> OpenCore is a boot manager that allows booting macOS on non-Apple hardware. macOS's built-in boot manager works only on Apple hardware and nothing else, that's why OpenCore is a must if installing macOS on non-Apple hardware. For example, when you boot up Windows, it first starts Windows Boot manager before even Windows loads. The same goes for any operating system.

## **What is UEFI?**
> The Unified Extensible Firmware Interface (UEFI) is a specification that defines a software interface between an operating system and platform firmware. UEFI replaces the legacy Basic Input/Output System (BIOS) firmware interface originally present in all IBM PC-compatible personal computers, with most UEFI firmware implementations providing support for legacy BIOS services. UEFI can support remote diagnostics and repair of computers, even with no operating system installed. (source: https://dortania.github.io/OpenCore-Install-Guide/terminology.html)

## **What is BIOS?**
> The Basic Input/Output System (BIOS) is firmware used to perform hardware initialization during the booting process (power-on startup), and to provide runtime services for operating systems and programs. The BIOS firmware comes preinstalled on a personal computer's system board, and it is the first software to run when powered on (source: Wikipedia). It's a legacy piece of software that was made back in the 70s and is still used to this day due to its maturity. (source: https://dortania.github.io/OpenCore-Install-Guide/terminology.html)

## **What is Secure Boot?**
> Secure Boot is a security feature built into UEFI firmware. It ensures that only operating systems and bootloaders signed with trusted digital certificates can start on the computer.

> Purpose: Prevents malware or unauthorized bootloaders from running during startup by verifying digital signatures against keys stored in the firmware.

> How it works:

> - When the PC powers on, UEFI checks the signature of the bootloader.

> - If the signature matches a trusted key (e.g., Microsoft, Apple), the boot process continues.

> - If not, the system blocks the boot, treating the image as potentially tampered.

> Hackintosh context:

> - Boot managers like Clover and OpenCore are not signed with vendor‑trusted keys.

> - Secure Boot will usually reject them as “untrusted.”

> - To install macOS on non‑Apple hardware, Secure Boot must typically be disabled in UEFI settings.

## **What is Trusted Platform Module (TPM)?**
> TPM is a dedicated security chip built into modern computers that provides hardware‑based cryptographic functions and system integrity checks.
> Purpose:
>   - Stores encryption keys, certificates, and passwords securely.
>   - Ensures that the system boots with trusted firmware and operating system components.
>   - Acts as a hardware “root of trust” for security features.

> How it works:
> - When the PC starts, TPM verifies that the boot process hasn’t been tampered with.
> - It can generate and protect cryptographic keys inside the chip, preventing them from being extracted.
> - Supports features like disk encryption (e.g., BitLocker) and secure authentication.

> Examples of use:
> - Windows BitLocker: Uses TPM to unlock encrypted drives only if the boot environment is trusted.
> - Windows 11 requirement: Microsoft mandates TPM 2.0 for installation to ensure baseline security.
> - Enterprise security: TPM is used in servers and laptops to enforce trusted computing.

> Hackintosh context:
> - macOS does not rely on TPM for boot integrity.
> - macOS doesn't know what TPM is as macOS never really supported TPM at all - instead, Apple uses T2 Chip in Macs from 2018 to 2020, System Integrity Protection (SIP) and Secure Enclave Processor (SEP) as an alternative. If not disabled or spoofed via SSDTs, macOS updates may fail or even brick the system.

## **What are kexts?**
Kexts, also known as Kernel Extensions, are macOS's drivers. They're used to perform different tasks like device drivers or for a different purpose (in Hackintoshing) like patching the OS, injecting information or running tasks. Kexts are not the only part of a good Hackintosh, as they're commonly paired with ACPI patches and fixes. (source: https://dortania.github.io/OpenCore-Install-Guide/terminology.html)

## **If the installation of macOS is successfull, please don't forget to confirm in the discussions** 
> [!IMPORTANT]
> If the installation process is successful using OpCore Simplify, please confirm it at [Successful Hackintosh Setup with OpCore Simplify](https://github.com/albert-robert-schumann/OpCore-Simplify-VulnerabilitiesFix/discussions/7). And don't forget to recommend other people this repository.
> This will help people build their own Hackintoshes too.

> OpCore Simplify is the ONLY tool that builds OpenCore EFI based on your complete hardware configuration, not just predefined options. This fundamental difference sets us apart from other tools in the Hackintosh community.

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
