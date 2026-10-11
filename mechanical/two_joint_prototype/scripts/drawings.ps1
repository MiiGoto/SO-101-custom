$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
. "$PSScriptRoot/connect_inventor.ps1"
$app.SilentOperation=$true
$template='C:/Users/Public/Documents/Autodesk/Inventor 2026/Templates/ja-JP/Metric/ISO.idw'
$pdf=$app.ApplicationAddIns.ItemById('{0AC6FD96-2F4D-42CE-8BE0-8AEA580399E4}')
$ctx=$app.TransientObjects.CreateTranslationContext();$ctx.Type=[Inventor.IOMechanismEnum]::kFileBrowseIOMechanism
$files=@(Get-ChildItem "$root/ipt/*.ipt")+@(Get-Item "$root/iam/SO101_TwoJoint_Prototype.iam")
$rows=@()
foreach($file in $files){
 $model=$app.Documents.Open($file.FullName,$false);$drawing=$app.Documents.Add([Inventor.DocumentTypeEnum]::kDrawingDocumentObject,$template,$false);$sheet=$drawing.ActiveSheet
 if($sheet.TitleBlock){$sheet.TitleBlock.Delete()}
 $w=$sheet.Width;$h=$sheet.Height;$scale=1.2;if($file.BaseName -in @('Base','Upper_Arm','Forearm','SO101_TwoJoint_Prototype')){$scale=.8}
 if($file.Extension -eq '.iam'){$scale=.4}
 $view=$sheet.DrawingViews.AddBaseView($model,$tg.CreatePoint2d($w*.3,$h*.65),$scale,[Inventor.ViewOrientationTypeEnum]::kFrontViewOrientation,[Inventor.DrawingViewStyleEnum]::kHiddenLineRemovedDrawingViewStyle)
 $sheet.DrawingViews.AddBaseView($model,$tg.CreatePoint2d($w*.75,$h*.65),$scale*.7,[Inventor.ViewOrientationTypeEnum]::kIsoTopRightViewOrientation,[Inventor.DrawingViewStyleEnum]::kHiddenLineRemovedDrawingViewStyle)|Out-Null
 $drawing.Update2($false)|Out-Null;$lines=@();$dims=0
 foreach($curve in $view.DrawingCurves([Type]::Missing)){try{if($curve.StartPoint -and $curve.EndPoint){$length=$curve.StartPoint.DistanceTo($curve.EndPoint);if($length -gt .3){$lines+=@{curve=$curve;length=$length}}}}catch{}}
 foreach($line in (@($lines|Where-Object {[Math]::Abs($_.curve.EndPoint.X-$_.curve.StartPoint.X) -ge [Math]::Abs($_.curve.EndPoint.Y-$_.curve.StartPoint.Y)}|Sort-Object length -Descending|Select-Object -First 1)+@($lines|Where-Object {[Math]::Abs($_.curve.EndPoint.X-$_.curve.StartPoint.X) -lt [Math]::Abs($_.curve.EndPoint.Y-$_.curve.StartPoint.Y)}|Sort-Object length -Descending|Select-Object -First 1))){try{$p=$line.curve.StartPoint;$q=$line.curve.EndPoint;$intent=$sheet.CreateGeometryIntent($line.curve);$horizontal=[Math]::Abs($q.X-$p.X) -ge [Math]::Abs($q.Y-$p.Y);$textPoint=$tg.CreatePoint2d($view.Position.X,($view.Position.Y-$view.Height/2-1.2));if(-not $horizontal){$textPoint=$tg.CreatePoint2d(($view.Position.X-$view.Width/2-1.2),$view.Position.Y)};$sheet.DrawingDimensions.GeneralDimensions.AddLinear($textPoint,$intent)|Out-Null;$dims++}catch{}}
 $notes="SO-101 TWO JOINT / REV P1 / FIT CHECK ONLY`r`n$($file.BaseName) / units mm / Inventor 2026.2`r`nNo horn spline or manufacturer hole pattern modeled.`r`nMaterial: full-solid PET mass proxy; print PLA+ or PETG after coupon checks.`r`nFrame assembly and power-on are HOLD. Measure servo and horn first."
 switch($file.BaseName){
 'Upper_Arm'{$notes+="`r`nAxis centers 90; plate 5; hubs OD32; bore OD8.`r`n4x diameter3.2 on PCD24 at each hub. Window48x12."}
 'Forearm'{$notes+="`r`nAxis-to-payload100; plate5; hub OD32; bore8.`r`n4x diameter3.2 PCD24 at joint; payload holes3.2 at y=+/-6."}
 'Servo_Mount_Coupon'{$notes+="`r`n52x52x4; window38.6x39.1. Check case clearance ONLY.`r`nSlots3.4x20 at x=+/-23; these are OUR clamp slots, not servo holes."}
 'Horn_Adapter_Test'{$notes+="`r`nOD30; t4; central access5; OUR 4x3.2 PCD24.`r`nHorn mating face is a drilling blank; confirm actual horn before drilling."}
 'Bearing_Fit_Coupon'{$notes+="`r`n65x25x8; bores16.0 /16.2 /16.4 left to right.`r`nNo bearing owned. Do not hammer bearing into unqualified FDM seat."}
 'Encoder_Alignment_Test'{$notes+="`r`n32x32x4; window18x18; slots3.4x18 at x=+/-13.`r`nGeneric board holder; board footprint and air gap require measurement."}
 'Encoder_Mount'{$notes+="`r`n30x30x3; window18x18; slots3.4x20 at x=+/-12.`r`nSensor active-plane position and standoff stack TBD."}
 'Bearing_Support'{$notes+="`r`nOD30 x8; through5.4; seat16.2 from z12 to18.`r`n625 candidate 5x16x5; retainer/shaft/fit not qualified."}
 'Joint_Stop'{$notes+="`r`nOD62 ID42 t4; M3 holes on radius25 at -20.33,95.33,140.33 deg.`r`nMoving lug and retention interfaces are HOLD; not a functioning stop yet."}
 'SO101_TwoJoint_Prototype'{$notes+="`r`nShoulder(0,0,0); elbow(90,0,0); tip(190,0,0) nominal.`r`nXY motion plane, Z axes; provisional shoulder0..75 /elbow0..120 deg.`r`nBearing/encoder/stop/spring attachment completion requires physical fit data."}
 }
 $sheet.DrawingNotes.GeneralNotes.AddFitted($tg.CreatePoint2d(1.5,$h*.3),$notes)|Out-Null
 $drawing.Update2($false)|Out-Null;$drawing.SaveAs("$root/idw/$($file.BaseName).idw",$false)
 $opts=$app.TransientObjects.CreateNameValueMap();$pdf.HasSaveCopyAsOptions($drawing,$ctx,$opts)|Out-Null;$opts.Value('All_Color_AS_Black')=1;$opts.Value('Vector_Resolution')=400
 $data=$app.TransientObjects.CreateDataMedium();$data.FileName="$root/pdf/$($file.BaseName).pdf";$pdf.SaveCopyAs($drawing,$ctx,$opts,$data)
 $rows+=@{name=$file.BaseName;native_dimensions=$dims;status='COMPLETED drawing file; fit and manufacturing HOLD'};$drawing.Close($true)
 Write-Output "Drawing: $($file.BaseName)"
}
$rows|ConvertTo-Json -Depth 5|Set-Content "$root/analysis/drawing_validation.json" -Encoding utf8
$app.SilentOperation=$false
