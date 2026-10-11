$ErrorActionPreference='Stop'
. "$PSScriptRoot/../../two_joint_prototype/scripts/connect_inventor.ps1"
$mech=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent;$app.SilentOperation=$true
if(-not ('JisTitleEdit' -as [type])){Add-Type -ReferencedAssemblies 'C:/Program Files/Autodesk/Inventor 2025/Bin/Autodesk.Inventor.Interop.dll' -TypeDefinition 'public static class JisTitleEdit {public static object Get(object o){var d=(Inventor.TitleBlockDefinition)o; Inventor.DrawingSketch s; d.Edit(out s); return s;}}'}
$pdf=$app.ApplicationAddIns.ItemById('{0AC6FD96-2F4D-42CE-8BE0-8AEA580399E4}')
foreach($folder in @('two_joint_revb','follower_six_axis')){
 $f=Get-ChildItem "$mech/$folder/idw/*.idw"|Select-Object -First 1;$d=$app.Documents.Open($f.FullName,$false);$s=$d.ActiveSheet;$w=$s.Width;$h=$s.Height
 $front=$s.DrawingViews.Item(1);$top=$s.DrawingViews.Item(2);$side=$s.DrawingViews.Item(3);$iso=$s.DrawingViews.Item(4)
 $front.Scale=.2;$iso.Scale=.2;$front.Position=$tg.CreatePoint2d($w*.27,$h*.49);$top.Position=$tg.CreatePoint2d($w*.27,$h*.8);$side.Position=$tg.CreatePoint2d($w*.60,$h*.49);$iso.Position=$tg.CreatePoint2d($w*.83,$h*.80)
 foreach($v in @($front,$top,$side,$iso)){$v.ShowLabel=$true;$v.Label.FormattedText='<StyleOverride Font="ＭＳ ゴシック" FontSize="0.25"><DrawingViewScale/></StyleOverride>'}
 $definition=$s.TitleBlock.Definition;$sk=[JisTitleEdit]::Get($definition);$rev=if($folder -eq 'two_joint_revb'){'B'}else{'A'};$number="SO101-ASM-$rev-001"
 foreach($tb in $sk.TextBoxes){if($tb.Text -like '図番*'){$tb.FormattedText="図番 $number / 改訂 $rev / 状態 製造HOLD"}}
 $definition.ExitEdit($true);$d.PropertySets.Item('Design Tracking Properties').Item('Part Number').Value=$number
 $d.Update2($true)|Out-Null;$d.Save()
 $ctx=$app.TransientObjects.CreateTranslationContext();$ctx.Type=[Inventor.IOMechanismEnum]::kFileBrowseIOMechanism;$opts=$app.TransientObjects.CreateNameValueMap();$pdf.HasSaveCopyAsOptions($d,$ctx,$opts)|Out-Null;$opts.Value('All_Color_AS_Black')=1;$data=$app.TransientObjects.CreateDataMedium();$data.FileName="$mech/$folder/pdf/$($f.BaseName).pdf";$pdf.SaveCopyAs($d,$ctx,$opts,$data);$d.Close($true)
 Write-Output "Assembly layout corrected $folder"
}
$app.SilentOperation=$false
