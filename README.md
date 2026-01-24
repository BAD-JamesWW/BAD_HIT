
<img width="1024" height="1024" alt="CompanyLogo" src="https://github.com/user-attachments/assets/77a92ff5-eeda-4082-829f-95346fb1cd6f" />

# **H.I.T. — Hash Integrity Tool**

## Company & Legal Information

H.I.T. (Hash Integrity Tool) is created and maintained by B.A.D. — Black Apex Development LLC (Ohio Entity #5448030).

This project is open-source and is intended to be freely used, modified, and redistributed under the terms of the project’s license.

However, (B.A.D.) Black Apex Development and any associated branding (including names, logos, and identity elements) are used to identify the original creator and official project releases.
Forks and modifications are allowed, but you may not claim affiliation with or endorsement by Black Apex Development.
If you redistribute or fork this project, do not represent your version as an official Black Apex Development release, and do not use the (B.A.D.) Black Apex Development name or branding in a way that suggests ownership or partnership.

© 2026 Black Apex Development LLC.


**H.I.T.** lets users create presets — saved collections of SHA-256 hashes generated from a chosen verification folder.
Users can then scan any folder and compare its files against a preset to confirm whether the contents match exactly, enabling fast, automated integrity verification.
H.I.T. also includes rich metadata to support deeper analysis of presets and verification results.

---

## Acknowledgements
This project uses:
- [Dear PyGui](https://github.com/hoffstadt/DearPyGui) — Licensed under the MIT License
- [Pygame](https://www.pygame.org/news) — LGPL-2.1 License

---

## **Features**
- Create presets (collections of SHA-256 hashes) from files in a selected verification folder.
- Presets are saved and can be referenced later.
- Automated verification of a folder’s files against a chosen preset.
- Built-in log output that displays status and results throughout usage.
- Rich metadata for deeper analysis of preset creation and verification results.

## **Youtube**
- [H.I.T. Demo Video]() — TODO

---

## **How to Use**

### **Installation & Execution**
**Supported Systems**: Windows 11
- **Run the update.bat**: Open a terminal in the H.I.T. main directory and run the "update.bat" file.
- **Run the run.bat**: Open a terminal in the H.I.T. main directory and run the "run.bat" file.
- Now unless an update happens, you can just run "run.bat" to execute H.I.T.

### **Home Screen**
- **Preset Name**: Enter a name for a new preset before creating it. This field is also used to select an existing preset for verification. The dropdown menu to the right shows all saved presets — selecting one will automatically fill this field.
- **Choose Verifcation Folder**: Opens your OS file picker to select a verification folder.
- **Verification Folder**: Displays the currently selected verification folder path.
- **Create Preset**: Generates a preset from the files in the selected verification folder, using the current Preset Name entered.
- **Verify**: Compares the current verification folder’s files against the selected preset using SHA-256 hash matching.
- **Clear Log**: Clears all text in the log window.


---

### **General Steps**
1. Name your preset
2. Pick a folder to generate your preset from
3. Create your preset
4. Verify a folder against your preset

---
