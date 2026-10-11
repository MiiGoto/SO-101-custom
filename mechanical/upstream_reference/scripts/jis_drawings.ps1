param([switch]$AssemblyOnly)
$ErrorActionPreference='Stop'
. "$PSScriptRoot/../../two_joint_prototype/scripts/connect_inventor.ps1"
$mech=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$app.SilentOperation=$true
if(-not ('JisTitleEdit' -as [type])){Add-Type -ReferencedAssemblies 'C:/Program Files/Autodesk/Inventor 2025/Bin/Autodesk.Inventor.Interop.dll' -TypeDefinition 'public static class JisTitleEdit {public static object Get(object o){var d=(Inventor.TitleBlockDefinition)o; Inventor.DrawingSketch s; d.Edit(out s); return s;}}'}
New-Item -ItemType Directory -Force "$mech/templates","$mech/release_review/pdf_qa"|Out-Null
$source='C:/Users/Public/Documents/Autodesk/Inventor 2026/Templates/ja-JP/Metric/JIS.idw'
$pdf=$app.ApplicationAddIns.ItemById('{0AC6FD96-2F4D-42CE-8BE0-8AEA580399E4}')
function Setup($drawing,$size,$number,$name,$material,$state){
 $standard=$drawing.StylesManager.ActiveStandardStyle;$standard.FirstAngleProjection=$false
 $sheet=$drawing.ActiveSheet;$sheet.Size=$size
 $drawing.StylesManager.ActiveStandardStyle.Name # emit checked native standard
 $drawing.PropertySets.Item('Design Tracking Properties').Item('Part Number').Value=$number
 $drawing.PropertySets.Item('Design Tracking Properties').Item('Description').Value=$name
 $drawing.PropertySets.Item('Inventor Summary Information').Item('Author').Value='SO-101-custom'
 # Preserve the installed JIS border and title-block geometry, replace instance by a project-specific Japanese block.
 if($sheet.TitleBlock){$sheet.TitleBlock.Delete()}
 $definition=$drawing.TitleBlockDefinitions.Add('SO101_JIS_Project')
 $sk=[JisTitleEdit]::Get($definition)
 $sk.SketchLines.AddAsTwoPointRectangle($tg.CreatePoint2d(0,0),$tg.CreatePoint2d(14,3.2))|Out-Null
 foreach($yy in @(.8,1.6,2.4)){$sk.SketchLines.AddByTwoPoints($tg.CreatePoint2d(0,$yy),$tg.CreatePoint2d(14,$yy))|Out-Null}
 $rev=if($name -match 'Follower_RevA'){'A'}else{'B'}
 $labels=@("図番 $number / 改訂 $rev / 状態 $state","名称 $name / 数量 BOM参照","材質 $material / 製法 FDM / 単位 mm","尺度 各図示 / 第三角法 / 作成 2026-10-11 / SO-101-custom")
 for($i=0;$i -lt 4;$i++){$tb=$sk.TextBoxes.AddFitted($tg.CreatePoint2d(.2,(3.05-$i*.8)),$labels[$i]);$tb.Style.Font='ＭＳ ゴシック';$tb.Style.FontSize=.25}
 $definition.ExitEdit($true);$sheet.AddTitleBlock($definition)|Out-Null
 # Explicit third-angle symbol (truncated-cone side view and concentric end view).
 $sym=$sheet.Sketches.Add();$sym.Edit()
 $x=2.0;$y=2.0
 $sym.SketchLines.AddByTwoPoints($tg.CreatePoint2d($x,$y),$tg.CreatePoint2d($x+1.2,$y+.2))|Out-Null
 $sym.SketchLines.AddByTwoPoints($tg.CreatePoint2d($x,$y+.8),$tg.CreatePoint2d($x+1.2,$y+.6))|Out-Null
 $sym.SketchLines.AddByTwoPoints($tg.CreatePoint2d($x,$y),$tg.CreatePoint2d($x,$y+.8))|Out-Null
 $sym.SketchLines.AddByTwoPoints($tg.CreatePoint2d($x+1.2,$y+.2),$tg.CreatePoint2d($x+1.2,$y+.6))|Out-Null
 $sym.SketchCircles.AddByCenterRadius($tg.CreatePoint2d($x+2,$y+.4),.4)|Out-Null
 $sym.SketchCircles.AddByCenterRadius($tg.CreatePoint2d($x+2,$y+.4),.2)|Out-Null
 $sym.ExitEdit()
 return $sheet
}
foreach($sizeName in @('A4','A3')){
 if($AssemblyOnly){continue}
 $dr=$app.Documents.Add([Inventor.DocumentTypeEnum]::kDrawingDocumentObject,$source,$false)
 $size=if($sizeName -eq 'A4'){[Inventor.DrawingSheetSizeEnum]::kA4DrawingSheetSize}else{[Inventor.DrawingSheetSizeEnum]::kA3DrawingSheetSize}
 $null=Setup $dr $size 'SO101-TEMPLATE' '製作図テンプレート' '部品ごとに指定' 'HOLD'
 $dr.SaveAs("$mech/templates/SO101_JIS_$sizeName.idw",$false);$dr.Close($true)
 $re=$app.Documents.Open("$mech/templates/SO101_JIS_$sizeName.idw",$false);$re.Close($true)
}
$files=@(Get-ChildItem "$mech/adapters/ipt/*.ipt"|Where-Object Name -notmatch Envelope)+@(Get-Item "$mech/follower_six_axis/ipt/Upper_arm_SO101.ipt","$mech/follower_six_axis/ipt/Under_arm_SO101.ipt","$mech/two_joint_revb/iam/SO101_TwoJoint_RevB.iam","$mech/follower_six_axis/iam/SO101_Custom_Follower_RevA.iam")
$records=@();$n=0
foreach($file in $files){
 if($AssemblyOnly -and $file.Extension -ne '.iam'){continue}
 $n++;$model=$app.Documents.Open($file.FullName,$false);$d=$app.Documents.Add([Inventor.DocumentTypeEnum]::kDrawingDocumentObject,$source,$false)
 $assembly=$file.Extension -eq '.iam';$size=if($assembly){[Inventor.DrawingSheetSizeEnum]::kA3DrawingSheetSize}else{[Inventor.DrawingSheetSizeEnum]::kA4DrawingSheetSize}
 $result=Setup $d $size "SO101-B-$('{0:d3}' -f $n)" $file.BaseName 'PLA+候補 / PETG候補' '製造HOLD';$sheet=@($result)[-1];$w=$sheet.Width;$h=$sheet.Height
 $scale=if($assembly){.45}elseif($file.BaseName -match 'arm_SO101'){.7}else{1.3}
 $front=$sheet.DrawingViews.AddBaseView($model,$tg.CreatePoint2d($w*.29,$h*.62),$scale,[Inventor.ViewOrientationTypeEnum]::kFrontViewOrientation,[Inventor.DrawingViewStyleEnum]::kHiddenLineDrawingViewStyle)
 $top=$sheet.DrawingViews.AddProjectedView($front,$tg.CreatePoint2d($w*.29,$h*.84),[Inventor.DrawingViewStyleEnum]::kFromBaseDrawingViewStyle)
 $side=$sheet.DrawingViews.AddProjectedView($front,$tg.CreatePoint2d($w*.59,$h*.62),[Inventor.DrawingViewStyleEnum]::kFromBaseDrawingViewStyle)
 $iso=$sheet.DrawingViews.AddBaseView($model,$tg.CreatePoint2d($w*.81,$h*.79),$scale*.55,[Inventor.ViewOrientationTypeEnum]::kIsoTopRightViewOrientation,[Inventor.DrawingViewStyleEnum]::kHiddenLineRemovedDrawingViewStyle)
 foreach($v in @($front,$top,$side,$iso)){$v.ShowLabel=$true;$v.Label.FormattedText='<DrawingViewScale/>'}
 $d.Update2($true)|Out-Null;$dims=0;$errors=@();$circles=@();$lines=@()
 if(-not $assembly){foreach($curve in $front.DrawingCurves([Type]::Missing)){try{if($curve.CurveType -eq [Inventor.CurveTypeEnum]::kCircleCurve){$circles+=$curve}elseif($curve.StartPoint -and $curve.EndPoint){$len=$curve.StartPoint.DistanceTo($curve.EndPoint);if($len -gt .25){$lines+=@{curve=$curve;length=$len}}}}catch{}}}
 foreach($horizontal in @($true,$false)){
  $line=$lines|Where-Object {([Math]::Abs($_.curve.StartPoint.Y-$_.curve.EndPoint.Y) -lt .001) -eq $horizontal}|Sort-Object length -Descending|Select-Object -First 1
  if($line){try{$pos=if($horizontal){$tg.CreatePoint2d($front.Position.X,($front.Position.Y-$front.Height/2-.8))}else{$tg.CreatePoint2d(($front.Position.X-$front.Width/2-.8),$front.Position.Y)};$sheet.DrawingDimensions.GeneralDimensions.AddLinear($pos,$sheet.CreateGeometryIntent($line.curve))|Out-Null;$dims++}catch{$errors+=$_.Exception.Message}}
 }
 $seen=@{};$i=0
 foreach($circle in $circles){if($i -ge 4){break};try{$rad=$circle.Geometry.Radius;$key=[Math]::Round($rad,4).ToString();if($seen.ContainsKey($key)){continue};$seen[$key]=$true;$sheet.DrawingDimensions.GeneralDimensions.AddDiameter($tg.CreatePoint2d(($front.Position.X+$front.Width/2+.8),($front.Position.Y-$i*.7)),$sheet.CreateGeometryIntent($circle),$false,$true,$true)|Out-Null;$dims++;$i++}catch{$errors+=$_.Exception.Message}}
 $notes="注記：JIS様式採用。規格完全適合の審査は未実施。`r`nFDM普通公差なし。重要な嵌合・取付寸法は現物確認後に確定。`r`n純正ホーン使用。スプライン未設計。サーボ・基板・磁石位置はHOLD。`r`n製作検査は3D正本と個別寸法条件を参照。印刷・組立・通電未承認。"
 if(-not $assembly){$note=$sheet.DrawingNotes.GeneralNotes.AddFitted($tg.CreatePoint2d(1.5,6.3),$notes);$note.TextStyle.Font='ＭＳ ゴシック';$note.TextStyle.FontSize=.25}
 $d.Update2($true)|Out-Null
 $folder=if($assembly){if($file.BaseName -match 'TwoJoint'){'two_joint_revb'}else{'follower_six_axis'}}else{'adapters'}
 $path="$mech/$folder/idw/$($file.BaseName)_JIS.idw";$d.SaveAs($path,$false)
 $ctx=$app.TransientObjects.CreateTranslationContext();$ctx.Type=[Inventor.IOMechanismEnum]::kFileBrowseIOMechanism;$opts=$app.TransientObjects.CreateNameValueMap();$pdf.HasSaveCopyAsOptions($d,$ctx,$opts)|Out-Null;$opts.Value('All_Color_AS_Black')=1;$opts.Value('Vector_Resolution')=400;$data=$app.TransientObjects.CreateDataMedium();$data.FileName="$mech/$folder/pdf/$($file.BaseName)_JIS.pdf";$pdf.SaveCopyAs($d,$ctx,$opts,$data)
 $records+=@{part=$file.BaseName;drawing=$path;associated_dimensions=$dims;views=$sheet.DrawingViews.Count;standard=$d.StylesManager.ActiveStandardStyle.Name;first_angle=$d.StylesManager.ActiveStandardStyle.FirstAngleProjection;errors=$errors;manufacturing='HOLD: incomplete location/depth/fit dimension audit'}
 $d.Close($true);$re=$app.Documents.Open($path,$false);$records[-1].missing_refs=@($re.ReferencedDocumentDescriptors|Where-Object ReferenceMissing|ForEach-Object FullDocumentName);$re.Close($true)
 Write-Output "JIS drawing saved: $($file.BaseName)"
}
$validationPath="$mech/release_review/drawing_validation.json"
if($AssemblyOnly -and (Test-Path $validationPath)){$records=@(Get-Content $validationPath -Raw|ConvertFrom-Json)+$records}
$records|ConvertTo-Json -Depth 8|Set-Content $validationPath -Encoding utf8
$app.SilentOperation=$false
