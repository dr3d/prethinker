[CmdletBinding()]
param(
  [string]$ModelTag = "qwen35-semparse:9b",
  [switch]$NoJsonFormat = $false,
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$PromptParts
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
  throw "ollama command not found on PATH."
}

$argsList = @("run", $ModelTag, "--think=false")
if (-not $NoJsonFormat) {
  $argsList += @("--format", "json")
}
if ($PromptParts -and $PromptParts.Count -gt 0) {
  $promptText = ($PromptParts -join " ").Trim()
  if ($promptText) {
    $argsList += $promptText
  }
}

Write-Host "Launching Ollama semantic parser lane with thinking disabled..."
if (-not $NoJsonFormat) {
  Write-Host "Response format locked to JSON."
}
& ollama @argsList
