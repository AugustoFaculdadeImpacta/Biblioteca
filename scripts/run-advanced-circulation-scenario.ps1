param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('atraso', 'limite', 'fifo', 'concorrencia')]
    [string]$Scenario,
    [switch]$CaptureFifoBaseline,
    [ValidateSet('ms', 's')]
    [string]$VenceEmUnit = 'ms',
    [switch]$ProbeDevolvidoEmNull,
    [switch]$UseBusinessLoan,
    [switch]$CheckReservation
)

$ErrorActionPreference = 'Stop'
$env:PYTHONDONTWRITEBYTECODE = '1'
Add-Type -AssemblyName System.Net.Http

$script:WorkspaceId = 151966
$script:MetadataBase = 'https://x8ki-letl-twmt.n7.xano.io/api:meta'
$script:ApiHost = 'x8ki-letl-twmt.n7.xano.io'
$script:ResultsPath = Join-Path $PSScriptRoot '..\openspec\changes\corrigir-regras-circulacao\RESULTS.md'
$script:Client = [System.Net.Http.HttpClient]::new()
$script:Fixtures = New-Object System.Collections.Generic.List[object]
$script:TableIds = @{}
$script:UserTokens = @{}
$script:BaselineUserIds = @()
$script:BaselineCounts = @{}
$script:RunError = $null
$script:FunctionalFailure = $false
$script:CurrentStage = "cenario $Scenario"

function Add-Result {
    param([Parameter(Mandatory = $true)][string]$Text)

    [System.IO.File]::AppendAllText(
        $script:ResultsPath,
        $Text + [Environment]::NewLine,
        [System.Text.UTF8Encoding]::new($false)
    )
}

function Invoke-Http {
    param(
        [Parameter(Mandatory = $true)][string]$Base,
        [Parameter(Mandatory = $true)][ValidateSet('GET', 'POST', 'PUT', 'DELETE')][string]$Method,
        [Parameter(Mandatory = $true)][string]$Path,
        [string]$Token,
        [switch]$Metadata,
        [object]$Body,
        [switch]$NoPause
    )

    if (-not $NoPause) {
        Start-Sleep -Seconds 2
    }

    $delays = @(3, 6, 12, 24, 48, 60)
    for ($attempt = 0; $attempt -le $delays.Count; $attempt++) {
        $request = [System.Net.Http.HttpRequestMessage]::new(
            [System.Net.Http.HttpMethod]::new($Method),
            "$Base/$($Path.TrimStart('/'))"
        )
        if (-not [string]::IsNullOrWhiteSpace($Token)) {
            $request.Headers.Authorization = [System.Net.Http.Headers.AuthenticationHeaderValue]::new('Bearer', $Token)
        }
        if ($Metadata) {
            [void]$request.Headers.Add('x-data-source', 'live')
        }
        if ($PSBoundParameters.ContainsKey('Body')) {
            $json = ConvertTo-Json -InputObject $Body -Depth 15 -Compress
            $request.Content = [System.Net.Http.StringContent]::new($json, [System.Text.Encoding]::UTF8, 'application/json')
        }

        $response = $null
        try {
            $response = $script:Client.SendAsync($request).GetAwaiter().GetResult()
            $status = [int]$response.StatusCode
            $content = $response.Content.ReadAsStringAsync().GetAwaiter().GetResult()
            $parsed = $null
            if (-not [string]::IsNullOrWhiteSpace($content)) {
                try {
                    $parsed = ConvertFrom-Json -InputObject $content -ErrorAction Stop
                }
                catch {
                    $parsed = $null
                }
            }
        }
        catch {
            throw "Falha de transporte HTTP na etapa '$script:CurrentStage'."
        }
        finally {
            if ($null -ne $response) {
                $response.Dispose()
            }
            $request.Dispose()
        }

        if ($status -ne 429) {
            return [pscustomobject]@{
                Status = $status
                Body = $parsed
                Method = $Method
            }
        }
        if ($Method -eq 'POST') {
            return [pscustomobject]@{
                Status = $status
                Body = $parsed
                Method = $Method
            }
        }
        if ($attempt -ge $delays.Count) {
            return [pscustomobject]@{
                Status = $status
                Body = $parsed
                Method = $Method
            }
        }
        Start-Sleep -Seconds $delays[$attempt]
    }
    throw 'Repetições HTTP encerradas sem resposta.'
}

function Invoke-ParallelPost {
    param([Parameter(Mandatory = $true)][object[]]$Calls)

    Start-Sleep -Seconds 2
    $pending = New-Object System.Collections.Generic.List[object]
    foreach ($call in $Calls) {
        $request = [System.Net.Http.HttpRequestMessage]::new(
            [System.Net.Http.HttpMethod]::Post,
            "$($script:ApiBase)/$($call.Path.TrimStart('/'))"
        )
        $request.Headers.Authorization = [System.Net.Http.Headers.AuthenticationHeaderValue]::new(
            'Bearer',
            [string]$call.Token
        )
        $json = ConvertTo-Json -InputObject $call.Body -Depth 12 -Compress
        $request.Content = [System.Net.Http.StringContent]::new(
            $json,
            [System.Text.Encoding]::UTF8,
            'application/json'
        )
        $pending.Add([pscustomobject]@{
            Request = $request
            Task = $script:Client.SendAsync($request)
            Label = $call.Label
            Path = $call.Path
            Token = $call.Token
            Body = $call.Body
        })
    }

    [System.Threading.Tasks.Task]::WaitAll([System.Threading.Tasks.Task[]]@($pending | ForEach-Object { $_.Task }))
    $results = New-Object System.Collections.Generic.List[object]
    foreach ($entry in $pending) {
        $response = $entry.Task.GetAwaiter().GetResult()
        $content = $response.Content.ReadAsStringAsync().GetAwaiter().GetResult()
        $parsed = $null
        if (-not [string]::IsNullOrWhiteSpace($content)) {
            try {
                $parsed = ConvertFrom-Json -InputObject $content -ErrorAction Stop
            }
            catch {
                $parsed = $null
            }
        }
        $result = [pscustomobject]@{
            Label = $entry.Label
            Status = [int]$response.StatusCode
            Body = $parsed
        }
        $response.Dispose()
        $entry.Request.Dispose()
        $results.Add($result)
    }
    return ,$results.ToArray()
}

function Get-ObjectId {
    param([object]$Value)

    if ($null -eq $Value) {
        return $null
    }
    if ($null -ne $Value.id) {
        return [int64]$Value.id
    }
    foreach ($property in @('record', 'item', 'data', 'usuario', 'reserva', 'solicitacao', 'emprestimo', 'exemplar')) {
        if ($null -ne $Value.$property -and $null -ne $Value.$property.id) {
            return [int64]$Value.$property.id
        }
    }
    return $null
}

