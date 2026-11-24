<#
.SYNOPSIS
  Sinopia installer for Windows (Windows PowerShell 5.1+ / PowerShell 7).

.DESCRIPTION
  Installs skill\sinopia from a LOCAL checkout into supported agents:
    claude -> ~\.claude\skills\sinopia  (+ ~\.claude\commands\sinopia.md, snp.md)
    codex  -> ~\.codex\skills\sinopia
    agy    -> plugin mode (default): ~\.gemini\config\plugins\sinopia\skills\sinopia
                                     + generated ~\.gemini\config\plugins\sinopia\plugin.json
              skill mode:            ~\.gemini\config\skills\sinopia
  -Target auto (default) installs for every agent whose config dir exists,
  falling back to claude.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\install.ps1 -Target all
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\install.ps1 -Target all -DryRun
#>
[CmdletBinding()]
param(
    [ValidateSet('claude', 'agy', 'codex', 'all', 'auto')]
    [string]$Target = 'auto',
    [switch]$DryRun,
    [string]$HomeDir = '',
    [string]$Source = '',
    [ValidateSet('plugin', 'skill')]
    [string]$AgyMode = 'plugin'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

# --- product metadata ---
$SkillName = 'sinopia'
$DisplayName = 'Sinopia'
$PluginVersion = '0.1.0'
$PluginDescription = 'Pre-build counsel: plain-language intake, mirror-back check, and an isolated senior review of a refined brief. Go, Pilot, or No-Go.'
$SuggestedPrompts = @(
    'Review this idea with Sinopia before I start building',
    'Run Sinopia pre-build counsel on my plan and surface hidden risks',
    'Help me clarify constraints and get a Go or Pilot verdict with Sinopia'
)

if (-not $HomeDir) {
    $HomeDir = $env:USERPROFILE
    if (-not $HomeDir) { $HomeDir = $HOME }
}
if (-not $HomeDir) { throw 'Cannot determine home directory; pass -HomeDir.' }

function Write-Step([string]$Message) { Write-Host $Message }

function Test-SkillRoot([string]$Dir) {
    if (-not $Dir) { return $false }
    return (Test-Path -LiteralPath (Join-Path $Dir "skill\$SkillName\SKILL.md") -PathType Leaf)
}

function Clear-ReadOnly([IO.FileSystemInfo]$Item) {
    if ($Item.Attributes -band [IO.FileAttributes]::ReadOnly) {
        $Item.Attributes = $Item.Attributes -band (-bnot [IO.FileAttributes]::ReadOnly)
    }
}

function Remove-Tree([string]$Path) {
    # Manual walk: junctions/symlinks anywhere in the tree are unlinked, never followed.
    $item = Get-Item -LiteralPath $Path -Force
    if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
        if ($item.PSIsContainer) { [IO.Directory]::Delete($Path) } else { Clear-ReadOnly $item; [IO.File]::Delete($Path) }
        return
    }
    if (-not $item.PSIsContainer) {
        Clear-ReadOnly $item
        [IO.File]::Delete($Path)
        return
    }
    foreach ($child in @(Get-ChildItem -LiteralPath $Path -Force)) { Remove-Tree $child.FullName }
    Clear-ReadOnly $item
    [IO.Directory]::Delete($Path)
}

function Remove-Dest([string]$Path) {
    # Safety: only ever remove a directory named after this product.
    if ($SkillName -ne 'sinopia') { throw "Refusing to remove: unexpected SkillName '$SkillName'." }
    if ((Split-Path -Leaf $Path) -ne $SkillName) { throw "Refusing to remove unexpected path: $Path" }
    if (-not (Test-Path -LiteralPath $Path)) { return }
    Remove-Tree $Path
}

function Set-TreeWritable([string]$Path) {
    # Copies from a read-only checkout keep the ReadOnly attribute; strip it so reinstalls work.
    Clear-ReadOnly (Get-Item -LiteralPath $Path -Force)
    Get-ChildItem -LiteralPath $Path -Recurse -Force | ForEach-Object { Clear-ReadOnly $_ }
}

function Install-SkillDir([string]$Label, [string]$Dest) {
    $srcDir = Join-Path $Source "skill\$SkillName"
    Write-Step "[$Label] skill -> $Dest"
    if ($DryRun) {
        if (Test-Path -LiteralPath $Dest) { Write-Step "[dry-run] would replace existing $Dest" }
        Write-Step "[dry-run] would copy $srcDir\* -> $Dest"
        return
    }
    Remove-Dest $Dest
    New-Item -ItemType Directory -Path $Dest -Force | Out-Null
    foreach ($child in @(Get-ChildItem -LiteralPath $srcDir -Force)) {
        if ($child.Name -eq '__pycache__') { continue }
        Copy-Item -LiteralPath $child.FullName -Destination $Dest -Recurse -Force
    }
    Get-ChildItem -LiteralPath $Dest -Recurse -Directory -Filter '__pycache__' -Force -ErrorAction SilentlyContinue |
        ForEach-Object { Remove-Tree $_.FullName }
    Set-TreeWritable $Dest
}

function Get-PluginJson {
    $manifest = [ordered]@{
        name             = $SkillName
        displayName      = $DisplayName
        version          = $PluginVersion
        description      = $PluginDescription
        suggestedPrompts = @($SuggestedPrompts)
    }
    return (ConvertTo-Json -InputObject $manifest -Depth 4)
}

