Function Set-IEProxy
{
 param(
  [bool]$Enable=$false,
  [string]$ProxyServer,
  [ValidateRange(1,65535)]
  [int]$port,
  [bool]$EnableAutoDetectSetting
 )
 
 #设置IE代理
 $proxyRegPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings"
 $enableProxy = Get-ItemProperty -Path $proxyRegPath -Name ProxyEnable
 if( -not $Enable) {
  Set-ItemProperty -path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name "ProxyEnable" -value 0
  Write-Host "IE代理已禁用。"
 }
 else {
  Set-ItemProperty -path $proxyRegPath -Name "ProxyEnable" -value 1
  Set-ItemProperty -path $proxyRegPath -Name "ProxyServer" -value ( $ProxyServer+":"+$port )
  Write-Host "IE代理已启用"
 }
 
 #设置IE自动检测配置
 [byte[]]$bytes=$null
 if($EnableAutoDetectSetting){
    $bytes = [byte[]]@(70,0,0,0,38,0,0,0,9,0,0,0,10,0,0,0,50,46,49,46,49,46,51,58,51,51,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,2,0,0,0,172,18,32,72,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
 }
 else{
    $bytes = [byte[]]@(70,0,0,0,39,0,0,0,1,0,0,0,10,0,0,0,50,46,49,46,49,46,51,58,51,51,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,2,0,0,0,172,18,32,72,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
 }
 Set-ItemProperty -Path "$proxyRegPath\Connections" -Name DefaultConnectionSettings -Value $bytes
}
# Set-IEProxy -Enable $false
Set-IEProxy -Enable $true



# 递归搜索当前目录下所有包含RJ的文件名，去除重复文件名后，保存到rjidList.txt文件中
Get-ChildItem -Recurse | foreach{if($_.Name.Contains("RJ")){$num++;$_.Name.Substring($_.Name.IndexOf('RJ'),8)}}|select -Unique| Out-File rjidList.txt
Write-Host "write fjids to rjid.txt"
Write-Host "counts:"+$num
Write-Host "start dlsiteSpider"
python dlsiteSpider.py
Pause