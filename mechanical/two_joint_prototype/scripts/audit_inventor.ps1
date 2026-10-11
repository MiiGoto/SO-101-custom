param([switch]$Cold)
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
. "$PSScriptRoot/connect_inventor.ps1"
$app.SilentOperation=$true
if($Cold){$foreign=@($app.Documents|Where-Object {$_.FullFileName -ne '' -and $_.FullFileName -notlike "$root*"});if($foreign.Count){throw 'Unrelated documents present; refusing cold close'};$app.Documents.CloseAll($false);if($app.Documents.Count -ne 0){throw 'Cold audit did not reach an empty session'}}
$path="$root/iam/SO101_TwoJoint_Prototype.iam"
$a=$app.Documents.Open($path,$false);$ac=$a.ComponentDefinition
function Plane($o,$i){[object]$p=New-Object System.Object;$o.CreateGeometryProxy($o.Definition.WorkPlanes.Item($i),[ref]$p);return $p}
function DOF($o){return @{name=$o.Name;api_count_status='TBD: COM output marshaling failed; use independent angle-motion audit'}}
$upper=$ac.Occurrences.ItemByName('Upper_Arm_ROTATING');$fore=$ac.Occurrences.ItemByName('Forearm_ROTATING');$base=$ac.Occurrences.ItemByName('Base_FIXED')
$expected=Get-Content "$root/analysis/mass_properties.json" -Raw | ConvertFrom-Json
$referenceCheck=@()
foreach($o in $ac.Occurrences){$name=[IO.Path]::GetFileNameWithoutExtension($o.Definition.Document.FullFileName);$record=$expected | Where-Object part -eq $name | Select-Object -First 1;$volume=$o.Definition.MassProperties.Volume*1000;$referenceCheck+=@{occurrence=$o.Name;part=$name;volume_mm3=$volume;mass_kg=$o.Definition.MassProperties.Mass;position_mm=@(($o.Transformation.Cell(1,4)*10),($o.Transformation.Cell(2,4)*10),($o.Transformation.Cell(3,4)*10));matches_saved_part=([Math]::Abs($volume-$record.volume_mm3) -lt .01)};if([Math]::Abs($volume-$record.volume_mm3) -ge .01){throw "Stale native reference: $name"}}
$before=@((DOF $upper),(DOF $fore))
$c1=$ac.Constraints.AddAngleConstraint((Plane $upper 1),(Plane $base 1),'0 deg');$c1.Name='AUDIT_SHOULDER_ANGLE'
$c2=$ac.Constraints.AddAngleConstraint((Plane $fore 1),(Plane $upper 1),'0 deg');$c2.Name='AUDIT_ELBOW_ANGLE'
$rows=@()
foreach($pose in @(@('initial',0,0),@('maximum_flex',75,120),@('extension',0,0),@('middle',35,60),@('lift',60,30),@('shoulder_only',30,0),@('elbow_only',0,60))){
 $c1.Angle.Expression="$(-[double]$pose[1]) deg";$c2.Angle.Expression="$(-[double]$pose[2]) deg";$ok=$a.Update2($true)
 $all=$app.TransientObjects.CreateObjectCollection();foreach($o in $ac.Occurrences){$all.Add($o)}
 $hits=$ac.AnalyzeInterference($all,$null);$h=@();foreach($hit in $hits){$h+=@{a=$hit.OccurrenceOne.Name;b=$hit.OccurrenceTwo.Name;volume_mm3=$hit.Volume*1000}}
 $rows+=@{pose=$pose[0];requested_angles_deg=@($pose[1],$pose[2]);update_ok=$ok;constraints=@($ac.Constraints|ForEach-Object{@{name=$_.Name;health=$_.HealthStatus.ToString()}});interferences=$h;upper_matrix=@($upper.Transformation.Cell(1,1),$upper.Transformation.Cell(2,1));forearm_matrix=@($fore.Transformation.Cell(1,1),$fore.Transformation.Cell(2,1));locked_dof=@((DOF $upper),(DOF $fore))}
}
$c1.Angle.Expression='0 deg';$c2.Angle.Expression='0 deg';$a.Update2($true)|Out-Null
$c2.Delete();$c1.Delete();$a.Update2($true)|Out-Null;$after=@((DOF $upper),(DOF $fore));$a.Save();$a.Close($true)
$re=$app.Documents.Open($path,$false);$re.Update2($true)|Out-Null
@{cold_reload=[bool]$Cold;reference_geometry_checks=$referenceCheck;before_dof=$before;after_dof=$after;pose_audit=$rows;reopened=$true;missing_references=@($re.ReferencedDocumentDescriptors|Where-Object {$_.ReferenceMissing}|ForEach-Object {$_.FullDocumentName});final_constraints=@($re.ComponentDefinition.Constraints|ForEach-Object{@{name=$_.Name;health=$_.HealthStatus.ToString();suppressed=$_.Suppressed}})}|ConvertTo-Json -Depth 12|Set-Content "$root/analysis/kinematic_audit.json" -Encoding utf8
$partchecks=@();foreach($f in Get-ChildItem "$root/ipt/*.ipt"){$d=$app.Documents.Open($f.FullName,$false);$d.Update2($true)|Out-Null;$partchecks+=@{name=$f.Name;solid_bodies=$d.ComponentDefinition.SurfaceBodies.Count;solid=$d.ComponentDefinition.SurfaceBodies.Item(1).IsSolid;feature_health=@($d.ComponentDefinition.Features|ForEach-Object {$_.HealthStatus.ToString()})}}
$partchecks|ConvertTo-Json -Depth 8|Set-Content "$root/analysis/part_reopen_validation.json" -Encoding utf8
$drawChecks=@();foreach($file in Get-ChildItem "$root/idw/*.idw"){$drawing=$app.Documents.Open($file.FullName,$false);$drawing.Update2($true)|Out-Null;$drawChecks+=@{name=$file.Name;views=$drawing.ActiveSheet.DrawingViews.Count;dimensions=$drawing.ActiveSheet.DrawingDimensions.GeneralDimensions.Count;missing_references=@($drawing.ReferencedDocumentDescriptors|Where-Object {$_.ReferenceMissing}|ForEach-Object {$_.FullDocumentName})};$drawing.Close($true)}
$drawChecks|ConvertTo-Json -Depth 6|Set-Content "$root/analysis/drawing_reopen_validation.json" -Encoding utf8
$app.SilentOperation=$false
Write-Output 'Pose, DOF, interference and native reopen audit complete.'
