$ErrorActionPreference='Stop'
. "$PSScriptRoot/../../two_joint_prototype/scripts/connect_inventor.ps1"
$mech=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$ref=Get-Content "$mech/upstream_reference/kinematic_reference.json" -Raw|ConvertFrom-Json
$path="$mech/two_joint_revb/iam/SO101_TwoJoint_RevB.iam";$a=$app.Documents.Open($path,$false);$ac=$a.ComponentDefinition
function Proxy($o,$obj){[object]$p=New-Object System.Object;$o.CreateGeometryProxy($obj,[ref]$p);return $p}
function Matrix($rows){$m=$tg.CreateMatrix();for($i=1;$i -le 4;$i++){for($j=1;$j -le 4;$j++){$v=[double]$rows[$i-1][$j-1];if($j -eq 4 -and $i -lt 4){$v/=10};$m.Cell($i,$j)=$v}};return $m}
$b=$ac.Occurrences.Add("$mech/follower_six_axis/ipt/REF_base_link.ipt",$tg.CreateMatrix());$b.Name='REF_base_link';$b.Grounded=$true;$b.Visible=$false;$b.BOMStructure=[Inventor.BOMStructureEnum]::kReferenceBOMStructure
$shoulder=$ac.Occurrences.ItemByName('REF_shoulder_link');$shoulder.Grounded=$false
for($k=1;$k -le 3;$k++){$ac.Constraints.AddFlushConstraint((Proxy $shoulder $shoulder.Definition.WorkPlanes.Item($k)),(Proxy $b $b.Definition.WorkPlanes.Item("JOINT_shoulder_pan_$k")),0)|Out-Null}
$meta=Get-Content "$mech/two_joint_revb/analysis/assembly.json" -Raw|ConvertFrom-Json
foreach($item in @($ref.parts|Where-Object link -eq 'base_link')){
 $d=$app.Documents.Open("$mech/follower_six_axis/ipt/$($item.part).ipt",$false);$o=$ac.Occurrences.Add($d.FullFileName,(Matrix $item.world));$o.Name=$item.part
 for($k=1;$k -le 3;$k++){$ac.Constraints.AddFlushConstraint((Proxy $o $d.ComponentDefinition.WorkPlanes.Item("LINK_FRAME_$k")),(Proxy $b $b.Definition.WorkPlanes.Item($k)),0)|Out-Null}
 $meta.body_records+=@{name=$o.Name;link=$item.link;local=$item.local;classification='UNMODIFIED_UPSTREAM'}
}
$a.Update2($true)|Out-Null;$a.Save();$mp=$ac.MassProperties;$meta.mass_kg=$mp.Mass;$meta.com_mm=@(($mp.CenterOfMass.X*10),($mp.CenterOfMass.Y*10),($mp.CenterOfMass.Z*10));$meta.occurrences=$ac.Occurrences.Count;$meta.constraints=@($ac.Constraints|ForEach-Object{@{name=$_.Name;health=$_.HealthStatus.ToString()}})
$meta|ConvertTo-Json -Depth 15|Set-Content "$mech/two_joint_revb/analysis/assembly.json" -Encoding utf8
'Rev B base restored from official geometry; pan rigidly locked, not motorized.'
