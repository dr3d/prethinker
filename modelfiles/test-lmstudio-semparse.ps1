param(
  [ValidateSet("lmstudio", "ollama")]
  [string]$Backend = "lmstudio",
  [string]$BaseUrl = "",
  [string]$Model = "qwen/qwen3.5-9b",
  [string]$Utterance = "If someone is a manager then they can approve budgets.",
  [string]$EnvFile = "",
  [bool]$TwoPass = $true,
  [int]$ContextLength = 4096,
  [int]$TimeoutSec = 90
)

$RepoRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($EnvFile)) {
  $EnvFile = Join-Path $RepoRoot ".env.local"
} elseif (-not [System.IO.Path]::IsPathRooted($EnvFile)) {
  $EnvFile = Join-Path $RepoRoot $EnvFile
}

if ([string]::IsNullOrWhiteSpace($BaseUrl)) {
  if ($Backend -eq "ollama") {
    $BaseUrl = "http://127.0.0.1:11434"
  } else {
    $BaseUrl = "http://127.0.0.1:1234"
  }
}

function Get-ApiKey {
  param([string]$Path)

  if ($env:PRETHINKER_API_KEY) { return $env:PRETHINKER_API_KEY }
  if ($env:LMSTUDIO_API_KEY) { return $env:LMSTUDIO_API_KEY }
  if ($env:OPENAI_API_KEY) { return $env:OPENAI_API_KEY }

  if (Test-Path $Path) {
    foreach ($line in Get-Content $Path) {
      if ($line -match "^LMSTUDIO_API_KEY=(.+)$") {
        return $Matches[1].Trim()
      }
    }
  }

  return $null
}

function Get-LastValidJsonObject {
  param(
    [string]$Text,
    [string[]]$RequiredKeys = @()
  )

  if ([string]::IsNullOrWhiteSpace($Text)) { return $null }

  $depth = 0
  $start = -1
  $best = $null

  for ($i = 0; $i -lt $Text.Length; $i++) {
    $ch = $Text[$i]
    if ($ch -eq '{') {
      if ($depth -eq 0) { $start = $i }
      $depth++
      continue
    }
    if ($ch -eq '}') {
      if ($depth -gt 0) { $depth-- }
      if ($depth -eq 0 -and $start -ge 0) {
        $candidate = $Text.Substring($start, $i - $start + 1)
        try {
          $parsed = $candidate | ConvertFrom-Json
          $ok = $true
          foreach ($k in $RequiredKeys) {
            if (-not ($parsed.PSObject.Properties.Name -contains $k)) {
              $ok = $false
              break
            }
          }
          if ($ok) { $best = $candidate }
        } catch {
          # ignore malformed candidates
        }
        $start = -1
      }
    }
  }

  return $best
}

