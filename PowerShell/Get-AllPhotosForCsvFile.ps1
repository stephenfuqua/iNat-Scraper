Param(
    [Parameter(Mandatory=$true)]
    [string]
    $csvFile
)

$observationUrlBase="https://api.inaturalist.org/v1/observations/"
$outputDirectory = "./" + $csvFile.Replace(".csv","")
New-Item -Force -Type Directory -Path $outputDirectory

function Get-ObservationPhotos {
    Param (
        [Parameter(Mandatory=$true)]
        [int]
        $observationId
    )

    # Retrieve observation's JSON description

    $observationUrl=$observationUrlBase+$observationId
    $observation = Invoke-RestMethod -Method Get -Uri $observationUrl

    <#
    $observation now contains the JSON data from the API call, expanded into a
    PowerShell object. The original JSON looks like this:

    {
        "results": [
            {
                // various fields
                "photos": [
                    {
                        "id": 53013554,
                        "license_code": "cc-by-nc-sa",
                        "url": "https://static.inaturalist.org/photos/53013554/square.jpeg?1569981125",
                        "attribution": "(c) Stephen Fuqua, some rights reserved (CC BY-NC-SA)",
                        "original_dimensions": {
                            "width": 1152,
                            "height": 2048
                        },
                        "flags": []
                    },
                ]
            }
        ]
    }

    Since the request was for only one observation, there should be only one result
    in the array. Thus we can access information such as 

    $observation.results[0].photos[0].url 

    The JSON data contains a URL to a small square image for display on the screen.
    However, the naming convention is straight forward - the URL contains the word
    "square" and we can change that to "original" to get the large file uploaded
    by the user.
    #>
    $result = $observation.results[0]

    # Loop through photos
    $baseName = $outputDirectory + "\" + "observationid-" + $observationId `
        + "." + $result.taxon.rank + "-" + $result.taxon.name + ".photoid-"

    $result.photos | ForEach-Object {
        $photo = $_

        # Replace "square" with "original" to get the full size image
        $url = $photo.url.Replace("square", "original")

        # Download the photo
        $fileName = $baseName + $photo.id + "." + $photo.license_code `
            + $photo.attribution + ".jpg"
        Invoke-WebRequest -Method Get -Uri $url -OutFile $fileName
 
    }
}

function Invoke-ProcessCsv {
    
    # Read the CSV file
    $csv = Import-Csv -Path $csvFile

    # Loop through the rows
    $csv | ForEach-Object {
        # Download each image file
        Get-ObservationPhotos -observationId $_.id
    }
}

Invoke-ProcessCsv