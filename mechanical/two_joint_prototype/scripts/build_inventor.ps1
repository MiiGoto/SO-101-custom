$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
. "$PSScriptRoot/connect_inventor.ps1"
$app.SilentOperation=$true
if($app.Documents.Count -gt 0){throw 'Save and close Inventor documents before regeneration to avoid duplicate native references.'}
foreach($folder in @('ipt','iam','stl','step','views','analysis','idw','pdf')){New-Item -ItemType Directory -Force "$root/$folder"|Out-Null}
$pt=$app.FileManager.GetTemplateFile([Inventor.DocumentTypeEnum]::kPartDocumentObject,[Inventor.SystemOfMeasureEnum]::kMetricSystemOfMeasure)
$at=$app.FileManager.GetTemplateFile([Inventor.DocumentTypeEnum]::kAssemblyDocumentObject,[Inventor.SystemOfMeasureEnum]::kMetricSystemOfMeasure)
$parts=@{}
$records=[System.Collections.Generic.List[object]]::new()
function NewPart($name){$script:doc=$app.Documents.Add([Inventor.DocumentTypeEnum]::kPartDocumentObject,$pt,$false);$script:cd=$doc.ComponentDefinition;$script:partname=$name;$lib=$app.AssetLibraries | Where-Object DisplayName -eq 'Inventor Material Library' | Select-Object -First 1;$asset=$lib.MaterialAssets.Item('MaterialInv_048').CopyTo($doc);$doc.ActiveMaterial=$asset}
function Sketch($z){$p=$cd.WorkPlanes.AddByPlaneAndOffset($cd.WorkPlanes.Item(3),$z/10,$false);$p.Visible=$false;return $cd.Sketches.Add($p,$false)}
function Extrude($s,$depth,$cut=$false){$op=[Inventor.PartFeatureOperationEnum]::kJoinOperation;if($cut){$op=[Inventor.PartFeatureOperationEnum]::kCutOperation};$d=$cd.Features.ExtrudeFeatures.CreateExtrudeDefinition($s.Profiles.AddForSolid(),$op);$d.SetDistanceExtent($depth/10,[Inventor.PartFeatureExtentDirectionEnum]::kPositiveExtentDirection);$f=$cd.Features.ExtrudeFeatures.Add($d);$s.Visible=$false;return $f}
function Box([double]$x,[double]$y,[double]$z,[double]$w,[double]$h,[double]$d,[bool]$cut=$false){$s=Sketch $z;$s.SketchLines.AddAsTwoPointRectangle($tg.CreatePoint2d(($x-$w/2)/10,($y-$h/2)/10),$tg.CreatePoint2d(($x+$w/2)/10,($y+$h/2)/10))|Out-Null;Extrude $s $d $cut|Out-Null}
function Disc([double]$x,[double]$y,[double]$z,[double]$r,[double]$d,[bool]$cut=$false){$s=Sketch $z;$s.SketchCircles.AddByCenterRadius($tg.CreatePoint2d($x/10,$y/10),$r/10)|Out-Null;Extrude $s $d $cut|Out-Null}
function Holes($x,$z,$d){foreach($a in @(0,90,180,270)){$t=$a*[Math]::PI/180;Disc ($x+12*[Math]::Cos($t)) (12*[Math]::Sin($t)) $z 1.6 $d $true}}
function SavePart($massOverride=0){
 $doc.Update2($true)|Out-Null
 if($cd.SurfaceBodies.Count -ne 1 -or -not $cd.SurfaceBodies.Item(1).IsSolid){throw "Invalid solid $partname"}
 # Template material is recorded; CAD solid mass is not a sliced FDM mass.
 if($massOverride -gt 0){$cd.MassProperties.Mass=$massOverride}
 $path="$root/ipt/$partname.ipt";$doc.SaveAs($path,$false);$parts[$partname]=$doc
 $mp=$cd.MassProperties;[double]$xx=0;[double]$yy=0;[double]$zz=0;[double]$xy=0;[double]$yz=0;[double]$xz=0
 $mp.XYZMomentsOfInertia([ref]$xx,[ref]$yy,[ref]$zz,[ref]$xy,[ref]$yz,[ref]$xz)
 Write-Output "Saved solid $partname"
 $records.Add([pscustomobject]@{part=$partname;mass_kg=$mp.Mass;volume_mm3=$mp.Volume*1000;com_mm=@(($mp.CenterOfMass.X*10),($mp.CenterOfMass.Y*10),($mp.CenterOfMass.Z*10));inertia_kg_m2=@(($xx*.0001),($yy*.0001),($zz*.0001),($xy*.0001),($yz*.0001),($xz*.0001));material=$doc.ActiveMaterial.DisplayName;mass_override=($massOverride -gt 0);solid_bodies=$cd.SurfaceBodies.Count;features=$cd.Features.Count})
}
NewPart 'Base';Box 0 -65 -40 130 8 85
foreach($x in @(-50,50)){Disc $x -65 -41 2.2 87 $true}
SavePart
NewPart 'Shoulder_Mount';Box 0 -58 -31 62 6 56;Box -27 -30 -31 8 56 24;Box 27 -30 -31 8 56 24;Box 0 -30 -31 62 56 4
foreach($x in @(-26,26)){Box $x -30 -32 3.4 22 58 $true}
SavePart
NewPart 'Upper_Arm';Box 45 0 0 90 22 5;Disc 0 0 0 16 5;Disc 90 0 0 16 5;Box 45 0 -1 48 12 7 $true
foreach($x in @(0,90)){Disc $x 0 -1 4 7 $true;Holes $x -1 7}
# Datum at true elbow output axis, independent of assumed servo case origin.
$cd.WorkAxes.AddFixed($tg.CreatePoint(9,0,0),$tg.CreateUnitVector(0,0,1),$false)|Out-Null
SavePart
NewPart 'Elbow_Mount';Box 90 -42 6 62 6 24;Box 63 -22 6 8 40 24;Box 117 -22 6 8 40 24;Box 90 -22 6 62 40 2
Disc 90 0 5 8 4 $true
foreach($x in @(64,116)){Box $x -20 5 3.4 18 27 $true}
SavePart
NewPart 'Forearm';Box 50 0 33 100 20 5;Disc 0 0 33 16 5;Disc 100 0 33 12 5;Box 50 0 32 55 10 7 $true;Disc 0 0 32 4 7 $true;Holes 0 32 7
foreach($y in @(-6,6)){Disc 100 $y 32 1.6 7 $true};SavePart
NewPart 'Servo_Horn_Adapter';Disc 0 0 -5 15 5;Disc 0 0 -6 2.5 7 $true;Holes 0 -6 7;SavePart
NewPart 'Elbow_Horn_Adapter';Disc 0 0 28 15 5;Disc 0 0 27 2.5 7 $true;Holes 0 27 7;SavePart
NewPart 'Payload_Mount';Box 100 0 38 22 22 4;foreach($y in @(-6,6)){Disc 100 $y 37 1.6 6 $true};Box 105 0 42 8 22 16;Disc 105 0 41 2 18 $true;SavePart
NewPart 'Joint_Stop';Disc 0 0 -9 31 4;Disc 0 0 -10 21 6 $true
foreach($a in @(-20.33,95.33,140.33)){Disc (25*[Math]::Cos($a*[Math]::PI/180)) (25*[Math]::Sin($a*[Math]::PI/180)) -10 1.6 6 $true};SavePart
NewPart 'Encoder_Mount';Box 0 0 23 30 30 3;Box 0 0 22 18 18 5 $true;foreach($x in @(-12,12)){Box $x 0 22 3.4 20 5 $true};SavePart
NewPart 'Bearing_Support';Disc 0 0 10 15 8;Disc 0 0 9 2.7 10 $true;Disc 0 0 12 8.1 7 $true;Holes 0 9 10;SavePart
NewPart 'Magnet_Carrier';Disc 0 0 18 5 5;Disc 0 0 17 2.6 3 $true;Disc 0 0 20.8 3.1 3 $true;SavePart
NewPart 'Spacer';Disc 0 0 5 6 5;Disc 0 0 4 1.6 7 $true;SavePart
NewPart 'Spring_Base_Anchor';Box -35 35 -43 14 30 6;Disc -35 40 -44 2.5 8 $true;SavePart
NewPart 'Spring_Link_Anchor';Box 25 0 -43 26 10 6;Disc 35 0 -44 2.5 8 $true;SavePart
# Envelope only: motor shape origin, mounting and internal COM remain unmeasured.
NewPart 'Servo_Envelope';Box 0 -19 -26 38 38.5 19;SavePart .042
NewPart 'Servo_Mount_Coupon';Box 0 0 0 52 52 4;Box 0 0 -1 38.6 39.1 6 $true;foreach($x in @(-23,23)){Box $x 0 -1 3.4 20 6 $true};SavePart
NewPart 'Horn_Adapter_Test';Disc 0 0 0 15 4;Disc 0 0 -1 2.5 6 $true;Holes 0 -1 6;SavePart
NewPart 'Encoder_Alignment_Test';Box 0 0 0 32 32 4;Box 0 0 -1 18 18 6 $true;foreach($x in @(-13,13)){Box $x 0 -1 3.4 18 6 $true};SavePart
NewPart 'Bearing_Fit_Coupon';Box 0 0 0 65 25 8;foreach($item in @(@(-21,8.0),@(0,8.1),@(21,8.2))){Disc $item[0] 0 -1 $item[1] 10 $true};SavePart
. "$PSScriptRoot/support_parts.fragment.ps1"
$records|ConvertTo-Json -Depth 8|Set-Content "$root/analysis/mass_properties.json" -Encoding utf8
$assembly=$app.Documents.Add([Inventor.DocumentTypeEnum]::kAssemblyDocumentObject,$at,$false);$ac=$assembly.ComponentDefinition
function Occ($name,$part,$x=0,$z=0){$m=$tg.CreateMatrix();$m.SetTranslation($tg.CreateVector($x/10,0,$z/10));$o=$ac.Occurrences.Add("$root/ipt/$part.ipt",$m);$o.Name=$name;return $o}
function Plane($o,$i){[object]$p=New-Object System.Object;$o.CreateGeometryProxy($o.Definition.WorkPlanes.Item($i),[ref]$p);return $p}
function Axis($o,$i=3){[object]$p=New-Object System.Object;$o.CreateGeometryProxy($o.Definition.WorkAxes.Item($i),[ref]$p);return $p}
function Rigid($o,$b,$offset=0){foreach($i in @(1,2,3)){$d=0;if($i -eq 3){$d=$offset/10};$ac.Constraints.AddFlushConstraint((Plane $o $i),(Plane $b $i),$d)|Out-Null}}
$base=Occ 'Base_FIXED' 'Base';$base.Grounded=$true
$sm=Occ 'Shoulder_Housing_Cradle' 'Shoulder_Mount';Rigid $sm $base
$motor1=Occ 'Shoulder_Motor_ASSUMED_ENVELOPE' 'Servo_Envelope';Rigid $motor1 $base
$upper=Occ 'Upper_Arm_ROTATING' 'Upper_Arm'
$ac.Constraints.AddMateConstraint((Axis $upper),(Axis $base),0)|Out-Null
$ac.Constraints.AddFlushConstraint((Plane $upper 3),(Plane $base 3),0)|Out-Null
$horn1=Occ 'Shoulder_Horn_Adapter' 'Servo_Horn_Adapter';Rigid $horn1 $upper
$em=Occ 'Elbow_Housing_Cradle' 'Elbow_Mount';Rigid $em $upper
$motor2=Occ 'Elbow_Motor_ASSUMED_ENVELOPE' 'Servo_Envelope' 90 34
# Explicit plane offsets rigidly locate motor envelope at elbow.
$ac.Constraints.AddFlushConstraint((Plane $motor2 1),(Plane $upper 1),-9)|Out-Null
$ac.Constraints.AddFlushConstraint((Plane $motor2 2),(Plane $upper 2),0)|Out-Null
$ac.Constraints.AddFlushConstraint((Plane $motor2 3),(Plane $upper 3),-3.4)|Out-Null
$forearm=Occ 'Forearm_ROTATING' 'Forearm' 90
$ac.Constraints.AddMateConstraint((Axis $forearm),(Axis $upper 4),0)|Out-Null
$ac.Constraints.AddFlushConstraint((Plane $forearm 3),(Plane $upper 3),0)|Out-Null
$horn2=Occ 'Elbow_Horn_Adapter' 'Elbow_Horn_Adapter' 90;Rigid $horn2 $forearm
$payload=Occ 'Payload_Mount' 'Payload_Mount' 90;Rigid $payload $forearm
. "$PSScriptRoot/support_assembly.fragment.ps1"
# Fit remains conditional on measured horns and sensor boards.
# until the actual opposing shaft, board and horn interfaces are measured.
$assembly.Update2($true)|Out-Null
$assembly.SaveAs("$root/iam/SO101_TwoJoint_Prototype.iam",$false)
$state=@{inventor_version=$app.SoftwareVersion.DisplayVersion;occurrences=$ac.Occurrences.Count;constraints=$ac.Constraints.Count;constraints_state=@($ac.Constraints|ForEach-Object{[pscustomobject]@{name=$_.Name;health=$_.HealthStatus.ToString();suppressed=$_.Suppressed}});status='CAD core assembly; hardware interfaces require physical measurement'}
$state|ConvertTo-Json -Depth 7|Set-Content "$root/analysis/assembly_validation.json" -Encoding utf8
foreach($entry in $parts.GetEnumerator()){
 foreach($fmt in @('stl','step')){
 $id='{533E9A98-FC3B-11D4-8E7E-0010B541CD80}';if($fmt -eq 'step'){$id='{90AF7F40-0C01-11D5-8E83-0010B541CD80}'}
 $translator=$app.ApplicationAddIns.ItemById($id);$ctx=$app.TransientObjects.CreateTranslationContext();$ctx.Type=[Inventor.IOMechanismEnum]::kFileBrowseIOMechanism;$opts=$app.TransientObjects.CreateNameValueMap();$translator.HasSaveCopyAsOptions($entry.Value,$ctx,$opts)|Out-Null
 if($fmt -eq 'stl'){$opts.Value('ExportUnits')=5;$opts.Value('Resolution')=1}else{$opts.Value('ApplicationProtocolType')=3}
 $data=$app.TransientObjects.CreateDataMedium();$data.FileName="$root/$fmt/$($entry.Key).$fmt";$translator.SaveCopyAs($entry.Value,$ctx,$opts,$data)
 }
}
$assembly.Save();$assembly.Close($true)
$check=$app.Documents.Open("$root/iam/SO101_TwoJoint_Prototype.iam",$false);$check.Update2($true)|Out-Null
$missing=@($check.ReferencedDocumentDescriptors|Where-Object {$_.ReferenceMissing}|ForEach-Object {$_.FullDocumentName})
@{missing_references=$missing;reopened=$true;occurrences=$check.ComponentDefinition.Occurrences.Count}|ConvertTo-Json|Set-Content "$root/analysis/reopen_validation.json" -Encoding utf8
$app.SilentOperation=$false
Write-Output 'Native CAD, neutral exports and reopen check saved.'
