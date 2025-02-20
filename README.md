
# Milvue Demo Congress

This repository hosts the demo system for the Milvue congress demonstration. This version demonstrates the use of **TechCareReport** with a PACS system.
The demo integrates with a Microsoft Word Plugin to generate reports and includes an AI Assistant.

**Note:** This demo setup works only on Microsoft Windows.

## Table of Contents

- [Global Scenario](#global-scenario)
- [Setup Instructions](#setup-instructions)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Configure the Environment](#2-configure-the-environment)
  - [3. Run Docker Compose](#3-run-docker-compose)
  - [4. Client Desktop Setup (Windows Only)](#4-client-desktop-setup-windows-only)
- [DICOM & Template Utilities](#dicom--template-utilities)
  - [Interactive Menu](#interactive-menu)
    - [Option 5: Import DICOM Folders](#option-5-import-dicom-folders)
    - [How to Use the Interactive Menu](#how-to-use-the-interactive-menu)
- [How to Update DICOMs and Templates](#how-to-update-dicoms-and-templates)
- [How to setup DICOM nodes in PACS](#how-to-setup-dicom-nodes-in-pacs)

## Global Scenario


1.  Open a browser and navigate to [http://demo.milvue.local](http://demo.milvue.local).
2.  Click on a study line to view details.
3.  View images and, when ready, click the **Create Report** button.
4.  When prompted for authorization, click on **Open the link**.
5.  Microsoft Word will open with the report template.
6.  In Microsoft Word, select the **Milvue** tab in the Ribbon and click **Insert AI results** (or use the Chat AI box to edit).
7.  When finished, click **Send To PACS**.
8.  Refresh the browser viewer page to see the final report.

## Setup Instructions


### 1\. Clone the Repository

    
    git clone git@github.com:github1-grousson/milvue-demo-congress.git
    cd milvue-demo-congress
    
    # if needed change the branch to have the DICOM and templates file for a specific congress
    git checkout <ECR2025>
    

### 2\. Configure the Environment

Copy the `.env.example` file to `.env`.

    cp .env.example .env

Edit the `.env` file and complete the API URL and token as needed.

    # The URL of the environement
    API_URL=

    # The Token for this system
    TOKEN=

### 3\. Run Docker Compose

    docker-compose up -d
    

### 4\. Client Desktop Setup (Windows Only)

1.  Edit your Windows Hosts file:
    *   Open Notepad as Administrator.
    *   Open `C:\Windows\System32\drivers\etc\hosts`.
    *   Add the following line:
        
            127.0.0.1 demo.milvue.local
        
    *   Save the file.
2.  Open a browser and navigate to [http://demo.milvue.local](http://demo.milvue.local).
3.  Word Macros Installation
    *   Click on **Option/About** and select **Install Word Macro**.
    *   Click on **Download Installer** Then follow the instructions.
    *   Note: The package that will be downloaded is a ZIP file. Extract it and run the installers. Start with the *TechCareReport.msi* to install Word add-in, then run the *MilvueReportMacroInstall.exe* to install the report macro.

## DICOM & Template Utilities


This repository includes several utilities to manage DICOM files and report templates. They are accessible via an **interactive menu**, which simplifies the following tasks:

1.  **Create CSV from DICOM folder:** Generates a CSV file listing studies (grouped by `StudyInstanceUID`) from the DICOM files.
2.  **Update DICOMs from CSV:** Updates DICOM tags based on the CSV file. **Note:** Do not change the `StudyInstanceUID` or `ReportTemplateName` columns.
3.  **Reorganize DICOM folders:** Regenerates the DICOM folder structure.
4.  **Create Report Templates from CSV:** Generates final report templates using the CSV file and a source template folder.
5.  **Import DICOM Folders:** Imports DICOM files from specific subfolders.

### Interactive Menu

To launch the interactive menu, run:

    
    ./admin.sh

if the script file is not set as executable, you can run it with :

    bash admin.sh
    

The menu will display:

    Milvue admin Utilities 1.x Main Menu
    ------------------------------------

        Create CSV from DICOM folder

          Update DICOMs from CSV

      Reorganize DICOMs folders names

     Create report templates from CSV

           Import DICOM folders

                 Exit
    

#### Option 5: Import DICOM Folders

When you select option **Import DICOM folders**, you will see a sub‐menu:

     Import DICOM folders
     --------------------

      Import '00_inputs'
    Import '01_outputs_fr'
    Import '02_outputs_en'
     
            Back
    
    
*   Selecting **1**, **2**, or **3** will call the `import` function with the corresponding subdirectory (relative to the DICOM root folder).
*   **Note**: If an instance already exist in the PACS, it will be skipped.
*   The default DICOM root is computed as: `<project dir>/assets/DICOM`
*   Available subdirectories are:
    *   `00_inputs`
    *   `01_outputs_fr`
    *   `02_outputs_en`   


## How to Update DICOMs and Templates

1.  **Create CSV from DICOMs:** Generate a CSV file from your DICOM folder.
2.  **Edit CSV:** Update the CSV file with the desired report template name in the last column (`ReportTemplateName`).  
    **Note:** Do not change the `StudyInstanceUID`.
3.  **Update DICOM Files:** Run the update utility to modify DICOM tags based on the CSV.
4.  **Reorganize DICOM Folder Structure:** Use the reorganize utility if needed.
5.  **Generate Final Templates:** Create final report templates based on the CSV file.
6.  **Import DICOM Files:** Use the import option from the interactive menu to import DICOM files from the source folders.
7.  **(Optional)** Generate DICOM results by pushing to the modality via the PACS.

## How to setup DICOM nodes in PACS

By default the PACS system is configured with three DICOM nodes:

  ```json
  "Milvue_prod" : ["MILVUE", "storescp", 1040],
  "Milvue_precert" : ["MILVUE", "storescp-precert", 1040],
  "MICRODICOM": ["MICRODICOM", "127.0.0.1", 11112]
  ```

Two nodes are configured for sending DICOM files to the Milvue AI engine and one node for sending DICOM files to the MICRODICOM local workstation.

1. Edit the file `orthanc.json`
2. Find the key `DicomModalities`
3. Update or add a new node with the following format:

    ```json
    "DicomModalities" : {
        "Milvue_AI_engine" :["MILVUE", "storescp", 1040],
        "MICRODICOM": ["MICRODICOM", "127.0.0.1", 11112]
    }
    ```
4. Save file
5. Restart the docker container
    ```bash
        docker compose stop
        docker compose up -d
    ```
