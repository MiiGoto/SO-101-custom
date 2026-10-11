$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
. "$PSScriptRoot/connect_inventor.ps1"
$app.SilentOperation=$true
$a=$app.Documents.Open("$root/iam/SO101_TwoJoint_Prototype.iam",$false)
$translator=$app.ApplicationAddIns.ItemById('{90AF7F40-0C01-11D5-8E83-0010B541CD80}')
$ctx=$app.TransientObjects.CreateTranslationContext();$ctx.Type=[Inventor.IOMechanismEnum]::kFileBrowseIOMechanism
$opts=$app.TransientObjects.CreateNameValueMap();$translator.HasSaveCopyAsOptions($a,$ctx,$opts)|Out-Null;$opts.Value('ApplicationProtocolType')=3
$data=$app.TransientObjects.CreateDataMedium();$data.FileName="$root/step/SO101_TwoJoint_Prototype.step";$translator.SaveCopyAs($a,$ctx,$opts,$data)
$imageResult=@{status='TBD';source='Inventor ActiveView'}
try{
 $a.Close($true);$a=$app.Documents.Open("$root/iam/SO101_TwoJoint_Prototype.iam",$true);$a.Activate()
 $camera=$app.ActiveView.Camera;$camera.ViewOrientationType=[Inventor.ViewOrientationTypeEnum]::kIsoTopRightViewOrientation;$camera.Apply();$app.ActiveView.Fit();$app.ActiveView.SaveAsBitmap("$root/views/inventor_assembly.png",1600,1200)
 $imageResult.status='COMPLETED'
}catch{$imageResult.error=$_.Exception.Message}
$imageResult|ConvertTo-Json|Set-Content "$root/analysis/inventor_view_validation.json" -Encoding utf8
$app.SilentOperation=$false
Write-Output 'Assembly STEP and view attempt saved.'
