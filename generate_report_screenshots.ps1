Add-Type -AssemblyName System.Drawing

$assetsDir = Join-Path $PSScriptRoot "assets"
New-Item -ItemType Directory -Path $assetsDir -Force | Out-Null

function New-Brush($hex) {
    $color = [System.Drawing.ColorTranslator]::FromHtml($hex)
    return New-Object System.Drawing.SolidBrush($color)
}

function New-Pen($hex, $width = 1) {
    $color = [System.Drawing.ColorTranslator]::FromHtml($hex)
    return New-Object System.Drawing.Pen($color, $width)
}

function Draw-Text($g, $text, $font, $brush, $x, $y) {
    $g.DrawString($text, $font, $brush, [float]$x, [float]$y)
}

function Draw-Rect($g, $brush, $pen, $x, $y, $w, $h) {
    $rect = New-Object System.Drawing.Rectangle($x, $y, $w, $h)
    if ($brush -ne $null) { $g.FillRectangle($brush, $rect) }
    if ($pen -ne $null) { $g.DrawRectangle($pen, $rect) }
}

function Draw-Input($g, $x, $y, $w, $label, $value, $isDropdown = $false) {
    Draw-Text $g $label $script:smallBold $script:textBrush $x ($y - 24)
    Draw-Rect $g $script:whiteBrush $script:borderPen $x $y $w 44
    Draw-Text $g $value $script:normalFont $script:textLightBrush ($x + 14) ($y + 11)
    if ($isDropdown) {
        Draw-Text $g "v" $script:normalBold ($script:primaryBrush) ($x + $w - 30) ($y + 11)
    }
}

$backgroundBrush = New-Brush "#F4F6F8"
$surfaceBrush = New-Brush "#FFFFFF"
$sidebarBrush = New-Brush "#102A43"
$primaryBrush = New-Brush "#1E3A5F"
$secondaryBrush = New-Brush "#4F86C6"
$successBrush = New-Brush "#2D9D78"
$warningBrush = New-Brush "#E9A23B"
$dangerBrush = New-Brush "#D64545"
$textBrush = New-Brush "#243B53"
$textLightBrush = New-Brush "#829AB1"
$whiteBrush = New-Brush "#FFFFFF"
$borderPen = New-Pen "#D9E2EC" 2
$lightPen = New-Pen "#EDF2F7" 2
$primaryPen = New-Pen "#1E3A5F" 2

$titleFont = New-Object System.Drawing.Font("Segoe UI", 24, [System.Drawing.FontStyle]::Bold)
$headingFont = New-Object System.Drawing.Font("Segoe UI", 18, [System.Drawing.FontStyle]::Bold)
$subheadingFont = New-Object System.Drawing.Font("Segoe UI", 14, [System.Drawing.FontStyle]::Bold)
$normalBold = New-Object System.Drawing.Font("Segoe UI", 11, [System.Drawing.FontStyle]::Bold)
$normalFont = New-Object System.Drawing.Font("Segoe UI", 11, [System.Drawing.FontStyle]::Regular)
$smallBold = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Bold)
$smallFont = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Regular)

$script:smallBold = $smallBold
$script:normalFont = $normalFont
$script:normalBold = $normalBold
$script:textBrush = $textBrush
$script:textLightBrush = $textLightBrush
$script:whiteBrush = $whiteBrush
$script:borderPen = $borderPen
$script:primaryBrush = $primaryBrush

# Main project screen.
$bitmap = New-Object System.Drawing.Bitmap(1400, 900)
$g = [System.Drawing.Graphics]::FromImage($bitmap)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.Clear([System.Drawing.ColorTranslator]::FromHtml("#F4F6F8"))

Draw-Rect $g $sidebarBrush $null 0 0 260 900
Draw-Text $g "Rental Management" $subheadingFont $whiteBrush 34 36
Draw-Text $g "System" $subheadingFont $whiteBrush 34 62

$navItems = @("Dashboard", "Properties", "Tenants", "Payments", "Settings")
for ($i = 0; $i -lt $navItems.Count; $i++) {
    $y = 135 + ($i * 62)
    $brush = if ($i -eq 1) { $secondaryBrush } else { $sidebarBrush }
    Draw-Rect $g $brush $null 22 $y 216 44
    Draw-Text $g $navItems[$i] $normalBold $whiteBrush 48 ($y + 11)
}

Draw-Rect $g $surfaceBrush $borderPen 260 0 1140 84
Draw-Text $g "Properties" $headingFont $textBrush 304 24
Draw-Text $g "Manage rental houses, apartments, tenants, and rent payments" $normalFont $textLightBrush 304 53

Draw-Text $g "Properties" $headingFont $textBrush 306 124
Draw-Text $g "This page lists rental houses, rooms, or apartments." $normalFont $textLightBrush 306 154
Draw-Rect $g $primaryBrush $null 1192 118 142 46
Draw-Text $g "+ Add Property" $normalBold $whiteBrush 1210 130

$cardX = 306
$cardY = 205
foreach ($card in @(
    @("Properties", "3", "Active rental properties", "#1E3A5F"),
    @("Tenants", "38", "Current registered tenants", "#2D9D78"),
    @("Payments", "UGX 33.5M", "Collected this month", "#4F86C6")
)) {
    Draw-Rect $g $surfaceBrush $borderPen $cardX $cardY 300 130
    $valueBrush = New-Brush $card[3]
    Draw-Text $g $card[1] $titleFont $valueBrush ($cardX + 24) ($cardY + 20)
    Draw-Text $g $card[0] $normalBold $textBrush ($cardX + 24) ($cardY + 70)
    Draw-Text $g $card[2] $smallFont $textLightBrush ($cardX + 24) ($cardY + 96)
    $cardX += 330
}

