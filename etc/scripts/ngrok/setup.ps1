<#
This script find, execute a ngrok.exe and update WEBHOOK_URL in .env (if not exist - create it)
#>

param(
    # ngrok directory path
    [string]$ngrok_path='/',
    
    #port for ngrok
    [int]$port=443
)

$ngrok_name='ngrok.exe'

if(!($ngrok_path.Contains('ngrok.exe')))
{
    if(!(($ngrok_path.EndsWith('\')) -and ($ngrok_path.EndsWith('/'))))
    {
        $ngrok_path = $ngrok_path + '\'
    }
    $ngrok_path = $ngrok_path + $ngrok_name
}


Write-Host "Full path to ngrok is:" -ForeGroundColor Yellow
$ngrok_path

$process = Start-Process -FilePath $ngrok_path -ArgumentList "http $port --log=stdout" -RedirectStandardOutput .\temp.log
Start-Sleep -Seconds 2 # TODO: try to change it

$output = Get-Content .\temp.log -Delimiter "url="

$address = $output[-1]
$address = $address.Replace("`n", "")

$webhook_url = "WEBHOOK_URL='", $address, "'" -join ""
$webhook_url

cd..
cd..
cd..

[string[]]$env = Get-Content .env
$changed=$false
foreach ($str in $env) {

    if($str.indexof("WEBHOOK_URL='") -ge 0)
    {
        $index = [array]::indexOf($env, $str)
        $env[$index] = $webhook_url
        $changed=$true
    }
}
if (!$changed)
{
    $env += $webhook_url
}

Set-Content .env -Value $env
