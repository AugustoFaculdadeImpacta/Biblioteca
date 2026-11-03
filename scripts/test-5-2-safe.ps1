$ErrorActionPreference = 'Stop'

$script:LibraryBase = 'https://x8ki-letl-twmt.n7.xano.io/api:MNu77wNi'
$script:MetadataBase = 'https://x8ki-letl-twmt.n7.xano.io/api:meta'
$script:WorkspaceId = 151966
$script:Branch = 'v1'
$script:TableIds = @{
    condicao_exemplar = 910520
    reserva = 910523
    emprestimo = 910521
    solicitacao_emprestimo = 910524
    exemplar = 910522
    titulo = 910525
    usuario = 910527
}
$script:Fixtures = New-Object System.Collections.Generic.List[object]
$script:Evidence = New-Object System.Collections.ArrayList
$script:CleanupEvidence = New-Object System.Collections.ArrayList
$script:CurrentStage = 'validacao de credenciais'
$script:LastStatus = 0
$script:FailureStage = $null
$script:FailureStatus = 0
$script:TestsPassed = $false

function Set-Stage {
    param([Parameter(Mandatory = $true)][string]$Stage)

    $script:CurrentStage = $Stage
}

function Invoke-JsonRequest {
    param(
        [Parameter(Mandatory = $true)][ValidateSet('Biblioteca', 'Metadata')][string]$Service,
        [Parameter(Mandatory = $true)][ValidateSet('GET', 'POST', 'DELETE')][string]$Method,
        [Parameter(Mandatory = $true)][string]$Path,
        [string]$Token,
        [object]$Body
    )

    $base = $script:LibraryBase
    if ($Service -eq 'Metadata') {
        $base = $script:MetadataBase
    }

    $headers = @{}
    if (-not [string]::IsNullOrWhiteSpace($Token)) {
        $headers['Authorization'] = "Bearer $Token"
    }
    if ($Service -eq 'Metadata') {
        $headers['x-data-source'] = 'live'
    }

    $request = @{
        Uri = "$base/$($Path.TrimStart('/'))"
        Method = $Method
        Headers = $headers
        UseBasicParsing = $true
        ErrorAction = 'Stop'
    }
    if ($PSBoundParameters.ContainsKey('Body')) {
        $request['ContentType'] = 'application/json; charset=utf-8'
        $request['Body'] = ConvertTo-Json -InputObject $Body -Depth 12 -Compress
    }

    $status = 0
    $content = $null
    $retryDelays = @(2, 4, 8, 16, 30)
    for ($attempt = 1; $attempt -le 6; $attempt++) {
        $httpResponse = $null
        $status = 0
        $content = $null
        try {
            $response = Invoke-WebRequest @request
            $status = [int]$response.StatusCode
            $content = $response.Content
        }
        catch {
            $httpResponse = $_.Exception.Response
            if ($null -ne $httpResponse) {
                $status = [int]$httpResponse.StatusCode
            }
        }

        if ($status -ne 429 -or $attempt -eq 6) {
            break
        }

        $retryAfter = $null
        if ($null -ne $httpResponse) {
            $retryAfter = $httpResponse.Headers['Retry-After']
        }

        $delay = $retryDelays[$attempt - 1]
        if (-not [string]::IsNullOrWhiteSpace([string]$retryAfter)) {
            $retrySeconds = 0
            if ([int]::TryParse([string]$retryAfter, [ref]$retrySeconds)) {
                $delay = [Math]::Max(0, $retrySeconds)
            }
            else {
                $retryDate = [DateTimeOffset]::MinValue
                if ([DateTimeOffset]::TryParse([string]$retryAfter, [ref]$retryDate)) {
                    $delay = [Math]::Max(0, [int][Math]::Ceiling(($retryDate - [DateTimeOffset]::UtcNow).TotalSeconds))
                }
            }
        }
        Start-Sleep -Seconds $delay
    }

    $script:LastStatus = $status
    $parsedBody = $null
    if (-not [string]::IsNullOrWhiteSpace($content)) {
        try {
            $parsedBody = ConvertFrom-Json -InputObject $content -ErrorAction Stop
        }
        catch {
            $parsedBody = $null
        }
    }

    return [pscustomobject]@{
        StatusCode = $status
        Body = $parsedBody
    }
}

function Assert-Status {
    param(
        [Parameter(Mandatory = $true)]$Response,
        [Parameter(Mandatory = $true)][int[]]$Expected
    )

    if ($Response.StatusCode -notin $Expected) {
        throw 'status inesperado'
    }
    [void]$script:Evidence.Add([pscustomobject]@{
        Scenario = $script:CurrentStage
        Status = [int]$Response.StatusCode
    })
}