function Get-SanitizedErrorSummary {
    param([object]$Body)

    $property = if ($null -eq $Body) { $null } else { $Body.PSObject.Properties['message'] }
    if ($null -eq $property -or [string]::IsNullOrWhiteSpace([string]$property.Value)) {
        return 'mensagem não informada'
    }

    $message = [string]$property.Value
    $message = $message -replace '(?i)\bBearer\s+\S+', 'Bearer [omitido]'
    $message = $message -replace '(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', '[e-mail]'
    $message = $message -replace '(?i)\bhttps?://\S+', '[url]'
    $message = $message -replace '(?i)\bzz-teste-[A-Za-z0-9_-]+', '[fixture]'
    $message = $message -replace '\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b', '[id]'
    $message = $message -replace '\b\d{3,}\b', '[número]'
    $message = $message -replace '\b[A-Za-z0-9._~+/-]{32,}\b', '[conteúdo]'
    $message = ($message -replace '[\r\n\t]+', ' ').Trim()
    if ($message.Length -gt 220) {
        $message = $message.Substring(0, 220) + '…'
    }
    return $message
}

function Register-Fixture {
    param(
        [Parameter(Mandatory = $true)][string]$Table,
        [Parameter(Mandatory = $true)][int64]$Id,
        [Parameter(Mandatory = $true)][string]$Kind
    )

    if (@($script:Fixtures | Where-Object { $_.Table -eq $Table -and $_.Id -eq $Id }).Count -gt 0) {
        return
    }
    $fixture = [pscustomobject]@{
        Table = $Table
        Id = $Id
        Kind = $Kind
    }
    $script:Fixtures.Add($fixture)
    Add-Result "- Fixture registrada: ``$Table/$Id`` ($Kind)."
}

function Get-PagedItems {
    param([Parameter(Mandatory = $true)][string]$Path)

    $all = New-Object System.Collections.Generic.List[object]
    $page = 1
    $expectedTotal = $null
    while ($true) {
        $separator = if ($Path.Contains('?')) { '&' } else { '?' }
        $response = Invoke-Http -Base $script:MetadataBase -Method GET -Path "$Path$separator`page=$page&per_page=100" -Token $script:MetadataToken -Metadata
        if ($response.Status -ne 200 -or $null -eq $response.Body) {
            throw "GET paginado falhou com HTTP $($response.Status)."
        }
        if ($null -eq $expectedTotal -and $null -ne $response.Body.itemsTotal) {
            $expectedTotal = [int]$response.Body.itemsTotal
        }
        foreach ($item in @($response.Body.items)) {
            if ($null -ne $item) {
                $all.Add($item)
            }
        }
        if ($null -eq $response.Body.nextPage) {
            break
        }
        $next = [int]$response.Body.nextPage
        if ($next -le $page) {
            throw 'Paginação sem progresso.'
        }
        $page = $next
    }
    if ($null -ne $expectedTotal -and $all.Count -ne $expectedTotal) {
        throw 'Paginação incompleta.'
    }
    return ,$all.ToArray()
}

function Get-Rows {
    param([Parameter(Mandatory = $true)][string]$Table)

    return ,(Get-PagedItems -Path "workspace/$($script:WorkspaceId)/table/$($script:TableIds[$Table])/content")
}

function Get-Record {
    param(
        [Parameter(Mandatory = $true)][string]$Table,
        [Parameter(Mandatory = $true)][int64]$Id
    )

    return Invoke-Http -Base $script:MetadataBase -Method GET -Path "workspace/$($script:WorkspaceId)/table/$($script:TableIds[$Table])/content/$Id" -Token $script:MetadataToken -Metadata
}

function New-Record {
    param(
        [Parameter(Mandatory = $true)][string]$Table,
        [Parameter(Mandatory = $true)][string]$Kind,
        [Parameter(Mandatory = $true)][hashtable]$Data
    )

    $response = Invoke-Http -Base $script:MetadataBase -Method POST -Path "workspace/$($script:WorkspaceId)/table/$($script:TableIds[$Table])/content" -Token $script:MetadataToken -Metadata -Body $Data
    if ($response.Status -lt 200 -or $response.Status -ge 300) {
        throw "POST individual em $Table falhou com HTTP $($response.Status)."
    }
    $id = Get-ObjectId $response.Body
    if ($null -eq $id) {
        throw "POST individual em $Table não retornou ID."
    }
    Register-Fixture -Table $Table -Id $id -Kind $Kind
    return $response.Body
}

function Update-Record {
    param(
        [Parameter(Mandatory = $true)][string]$Table,
        [Parameter(Mandatory = $true)][int64]$Id,
        [Parameter(Mandatory = $true)][hashtable]$Changes,
        [switch]$OnlyChanges
    )

    if ($OnlyChanges) {
        $body = $Changes
    }
    else {
        $current = Get-Record -Table $Table -Id $Id
        if ($current.Status -ne 200 -or $null -eq $current.Body) {
            throw "GET antes do PUT em $Table/$Id falhou com HTTP $($current.Status)."
        }
        $body = @{}
        foreach ($property in $current.Body.PSObject.Properties) {
            if ($property.Name -ne 'id') {
                $body[$property.Name] = $property.Value
            }
        }
        foreach ($key in $Changes.Keys) {
            $body[$key] = $Changes[$key]
        }
    }
    $update = Invoke-Http -Base $script:MetadataBase -Method PUT -Path "workspace/$($script:WorkspaceId)/table/$($script:TableIds[$Table])/content/$Id" -Token $script:MetadataToken -Metadata -Body $body
    $readback = Get-Record -Table $Table -Id $Id
    return [pscustomobject]@{
        UpdateStatus = $update.Status
        ReadStatus = $readback.Status
        Record = $readback.Body
    }
}