function Invoke-ModelPrompt {
  param(
    [string]$Backend,
    [string]$BaseUrl,
    [string]$Model,
    [string]$PromptText,
    [int]$ContextLength,
    [int]$TimeoutSec,
    [hashtable]$Headers
  )

  try {
    if ($Backend -eq "ollama") {
      $body = @{
        model = $Model
        stream = $false
        messages = @(
          @{
            role = "user"
            content = $PromptText
          }
        )
        options = @{
          temperature = 0
          num_ctx = $ContextLength
        }
      } | ConvertTo-Json -Depth 12

      $resp = Invoke-RestMethod -Method Post -Uri "$($BaseUrl.TrimEnd('/'))/api/chat" -Headers $Headers -Body $body -TimeoutSec $TimeoutSec

      $msg = ""
      $reasoning = ""
      if ($resp.message) {
        if ($resp.message.content) {
          $msg = [string]$resp.message.content
        }
        # Ollama commonly returns hidden reasoning here for thinking-capable models.
        if ($resp.message.thinking) {
          $reasoning = [string]$resp.message.thinking
        }
      } elseif ($resp.response) {
        $msg = [string]$resp.response
      }
      if (-not $reasoning -and $resp.thinking) {
        $reasoning = [string]$resp.thinking
      }

      return [pscustomobject]@{
        success = $true
        message = $msg
        reasoning = $reasoning
        raw = $resp
      }
    }

    $body = @{
      model = $Model
      input = $PromptText
      temperature = 0
      context_length = $ContextLength
    } | ConvertTo-Json -Depth 10

    if ($env:SEM_PARSE_DEBUG -eq "1") {
      Write-Host "DEBUG backend=$Backend uri=$($BaseUrl.TrimEnd('/'))/api/v1/chat model=$Model ctx=$ContextLength"
      Write-Host "DEBUG body (first 800 chars):"
      if ($body.Length -gt 800) {
        Write-Host $body.Substring(0, 800)
      } else {
        Write-Host $body
      }
    }

    $resp = Invoke-RestMethod -Method Post -Uri "$($BaseUrl.TrimEnd('/'))/api/v1/chat" -Headers $Headers -Body $body -TimeoutSec $TimeoutSec

    $msg = ""
    $reasoning = ""
    if ($resp.output) {
      foreach ($item in @($resp.output)) {
        if ($item.type -eq "message" -and $item.content) {
          $msg = [string]$item.content
        }
        if ($item.type -eq "reasoning" -and $item.content) {
          $reasoning = [string]$item.content
        }
      }
    }

    return [pscustomobject]@{
      success = $true
      message = $msg
      reasoning = $reasoning
      raw = $resp
    }
  } catch {
    $errMessage = $_.Exception.Message
    $errBody = ""
    try {
      if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $errBody = $reader.ReadToEnd()
      }
    } catch {
      # ignore secondary error parsing failure payload
    }
    if ($errBody) {
      $errMessage = "$errMessage`nHTTP body: $errBody"
    }
    return [pscustomobject]@{
      success = $false
      error = $errMessage
      raw = $null
      message = ""
      reasoning = ""
    }
  }
}

function Get-RouteHeuristic {
  param([string]$Text)
  $lower = $Text.ToLowerInvariant()
  if ($lower -match "\b(retract|remove|delete|undo|correction|actually)\b") { return "retract" }
  if ($lower -match "\b(if|whenever|then)\b") { return "assert_rule" }
  if ($lower -match "\?$" -or $lower -match "^\s*(who|what|where|when|why|how)\b") { return "query" }
  if ($lower -match "\b(translate|summarize|rewrite|format|explain)\b") { return "other" }
  return "assert_fact"
}

function Build-ClassifierPrompt {
  param([string]$Utterance)
  return @"
/no_think
Return minified JSON only:
{"route":"assert_fact|assert_rule|query|retract|other","needs_clarification":true|false,"ambiguity_risk":"low|medium|high","reason":"<=12 words"}
Utterance:
$Utterance
"@
}

