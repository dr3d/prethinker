[CmdletBinding()]
param(
  [string]$ModelTag = "qwen35-semparse:9b",
  [string]$BaseModel = "qwen3.5:9b",
  [string]$PromptFile = "modelfiles/semantic_parser_system_prompt.md",
  [string]$CanonicalModelfile = "modelfiles/qwen35-9b-semantic-parser.Modelfile",
  [string]$TempModelfile = "tmp/qwen35_semparse_latest.Modelfile",
  [switch]$SkipCanonicalUpdate = $false,
  [switch]$RunSmokeTest = $false,
  [string]$SmokeUtterance = "my mother is ann"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-RepoPath {
  param([string]$PathSpec)
  if ([System.IO.Path]::IsPathRooted($PathSpec)) {
    return [System.IO.Path]::GetFullPath($PathSpec)
  }
  return [System.IO.Path]::GetFullPath((Join-Path $script:RepoRoot $PathSpec))
}

if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
  throw "ollama command not found on PATH."
}

$script:RepoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $script:RepoRoot
try {
  $promptPath = Resolve-RepoPath $PromptFile
  if (-not (Test-Path -LiteralPath $promptPath)) {
    throw "Prompt file not found: $promptPath"
  }

  $promptText = (Get-Content -LiteralPath $promptPath -Raw -Encoding UTF8).Trim()
  if ([string]::IsNullOrWhiteSpace($promptText)) {
    throw "Prompt file is empty: $promptPath"
  }
  if ($promptText.Contains('"""')) {
    throw 'Prompt contains triple quotes ("""), which breaks Modelfile SYSTEM block.'
  }

  $modelfileText = @"
FROM $BaseModel

PARAMETER temperature 0
PARAMETER top_p 0.1
PARAMETER top_k 20
PARAMETER repeat_penalty 1.05
PARAMETER num_ctx 8192
PARAMETER num_predict 900
PARAMETER stop "```"

SYSTEM """
$promptText
"""
"@

  $tempPath = Resolve-RepoPath $TempModelfile
  $tempDir = Split-Path -Parent $tempPath
  if ($tempDir -and -not (Test-Path -LiteralPath $tempDir)) {
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
  }
  Set-Content -LiteralPath $tempPath -Value $modelfileText -Encoding UTF8
  Write-Host "Temp Modelfile: $tempPath"

  if (-not $SkipCanonicalUpdate) {
    $canonicalPath = Resolve-RepoPath $CanonicalModelfile
    try {
      $canonicalDir = Split-Path -Parent $canonicalPath
      if ($canonicalDir -and -not (Test-Path -LiteralPath $canonicalDir)) {
        New-Item -ItemType Directory -Path $canonicalDir -Force | Out-Null
      }
      Set-Content -LiteralPath $canonicalPath -Value $modelfileText -Encoding UTF8
      Write-Host "Updated canonical Modelfile: $canonicalPath"
    }
    catch {
      Write-Warning ("Could not update canonical Modelfile (" + $canonicalPath + "): " + $_.Exception.Message)
      Write-Host "Continuing build from temp Modelfile."
    }
  }

  Write-Host "Rebaking model '$ModelTag' from base '$BaseModel'..."
  & ollama create $ModelTag -f $tempPath
  if ($LASTEXITCODE -ne 0) {
    throw "ollama create failed with exit code $LASTEXITCODE"
  }

  Write-Host ""
  Write-Host "Model list entry:"
  & ollama list | Select-String -Pattern ([regex]::Escape($ModelTag))

  if ($RunSmokeTest) {
    Write-Host ""
    Write-Host "Smoke test:"
    & ollama run $ModelTag --think=false --format json $SmokeUtterance
  }

  Write-Host ""
  Write-Host "Done. Model '$ModelTag' now uses prompt from '$PromptFile'."
  Write-Host "IMPORTANT: Ollama CLI enables thinking by default for thinking-capable models."
  Write-Host "For Prethinker parser use, do not run raw 'ollama run $ModelTag' by itself."
  Write-Host "Use: powershell -ExecutionPolicy Bypass -File scripts\run_semparse_cli.ps1 -ModelTag $ModelTag"
}
finally {
  Pop-Location
}
