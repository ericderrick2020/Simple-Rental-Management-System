param([int]$StopWordProcessId = 0)
$ErrorActionPreference = 'Stop'
if ($StopWordProcessId -ne 0) {
    $helperProcess = Get-Process -Id $StopWordProcessId -ErrorAction SilentlyContinue
    if ($null -ne $helperProcess -and $helperProcess.ProcessName -eq 'WINWORD') {
        Stop-Process -Id $helperProcess.Id -Force
        Write-Output 'Closed the stalled report export helper. The saved Word document is retained.'
    }
    exit
}
$reportDirectory = Join-Path $PSScriptRoot 'template_matched_report'
$documentPath = Join-Path $reportDirectory 'Nahabwe_Derrick_Eric_Rental_Management_System_Project_Report.docx'
$pdfPath = Join-Path $reportDirectory 'Nahabwe_Derrick_Eric_Rental_Management_System_Project_Report.pdf'
$word = $null
$document = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.AutomationSecurity = 3
    $document = $word.Documents.Open($documentPath)
    $document.Fields.Update() | Out-Null
    $document.Repaginate()
    foreach ($contents in $document.TablesOfContents) {
        $contents.Update()
    }
    $document.Repaginate()
    foreach ($contents in $document.TablesOfContents) {
        $contents.UpdatePageNumbers()
    }
    $document.Save()
    $document.ExportAsFixedFormat($pdfPath, 17)
    Write-Output ('Finalized Word and PDF. Pages: ' + $document.ComputeStatistics(2))
} finally {
    if ($null -ne $document) { $document.Close(0) }
    if ($null -ne $word) { $word.Quit() }
}