function Build-ExtractorPrompt {
  param(
    [string]$Utterance,
    [string]$Route
  )

  $routeGuidance = switch ($Route) {
    "assert_fact" { "Route lock: assert_fact. Extract one best factual predicate statement." }
    "assert_rule" { "Route lock: assert_rule. Extract one best conditional rule using ':-' syntax." }
    "query" { "Route lock: query. Convert to query goal without '?-' prefix." }
    "retract" { "Route lock: retract. Use retract(<fact>). as logic_string." }
    default { "Route lock: other. Keep logic_string empty and set intent=other unless a clear logic form exists." }
  }

  return @"
/no_think
$routeGuidance
Return JSON only with exactly these keys:
intent,logic_string,components,facts,rules,queries,confidence,ambiguities,needs_clarification,rationale
Rules:
- intent in assert_fact|assert_rule|query|retract|other
- components object with arrays: atoms,variables,predicates
- facts/rules/queries arrays of Prolog strings ending with '.'
- queries must not include '?-'
- atoms lowercase snake_case, variables Uppercase
- confidence object with overall,intent,logic floats in [0,1]
- logic_string MUST be Prolog, never natural-language explanation
- if intent=assert_fact => logic_string == facts[0]
- if intent=assert_rule => logic_string == rules[0]
- if intent=query => logic_string == queries[0]
- if intent=retract => logic_string == retract(<fact>).
- if intent=other => logic_string is empty string and facts/rules/queries are empty
- no markdown, no extra text
Examples:
1) Utterance: "Who is John's parent?"
{"intent":"query","logic_string":"parent(X, john).","components":{"atoms":["john"],"variables":["X"],"predicates":["parent"]},"facts":[],"rules":[],"queries":["parent(X, john)."],"confidence":{"overall":0.95,"intent":1.0,"logic":0.95},"ambiguities":[],"needs_clarification":false,"rationale":"Direct relationship query."}
2) Utterance: "John likes it."
{"intent":"assert_fact","logic_string":"likes(john, X).","components":{"atoms":["john"],"variables":["X"],"predicates":["likes"]},"facts":["likes(john, X)."],"rules":[],"queries":[],"confidence":{"overall":0.8,"intent":0.95,"logic":0.75},"ambiguities":["Referent of pronoun 'it' is unresolved."],"needs_clarification":true,"rationale":"Pronoun unresolved; variable placeholder used."}
3) Utterance: "Actually, retract that: John is not Bob's parent."
{"intent":"retract","logic_string":"retract(parent(bob, john)).","components":{"atoms":["bob","john"],"variables":[],"predicates":["parent"]},"facts":["parent(bob, john)."],"rules":[],"queries":[],"confidence":{"overall":0.9,"intent":0.98,"logic":0.88},"ambiguities":[],"needs_clarification":false,"rationale":"Retraction request mapped to retract/1 target fact."}
4) Utterance: "Translate this to French: the build passed."
{"intent":"other","logic_string":"","components":{"atoms":[],"variables":[],"predicates":[]},"facts":[],"rules":[],"queries":[],"confidence":{"overall":0.9,"intent":0.95,"logic":0.9},"ambiguities":[],"needs_clarification":false,"rationale":"Translation command is out of logic-routing scope."}
Utterance:
$Utterance
"@
}

function Build-RepairPrompt {
  param(
    [string]$Utterance,
    [string]$Route,
    [string]$InvalidJson,
    [string[]]$Errors
  )
  $errorBlock = ($Errors | ForEach-Object { "- $_" }) -join "`n"
  return @"
/no_think
You are a strict JSON repairer for semantic parsing output.
Fix the candidate JSON so it matches the required schema and route constraints.
Return corrected JSON only. No markdown.
Route lock: $Route
Required keys:
intent,logic_string,components,facts,rules,queries,confidence,ambiguities,needs_clarification,rationale
Hard constraints:
- intent in assert_fact|assert_rule|query|retract|other
- components={atoms:[],variables:[],predicates:[]}
- confidence={overall:0..1,intent:0..1,logic:0..1}
- arrays: facts,rules,queries,ambiguities
- logic_string must be Prolog or empty (for intent=other only)
- assert_fact => logic_string == facts[0]
- assert_rule => logic_string == rules[0]
- query => logic_string == queries[0] and no '?-'
- retract => logic_string == retract(<fact>).
- other => logic_string=='' and facts/rules/queries empty
Original utterance:
$Utterance
Validation errors to fix:
$errorBlock
Candidate JSON:
$InvalidJson
"@
}

