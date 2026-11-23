# Local synthetic English audio for genuine Whisper verification; no private recording.
$voice = New-Object -ComObject SAPI.SpVoice
$audioStream = New-Object -ComObject SAPI.SpFileStream
$target = Join-Path (Get-Location) 'tmp/groq-live/merchant-voice.wav'
New-Item -ItemType Directory -Force -Path (Split-Path $target) | Out-Null
try {
    $audioStream.Open($target, 3)
    $voice.AudioOutputStream = $audioStream
    $null = $voice.Speak('Karim paid five hundred taka of his old debt. He also bought two hundred taka of new goods on credit.')
} finally {
    $audioStream.Close()
}
Get-Item -LiteralPath $target | Select-Object Length
