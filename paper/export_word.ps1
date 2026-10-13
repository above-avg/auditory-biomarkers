param([Parameter(Mandatory=$true)][string]$InputFile,[Parameter(Mandatory=$true)][string]$OutputPdf)
$ErrorActionPreference = 'Stop'
$taskWord = $null
$taskDocument = $null
try {
    $taskWord = New-Object -ComObject Word.Application
    $taskWord.Visible = $false
    $taskWord.DisplayAlerts = 0
    $taskWord.AutomationSecurity = 3
    $taskDocument = $taskWord.Documents.Open($InputFile, $false, $true)
    $taskDocument.Repaginate()
    $taskDocument.ExportAsFixedFormat($OutputPdf, 17)
    Write-Output ('Pages: ' + $taskDocument.ComputeStatistics(2))
} finally {
    if ($null -ne $taskDocument) { $taskDocument.Close(0) }
    if ($null -ne $taskWord) { $taskWord.Quit() }
}
