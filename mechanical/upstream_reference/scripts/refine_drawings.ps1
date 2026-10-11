$ErrorActionPreference='Stop'
. "$PSScriptRoot/../../two_joint_prototype/scripts/connect_inventor.ps1"
$mech=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent;$app.SilentOperation=$true
$pdf=$app.ApplicationAddIns.ItemById('{0AC6FD96-2F4D-42CE-8BE0-8AEA580399E4}')
$rows=@()
foreach($f in Get-ChildItem "$mech/adapters/idw/*_JIS.idw"){
 $d=$app.Documents.Open($f.FullName,$false);$sheet=$d.ActiveSheet;$front=$sheet.DrawingViews.Item(1);$top=$sheet.DrawingViews.Item(2);$side=$sheet.DrawingViews.Item(3);$iso=$sheet.DrawingViews.Item(4)
 $scale=if($f.Name -match 'arm_SO101'){.5}else{1.0};$front.Scale=$scale;$iso.Scale=$scale*.5
 foreach($v in @($front,$top,$side,$iso)){$v.ShowLabel=$true;$v.Label.FormattedText='<DrawingViewScale/>'}
 foreach($dim in @($sheet.DrawingDimensions.GeneralDimensions)){$dim.Delete()}
 $d.Update2($true)|Out-Null;$lines=@();$circles=@();$seen=@{};$errors=@();$h=0;$v=0;$diam=0
 foreach($c in $front.DrawingCurves([Type]::Missing)){
  try{if($c.CurveType -eq [Inventor.CurveTypeEnum]::kCircleCurve){$circles+=$c}elseif($c.StartPoint -and $c.EndPoint){$length=$c.StartPoint.DistanceTo($c.EndPoint);if($length -gt .2){$lines+=@{curve=$c;length=$length;horizontal=([Math]::Abs($c.StartPoint.Y-$c.EndPoint.Y) -lt .001)}}}}catch{}
 }
 foreach($line in @($lines|Sort-Object length -Descending)){
  $mm=[Math]::Round(($line.length/$scale*10),2);$key="$($line.horizontal)/$mm";if($seen.ContainsKey($key)){continue};$seen[$key]=$true
  if($line.horizontal){if($h -ge 3){continue};$p=$tg.CreatePoint2d($front.Position.X,($front.Position.Y-$front.Height/2-.6-$h*.65));$h++}else{if($v -ge 3){continue};$p=$tg.CreatePoint2d(($front.Position.X-$front.Width/2-.6-$v*.65),$front.Position.Y);$v++}
  try{$sheet.DrawingDimensions.GeneralDimensions.AddLinear($p,$sheet.CreateGeometryIntent($line.curve))|Out-Null}catch{$errors+=$_.Exception.Message}
 }
 $seen=@{}
 foreach($c in $circles){try{
  $radius=$c.ModelGeometry.Geometry.Radius;$key=[Math]::Round($radius,5).ToString();$sheet.Centermarks.Add($sheet.CreateGeometryIntent($c))|Out-Null
  if($seen.ContainsKey($key) -or $diam -ge 4){continue};$seen[$key]=$true
  $sheet.DrawingDimensions.GeneralDimensions.AddDiameter($tg.CreatePoint2d(($front.Position.X+$front.Width/2+.6),($front.Position.Y-($diam-1)*.8)),$sheet.CreateGeometryIntent($c),$false,$true,$true)|Out-Null;$diam++
 }catch{$errors+=$_.Exception.Message}}
 # Thickness is associated with a visible edge of the right projected view.
 $shortest=$null;$min=999
 foreach($c in $side.DrawingCurves([Type]::Missing)){try{if($c.StartPoint -and $c.EndPoint -and [Math]::Abs($c.StartPoint.Y-$c.EndPoint.Y) -lt .001){$l=$c.StartPoint.DistanceTo($c.EndPoint);if($l -gt .1 -and $l -lt $min){$min=$l;$shortest=$c}}}catch{}}
 if($shortest){try{$sheet.DrawingDimensions.GeneralDimensions.AddLinear($tg.CreatePoint2d($side.Position.X,($side.Position.Y-$side.Height/2-.6)),$sheet.CreateGeometryIntent($shortest))|Out-Null}catch{$errors+=$_.Exception.Message}}
 # Hole pitch on the bearing coupon uses two model-linked center intents.
 if($f.Name -match 'Bearing_Fit' -and $circles.Count -ge 3){$sorted=@($circles|Sort-Object {$_.CenterPoint.X});for($i=0;$i -lt 2;$i++){try{$a=$sheet.CreateGeometryIntent($sorted[$i],[Inventor.PointIntentEnum]::kCenterPointIntent);$b=$sheet.CreateGeometryIntent($sorted[$i+1],[Inventor.PointIntentEnum]::kCenterPointIntent);$sheet.DrawingDimensions.GeneralDimensions.AddLinear($tg.CreatePoint2d(($front.Position.X+($i-.5)*2),($front.Position.Y+$front.Height/2+.6)),$a,$b,[Inventor.DimensionTypeEnum]::kHorizontalDimensionType)|Out-Null}catch{$errors+=$_.Exception.Message}}}
 $d.Update2($true)|Out-Null;$d.Save()
 $ctx=$app.TransientObjects.CreateTranslationContext();$ctx.Type=[Inventor.IOMechanismEnum]::kFileBrowseIOMechanism;$opts=$app.TransientObjects.CreateNameValueMap();$pdf.HasSaveCopyAsOptions($d,$ctx,$opts)|Out-Null;$opts.Value('All_Color_AS_Black')=1;$data=$app.TransientObjects.CreateDataMedium();$data.FileName="$mech/adapters/pdf/$($f.BaseName).pdf";$pdf.SaveCopyAs($d,$ctx,$opts,$data)
 $rows+=@{part=$f.BaseName;associated_dimensions=$sheet.DrawingDimensions.GeneralDimensions.Count;center_marks=$sheet.Centermarks.Count;scale=$front.Scale;errors=$errors;full_dimension_audit='HOLD; servo/horn interfaces remain TBD'};$d.Close($true)
 Write-Output "Refined $($f.BaseName)"
}
$rows|ConvertTo-Json -Depth 8|Set-Content "$mech/release_review/refined_dimensions.json" -Encoding utf8
$app.SilentOperation=$false