function Convert-ToEpochMilliseconds {
    param([Parameter(Mandatory = $true)][object]$Value)

    if ($Value -is [DateTimeOffset]) {
        return $Value.ToUnixTimeMilliseconds()
    }
    if ($Value -is [DateTime]) {
        return ([DateTimeOffset]$Value).ToUnixTimeMilliseconds()
    }
    if ($Value -is [byte] -or $Value -is [int16] -or $Value -is [int32] -or $Value -is [int64] -or $Value -is [single] -or $Value -is [double] -or $Value -is [decimal]) {
        $number = [double]$Value
        if ([Math]::Abs($number) -lt 100000000000) {
            return [int64]($number * 1000)
        }
        return [int64]$number
    }
    $text = [string]$Value
    $numberValue = 0.0
    if ([double]::TryParse($text, [Globalization.NumberStyles]::Float, [Globalization.CultureInfo]::InvariantCulture, [ref]$numberValue)) {
        if ([Math]::Abs($numberValue) -lt 100000000000) {
            return [int64]($numberValue * 1000)
        }
        return [int64]$numberValue
    }
    return [DateTimeOffset]::Parse($text, [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal).ToUnixTimeMilliseconds()
}

function New-RandomPassword {
    $bytes = New-Object byte[] 32
    $random = [Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $random.GetBytes($bytes)
    }
    finally {
        $random.Dispose()
    }
    return [Convert]::ToBase64String($bytes).TrimEnd('=').Replace('+', '-').Replace('/', '_') + 'Zz9!'
}

function New-TestUser {
    param([Parameter(Mandatory = $true)][ValidateSet('bibliotecario', 'estudante')][string]$Role)

    $suffix = [guid]::NewGuid().ToString('N')
    $email = "zz-teste-$suffix" + [string][char]64 + 'exemplo.invalid'
    $password = New-RandomPassword
    $user = New-Record -Table 'usuario' -Kind "usuario sintetico $Role" -Data @{
        nome = "zz-teste-$suffix"
        email = $email
        senha = $password
        perfil = $Role
    }
    $id = Get-ObjectId $user
    $login = Invoke-Http -Base $script:ApiBase -Method POST -Path 'auth/login' -Body @{
        email = $email
        senha = $password
    }
    if ($login.Status -ne 200 -or [string]::IsNullOrWhiteSpace([string]$login.Body.authToken) -or $login.Body.usuario.perfil -cne $Role) {
        throw "Login do usuário sintético $Role não confirmado (HTTP $($login.Status))."
    }
    $tokenKey = if ($Role -eq 'bibliotecario') { 'bibliotecario' } else { "estudante-$id" }
    $script:UserTokens[$tokenKey] = [string]$login.Body.authToken
    return $id
}

function New-TestTitle {
    param([Parameter(Mandatory = $true)][string]$Label)

    $suffix = [guid]::NewGuid().ToString('N')
    $record = New-Record -Table 'titulo' -Kind "titulo sintetico $Label" -Data @{
        titulo = "zz-teste-$Label-$suffix"
        autores = 'Autor de teste'
    }
    return Get-ObjectId $record
}

function New-TestExemplar {
    param(
        [Parameter(Mandatory = $true)][int64]$TitleId,
        [Parameter(Mandatory = $true)][string]$Label,
        [string]$State = 'disponivel'
    )

    $record = New-Record -Table 'exemplar' -Kind "exemplar sintetico $Label" -Data @{
        titulo_id = $TitleId
        codigo_tombo = "ZZ-$([guid]::NewGuid().ToString('N'))"
        estado = $State
    }
    return Get-ObjectId $record
}

function New-TestLoan {
    param(
        [Parameter(Mandatory = $true)][int64]$UserId,
        [Parameter(Mandatory = $true)][int64]$ExemplarId,
        [Parameter(Mandatory = $true)][string]$Label,
        [switch]$ExplicitNullDevolvidoEm
    )

    $now = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
    $data = @{
        usuario_id = $UserId
        exemplar_id = $ExemplarId
        retirado_em = $now - 86400000
        vence_em = $now + 86400000
    }
    if ($ExplicitNullDevolvidoEm) {
        $data.devolvido_em = $null
    }
    $record = New-Record -Table 'emprestimo' -Kind "emprestimo sintetico $Label" -Data $data
    return Get-ObjectId $record
}

function New-TestRequest {
    param(
        [Parameter(Mandatory = $true)][int64]$UserId,
        [Parameter(Mandatory = $true)][int64]$TitleId,
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][int64]$RequestedAt
    )

    $record = New-Record -Table 'solicitacao_emprestimo' -Kind "solicitacao sintetica $Label" -Data @{
        usuario_id = $UserId
        titulo_id = $TitleId
        solicitada_em = $RequestedAt
        estado = 'pendente'
    }
    return Get-ObjectId $record
}

function New-TestReservation {
    param(
        [Parameter(Mandatory = $true)][int64]$UserId,
        [Parameter(Mandatory = $true)][int64]$TitleId,
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][int64]$CreatedAt
    )

    $record = New-Record -Table 'reserva' -Kind "reserva sintetica $Label" -Data @{
        usuario_id = $UserId
        titulo_id = $TitleId
        criada_em = $CreatedAt
        estado = 'aguardando'
    }
    return Get-ObjectId $record
}

function Register-RelatedReservations {
    param(
        [Parameter(Mandatory = $true)][int64]$UserId,
        [Parameter(Mandatory = $true)][int64]$TitleId
    )

    $related = @(Get-Rows -Table 'reserva' | Where-Object {
        [int64]$_.usuario_id -eq $UserId -and [int64]$_.titulo_id -eq $TitleId
    })
    foreach ($reservation in $related) {
        Register-Fixture -Table 'reserva' -Id ([int64]$reservation.id) -Kind 'reserva vinculada a solicitacao do cenario'
    }
}

function Register-RelatedLoans {
    param(
        [Parameter(Mandatory = $true)][int64]$UserId,
        [Parameter(Mandatory = $true)][object[]]$ExemplarIds,
        [Parameter(Mandatory = $true)][string]$Kind
    )

    $exemplarIdSet = @{}
    foreach ($exemplarId in $ExemplarIds) {
        $exemplarIdSet[[string]$exemplarId] = $true
    }
    $related = @(Get-Rows -Table 'emprestimo' | Where-Object {
        [string]$_.usuario_id -eq [string]$UserId -and $exemplarIdSet.ContainsKey([string]$_.exemplar_id)
    })
    foreach ($loan in $related) {
        Register-Fixture -Table 'emprestimo' -Id ([int64]$loan.id) -Kind $Kind
    }
    return $related.Count
}

function Register-RelatedExemplars {
    param(
        [Parameter(Mandatory = $true)][int64]$TitleId,
        [Parameter(Mandatory = $true)][string]$Kind
    )

    $related = @(Get-Rows -Table 'exemplar' | Where-Object { [string]$_.titulo_id -eq [string]$TitleId })
    foreach ($exemplar in $related) {
        Register-Fixture -Table 'exemplar' -Id ([int64]$exemplar.id) -Kind $Kind
    }
    return ,$related
}

function Invoke-Business {
    param(
        [Parameter(Mandatory = $true)][string]$Method,
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Token,
        [object]$Body = @{}
    )

    if ($Method -eq 'GET') {
        return Invoke-Http -Base $script:ApiBase -Method GET -Path $Path -Token $Token
    }
    return Invoke-Http -Base $script:ApiBase -Method $Method -Path $Path -Token $Token -Body $Body
}

