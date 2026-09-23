param()

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")
$ResearchEnvPath = Join-Path $ProjectRoot ".env.research.codex"

function Import-EnvFile {
  param([string]$Path)

  if (-not (Test-Path -LiteralPath $Path)) { return }

  foreach ($line in Get-Content -LiteralPath $Path) {
    $trimmed = $line.Trim()
    if ($trimmed.Length -eq 0 -or $trimmed.StartsWith("#")) { continue }
    if ($trimmed -match '^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$') {
      $name = $matches[1]
      $value = $matches[2].Trim()
      if (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'"))) {
        $value = $value.Substring(1, $value.Length - 2)
      }
      [Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
  }
}

function Has-Command {
  param([string]$Name)
  return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Has-Env {
  param([string]$Name)
  return [bool]([Environment]::GetEnvironmentVariable($Name, "Process") -or [Environment]::GetEnvironmentVariable($Name, "User") -or [Environment]::GetEnvironmentVariable($Name, "Machine"))
}

Import-EnvFile -Path $ResearchEnvPath

[pscustomobject]@{
  brave_cli = Has-Command "brave"
  brave_api_key_present = ((Has-Env "BRAVE_API_KEY") -or (Has-Env "BRAVE_SEARCH_API_KEY"))
  brave_local_env_present = Test-Path -LiteralPath $ResearchEnvPath
  brave_wrapper_present = Test-Path -LiteralPath (Join-Path $ProjectRoot "scripts\brave-search.ps1")
  tavily_cli = Has-Command "tavily"
  tavily_api_key_present = Has-Env "TAVILY_API_KEY"
  firecrawl_cli = Has-Command "firecrawl"
  firecrawl_api_key_present = Has-Env "FIRECRAWL_API_KEY"
  node_present = Has-Command "node"
  npm_present = Has-Command "npm"
  note = "Nao imprime valores de chaves. web.run do Codex nao e detectavel via PowerShell."
} | ConvertTo-Json