function Get-RecordId {
    param(
        [Parameter(Mandatory = $true)]$Object,
        [Parameter(Mandatory = $true)][string]$Field
    )

    if ($null -eq $Object -or $null -eq $Object.$Field) {
        throw 'identificador ausente na resposta'
    }
    return [int64]$Object.$Field
}

function Register-Fixture {
    param(
        [Parameter(Mandatory = $true)][int]$TableId,
        [Parameter(Mandatory = $true)][int64]$RecordId,
        [Parameter(Mandatory = $true)][string]$Description
    )

    [void]$script:Fixtures.Add([pscustomobject]@{
        tableId = $TableId
        recordId = $RecordId
        descricao = $Description
    })
}

function Invoke-StudentSignup {
    param([Parameter(Mandatory = $true)][string]$Label)

    Set-Stage "cadastro do estudante $Label"
    $suffix = [guid]::NewGuid().ToString('N')
    $email = "teste-5-2-$suffix@example.invalid"
    $password = "T5.2-$([guid]::NewGuid().ToString('N'))!aA9"
    $name = "Estudante sintetico $Label $($suffix.Substring(0, 8))"
    $response = Invoke-JsonRequest -Service Biblioteca -Method POST -Path 'auth/signup' -Body @{
        nome = $name
        email = $email
        senha = $password
    }
    $userId = Get-RecordId -Object $response.Body.usuario -Field 'id'
    Register-Fixture -TableId $script:TableIds.usuario -RecordId $userId -Description "estudante sintetico $Label"
    Assert-Status -Response $response -Expected @(200)
    if ([string]::IsNullOrWhiteSpace([string]$response.Body.authToken)) {
        throw 'token de cadastro ausente'
    }
    return [pscustomobject]@{
        Id = $userId
        Email = $email
        Password = $password
        SignupToken = [string]$response.Body.authToken
    }
}

function Assert-StudentIdentity {
    param(
        [Parameter(Mandatory = $true)]$Student,
        [Parameter(Mandatory = $true)][string]$Token,
        [Parameter(Mandatory = $true)][string]$Label
    )

    Set-Stage "validacao de identidade do estudante $Label"
    $response = Invoke-JsonRequest -Service Biblioteca -Method GET -Path 'auth/me' -Token $Token
    Assert-Status -Response $response -Expected @(200)
    if ($response.Body.perfil -cne 'estudante' -or [int64]$response.Body.id -ne $Student.Id) {
        throw 'identidade ou perfil inesperado'
    }
}

function Convert-ToUtcDateTimeOffset {
    param([Parameter(Mandatory = $true)]$Value)

    if ($Value -is [ValueType] -or [string]$Value -match '^\d+$') {
        $seconds = [int64]$Value
        if ($seconds -gt 100000000000) {
            return [DateTimeOffset]::FromUnixTimeMilliseconds($seconds)
        }
        return [DateTimeOffset]::FromUnixTimeSeconds($seconds)
    }

    return [DateTimeOffset]::Parse(
        [string]$Value,
        [Globalization.CultureInfo]::InvariantCulture,
        [Globalization.DateTimeStyles]::AssumeUniversal
    )
}

function Find-Reservation {
    param(
        [Parameter(Mandatory = $true)]$Reservations,
        [Parameter(Mandatory = $true)][int64]$ReservationId
    )

    foreach ($reservation in @($Reservations)) {
        if ($null -ne $reservation -and [int64]$reservation.id -eq $ReservationId) {
            return $reservation
        }
    }
    return $null
}

function Invoke-FixtureCleanup {
    param(
        [Parameter(Mandatory = $true)][object]$Fixture,
        [Parameter(Mandatory = $true)][string]$MetadataToken
    )

    $recordPath = "workspace/$($script:WorkspaceId)/table/$($Fixture.tableId)/content/$($Fixture.recordId)"
    $initial = Invoke-JsonRequest -Service Metadata -Method GET -Path $recordPath -Token $MetadataToken
    $deleted = Invoke-JsonRequest -Service Metadata -Method DELETE -Path $recordPath -Token $MetadataToken
    $confirmed = Invoke-JsonRequest -Service Metadata -Method GET -Path $recordPath -Token $MetadataToken

    $passed = ($initial.StatusCode -eq 200) -and
        ($deleted.StatusCode -ge 200 -and $deleted.StatusCode -lt 300) -and
        ($confirmed.StatusCode -eq 404)
    [void]$script:CleanupEvidence.Add([pscustomobject]@{
        Description = $Fixture.descricao
        Id = [int64]$Fixture.recordId
        InitialGet = [int]$initial.StatusCode
        Delete = [int]$deleted.StatusCode
        ConfirmGet = [int]$confirmed.StatusCode
        Passed = $passed
    })
}