function Test-Precheck {
    param([switch]$AllowExpiredFixture)

    $branches = Invoke-Http -Base $script:MetadataBase -Method GET -Path "workspace/$($script:WorkspaceId)/branch" -Token $script:MetadataToken -Metadata
    if ($branches.Status -ne 200 -or @($branches.Body | Where-Object { $_.label -eq 'v1' -and $_.live -eq $true }).Count -ne 1) {
        throw 'Branch v1 live não confirmada.'
    }
    $rows = @{}
    foreach ($table in @('reserva', 'emprestimo', 'solicitacao_emprestimo', 'usuario', 'exemplar', 'titulo')) {
        $rows[$table] = Get-Rows -Table $table
        $allowed = @($script:Fixtures | Where-Object { $_.Table -eq $table } | ForEach-Object { [string]$_.Id })
        if ($table -eq 'usuario') {
            $allowed += @($script:BaselineUserIds | ForEach-Object { [string]$_ })
        }
        if (@($rows[$table] | Where-Object { [string]$_.id -notin $allowed }).Count -gt 0) {
            throw "Pré-check detectou registros fora das fixtures em $table."
        }
    }
    $now = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
    $offered = @($rows.reserva | Where-Object { $_.estado -eq 'ofertada' })
    $unclassifiable = @($offered | Where-Object { $null -eq $_.expira_em })
    $expired = @($offered | Where-Object {
        $null -ne $_.expira_em -and (Convert-ToEpochMilliseconds $_.expira_em) -lt $now
    })
    $active = @($rows.emprestimo | Where-Object { $null -eq $_.devolvido_em })
    $pending = @($rows.solicitacao_emprestimo | Where-Object { $_.estado -eq 'pendente' })
    $fixtureReservationIds = @($script:Fixtures | Where-Object { $_.Table -eq 'reserva' } | ForEach-Object { [string]$_.Id })
    $fixtureLoanIds = @($script:Fixtures | Where-Object { $_.Table -eq 'emprestimo' } | ForEach-Object { [string]$_.Id })
    $fixtureRequestIds = @($script:Fixtures | Where-Object { $_.Table -eq 'solicitacao_emprestimo' } | ForEach-Object { [string]$_.Id })
    if ($unclassifiable.Count -gt 0 -or
        @($expired | Where-Object { [string]$_.id -notin $fixtureReservationIds }).Count -gt 0 -or
        @($active | Where-Object { [string]$_.id -notin $fixtureLoanIds }).Count -gt 0 -or
        @($pending | Where-Object { [string]$_.id -notin $fixtureRequestIds }).Count -gt 0) {
        throw 'Pré-check detectou estado crítico fora das fixtures ou não classificável.'
    }
    if (-not $AllowExpiredFixture -and ($expired.Count -gt 0 -or $active.Count -gt 0 -or $pending.Count -gt 0)) {
        throw 'Pré-check encontrou estado crítico antes de teste global.'
    }
    if ($AllowExpiredFixture -and $expired.Count -ne 1) {
        throw 'Pré-check não encontrou exatamente uma oferta vencida de fixture.'
    }
    return [pscustomobject]@{
        Expired = $expired.Count
        Active = $active.Count
        Pending = $pending.Count
    }
}

function Remove-Fixtures {
    foreach ($table in @('reserva', 'emprestimo', 'solicitacao_emprestimo', 'exemplar', 'titulo', 'usuario')) {
        foreach ($fixture in @($script:Fixtures | Where-Object { $_.Table -eq $table })) {
            $path = "workspace/$($script:WorkspaceId)/table/$($script:TableIds[$table])/content/$($fixture.Id)"
            $before = Invoke-Http -Base $script:MetadataBase -Method GET -Path $path -Token $script:MetadataToken -Metadata
            if ($before.Status -ne 200) {
                Add-Result "- Limpeza interrompida: ``$table/$($fixture.Id)``; GET inicial HTTP $($before.Status)."
                return $false
            }
            $deleted = Invoke-Http -Base $script:MetadataBase -Method DELETE -Path $path -Token $script:MetadataToken -Metadata
            if ($deleted.Status -lt 200 -or $deleted.Status -ge 300) {
                Add-Result "- Limpeza interrompida: ``$table/$($fixture.Id)``; DELETE HTTP $($deleted.Status)."
                return $false
            }
            $after = Invoke-Http -Base $script:MetadataBase -Method GET -Path $path -Token $script:MetadataToken -Metadata
            if ($after.Status -ne 404) {
                Add-Result "- Limpeza interrompida: ``$table/$($fixture.Id)``; GET pós-DELETE HTTP $($after.Status)."
                return $false
            }
            Add-Result "- Limpeza confirmada: ``$table/$($fixture.Id)``; DELETE HTTP $($deleted.Status), GET HTTP 404."
            [void]$script:Fixtures.Remove($fixture)
        }
    }
    return $true
}

function Get-FinalCounts {
    $counts = @{}
    foreach ($table in @('reserva', 'emprestimo', 'solicitacao_emprestimo', 'exemplar', 'titulo', 'usuario')) {
        $counts[$table] = (Get-Rows -Table $table).Count
    }
    $currentUsers = @((Get-Rows -Table 'usuario') | ForEach-Object { [string]$_.id } | Sort-Object)
    $originalUsers = @($script:BaselineUserIds | ForEach-Object { [string]$_ } | Sort-Object)
    $usersPreserved = (($currentUsers -join ',') -ceq ($originalUsers -join ','))
    $pass = $counts.reserva -eq 0 -and $counts.emprestimo -eq 0 -and
        $counts.solicitacao_emprestimo -eq 0 -and $counts.exemplar -eq 0 -and
        $counts.titulo -eq $script:BaselineCounts.titulo -and $counts.usuario -eq 2 -and $usersPreserved
    Add-Result "- Contagens após limpeza do cenário: reserva=$($counts.reserva), emprestimo=$($counts.emprestimo), solicitacao_emprestimo=$($counts.solicitacao_emprestimo), exemplar=$($counts.exemplar), titulo=$($counts.titulo), usuario=$($counts.usuario); usuários originais preservados=$usersPreserved."
    return $pass
}

function Initialize-Target {
    $script:MetadataToken = (xano profile token 2>$null | Out-String).Trim()
    if ([string]::IsNullOrWhiteSpace($script:MetadataToken)) {
        throw 'Credencial Xano não disponível no perfil selecionado.'
    }

    $groups = Get-PagedItems -Path "workspace/$($script:WorkspaceId)/apigroup?branch=v1"
    $library = @($groups | Where-Object { $_.name -eq 'Biblioteca' -and $_.branch -eq 'v1' })
    if ($library.Count -ne 1) {
        throw 'Grupo Biblioteca da branch v1 não foi resolvido unicamente.'
    }
    $spec = Invoke-Http -Base $script:MetadataBase -Method GET -Path "workspace/$($script:WorkspaceId)/apigroup/$($library[0].id)/openapi" -Token $script:MetadataToken -Metadata
    if ($spec.Status -ne 200 -or $null -eq $spec.Body.servers -or $null -eq $spec.Body.paths) {
        throw 'OpenAPI oficial do grupo Biblioteca indisponível.'
    }
    $server = [string]$spec.Body.servers[0].url
    if ($server -match '\{host\}' -and $null -ne $spec.Body.servers[0].variables.host.default) {
        $server = $server.Replace('{host}', [string]$spec.Body.servers[0].variables.host.default)
    }
    $uri = [uri]$server
    if ($uri.Host -ne $script:ApiHost -or $uri.Query -or $uri.AbsolutePath -notmatch '^/api:[A-Za-z0-9_-]+$') {
        throw 'Origem pública do grupo não corresponde ao host permitido.'
    }
    $script:ApiBase = $uri.GetLeftPart([System.UriPartial]::Path)

    $tables = Get-PagedItems -Path "workspace/$($script:WorkspaceId)/table"
    foreach ($table in $tables) {
        if ($table.name -in @('reserva', 'emprestimo', 'solicitacao_emprestimo', 'usuario', 'exemplar', 'titulo')) {
            $script:TableIds[$table.name] = [int64]$table.id
        }
    }
    foreach ($name in @('reserva', 'emprestimo', 'solicitacao_emprestimo', 'usuario', 'exemplar', 'titulo')) {
        if (-not $script:TableIds.ContainsKey($name)) {
            throw "Tabela autorizada ausente: $name."
        }
    }

    $script:BaselineUserIds = @((Get-Rows -Table 'usuario') | ForEach-Object { [int64]$_.id })
    if ($script:BaselineUserIds.Count -ne 2) {
        throw 'Quantidade inicial de usuários não é 2.'
    }
    foreach ($table in @('reserva', 'emprestimo', 'solicitacao_emprestimo', 'exemplar', 'titulo', 'usuario')) {
        $rows = Get-Rows -Table $table
        $script:BaselineCounts[$table] = $rows.Count
        $allowedIds = @($script:BaselineUserIds | ForEach-Object { [string]$_ })
        if ($table -eq 'usuario' -and @($rows | Where-Object { [string]$_.id -notin $allowedIds }).Count -gt 0) {
            throw 'Usuário adicional encontrado no pré-check.'
        }
        if ($table -ne 'usuario' -and $rows.Count -ne 0) {
            throw "Pré-check encontrou dados preexistentes em $table."
        }
    }
    if ($script:BaselineCounts.usuario -ne 2) {
        throw 'Pré-check encontrou contagem de usuários inesperada.'
    }
    $initial = Test-Precheck
    Add-Result "- Pré-check do cenário ``$Scenario``: branch v1 live; contagens-base reserva=0, emprestimo=0, solicitacao_emprestimo=0, exemplar=0, titulo=0, usuario=2; estados críticos=0. PASSOU."
}

