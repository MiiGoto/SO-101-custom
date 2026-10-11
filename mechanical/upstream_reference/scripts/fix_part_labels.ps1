$ErrorActionPreference='Stop'
. "$PSScriptRoot/../../two_joint_prototype/scripts/connect_inventor.ps1"
$mech=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent;$app.SilentOperation=$true
$pdf=$app.ApplicationAddIns.ItemById('{0AC6FD96-2F4D-42CE-8BE0-8AEA580399E4}')
foreach($f in Get-ChildItem "$mech/adapters/idw/*_JIS.idw"){
 $d=$app.Documents.Open($f.FullName,$false);$s=$d.ActiveSheet;$front=$s.DrawingViews.Item(1);$iso=$s.DrawingViews.Item(4)
 $s.DrawingViews.Item(2).ShowLabel=$false;$s.DrawingViews.Item(3).ShowLabel=$false
 foreach($v in @($front,$iso)){$v.Label.FormattedText='<StyleOverride Font="ＭＳ ゴシック" FontSize="0.25"><DrawingViewScale/></StyleOverride>'}
 $front.Label.Position=$tg.CreatePoint2d($front.Position.X,($front.Position.Y-$front.Height/2-2.8))
 $d.Update2($true)|Out-Null;$d.Save()
 $ctx=$app.TransientObjects.CreateTranslationContext();$ctx.Type=[Inventor.IOMechanismEnum]::kFileBrowseIOMechanism;$opts=$app.TransientObjects.CreateNameValueMap();$pdf.HasSaveCopyAsOptions($d,$ctx,$opts)|Out-Null;$opts.Value('All_Color_AS_Black')=1;$data=$app.TransientObjects.CreateDataMedium();$data.FileName="$mech/adapters/pdf/$($f.BaseName).pdf";$pdf.SaveCopyAs($d,$ctx,$opts,$data);$d.Close($true)
}
$app.SilentOperation=$false
'Scale labels resized and separated from fit-check dimensions.'
