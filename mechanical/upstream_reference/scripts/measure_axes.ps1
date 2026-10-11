$ErrorActionPreference='Stop'
. "$PSScriptRoot/../../two_joint_prototype/scripts/connect_inventor.ps1"
$root=Split-Path $PSScriptRoot -Parent;$mech=Split-Path $root -Parent
$ref=Get-Content "$root/kinematic_reference.json" -Raw|ConvertFrom-Json
$rows=@()
foreach($name in @('Upper_arm_SO101','Under_arm_SO101','Wrist_Roll_Pitch_SO101')){
 $item=$ref.parts|Where-Object part -eq $name;$d=$app.Documents.Open("$mech/follower_six_axis/ipt/$name.ipt",$false);$cyl=@()
 foreach($body in $d.ComponentDefinition.SurfaceBodies){foreach($face in $body.Faces){if($face.SurfaceType -eq [Inventor.SurfaceTypeEnum]::kCylinderSurface){$g=$face.Geometry;$cyl+=@{radius_mm=$g.Radius*10;point_mm=@(($g.BasePoint.X*10),($g.BasePoint.Y*10),($g.BasePoint.Z*10));axis=@($g.AxisVector.X,$g.AxisVector.Y,$g.AxisVector.Z)}}}}
 $box=$d.ComponentDefinition.RangeBox
 $rows+=@{part=$name;cylinders=$cyl;bounds_min_mm=@(($box.MinPoint.X*10),($box.MinPoint.Y*10),($box.MinPoint.Z*10));bounds_max_mm=@(($box.MaxPoint.X*10),($box.MaxPoint.Y*10),($box.MaxPoint.Z*10));solid_bodies=@($d.ComponentDefinition.SurfaceBodies|ForEach-Object {$_.IsSolid});world=$item.world;local=$item.local}
}
$rows|ConvertTo-Json -Depth 10|Set-Content "$root/axis_geometry.json" -Encoding utf8
Write-Output 'Real STEP cylindrical-axis geometry measured.'
