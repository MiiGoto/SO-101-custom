param([switch]$TwoOnly)
$ErrorActionPreference='Stop'
. "$PSScriptRoot/../../two_joint_prototype/scripts/connect_inventor.ps1"
$mech=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$ref=Get-Content "$mech/upstream_reference/kinematic_reference.json" -Raw|ConvertFrom-Json
$app.SilentOperation=$true
function Proxy($o,$obj){[object]$p=New-Object System.Object;$o.CreateGeometryProxy($obj,[ref]$p);return $p}
foreach($group in @(@('two_joint_revb','SO101_TwoJoint_RevB'),@('follower_six_axis','SO101_Custom_Follower_RevA'))){
 if($TwoOnly -and $group[0] -ne 'two_joint_revb'){continue}
 $folder=$group[0];$file=$group[1];$a=$app.Documents.Open("$mech/$folder/iam/$file.iam",$false);$ac=$a.ComponentDefinition
 $meta=Get-Content "$mech/$folder/analysis/assembly.json" -Raw|ConvertFrom-Json
 $angles=@();$baseline=@();$poses=@();$dof=@()
 foreach($jr in $meta.joint_records){$j=$ref.joints|Where-Object name -eq $jr.name;$parent=$ac.Occurrences.ItemByName($jr.parent);$child=$ac.Occurrences.ItemByName($jr.child)
  $p=$parent.Definition.WorkPlanes.Item("JOINT_$($j.name)_1")
  $c=$ac.Constraints.AddAngleConstraint((Proxy $child $child.Definition.WorkPlanes.Item(1)),(Proxy $parent $p),'0 deg');$c.Name="AUDIT_$($j.name)";$angles+=@{joint=$j;constraint=$c;child=$child}
 }
 # Each unconstrained revolute is driven alone while the other angles remain fixed.
 foreach($entry in $angles){$entry.constraint.Angle.Expression='-10 deg';$ok=$a.Update2($true);$m=$entry.child.Transformation;$rotation=@();for($i=1;$i -le 3;$i++){for($j=1;$j -le 3;$j++){$rotation+=$m.Cell($i,$j)}};$dof+=@{joint=$entry.joint.name;command_deg=10;update_ok=$ok;world_rotation=$rotation;constraint_health=@($ac.Constraints|ForEach-Object {$_.HealthStatus.ToString()})};$entry.constraint.Angle.Expression='0 deg';$a.Update2($true)|Out-Null}
 # 5-degree grid along one axis at a time: scoped sweep, not a proof over the Cartesian product.
 foreach($entry in $angles){foreach($deg in @(-30,-15,0,15,30)){
  $entry.constraint.Angle.Expression="$(-$deg) deg";$ok=$a.Update2($true)
  $all=$app.TransientObjects.CreateObjectCollection();foreach($o in $ac.Occurrences){if($o.Visible){$all.Add($o)}}
  $hits=$ac.AnalyzeInterference($all,$null);$h=@();foreach($hit in $hits){$h+=@{a=$hit.OccurrenceOne.Name;b=$hit.OccurrenceTwo.Name;volume_mm3=$hit.Volume*1000}}
  $poses+=@{joint=$entry.joint.name;angle_deg=$deg;update_ok=$ok;interferences=$h}
 };$entry.constraint.Angle.Expression='0 deg';$a.Update2($true)|Out-Null}
 foreach($entry in $angles){$entry.constraint.Delete()};$a.Update2($true)|Out-Null;$a.Save();$a.Close($true)
 $a=$app.Documents.Open("$mech/$folder/iam/$file.iam",$true);$a.Activate();$a.Update2($true)|Out-Null
 $camera=$app.ActiveView.Camera;$camera.ViewOrientationType=[Inventor.ViewOrientationTypeEnum]::kIsoTopRightViewOrientation;$camera.Apply();$app.ActiveView.Fit();$app.ActiveView.SaveAsBitmap("$mech/$folder/views/inventor_assembly.png",1400,1100)
 @{reopened=$true;missing_refs=@($a.ReferencedDocumentDescriptors|Where-Object ReferenceMissing|ForEach-Object FullDocumentName);constraints=@($a.ComponentDefinition.Constraints|ForEach-Object{@{name=$_.Name;health=$_.HealthStatus.ToString()}});independent_motion=$dof;sampled_sweeps=$poses;scope='Independent 10-degree motion and five poses per axis; full coupled range, physical horn and cables NOT VERIFIED'}|ConvertTo-Json -Depth 12|Set-Content "$mech/$folder/analysis/motion_interference.json" -Encoding utf8
 Write-Output "Motion/reopen audit saved $folder"
}
$app.SilentOperation=$false