function Get-ReturnedTimestampState {
    param([Parameter(Mandatory = $true)][object]$Record)

    $property = $Record.PSObject.Properties['devolvido_em']
    if ($null -eq $property -or $null -eq $property.Value) {
        return 'null'
    }
    if (($property.Value -is [byte] -or $property.Value -is [int16] -or $property.Value -is [int32] -or $property.Value -is [int64] -or $property.Value -is [single] -or $property.Value -is [double] -or $property.Value -is [decimal]) -and [double]$property.Value -eq 0) {
        return 'numero_zero'
    }
    return 'preenchido'
}

function Invoke-DevolvidoEmNullProbe {
    $student = New-TestUser -Role 'estudante'
    $title = New-TestTitle -Label 'null-probe'
    $exemplar = New-TestExemplar -TitleId $title -Label 'null-probe' -State 'emprestado'
    $loan = New-TestLoan -UserId $student -ExemplarId $exemplar -Label 'null-probe' -ExplicitNullDevolvidoEm
    $postRead = Get-Record -Table 'emprestimo' -Id $loan
    if ($postRead.Status -ne 200) {
        throw "GET após POST da fixture de empréstimo falhou com HTTP $($postRead.Status)."
    }
    $postState = Get-ReturnedTimestampState -Record $postRead.Body
    Add-Result "- Probe devolvido_em null: POST individual incluiu JSON null; GET HTTP $($postRead.Status); estado lido=$postState."
    if ($postState -eq 'null') {
        return
    }

    $put = Update-Record -Table 'emprestimo' -Id $loan -Changes @{ devolvido_em = $null } -OnlyChanges
    if ($put.ReadStatus -ne 200) {
        throw "GET após PUT null de devolvido_em falhou com HTTP $($put.ReadStatus)."
    }
    $putState = Get-ReturnedTimestampState -Record $put.Record
    Add-Result "- Probe devolvido_em null: PUT individual enviou somente JSON null para devolvido_em; PUT HTTP $($put.UpdateStatus); GET HTTP $($put.ReadStatus); estado lido=$putState."
    if ($put.UpdateStatus -lt 200 -or $put.UpdateStatus -ge 300) {
        throw "PUT null de devolvido_em falhou com HTTP $($put.UpdateStatus)."
    }
}