function Validate-OutputShape {
  param([psobject]$Parsed)

  $required = @(
    "intent","logic_string","components","facts","rules","queries",
    "confidence","ambiguities","needs_clarification","rationale"
  )
  $missing = @()
  foreach ($k in $required) {
    if (-not ($Parsed.PSObject.Properties.Name -contains $k)) { $missing += $k }
  }
  $allowedIntent = @("assert_fact","assert_rule","query","retract","other")
  $intentOk = $allowedIntent -contains [string]$Parsed.intent

  $logicString = [string]$Parsed.logic_string
  $logicOk = [string]::IsNullOrWhiteSpace($logicString) -or $logicString.Trim().EndsWith(".")
  $logicString = $logicString.Trim()

  $componentsOk = $false
  if ($Parsed.components -is [psobject]) {
    $cn = $Parsed.components.PSObject.Properties.Name
    $componentsOk = ($cn -contains "atoms") -and ($cn -contains "variables") -and ($cn -contains "predicates")
    if ($componentsOk) {
      $componentsOk = ($Parsed.components.atoms -is [System.Collections.IEnumerable]) -and
                      ($Parsed.components.variables -is [System.Collections.IEnumerable]) -and
                      ($Parsed.components.predicates -is [System.Collections.IEnumerable])
    }
  }

  $confidenceOk = $false
  if ($Parsed.confidence -is [psobject]) {
    $kn = $Parsed.confidence.PSObject.Properties.Name
    $confidenceOk = ($kn -contains "overall") -and ($kn -contains "intent") -and ($kn -contains "logic")
  }

  $arraysOk = ($Parsed.facts -is [System.Collections.IEnumerable]) -and
              ($Parsed.rules -is [System.Collections.IEnumerable]) -and
              ($Parsed.queries -is [System.Collections.IEnumerable]) -and
              ($Parsed.ambiguities -is [System.Collections.IEnumerable])

  $queryPrefixViolation = $false
  foreach ($q in @($Parsed.queries)) {
    if ([string]$q -match "^\s*\?-") { $queryPrefixViolation = $true; break }
  }

  $prologGoalPattern = "^[a-z][a-z0-9_]*\(([^()]*)\)\.$"
  $prologRulePattern = "^[a-z][a-z0-9_]*\(([^()]*)\)\s*:-\s*.+\.$"
  $prologRetractPattern = "^retract\(\s*[a-z][a-z0-9_]*\(([^()]*)\)\s*\)\.$"

  $routeConsistencyOk = $true
  $routeErrors = @()
  $intent = [string]$Parsed.intent
  $facts = @($Parsed.facts | ForEach-Object { [string]$_ })
  $rules = @($Parsed.rules | ForEach-Object { [string]$_ })
  $queries = @($Parsed.queries | ForEach-Object { [string]$_ })

  switch ($intent) {
    "assert_fact" {
      if ($facts.Count -lt 1) { $routeConsistencyOk = $false; $routeErrors += "assert_fact requires facts[0]." }
      if ($facts.Count -gt 0 -and $logicString -ne $facts[0].Trim()) { $routeConsistencyOk = $false; $routeErrors += "logic_string must equal facts[0] for assert_fact." }
      if ($facts.Count -gt 0 -and -not ($facts[0].Trim() -match $prologGoalPattern)) { $routeConsistencyOk = $false; $routeErrors += "facts[0] is not a valid Prolog fact/goal string." }
    }
    "assert_rule" {
      if ($rules.Count -lt 1) { $routeConsistencyOk = $false; $routeErrors += "assert_rule requires rules[0]." }
      if ($rules.Count -gt 0 -and $logicString -ne $rules[0].Trim()) { $routeConsistencyOk = $false; $routeErrors += "logic_string must equal rules[0] for assert_rule." }
      if ($rules.Count -gt 0 -and -not ($rules[0].Trim() -match $prologRulePattern)) { $routeConsistencyOk = $false; $routeErrors += "rules[0] is not a valid Prolog rule string." }
    }
    "query" {
      if ($queries.Count -lt 1) { $routeConsistencyOk = $false; $routeErrors += "query requires queries[0]." }
      if ($queries.Count -gt 0 -and $logicString -ne $queries[0].Trim()) { $routeConsistencyOk = $false; $routeErrors += "logic_string must equal queries[0] for query." }
      if ($queries.Count -gt 0 -and -not ($queries[0].Trim() -match $prologGoalPattern)) { $routeConsistencyOk = $false; $routeErrors += "queries[0] is not a valid Prolog query-goal string." }
    }
    "retract" {
      if (-not ($logicString -match $prologRetractPattern)) { $routeConsistencyOk = $false; $routeErrors += "retract intent requires logic_string format retract(<fact>)." }
      if ($facts.Count -gt 0 -and -not ($facts[0].Trim() -match $prologGoalPattern)) { $routeConsistencyOk = $false; $routeErrors += "facts[0] should be canonical positive target fact when provided." }
    }
    "other" {
      if (-not [string]::IsNullOrWhiteSpace($logicString)) { $routeConsistencyOk = $false; $routeErrors += "other intent requires empty logic_string." }
      if ($facts.Count -gt 0 -or $rules.Count -gt 0 -or $queries.Count -gt 0) { $routeConsistencyOk = $false; $routeErrors += "other intent requires empty facts/rules/queries." }
    }
  }

  $confidenceRangeOk = $true
  if ($Parsed.confidence -is [psobject]) {
    foreach ($k in @("overall","intent","logic")) {
      $v = $Parsed.confidence.$k
      $num = $null
      if (-not [double]::TryParse([string]$v, [ref]$num)) {
        $confidenceRangeOk = $false
      } elseif ($num -lt 0 -or $num -gt 1) {
        $confidenceRangeOk = $false
      }
    }
  }
  $errors = @()
  if ($missing.Count -gt 0) { $errors += "Missing keys: $($missing -join ', ')." }
  if (-not $intentOk) { $errors += "intent is not in allowed set." }
  if (-not $logicOk) { $errors += "logic_string must be empty or end with '.'." }
  if (-not $componentsOk) { $errors += "components shape invalid." }
  if (-not $confidenceOk) { $errors += "confidence shape invalid." }
  if (-not $confidenceRangeOk) { $errors += "confidence values must be numeric in [0,1]." }
  if (-not $arraysOk) { $errors += "facts/rules/queries/ambiguities must be arrays." }
  if ($queryPrefixViolation) { $errors += "queries must not include '?-' prefix." }
  if (-not $routeConsistencyOk) { $errors += $routeErrors }

  return [pscustomobject]@{
    missing = $missing
    intentOk = $intentOk
    logicOk = $logicOk
    componentsOk = $componentsOk
    confidenceOk = $confidenceOk
    confidenceRangeOk = $confidenceRangeOk
    arraysOk = $arraysOk
    queryPrefixViolation = $queryPrefixViolation
    routeConsistencyOk = $routeConsistencyOk
    errors = $errors
    passed = ($missing.Count -eq 0) -and $intentOk -and $logicOk -and $componentsOk -and $confidenceOk -and $confidenceRangeOk -and $arraysOk -and (-not $queryPrefixViolation) -and $routeConsistencyOk
  }
}