$librarianToken = [Environment]::GetEnvironmentVariable('XANO_TEST_LIBRARIAN_TOKEN', 'Process')
$metadataToken = [Environment]::GetEnvironmentVariable('XANO_TEST_METADATA_TOKEN', 'Process')
if ([string]::IsNullOrWhiteSpace($librarianToken) -or [string]::IsNullOrWhiteSpace($metadataToken)) {
    Write-Output 'Falha na etapa: credenciais obrigatorias ausentes (XANO_TEST_LIBRARIAN_TOKEN e/ou XANO_TEST_METADATA_TOKEN).'
    exit 1
}

try {
    Set-Stage 'validacao do token de bibliotecario'
    $librarian = Invoke-JsonRequest -Service Biblioteca -Method GET -Path 'auth/me' -Token $librarianToken
    Assert-Status -Response $librarian -Expected @(200)
    if ($librarian.Body.perfil -cne 'bibliotecario') {
        throw 'perfil autenticado nao e bibliotecario'
    }

    Set-Stage 'validacao do token de metadata e destino'
    $workspace = Invoke-JsonRequest -Service Metadata -Method GET -Path "workspace/$($script:WorkspaceId)" -Token $metadataToken
    Assert-Status -Response $workspace -Expected @(200)
    if ([int64]$workspace.Body.id -ne $script:WorkspaceId) {
        throw 'workspace inesperado'
    }

    $runTag = [guid]::NewGuid().ToString('N').Substring(0, 10)

    $studentA = Invoke-StudentSignup -Label 'A'
    Assert-StudentIdentity -Student $studentA -Token $studentA.SignupToken -Label 'A com token de cadastro'

    Set-Stage 'login do estudante A'
    $login = Invoke-JsonRequest -Service Biblioteca -Method POST -Path 'auth/login' -Body @{
        email = $studentA.Email
        senha = $studentA.Password
    }
    Assert-Status -Response $login -Expected @(200)
    if ([string]::IsNullOrWhiteSpace([string]$login.Body.authToken)) {
        throw 'token de login ausente'
    }
    $studentALoginToken = [string]$login.Body.authToken
    Assert-StudentIdentity -Student $studentA -Token $studentALoginToken -Label 'A com token de login'

    Set-Stage 'criacao do titulo de teste'
    $titleResponse = Invoke-JsonRequest -Service Biblioteca -Method POST -Path 'catalogo/titulos' -Token $librarianToken -Body @{
        titulo = "Teste seguro 5.2 $runTag"
        autores = 'Autor sintetico'
    }
    $titleId = Get-RecordId -Object $titleResponse.Body -Field 'id'
    Register-Fixture -TableId $script:TableIds.titulo -RecordId $titleId -Description 'titulo sintetico'
    Assert-Status -Response $titleResponse -Expected @(200)

    Set-Stage 'criacao do exemplar de teste'
    $copyResponse = Invoke-JsonRequest -Service Biblioteca -Method POST -Path 'admin/exemplares' -Token $librarianToken -Body @{
        titulo_id = $titleId
    }
    $copyId = Get-RecordId -Object $copyResponse.Body -Field 'id'
    Register-Fixture -TableId $script:TableIds.exemplar -RecordId $copyId -Description 'exemplar sintetico'
    Assert-Status -Response $copyResponse -Expected @(200)

    Set-Stage 'solicitacao de emprestimo pelo estudante A'
    $requestResponse = Invoke-JsonRequest -Service Biblioteca -Method POST -Path 'solicitacoes-emprestimo' -Token $studentA.SignupToken -Body @{
        titulo_id = $titleId
    }
    $requestId = Get-RecordId -Object $requestResponse.Body -Field 'id'
    Register-Fixture -TableId $script:TableIds.solicitacao_emprestimo -RecordId $requestId -Description 'solicitacao sintetica'
    Assert-Status -Response $requestResponse -Expected @(200)

    Set-Stage 'retirada pelo bibliotecario'
    $loanResponse = Invoke-JsonRequest -Service Biblioteca -Method POST -Path "admin/solicitacoes/$requestId/retirada" -Token $librarianToken
    $loanId = Get-RecordId -Object $loanResponse.Body -Field 'id'
    Register-Fixture -TableId $script:TableIds.emprestimo -RecordId $loanId -Description 'emprestimo sintetico'
    Assert-Status -Response $loanResponse -Expected @(200)

    $studentB = Invoke-StudentSignup -Label 'B'
    Assert-StudentIdentity -Student $studentB -Token $studentB.SignupToken -Label 'B'
    $studentC = Invoke-StudentSignup -Label 'C'
    Assert-StudentIdentity -Student $studentC -Token $studentC.SignupToken -Label 'C'

    Set-Stage 'reserva do estudante B enquanto A esta com o exemplar'
    $reservationBResponse = Invoke-JsonRequest -Service Biblioteca -Method POST -Path 'reservas' -Token $studentB.SignupToken -Body @{
        titulo_id = $titleId
    }
    $reservationBId = Get-RecordId -Object $reservationBResponse.Body -Field 'id'
    Register-Fixture -TableId $script:TableIds.reserva -RecordId $reservationBId -Description 'reserva sintetica B'
    Assert-Status -Response $reservationBResponse -Expected @(200)

    Set-Stage 'reserva do estudante C enquanto A esta com o exemplar'
    $reservationCResponse = Invoke-JsonRequest -Service Biblioteca -Method POST -Path 'reservas' -Token $studentC.SignupToken -Body @{
        titulo_id = $titleId
    }
    $reservationCId = Get-RecordId -Object $reservationCResponse.Body -Field 'id'
    Register-Fixture -TableId $script:TableIds.reserva -RecordId $reservationCId -Description 'reserva sintetica C'
    Assert-Status -Response $reservationCResponse -Expected @(200)

    Set-Stage 'devolucao do emprestimo de A e oferta da fila'
    $returnResponse = Invoke-JsonRequest -Service Biblioteca -Method POST -Path "admin/emprestimos/$loanId/devolucao" -Token $librarianToken
    Assert-Status -Response $returnResponse -Expected @(200)
    if ($null -eq $returnResponse.Body.emprestimo -or [int64]$returnResponse.Body.emprestimo.id -ne $loanId) {
        throw 'devolucao nao retornou o emprestimo esperado'
    }
    if ($null -eq $returnResponse.Body.reserva_ofertada -or [int64]$returnResponse.Body.reserva_ofertada.id -ne $reservationBId) {
        throw 'a devolucao nao ofertou a reserva B'
    }

    Set-Stage 'consulta das reservas do estudante B'
    $myReservationsB = Invoke-JsonRequest -Service Biblioteca -Method GET -Path 'minhas/reservas' -Token $studentB.SignupToken
    Assert-Status -Response $myReservationsB -Expected @(200)
    $myReservationB = Find-Reservation -Reservations $myReservationsB.Body -ReservationId $reservationBId
    if ($null -eq $myReservationB -or $myReservationB.estado -cne 'ofertada') {
        throw 'reserva B nao esta ofertada'
    }

    Set-Stage 'consulta das reservas do estudante C'
    $myReservationsC = Invoke-JsonRequest -Service Biblioteca -Method GET -Path 'minhas/reservas' -Token $studentC.SignupToken
    Assert-Status -Response $myReservationsC -Expected @(200)
    $myReservationC = Find-Reservation -Reservations $myReservationsC.Body -ReservationId $reservationCId
    if ($null -eq $myReservationC -or $myReservationC.estado -cne 'aguardando') {
        throw 'reserva C nao continua aguardando'
    }

    Set-Stage 'validacao da oferta de 48 horas'
    $offeredAt = Convert-ToUtcDateTimeOffset -Value $myReservationB.ofertada_em
    $expiresAt = Convert-ToUtcDateTimeOffset -Value $myReservationB.expira_em
    if (($expiresAt - $offeredAt).TotalSeconds -ne 172800) {
        throw 'prazo da oferta diferente de 172800 segundos'
    }

    Set-Stage 'negacao de criacao de titulo por estudante'
    $deniedTitle = Invoke-JsonRequest -Service Biblioteca -Method POST -Path 'catalogo/titulos' -Token $studentA.SignupToken -Body @{
        titulo = "Negado teste seguro 5.2 $runTag"
        autores = 'Autor sintetico'
    }
    Assert-Status -Response $deniedTitle -Expected @(403)

    Set-Stage 'registro de condicao danificado'
    $conditionResponse = Invoke-JsonRequest -Service Biblioteca -Method POST -Path "admin/exemplares/$copyId/condicoes" -Token $librarianToken -Body @{
        tipo = 'danificado'
        observacao = 'Condicao sintetica para teste seguro 5.2.'
    }
    $conditionId = Get-RecordId -Object $conditionResponse.Body -Field 'id'
    Register-Fixture -TableId $script:TableIds.condicao_exemplar -RecordId $conditionId -Description 'condicao sintetica danificado'
    Assert-Status -Response $conditionResponse -Expected @(200)

    Set-Stage 'consulta do historico de condicoes'
    $conditionHistory = Invoke-JsonRequest -Service Biblioteca -Method GET -Path "admin/exemplares/$copyId/condicoes" -Token $librarianToken
    Assert-Status -Response $conditionHistory -Expected @(200)
    $foundCondition = $false
    foreach ($condition in @($conditionHistory.Body)) {
        if ($null -ne $condition -and [int64]$condition.id -eq $conditionId -and $condition.tipo -ceq 'danificado') {
            $foundCondition = $true
        }
    }
    if (-not $foundCondition) {
        throw 'condicao sintetica ausente do historico'
    }

    $script:TestsPassed = $true
}
catch {
    $script:FailureStage = $script:CurrentStage
    $script:FailureStatus = $script:LastStatus
}
finally {
    if (-not [string]::IsNullOrWhiteSpace($metadataToken)) {
        $cleanupOrder = @(
            $script:TableIds.condicao_exemplar,
            $script:TableIds.reserva,
            $script:TableIds.emprestimo,
            $script:TableIds.solicitacao_emprestimo,
            $script:TableIds.exemplar,
            $script:TableIds.titulo,
            $script:TableIds.usuario
        )
        foreach ($tableId in $cleanupOrder) {
            foreach ($fixture in @($script:Fixtures | Where-Object { $_.tableId -eq $tableId })) {
                Invoke-FixtureCleanup -Fixture $fixture -MetadataToken $metadataToken
            }
        }
    }
}