function Invoke-ScenarioAtraso {
    param(
        [ValidateSet('ms', 's')][string]$TimestampUnit = 'ms',
        [switch]$UseBusinessLoanFixture,
        [switch]$ProbeNullOnly,
        [switch]$CheckReservation
    )

    if ($ProbeNullOnly) {
        Invoke-DevolvidoEmNullProbe
        return
    }
    $student = New-TestUser -Role 'estudante'
    $title = New-TestTitle -Label 'atraso'
    $exemplarState = if ($UseBusinessLoanFixture) { 'disponivel' } else { 'emprestado' }
    $exemplar = New-TestExemplar -TitleId $title -Label 'atraso' -State $exemplarState
    if ($UseBusinessLoanFixture) {
        $librarian = New-TestUser -Role 'bibliotecario'
        $requestId = New-TestRequest -UserId $student -TitleId $title -Label 'atraso' -RequestedAt ([DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds() - 60000)
        $withdrawal = Invoke-Business -Method POST -Path "admin/solicitacoes/$requestId/retirada" -Token $script:UserTokens['bibliotecario']
        if ($withdrawal.Status -lt 200 -or $withdrawal.Status -ge 300) {
            throw "Criação da fixture pela retirada de negócio falhou com HTTP $($withdrawal.Status)."
        }
        $loan = Get-ObjectId $withdrawal.Body
        if ($null -eq $loan) {
            $related = @(Get-Rows -Table 'emprestimo' | Where-Object {
                [string]$_.usuario_id -eq [string]$student -and [string]$_.exemplar_id -eq [string]$exemplar
            })
            if ($related.Count -ne 1) {
                throw 'Retirada de negócio não permitiu identificar unicamente a fixture do empréstimo.'
            }
            $loan = [int64]$related[0].id
            Register-Fixture -Table 'emprestimo' -Id $loan -Kind 'emprestimo criado pela rota de retirada'
        }
        else {
            Register-Fixture -Table 'emprestimo' -Id $loan -Kind 'emprestimo criado pela rota de retirada'
        }
    }
    else {
        $loan = New-TestLoan -UserId $student -ExemplarId $exemplar -Label 'atraso' -ExplicitNullDevolvidoEm
    }
    $creationRead = Get-Record -Table 'emprestimo' -Id $loan
    if ($creationRead.Status -ne 200 -or $null -eq $creationRead.Body) {
        throw "GET da fixture antes de alterar vence_em falhou com HTTP $($creationRead.Status)."
    }
    $createdDue = $creationRead.Body.vence_em
    $createdDueType = if ($null -eq $createdDue) { 'null' } else { $createdDue.GetType().FullName }
    $createdDueMagnitude = if ($null -eq $createdDue) { 'ausente' } elseif ([Math]::Abs([double]$createdDue) -lt 100000000000) { 'segundos' } else { 'milissegundos' }
    $createdReturnedState = Get-ReturnedTimestampState -Record $creationRead.Body
    Add-Result "- Empréstimo recém-criado ($TimestampUnit; origem=$(if ($UseBusinessLoanFixture) { 'rota_de_negocio' } else { 'Metadata_API'})): GET HTTP $($creationRead.Status); devolvido_em=$createdReturnedState; vence_em_tipo=$createdDueType; vence_em_magnitude=$createdDueMagnitude."

    $targetMs = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds() - 3600000
    $target = if ($TimestampUnit -eq 's') { [int64][Math]::Floor($targetMs / 1000) } else { $targetMs }
    $mutation = Update-Record -Table 'emprestimo' -Id $loan -Changes @{ vence_em = $target } -OnlyChanges
    $readRecord = $mutation.Record
    $readType = if ($null -eq $readRecord.vence_em) { 'null' } else { $readRecord.vence_em.GetType().FullName }
    $observedMagnitude = 'ausente'
    $returnedType = 'ausente'
    $returnedState = 'ausente'
    $pastNow = $false
    $ownerMatches = $false
    $notReturned = $false
    $exemplarMatches = $false
    if ($mutation.ReadStatus -eq 200 -and $null -ne $readRecord) {
        $rawTimestamp = [double]$readRecord.vence_em
        $observedMagnitude = if ([Math]::Abs($rawTimestamp) -lt 100000000000) { 'segundos' } else { 'milissegundos' }
        $pastNow = (Convert-ToEpochMilliseconds $readRecord.vence_em) -lt [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
        $ownerMatches = [string]$readRecord.usuario_id -eq [string]$student
        $returnedProperty = $readRecord.PSObject.Properties['devolvido_em']
        if ($null -eq $returnedProperty) {
            $returnedState = 'campo_ausente'
        }
        elseif ($null -eq $returnedProperty.Value) {
            $returnedState = 'null'
            $returnedType = 'null'
            $notReturned = $true
        }
        else {
            $returnedType = $returnedProperty.Value.GetType().FullName
            if ($returnedProperty.Value -is [string] -and [string]::IsNullOrWhiteSpace($returnedProperty.Value)) {
                $returnedState = 'texto_vazio'
            }
            elseif (($returnedProperty.Value -is [byte] -or $returnedProperty.Value -is [int16] -or $returnedProperty.Value -is [int32] -or $returnedProperty.Value -is [int64] -or $returnedProperty.Value -is [single] -or $returnedProperty.Value -is [double] -or $returnedProperty.Value -is [decimal]) -and [double]$returnedProperty.Value -eq 0) {
                $returnedState = 'numero_zero'
            }
            else {
                $returnedState = 'valor_preenchido'
            }
        }
        $exemplarMatches = [string]$readRecord.exemplar_id -eq [string]$exemplar
    }
    $exemplarRead = Get-Record -Table 'exemplar' -Id $exemplar
    $exemplarState = if ($exemplarRead.Status -eq 200) { [string]$exemplarRead.Body.estado } else { "GET HTTP $($exemplarRead.Status)" }
    if ($returnedState -eq 'numero_zero') {
        $notReturned = $true
    }
    $fixtureValid = $ownerMatches -and $notReturned -and $exemplarMatches -and $exemplarState -eq 'emprestado' -and $pastNow
    Add-Result "- Diagnóstico vence_em ($TimestampUnit): envio epoch-$TimestampUnit; PUT HTTP $($mutation.UpdateStatus); GET empréstimo HTTP $($mutation.ReadStatus); tipo=$readType; magnitude=$observedMagnitude; devolvido_em=$returnedState (tipo $returnedType); usuário_fixture_corresponde=$ownerMatches; exemplar_fixture_corresponde=$exemplarMatches; vence_em_anterior_ao_agora=$pastNow; estado_exemplar=$exemplarState."
    if ($mutation.UpdateStatus -lt 200 -or $mutation.UpdateStatus -ge 300 -or $mutation.ReadStatus -ne 200 -or $exemplarRead.Status -ne 200 -or -not $fixtureValid) {
        throw 'Mutação de vence_em não confirmada; cenário de atraso não foi chamado.'
    }

    $request = Invoke-Business -Method POST -Path 'solicitacoes-emprestimo' -Token $script:UserTokens["estudante-$student"] -Body @{ titulo_id = $title }
    $requestRejected = $request.Status -ge 400 -and (($request.Body | ConvertTo-Json -Depth 12 -Compress) -match '(?i)atrasad')
    $requestResponseFields = if ($null -eq $request.Body) { 'corpo_vazio' } else { (@($request.Body.PSObject.Properties | ForEach-Object { $_.Name } | Sort-Object) -join ',') }
    if ($request.Status -ge 200 -and $request.Status -lt 300) {
        $created = Get-ObjectId $request.Body
        if ($null -ne $created) {
            Register-Fixture -Table 'solicitacao_emprestimo' -Id $created -Kind 'solicitacao inesperada pela API'
        }
    }
    Register-RelatedReservations -UserId $student -TitleId $title
    $relatedRequests = @(Get-Rows -Table 'solicitacao_emprestimo' | Where-Object {
        [string]$_.usuario_id -eq [string]$student -and [string]$_.titulo_id -eq [string]$title
    })
    foreach ($relatedRequest in $relatedRequests) {
        Register-Fixture -Table 'solicitacao_emprestimo' -Id ([int64]$relatedRequest.id) -Kind 'solicitacao vinculada a fixture de atraso'
    }
    $relatedReservations = @(Get-Rows -Table 'reserva' | Where-Object {
        [string]$_.usuario_id -eq [string]$student -and [string]$_.titulo_id -eq [string]$title
    })
    foreach ($relatedReservation in $relatedReservations) {
        Register-Fixture -Table 'reserva' -Id ([int64]$relatedReservation.id) -Kind 'reserva vinculada a solicitacao do cenario'
    }

    if (-not $CheckReservation) {
        if ($requestRejected -and $relatedRequests.Count -eq 0 -and $relatedReservations.Count -eq 0) {
            Add-Result "- Cenário atraso ($TimestampUnit): solicitação HTTP $($request.Status) rejeitada por atraso e sem registros laterais. Verificação de reserva adiada ao Lote 2. PASSOU."
            return
        }
        Add-Result "- Divergência funcional atraso na solicitação ($TimestampUnit): HTTP $($request.Status), campos_resposta=$requestResponseFields, solicitações_fixture=$($relatedRequests.Count), reservas_fixture=$($relatedReservations.Count)."
        $script:FunctionalFailure = $true
        throw "Divergência funcional no bloqueio por atraso da solicitação com vence_em em $TimestampUnit."
    }

    $reservation = Invoke-Business -Method POST -Path 'reservas' -Token $script:UserTokens["estudante-$student"] -Body @{ titulo_id = $title }
    $reservationRejected = $reservation.Status -ge 400 -and (($reservation.Body | ConvertTo-Json -Depth 12 -Compress) -match '(?i)atrasad')
    if ($reservation.Status -ge 200 -and $reservation.Status -lt 300) {
        $created = Get-ObjectId $reservation.Body
        if ($null -ne $created) {
            Register-Fixture -Table 'reserva' -Id $created -Kind 'reserva inesperada pela API'
        }
    }
    Register-RelatedReservations -UserId $student -TitleId $title
    $relatedRequests = @(Get-Rows -Table 'solicitacao_emprestimo' | Where-Object {
        [string]$_.usuario_id -eq [string]$student -and [string]$_.titulo_id -eq [string]$title
    })
    foreach ($relatedRequest in $relatedRequests) {
        Register-Fixture -Table 'solicitacao_emprestimo' -Id ([int64]$relatedRequest.id) -Kind 'solicitacao vinculada a fixture de atraso'
    }
    $relatedReservations = @(Get-Rows -Table 'reserva' | Where-Object {
        [string]$_.usuario_id -eq [string]$student -and [string]$_.titulo_id -eq [string]$title
    })
    foreach ($relatedReservation in $relatedReservations) {
        Register-Fixture -Table 'reserva' -Id ([int64]$relatedReservation.id) -Kind 'reserva vinculada a fixture de atraso'
    }
    if ($requestRejected -and $reservationRejected -and $relatedRequests.Count -eq 0 -and $relatedReservations.Count -eq 0) {
        Add-Result "- Cenário atraso ($TimestampUnit): solicitação HTTP $($request.Status), reserva HTTP $($reservation.Status), ambas rejeitadas por atraso e sem registros laterais. PASSOU."
        return
    }
    Add-Result "- Divergência funcional atraso ($TimestampUnit): solicitação HTTP $($request.Status), campos_resposta=$requestResponseFields, id_resposta=$(if ($null -ne (Get-ObjectId $request.Body)) { 'presente' } else { 'ausente' }), reserva HTTP $($reservation.Status), solicitações_fixture=$($relatedRequests.Count), reservas_fixture=$($relatedReservations.Count)."
    $script:FunctionalFailure = $true
    throw "Divergência funcional no bloqueio por atraso com vence_em em $TimestampUnit."
}

function Invoke-ScenarioLimite {
    $librarian = New-TestUser -Role 'bibliotecario'
    $student = New-TestUser -Role 'estudante'
    $titleA = New-TestTitle -Label 'limite-a'
    $titleB = New-TestTitle -Label 'limite-b'
    $exemplarA = New-TestExemplar -TitleId $titleA -Label 'limite-a'
    $exemplarB = New-TestExemplar -TitleId $titleB -Label 'limite-b'
    $requestA = New-TestRequest -UserId $student -TitleId $titleA -Label 'limite-a' -RequestedAt ([DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds() - 120000)
    $requestB = New-TestRequest -UserId $student -TitleId $titleB -Label 'limite-b' -RequestedAt ([DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds() - 60000)
    $outcomes = Invoke-ParallelPost -Calls @(
        @{ Path = "admin/solicitacoes/$requestA/retirada"; Token = $script:UserTokens['bibliotecario']; Body = @{}; Label = 'a' },
        @{ Path = "admin/solicitacoes/$requestB/retirada"; Token = $script:UserTokens['bibliotecario']; Body = @{}; Label = 'b' }
    )
    $accepted = @($outcomes | Where-Object { $_.Status -ge 200 -and $_.Status -lt 300 }).Count
    foreach ($outcome in $outcomes) {
        if ($outcome.Status -ge 200 -and $outcome.Status -lt 300) {
            $loanId = Get-ObjectId $outcome.Body
            if ($null -ne $loanId) {
                Register-Fixture -Table 'emprestimo' -Id $loanId -Kind 'emprestimo criado pela retirada concorrente'
            }
        }
    }
    [void](Register-RelatedLoans -UserId $student -ExemplarIds @($exemplarA, $exemplarB) -Kind 'emprestimo ligado a retirada concorrente')
    $registeredLoans = @($script:Fixtures | Where-Object { $_.Table -eq 'emprestimo' }).Count
    if ($registeredLoans -lt $accepted) {
        throw 'Retirada aceita sem registro de empréstimo identificável para limpeza.'
    }
    Add-Result "- Cenário limite concorrente: respostas HTTP $($outcomes[0].Status)/$($outcomes[1].Status); retiradas aceitas=$accepted, esperado=1."
    if ($accepted -ne 1) {
        $script:FunctionalFailure = $true
        throw "Divergência funcional do limite concorrente: retiradas aceitas=$accepted; esperado=1."
    }
}

function Invoke-ScenarioFifo {
    param([switch]$CaptureBaseline)

    $librarian = New-TestUser -Role 'bibliotecario'
    $studentA = New-TestUser -Role 'estudante'
    $studentB = New-TestUser -Role 'estudante'
    $studentC = New-TestUser -Role 'estudante'
    $title = New-TestTitle -Label 'fifo'
    $exemplar = New-TestExemplar -TitleId $title -Label 'fifo'
    $createdAt = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds() - 120000
    $first = New-TestReservation -UserId $studentA -TitleId $title -Label 'fifo-a' -CreatedAt $createdAt
    $second = New-TestReservation -UserId $studentB -TitleId $title -Label 'fifo-b' -CreatedAt $createdAt
    $third = New-TestReservation -UserId $studentC -TitleId $title -Label 'fifo-c' -CreatedAt $createdAt
    $queue = Invoke-Business -Method GET -Path "admin/titulos/$title/fila-reservas" -Token $script:UserTokens['bibliotecario']
    $queueIds = @($queue.Body | ForEach-Object { [string]$_.id })
    $expectedQueueIds = @([string]$first, [string]$second, [string]$third)
    if ($queue.Status -ne 200 -or $queueIds.Count -ne $expectedQueueIds.Count -or ($queueIds -join ',') -ne ($expectedQueueIds -join ',')) {
        throw "Consulta FIFO não confirmou a ordem das fixtures (HTTP $($queue.Status))."
    }
    Add-Result '- Consulta FIFO: três reservas com `criada_em` igual retornaram por `id` crescente.'

    $offer = Invoke-Business -Method POST -Path 'admin/reservas/ofertar-proxima' -Token $script:UserTokens['bibliotecario'] -Body @{
        titulo_id = $title
        exemplar_id = $exemplar
    }
    $offeredId = Get-ObjectId $offer.Body.reserva
    if ($CaptureBaseline) {
        if ($offer.Status -ne 500) {
            throw "Reprodução baseline esperava HTTP 500 na oferta FIFO; observado HTTP $($offer.Status)."
        }
        $keys = if ($null -eq $offer.Body) { 'corpo vazio' } else { (@($offer.Body.PSObject.Properties | ForEach-Object { $_.Name } | Sort-Object) -join ',') }
        $errorCode = if ($null -ne $offer.Body -and $null -ne $offer.Body.code -and [string]$offer.Body.code -match '^[A-Za-z0-9_-]{1,64}$') { [string]$offer.Body.code } else { 'não informado' }
        $safeMessage = Get-SanitizedErrorSummary -Body $offer.Body
        Add-Result "- Reprodução FIFO baseline: HTTP 500; código=$errorCode; campos da resposta=$keys; mensagem sanitizada=$safeMessage; trace omitido."
        return
    }

    if ($offer.Status -ne 200 -or $offeredId -ne $first) {
        $keys = if ($null -eq $offer.Body) { 'corpo vazio' } else { (@($offer.Body.PSObject.Properties | ForEach-Object { $_.Name } | Sort-Object) -join ',') }
        $errorCode = if ($null -ne $offer.Body -and $null -ne $offer.Body.code -and [string]$offer.Body.code -match '^[A-Za-z0-9_-]{1,64}$') { [string]$offer.Body.code } else { 'não informado' }
        Add-Result "- Falha FIFO: HTTP $($offer.Status); código=$errorCode; campos da resposta=$keys; mensagem/trace omitidos."
        throw "Oferta FIFO não confirmou HTTP 200 para a reserva mais antiga (HTTP $($offer.Status))."
    }
    Add-Result '- Oferta FIFO: HTTP 200 e reserva mais antiga selecionada.'
    Add-Result '- Processador global de expiração não executado neste cenário.'
}

function Invoke-ScenarioConcorrencia {
    $librarian = New-TestUser -Role 'bibliotecario'
    $studentA = New-TestUser -Role 'estudante'
    $studentB = New-TestUser -Role 'estudante'
    $title = New-TestTitle -Label 'ultimo-exemplar'
    $exemplar = New-TestExemplar -TitleId $title -Label 'ultimo-exemplar'
    $requestA = New-TestRequest -UserId $studentA -TitleId $title -Label 'ultimo-a' -RequestedAt ([DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds() - 120000)
    $requestB = New-TestRequest -UserId $studentB -TitleId $title -Label 'ultimo-b' -RequestedAt ([DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds() - 60000)
    $outcomes = Invoke-ParallelPost -Calls @(
        @{ Path = "admin/solicitacoes/$requestA/retirada"; Token = $script:UserTokens['bibliotecario']; Body = @{}; Label = 'a' },
        @{ Path = "admin/solicitacoes/$requestB/retirada"; Token = $script:UserTokens['bibliotecario']; Body = @{}; Label = 'b' }
    )
    $accepted = @($outcomes | Where-Object { $_.Status -ge 200 -and $_.Status -lt 300 }).Count
    foreach ($outcome in $outcomes) {
        if ($outcome.Status -ge 200 -and $outcome.Status -lt 300) {
            $loanId = Get-ObjectId $outcome.Body
            if ($null -ne $loanId) {
                Register-Fixture -Table 'emprestimo' -Id $loanId -Kind 'emprestimo criado na disputa do exemplar'
            }
        }
    }
    [void](Register-RelatedLoans -UserId $studentA -ExemplarIds @($exemplar) -Kind 'emprestimo ligado a retirada concorrente')
    [void](Register-RelatedLoans -UserId $studentB -ExemplarIds @($exemplar) -Kind 'emprestimo ligado a retirada concorrente')
    $registeredLoans = @($script:Fixtures | Where-Object { $_.Table -eq 'emprestimo' }).Count
    if ($registeredLoans -lt $accepted) {
        throw 'Retirada aceita sem registro de empréstimo identificável para limpeza.'
    }
    Add-Result "- Concorrência do último exemplar: respostas HTTP $($outcomes[0].Status)/$($outcomes[1].Status); retiradas aceitas=$accepted, esperado=1."

    $codeTitle = New-TestTitle -Label 'codigo-tombo'
    $codes = Invoke-ParallelPost -Calls @(
        @{ Path = 'admin/exemplares'; Token = $script:UserTokens['bibliotecario']; Body = @{ titulo_id = $codeTitle }; Label = 'a' },
        @{ Path = 'admin/exemplares'; Token = $script:UserTokens['bibliotecario']; Body = @{ titulo_id = $codeTitle }; Label = 'b' }
    )
    $codeExemplarIds = New-Object System.Collections.Generic.List[int64]
    foreach ($outcome in $codes) {
        if ($outcome.Status -ge 200 -and $outcome.Status -lt 300) {
            $id = Get-ObjectId $outcome.Body
            if ($null -ne $id) {
                Register-Fixture -Table 'exemplar' -Id $id -Kind 'exemplar criado na disputa de código'
                $codeExemplarIds.Add([int64]$id)
            }
        }
    }
    $createdExemplars = Register-RelatedExemplars -TitleId $codeTitle -Kind 'exemplar criado na disputa de código'
    foreach ($exemplar in $createdExemplars) {
        $id = [int64]$exemplar.id
        if (-not $codeExemplarIds.Contains($id)) {
            $codeExemplarIds.Add($id)
        }
    }
    $createdCount = $codeExemplarIds.Count
    $codesCollected = New-Object System.Collections.Generic.List[string]
    foreach ($id in $codeExemplarIds) {
        $record = Get-Record -Table 'exemplar' -Id $id
        if ($record.Status -eq 200 -and -not [string]::IsNullOrWhiteSpace([string]$record.Body.codigo_tombo)) {
            $codesCollected.Add([string]$record.Body.codigo_tombo)
        }
    }
    $uniqueCount = @($codesCollected | Select-Object -Unique).Count
    if ($createdCount -lt @($codes | Where-Object { $_.Status -ge 200 -and $_.Status -lt 300 }).Count) {
        throw 'Criação aceita sem exemplar identificável para limpeza.'
    }
    Add-Result "- Concorrência de tombo: respostas HTTP $($codes[0].Status)/$($codes[1].Status); exemplares criados=$createdCount; códigos distintos=$uniqueCount."
}

try {
    if ($CaptureFifoBaseline -and $Scenario -ne 'fifo') {
        throw 'CaptureFifoBaseline só pode ser usado com Scenario fifo.'
    }
    if (($ProbeDevolvidoEmNull -or $UseBusinessLoan) -and $Scenario -ne 'atraso') {
        throw 'ProbeDevolvidoEmNull e UseBusinessLoan só podem ser usados com Scenario atraso.'
    }
    if ($CheckReservation -and $Scenario -ne 'atraso') {
        throw 'CheckReservation só pode ser usado com Scenario atraso.'
    }
    Initialize-Target
    $script:CurrentStage = "execucao do cenario $Scenario"
    switch ($Scenario) {
        'atraso' { Invoke-ScenarioAtraso -TimestampUnit $VenceEmUnit -UseBusinessLoanFixture:$UseBusinessLoan -ProbeNullOnly:$ProbeDevolvidoEmNull -CheckReservation:$CheckReservation }
        'limite' { Invoke-ScenarioLimite }
        'fifo' { Invoke-ScenarioFifo -CaptureBaseline:$CaptureFifoBaseline }
        'concorrencia' { Invoke-ScenarioConcorrencia }
    }
}
catch {
    $script:RunError = $_.Exception.Message
    Add-Result "- Cenário ``$Scenario`` interrompido em '$script:CurrentStage': $($script:RunError)"
}

if ($script:Fixtures.Count -gt 0) {
    try {
        $clean = Remove-Fixtures
    }
    catch {
        $clean = $false
        Add-Result "- Erro durante limpeza do cenário ``$Scenario``: $($_.Exception.Message)"
    }
    if (-not $clean) {
        $remaining = @($script:Fixtures | ForEach-Object { "$($_.Table)/$($_.Id)" }) -join ', '
        Add-Result "- IDs que permanecem para limpeza manual: $remaining"
        'scenario=STOPPED'
        'cleanup=FAILED'
        'remaining_fixture_ids=' + $remaining
        $script:Client.Dispose()
        exit 2
    }
}

if ($script:TableIds.Count -gt 0 -and $null -ne $script:MetadataToken) {
    try {
        if (-not (Get-FinalCounts)) {
            $script:RunError = 'Contagem final difere do gate ou os usuários originais não foram preservados.'
        }
    }
    catch {
        $script:RunError = "Falha ao confirmar contagens após limpeza: $($_.Exception.Message)"
    }
}

if ($null -ne $script:RunError) {
    if ($script:FunctionalFailure) {
        'scenario=FAIL'
    }
    else {
        'scenario=STOPPED'
    }
    'cleanup=CONFIRMED'
    'reason=' + $script:RunError
    $script:Client.Dispose()
    if ($script:FunctionalFailure) { exit 4 }
    exit 3
}

Add-Result "- Cenário ``$Scenario`` terminou e suas fixtures foram removidas antes de qualquer outro cenário."
'scenario=COMPLETE'
'cleanup=CONFIRMED'
$script:Client.Dispose()