$apiKey = Get-ApiKey -Path $EnvFile
$headers = @{ "Content-Type" = "application/json" }
if ($Backend -eq "lmstudio" -and $apiKey) {
  $headers["Authorization"] = "Bearer $apiKey"
}

$route = ""
$classifierSource = "heuristic"
$heuristicRoute = Get-RouteHeuristic -Text $Utterance

if ($TwoPass) {
  $classifierPrompt = Build-ClassifierPrompt -Utterance $Utterance
  $cls = Invoke-ModelPrompt -Backend $Backend -BaseUrl $BaseUrl -Model $Model -PromptText $classifierPrompt -ContextLength 2048 -TimeoutSec $TimeoutSec -Headers $headers
  if ($cls.success) {
    $clsMessage = [string]$cls.message
    if (-not $clsMessage -and $cls.reasoning) {
      $clsMessage = Get-LastValidJsonObject -Text ([string]$cls.reasoning) -RequiredKeys @("route")
    }
    if ($clsMessage) {
      try {
        $parsedCls = $clsMessage | ConvertFrom-Json
        $candidateRoute = [string]$parsedCls.route
        if (@("assert_fact","assert_rule","query","retract","other") -contains $candidateRoute) {
          $route = $candidateRoute
          $classifierSource = "model"
        }
      } catch {
        # fall through to heuristic
      }
    }
  }
  if ($heuristicRoute -ne "assert_fact") {
    $route = $heuristicRoute
    $classifierSource = "heuristic_priority"
  } elseif (-not $route) {
    $route = $heuristicRoute
  }
} else {
  $route = $heuristicRoute
  $classifierSource = "one_pass"
}