$cleanupPassed = $true
foreach ($cleanupResult in $script:CleanupEvidence) {
    if (-not $cleanupResult.Passed) {
        $cleanupPassed = $false
    }
}

if ($null -ne $script:FailureStage) {
    Write-Output "Falha na etapa: $($script:FailureStage) (HTTP $($script:FailureStatus)); limpeza $(if ($cleanupPassed) { 'confirmada' } else { 'incompleta' })."
    exit 1
}
if (-not $script:TestsPassed) {
    Write-Output 'Falha na etapa: execucao dos cenarios.'
    exit 1
}
if (-not $cleanupPassed) {
    Write-Output 'Falha na etapa: limpeza; ao menos uma exclusao nao foi confirmada com HTTP 404.'
    exit 1
}

$date = Get-Date -Format 'yyyy-MM-dd'
$reportLines = @(
    ''
    ('## Verificacao segura 5.2 - {0}' -f $date)
    ''
    '### Cenarios e HTTP/status'
)
foreach ($item in $script:Evidence) {
    $reportLines += "- $($item.Scenario): HTTP $($item.Status)."
}
$reportLines += @(
    ''
    '### IDs de fixtures (sem dados pessoais)'
)
foreach ($fixture in $script:Fixtures) {
    $reportLines += "- $($fixture.descricao): ID $($fixture.recordId)."
}
$reportLines += @(
    ''
    '### Limpeza'
)
foreach ($cleanupResult in $script:CleanupEvidence) {
    $reportLines += "- $($cleanupResult.Description), ID $($cleanupResult.Id): GET previo $($cleanupResult.InitialGet), DELETE $($cleanupResult.Delete), GET de confirmacao $($cleanupResult.ConfirmGet)."
}
$reportLines += @(
    '- Todas as exclusoes foram confirmadas por GET individual com HTTP 404.'
    ''
    '### Limitacoes'
    '- Expiracao, atraso, limite de emprestimo e concorrencia nao foram testados nesta execucao live; a tarefa 5.2 permanece pendente.'
)

$resultsPath = Join-Path (Split-Path -Parent $PSScriptRoot) 'openspec\changes\estrutura-inicial-xano-biblioteca\RESULTS.md'
Add-Content -LiteralPath $resultsPath -Value ($reportLines -join [Environment]::NewLine) -Encoding UTF8

Write-Output 'Cenarios seguros aprovados; limpeza confirmada para todos os fixtures.'
