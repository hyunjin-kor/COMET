<#
Export the editable Figure 1 and Figure 2(a) PowerPoint sources for the paper.
Slides 1 and 2 contain English and Korean, respectively. The source decks are
opened without a window and are never saved or overwritten by this script.
Requires the installed Microsoft PowerPoint application.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$sourceDir = Join-Path $repo 'docs/paper/diagram-sources-2026-09-12'
$outputDir = Join-Path $sourceDir 'exports'
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
$existingPowerPoint = @(Get-Process POWERPNT -ErrorAction SilentlyContinue)
$application = New-Object -ComObject PowerPoint.Application
$records = @()
try {
    foreach ($name in @('fig1_workflow', 'fig2a_cost_model')) {
        $source = Join-Path $sourceDir ($name + '.pptx')
        $presentation = $application.Presentations.Open($source, 0, -1, 0)
        try {
            if ($presentation.Slides.Count -ne 2) { throw "$name must have English and Korean slides" }
            $widthMm = [math]::Round($presentation.PageSetup.SlideWidth * 25.4 / 72, 3)
            $heightMm = [math]::Round($presentation.PageSetup.SlideHeight * 25.4 / 72, 3)
            $widthPx = [int][math]::Round($widthMm / 25.4 * 400)
            $heightPx = [int][math]::Round($heightMm / 25.4 * 400)
            $exports = @()
            for ($index = 1; $index -le 2; $index++) {
                $language = @('en', 'ko')[$index - 1]
                $stem = $name + '.' + $language
                $png = Join-Path $outputDir ($stem + '.png')
                $svg = Join-Path $outputDir ($stem + '.svg')
                $slide = $presentation.Slides.Item($index)
                $slide.Export($png, 'PNG', $widthPx, $heightPx)
                # A full-slide white rectangle fixes the SVG viewBox to the slide.
                # Grouping affects only this untitled in-memory copy of the deck.
                $indices = [object[]](1..$slide.Shapes.Count)
                $group = $slide.Shapes.Range($indices).Group()
                $group.Export($svg, 6)
                $exports += [ordered]@{
                    language = $language
                    png = 'exports/' + $stem + '.png'
                    png_sha256 = (Get-FileHash -LiteralPath $png -Algorithm SHA256).Hash.ToLowerInvariant()
                    svg = 'exports/' + $stem + '.svg'
                    svg_sha256 = (Get-FileHash -LiteralPath $svg -Algorithm SHA256).Hash.ToLowerInvariant()
                }
            }
            $records += [ordered]@{
                source = $name + '.pptx'
                source_sha256 = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()
                width_mm = $widthMm
                height_mm = $heightMm
                png_dpi_at_slide_size = 400
                exports = $exports
            }
        } finally {
            $presentation.Saved = -1
            $presentation.Close()
            [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($presentation)
        }
    }
    $manifest = [ordered]@{ renderer = 'Microsoft PowerPoint'; diagrams = $records }
    $json = $manifest | ConvertTo-Json -Depth 8
    [IO.File]::WriteAllText((Join-Path $sourceDir 'exports.json'), $json + "`n", [Text.UTF8Encoding]::new($false))
} finally {
    if ($existingPowerPoint.Count -eq 0 -and $application.Presentations.Count -eq 0) { $application.Quit() }
    [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($application)
}
Write-Output 'Exported English and Korean Figure 1 and Figure 2(a) from PowerPoint.'