Write-Host "route: $route (source: $classifierSource)"

$extractPrompt = Build-ExtractorPrompt -Utterance $Utterance -Route $route
$run = Invoke-ModelPrompt -Backend $Backend -BaseUrl $BaseUrl -Model $Model -PromptText $extractPrompt -ContextLength $ContextLength -TimeoutSec $TimeoutSec -Headers $headers

if (-not $run.success) {
  Write-Error "Model call failed: $($run.error)"
  exit 1
}

$message = [string]$run.message
if (-not $message -and $run.reasoning) {
  $message = Get-LastValidJsonObject -Text ([string]$run.reasoning) -RequiredKeys @("intent","components","confidence")
  if ($message) {
    Write-Host "No message payload; using JSON fallback extracted from reasoning."
  }
}

if (-not $message) {
  Write-Host "No message payload found. Raw response:"
  $run.raw | ConvertTo-Json -Depth 10
  exit 1
}

Write-Host "Model output:"
Write-Host $message

try {
  $parsed = $message | ConvertFrom-Json
  Write-Host ""
  Write-Host "JSON parse: OK"
  $v = Validate-OutputShape -Parsed $parsed
  if (-not $v.passed) {
    $repairPrompt = Build-RepairPrompt -Utterance $Utterance -Route $route -InvalidJson $message -Errors @($v.errors)
    $repairRun = Invoke-ModelPrompt -Backend $Backend -BaseUrl $BaseUrl -Model $Model -PromptText $repairPrompt -ContextLength $ContextLength -TimeoutSec $TimeoutSec -Headers $headers
    if ($repairRun.success) {
      $repairMessage = [string]$repairRun.message
      if (-not $repairMessage -and $repairRun.reasoning) {
        $repairMessage = Get-LastValidJsonObject -Text ([string]$repairRun.reasoning) -RequiredKeys @("intent","components","confidence")
      }
      if ($repairMessage) {
        Write-Host "repair_pass: applied"
        Write-Host "Repaired output:"
        Write-Host $repairMessage
        try {
          $parsed = $repairMessage | ConvertFrom-Json
          $v = Validate-OutputShape -Parsed $parsed
          $message = $repairMessage
        } catch {
          Write-Host "repair_pass: parse_failed"
        }
      }
    }
  }
  Write-Host "intent: $($parsed.intent)"
  Write-Host "logic_string: $($parsed.logic_string)"
  Write-Host "required_keys_missing: $($v.missing.Count)"
  Write-Host "intent_allowed: $($v.intentOk)"
  Write-Host "logic_format_ok: $($v.logicOk)"
  Write-Host "components_shape_ok: $($v.componentsOk)"
  Write-Host "confidence_shape_ok: $($v.confidenceOk)"
  Write-Host "confidence_range_ok: $($v.confidenceRangeOk)"
  Write-Host "arrays_shape_ok: $($v.arraysOk)"
  Write-Host "query_prefix_violation: $($v.queryPrefixViolation)"
  Write-Host "route_consistency_ok: $($v.routeConsistencyOk)"
  if ($v.errors.Count -gt 0) {
    Write-Host "validation_errors:"
    foreach ($err in $v.errors) { Write-Host "- $err" }
  }
  if (-not $v.passed) {
    Write-Host "validation_status: FAILED"
    exit 3
  }
  Write-Host "validation_status: PASSED"
} catch {
  Write-Host ""
  Write-Host "JSON parse: FAILED"
  exit 2
}