# --- locate source (local checkout only) -----------------------------------
if (-not $Source) {
    $scriptDir = $null
    if ($PSCommandPath) { $scriptDir = Split-Path -Parent $PSCommandPath }
    elseif ($MyInvocation.MyCommand.Path) { $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path }
    if ($scriptDir) {
        foreach ($cand in @($scriptDir, (Split-Path -Parent $scriptDir))) {
            if ($cand -and (Test-SkillRoot $cand)) { $Source = (Resolve-Path -LiteralPath $cand).Path; break }
        }
    }
    if (-not $Source) {
        Write-Error ("Local $DisplayName checkout not found (expected skill\$SkillName\SKILL.md next to or above this script). " +
            'Clone https://github.com/Excelsus4/sinopia and run tools\install.ps1 from the checkout, or pass -Source <repo root>.') -ErrorAction Continue
        exit 1
    }
}
elseif (-not (Test-SkillRoot $Source)) {
    Write-Error "skill\$SkillName\SKILL.md not found under '$Source'. Pass -Source <repo root> of a $DisplayName checkout." -ErrorAction Continue
    exit 1
}
else {
    $Source = (Resolve-Path -LiteralPath $Source).Path
}
Write-Step "Source: $Source"

# --- resolve targets -------------------------------------------------------
$targets = @()
switch ($Target) {
    'all' { $targets = @('claude', 'agy', 'codex') }
    'auto' {
        if (Test-Path -LiteralPath (Join-Path $HomeDir '.claude') -PathType Container) { $targets += 'claude' }
        if (Test-Path -LiteralPath (Join-Path $HomeDir '.gemini') -PathType Container) { $targets += 'agy' }
        if (Test-Path -LiteralPath (Join-Path $HomeDir '.codex') -PathType Container) { $targets += 'codex' }
        if ($targets.Count -eq 0) {
            Write-Step 'No agent config dirs detected; defaulting to claude'
            $targets = @('claude')
        }
    }
    default { $targets = @($Target) }
}

foreach ($t in $targets) {
    switch ($t) {
        'claude' {
            Install-SkillDir 'claude' (Join-Path $HomeDir ".claude\skills\$SkillName")
            $cmdDir = Join-Path $HomeDir '.claude\commands'
            $cmdSrcDir = Join-Path $Source 'commands'
            $cmdFiles = @()
            if (Test-Path -LiteralPath $cmdSrcDir -PathType Container) {
                $cmdFiles = @(Get-ChildItem -LiteralPath $cmdSrcDir -Filter '*.md' -File | Sort-Object Name)
            }
            if ($cmdFiles.Count -eq 0) {
                Write-Step "[claude] warning: no $cmdSrcDir\*.md found; skipping slash commands"
            }
            else {
                if (-not $DryRun) { New-Item -ItemType Directory -Path $cmdDir -Force | Out-Null }
                foreach ($f in $cmdFiles) {
                    $cmdDest = Join-Path $cmdDir $f.Name
                    Write-Step "[claude] command -> $cmdDest"
                    if ($DryRun) { Write-Step "[dry-run] would copy $($f.FullName) -> $cmdDest"; continue }
                    if (Test-Path -LiteralPath $cmdDest) {
                        $old = Get-Item -LiteralPath $cmdDest -Force
                        if ($old.PSIsContainer) { throw "Refusing to overwrite directory: $cmdDest" }
                        Clear-ReadOnly $old
                        [IO.File]::Delete($cmdDest)
                    }
                    Copy-Item -LiteralPath $f.FullName -Destination $cmdDest -Force
                    Clear-ReadOnly (Get-Item -LiteralPath $cmdDest -Force)
                }
            }
        }
        'codex' {
            Install-SkillDir 'codex' (Join-Path $HomeDir ".codex\skills\$SkillName")
        }
        'agy' {
            $pluginRoot = Join-Path $HomeDir ".gemini\config\plugins\$SkillName"
            $skillModeDir = Join-Path $HomeDir ".gemini\config\skills\$SkillName"
            if ($AgyMode -eq 'skill') {
                if (Test-Path -LiteralPath $pluginRoot) {
                    Write-Step "[agy] warning: plugin-mode install also exists at $pluginRoot (remove it to avoid a duplicate skill)"
                }
                Install-SkillDir 'agy' $skillModeDir
            }
            else {
                if (Test-Path -LiteralPath $skillModeDir) {
                    Write-Step "[agy] warning: skill-mode install also exists at $skillModeDir (remove it to avoid a duplicate skill)"
                }
                Write-Step "[agy] plugin -> $pluginRoot"
                if (-not $DryRun) { Remove-Dest $pluginRoot }
                Install-SkillDir 'agy' (Join-Path $pluginRoot "skills\$SkillName")
                $manifestPath = Join-Path $pluginRoot 'plugin.json'
                $json = Get-PluginJson
                Write-Step "[agy] manifest -> $manifestPath"
                if ($DryRun) {
                    Write-Step "[dry-run] would write $manifestPath :"
                    Write-Step $json
                }
                else {
                    # UTF-8 without BOM on both Windows PowerShell 5.1 and PowerShell 7.
                    [IO.File]::WriteAllText($manifestPath, $json + "`n", (New-Object System.Text.UTF8Encoding($false)))
                }
            }
        }
    }
}

if ($DryRun) {
    Write-Step 'Dry run complete. No files were changed.'
}
else {
    Write-Step ("$DisplayName installed for: " + ($targets -join ', '))
    Write-Step "Start a new agent session and run /$SkillName (or /snp in Claude Code)."
}
