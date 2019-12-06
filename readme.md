# iNat-Scraper

Tools for automating retrieval of data and/or files from iNaturalist.

## Downloading Photos

### User Story

> As an iNaturalist curator, I want to download all photos associated with an observation, so that I will have an archive of photos related to the project(s) I am curating.

### Conditions of Satisfaction

* Read observation Ids from a CSV file containing a column called "id".
* Store each photo with a name in the following format (each {abc} token is a template indicating a source of information)
: `observationid-{observationId}.{taxon-rank}-{taxon-name}.photoid-{photoId}.{license}.{attribution}.jpg`

## PowerShell Solution

The script `Get-AllPhotosForCsvFile.ps1` in the PowerShell directory achieves the story described above. To run this:

1. Download [Get-AllPhotosForCsvFile.ps1](PowerShell/Get-AllPhotosForCsvFile.ps1).
1. In Windows Explorer, find the directory where you saved (or moved) the file.
1. Place a copy of your iNaturalist CSV file into the same directory as the script.
1. Still in Windows Explorer: click in the small directory path input box, between the arrows and the search box. Copy the path there.
1. From the Windows start menu, find PowerShell and run it.
1. Type the command `cd `, then Control-V to paste the download directory, and hit enter. You've now made the download directory into the active directory. Thus something like 

    ```powershell
    cd c:\some\directory\name
    ```

1. Type the following command and then hit enter:

    ```powershell
    .\Get-AllPhotosForCsvFile.ps1 -csvFile <type or paste the csv file name>
    ```

1. It will begin processing your photos, placing them into a directory named after the input file. 

<dl>
<dt>:warning: Nota bene</dt>
<dd>
This could take a long time. Right now there is no built-in retry mechanism that will allow you to start over if the process dies for some reason. In that case, you'll need to edit the CSV file by removing the lines for the files that were already downloaded. If you need to cancel the download process for some reason, type Control-C at any time.
</dd>
</dl>

## About
Copyright &copy; Stephen A. Fuqua, 2019. Available for free and unfettered use under terms of the [MIT license](license).