Draw-Rect $g $surfaceBrush $borderPen 306 380 1028 380
Draw-Text $g "Property Records" $subheadingFont $textBrush 334 410
Draw-Text $g "Search" $smallBold $textBrush 334 464
Draw-Rect $g $whiteBrush $borderPen 386 452 360 42
Draw-Text $g "Search by name or location" $normalFont $textLightBrush 402 462
Draw-Rect $g $surfaceBrush $borderPen 764 452 150 42
Draw-Text $g "Active  v" $normalFont $textBrush 785 462

$headers = @("Property Name", "Location", "Units", "Monthly Rent")
$xValues = @(334, 626, 850, 1030)
for ($i = 0; $i -lt $headers.Count; $i++) {
    Draw-Text $g $headers[$i] $smallBold $textBrush $xValues[$i] 536
}
$rows = @(
    @("Rocky Estates", "Kampala", "20", "UGX 1,200,000"),
    @("Entebbe Apartment", "Entebbe", "10", "UGX 500,000"),
    @("Kampala Flats", "Kampala", "12", "UGX 850,000")
)
for ($r = 0; $r -lt $rows.Count; $r++) {
    $y = 585 + ($r * 54)
    Draw-Rect $g $null $lightPen 326 ($y - 17) 980 45
    for ($c = 0; $c -lt $rows[$r].Count; $c++) {
        Draw-Text $g $rows[$r][$c] $normalFont $textBrush $xValues[$c] $y
    }
}

$mainPath = Join-Path $assetsDir "report_project_screen.png"
$bitmap.Save($mainPath, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose()
$bitmap.Dispose()

# Add tenant modal screen.
$bitmap = New-Object System.Drawing.Bitmap(1400, 900)
$g = [System.Drawing.Graphics]::FromImage($bitmap)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.Clear([System.Drawing.ColorTranslator]::FromHtml("#F4F6F8"))

Draw-Rect $g $sidebarBrush $null 0 0 260 900
Draw-Text $g "Rental Management" $subheadingFont $whiteBrush 34 36
Draw-Text $g "System" $subheadingFont $whiteBrush 34 62
for ($i = 0; $i -lt $navItems.Count; $i++) {
    $y = 135 + ($i * 62)
    $brush = if ($i -eq 2) { $secondaryBrush } else { $sidebarBrush }
    Draw-Rect $g $brush $null 22 $y 216 44
    Draw-Text $g $navItems[$i] $normalBold $whiteBrush 48 ($y + 11)
}

Draw-Rect $g $surfaceBrush $borderPen 260 0 1140 84
Draw-Text $g "Tenants" $headingFont $textBrush 304 24
Draw-Text $g "Store tenant contacts, selected property, unit, and rent status" $normalFont $textLightBrush 304 53
Draw-Text $g "Tenants" $headingFont $textBrush 306 124
Draw-Text $g "This page stores tenant names, contacts, and rental details." $normalFont $textLightBrush 306 154
Draw-Rect $g $primaryBrush $null 1180 118 154 46
Draw-Text $g "+ Add Tenant" $normalBold $whiteBrush 1204 130

Draw-Rect $g $surfaceBrush $borderPen 306 210 1028 300
Draw-Text $g "Tenant Records" $subheadingFont $textBrush 334 240
Draw-Text $g "Sarah N.      +256 700 123 456      Rocky Estates / B12      UGX 1,200,000      Active" $normalFont $textBrush 334 310
Draw-Text $g "Daniel K.     +256 752 444 980      Kampala Flats / 04       UGX 850,000        Active" $normalFont $textBrush 334 365

$overlay = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(120, 244, 246, 248))
Draw-Rect $g $overlay $null 260 84 1140 816

Draw-Rect $g $surfaceBrush $primaryPen 380 190 760 520
Draw-Text $g "Add Tenant" $headingFont $textBrush 424 224
Draw-Text $g "Capture the tenant profile, selected property, assigned unit, and rent status." $normalFont $textLightBrush 424 258

Draw-Input $g 424 330 285 "Tenant Name" "Sarah N."
Draw-Input $g 765 330 285 "Phone Number" "+256 700 123 456"
Draw-Input $g 424 420 285 "Email Address" "sarah@example.com"
Draw-Input $g 765 420 285 "Property" "Rocky Estates - Kampala" $true
Draw-Input $g 424 510 285 "Unit Number" "B12"
Draw-Input $g 765 510 285 "Lease Start Date" "2026-08-18"
Draw-Input $g 424 600 285 "Monthly Rent" "1200000"
Draw-Input $g 765 600 285 "Status" "Active" $true

Draw-Rect $g $surfaceBrush $borderPen 784 660 112 42
Draw-Text $g "Cancel" $normalBold $textBrush 812 670
Draw-Rect $g $primaryBrush $null 914 660 136 42
Draw-Text $g "Save Tenant" $normalBold $whiteBrush 934 670

$tenantPath = Join-Path $assetsDir "report_add_tenant_screen.png"
$bitmap.Save($tenantPath, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose()
$bitmap.Dispose()

Write-Host "Created $mainPath"
Write-Host "Created $tenantPath"
