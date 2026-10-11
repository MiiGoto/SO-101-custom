$ErrorActionPreference='Stop'
. "$PSScriptRoot/../../two_joint_prototype/scripts/connect_inventor.ps1"
$root=Split-Path $PSScriptRoot -Parent;$mech=Split-Path $root -Parent
$ref=Get-Content "$root/kinematic_reference.json" -Raw|ConvertFrom-Json
$app.SilentOperation=$true
foreach($folder in @('two_joint_revb','follower_six_axis','adapters')){foreach($sub in @('ipt','iam','stl','step','analysis','views','idw','pdf')){New-Item -ItemType Directory -Force "$mech/$folder/$sub"|Out-Null}}
$pt=$app.FileManager.GetTemplateFile([Inventor.DocumentTypeEnum]::kPartDocumentObject,[Inventor.SystemOfMeasureEnum]::kMetricSystemOfMeasure)
$at=$app.FileManager.GetTemplateFile([Inventor.DocumentTypeEnum]::kAssemblyDocumentObject,[Inventor.SystemOfMeasureEnum]::kMetricSystemOfMeasure)
function Matrix($rows){$m=$tg.CreateMatrix();for($i=1;$i -le 4;$i++){for($j=1;$j -le 4;$j++){$v=[double]$rows[$i-1][$j-1];if($j -eq 4 -and $i -lt 4){$v/=10};$m.Cell($i,$j)=$v}};return $m}
function Origin($rows){return $tg.CreatePoint(([double]$rows[0][3]/10),([double]$rows[1][3]/10),([double]$rows[2][3]/10))}
function Unit($rows,[int]$col){return $tg.CreateUnitVector([double]$rows[0][$col],[double]$rows[1][$col],[double]$rows[2][$col])}
function FramePlanes($cd,$rows,$tag){$p=Origin $rows;$x=Unit $rows 0;$y=Unit $rows 1;$z=Unit $rows 2;$list=@();foreach($axes in @(@($y,$z),@($z,$x),@($x,$y))){$w=$cd.WorkPlanes.AddFixed($p,$axes[0],$axes[1],$false);$w.Visible=$false;$w.Name="$tag$($list.Count+1)";$list+=$w};return ,$list}
function Proxy($o,$obj){[object]$p=New-Object System.Object;$o.CreateGeometryProxy($obj,[ref]$p);return $p}
function Export($doc,$path,$fmt){$id=if($fmt -eq 'stl'){'{533E9A98-FC3B-11D4-8E7E-0010B541CD80}'}else{'{90AF7F40-0C01-11D5-8E83-0010B541CD80}'};$ad=$app.ApplicationAddIns.ItemById($id);$ctx=$app.TransientObjects.CreateTranslationContext();$ctx.Type=[Inventor.IOMechanismEnum]::kFileBrowseIOMechanism;$opts=$app.TransientObjects.CreateNameValueMap();$ad.HasSaveCopyAsOptions($doc,$ctx,$opts)|Out-Null;if($fmt -eq 'stl'){$opts.Value('ExportUnits')=5;$opts.Value('Resolution')=1}else{$opts.Value('ApplicationProtocolType')=3};$data=$app.TransientObjects.CreateDataMedium();$data.FileName=$path;$ad.SaveCopyAs($doc,$ctx,$opts,$data)}
function Box($cd,[double]$x,[double]$y,[double]$z,[double]$w,[double]$h,[double]$depth,[bool]$cut=$false){$pl=$cd.WorkPlanes.AddByPlaneAndOffset($cd.WorkPlanes.Item(3),$z/10,$false);$pl.Visible=$false;$s=$cd.Sketches.Add($pl,$false);$s.SketchLines.AddAsTwoPointRectangle($tg.CreatePoint2d(($x-$w/2)/10,($y-$h/2)/10),$tg.CreatePoint2d(($x+$w/2)/10,($y+$h/2)/10))|Out-Null;$op=[Inventor.PartFeatureOperationEnum]::kJoinOperation;if($cut){$op=[Inventor.PartFeatureOperationEnum]::kCutOperation};$e=$cd.Features.ExtrudeFeatures.CreateExtrudeDefinition($s.Profiles.AddForSolid(),$op);$e.SetDistanceExtent($depth/10,[Inventor.PartFeatureExtentDirectionEnum]::kPositiveExtentDirection);$cd.Features.ExtrudeFeatures.Add($e)|Out-Null;$s.Visible=$false}
function MassRow($d,$name){$mp=$d.ComponentDefinition.MassProperties;[double]$xx=0;[double]$yy=0;[double]$zz=0;[double]$xy=0;[double]$yz=0;[double]$xz=0;$mp.XYZMomentsOfInertia([ref]$xx,[ref]$yy,[ref]$zz,[ref]$xy,[ref]$yz,[ref]$xz);return @{name=$name;mass_kg=$mp.Mass;volume_mm3=$mp.Volume*1000;com_mm=@(($mp.CenterOfMass.X*10),($mp.CenterOfMass.Y*10),($mp.CenterOfMass.Z*10));inertia_kg_m2=@(($xx*.0001),($yy*.0001),($zz*.0001),($xy*.0001),($yz*.0001),($xz*.0001));material=$d.ActiveMaterial.DisplayName}}
$parts=@{};$mass=@();$planes=@{}
# STEP geometry is unchanged; only named link-frame datum planes are added.
foreach($item in $ref.parts){
 $name=$item.part
 if(Test-Path "$mech/follower_six_axis/ipt/$name.ipt"){$d=$app.Documents.Open("$mech/follower_six_axis/ipt/$name.ipt",$false);$planes[$name]=@($d.ComponentDefinition.WorkPlanes.Item('LINK_FRAME_1'),$d.ComponentDefinition.WorkPlanes.Item('LINK_FRAME_2'),$d.ComponentDefinition.WorkPlanes.Item('LINK_FRAME_3'));$parts[$name]=$d;$mass+=MassRow $d $name;continue}
 $d=$app.Documents.Open("$root/step/$name.step",$false)
 if($d.DocumentType -eq [Inventor.DocumentTypeEnum]::kAssemblyDocumentObject){
  $d.SaveAs("$root/native/${name}_source.iam",$false)
  $src=$d;$d=$app.Documents.Add([Inventor.DocumentTypeEnum]::kPartDocumentObject,$pt,$false)
  $derived=$d.ComponentDefinition.ReferenceComponents.DerivedAssemblyComponents.CreateDefinition($src.FullFileName)
  $derived.DeriveStyle=[Inventor.DerivedComponentStyleEnum]::kDeriveAsMultipleBodies
  $derived.InclusionOption=[Inventor.DerivedComponentOptionEnum]::kDerivedIncludeAll
  $d.ComponentDefinition.ReferenceComponents.DerivedAssemblyComponents.Add($derived)|Out-Null
 }
 $lib=$app.AssetLibraries|Where-Object DisplayName -eq 'Inventor Material Library'|Select-Object -First 1;$mat=$lib.MaterialAssets.Item('MaterialInv_048').CopyTo($d);$d.ActiveMaterial=$mat
 $m=Matrix $item.local;$m.Invert();$rows=@();for($i=1;$i -le 4;$i++){$r=@();for($j=1;$j -le 4;$j++){$v=$m.Cell($i,$j);if($j -eq 4 -and $i -lt 4){$v*=10};$r+=$v};$rows+=,$r}
 $planes[$name]=FramePlanes $d.ComponentDefinition $rows 'LINK_FRAME_'
 $d.SaveAs("$mech/follower_six_axis/ipt/$name.ipt",$false);$parts[$name]=$d;$mass+=MassRow $d $name
 Write-Output "Imported native solid: $name"
}
# Hidden kinematic datum carriers are reference items, not manufactured links.
$carriers=@{};$jointPlanes=@{};$jointAxes=@{}
foreach($prop in $ref.frames.PSObject.Properties){
 $link=$prop.Name;$d=$app.Documents.Add([Inventor.DocumentTypeEnum]::kPartDocumentObject,$pt,$false);Box $d.ComponentDefinition 0 0 0 1 1 .1;$d.ComponentDefinition.MassProperties.Mass=1e-9
 foreach($joint in @($ref.joints|Where-Object parent -eq $link)){$jointPlanes[$joint.name]=FramePlanes $d.ComponentDefinition $joint.origin ('JOINT_'+$joint.name+'_');$ax=$d.ComponentDefinition.WorkAxes.AddFixed((Origin $joint.origin),(Unit $joint.origin 2),$false);$ax.Visible=$false;$jointAxes[$joint.name]=$ax}
 $d.SaveAs("$mech/follower_six_axis/ipt/REF_$link.ipt",$false);$carriers[$link]=$d
}
# Authored motor envelopes, no spline or OEM hole pattern. Cradles have own adjustable clamp slots.
foreach($type in @('Vstone','XL330')){
 $d=$app.Documents.Add([Inventor.DocumentTypeEnum]::kPartDocumentObject,$pt,$false);$cd=$d.ComponentDefinition
 if($type -eq 'Vstone'){Box $cd 0 -19 -26 38 38.5 19;$cd.MassProperties.Mass=.042}else{Box $cd 0 -7.5 -26 20 34 26;$cd.MassProperties.Mass=.018}
 $d.SaveAs("$mech/adapters/ipt/${type}_Envelope.ipt",$false);$parts["${type}_Envelope"]=$d;$mass+=MassRow $d "${type}_Envelope"
 $d=$app.Documents.Add([Inventor.DocumentTypeEnum]::kPartDocumentObject,$pt,$false);$cd=$d.ComponentDefinition
 $w=if($type -eq 'Vstone'){38.6}else{20.6};$h=if($type -eq 'Vstone'){39.1}else{34.6};$cy=if($type -eq 'Vstone'){-19}else{-7.5}
 Box $cd 0 $cy -30 ($w+14) ($h+8) 4;Box $cd (-$w/2-2) $cy -26 4 ($h+8) 22;Box $cd ($w/2+2) $cy -26 4 ($h+8) 22
 foreach($x in @((-$w/2-5),($w/2+5))){Box $cd $x $cy -31 3.4 20 6 $true}
 $d.SaveAs("$mech/adapters/ipt/${type}_Cradle_HOLD.ipt",$false);$parts["${type}_Cradle_HOLD"]=$d;$mass+=MassRow $d "${type}_Cradle_HOLD";Export $d "$mech/adapters/stl/${type}_Cradle_HOLD.stl" 'stl';Export $d "$mech/adapters/step/${type}_Cradle_HOLD.step" 'step'
}
# Validated Rev A coupons are retained, copied to new artifact paths without altering originals.
foreach($name in @('Servo_Mount_Coupon','Horn_Adapter_Test','Encoder_Alignment_Test','Bearing_Fit_Coupon')){Copy-Item "$mech/two_joint_prototype/ipt/$name.ipt" "$mech/adapters/ipt/$name.ipt";Copy-Item "$mech/two_joint_prototype/stl/$name.stl" "$mech/adapters/stl/$name.stl"}
$mass|ConvertTo-Json -Depth 8|Set-Content "$mech/follower_six_axis/analysis/part_mass_properties.json" -Encoding utf8
function BuildAssembly($folder,$filename,[bool]$two){
 $a=$app.Documents.Add([Inventor.DocumentTypeEnum]::kAssemblyDocumentObject,$at,$false);$ac=$a.ComponentDefinition;$occ=@{};$rows=@();$jointrecords=@()
 $allowed=if($two){@('base_link','shoulder_link','upper_arm_link','lower_arm_link')}else{@($ref.frames.PSObject.Properties.Name)}
 foreach($link in $allowed){$frame=$ref.frames.$link;$o=$ac.Occurrences.Add($carriers[$link].FullFileName,(Matrix $frame));$o.Name="REF_$link";$o.Visible=$false;$o.BOMStructure=[Inventor.BOMStructureEnum]::kReferenceBOMStructure;$occ[$link]=$o}
 $baseLink='base_link';$occ[$baseLink].Grounded=$true
 foreach($joint in $ref.joints){if($joint.parent -notin $allowed -or $joint.child -notin $allowed){continue};$parent=$occ[$joint.parent];$child=$occ[$joint.child]
  if($two -and $joint.name -eq 'shoulder_pan'){for($k=0;$k -lt 3;$k++){$ac.Constraints.AddFlushConstraint((Proxy $child $child.Definition.WorkPlanes.Item($k+1)),(Proxy $parent $jointPlanes[$joint.name][$k]),0)|Out-Null};continue}
  $c=$ac.Constraints.AddMateConstraint((Proxy $child $child.Definition.WorkAxes.Item(3)),(Proxy $parent $jointAxes[$joint.name]),0);$c.Name="$($joint.name)_AXIS"
  $c=$ac.Constraints.AddFlushConstraint((Proxy $child $child.Definition.WorkPlanes.Item(3)),(Proxy $parent $jointPlanes[$joint.name][2]),0);$c.Name="$($joint.name)_AXIAL"
  $jointrecords+=@{name=$joint.name;parent=$parent.Name;child=$child.Name;range=$joint.limits_rad;motor=$joint.motor}
 }
 foreach($item in $ref.parts){if($item.link -notin $allowed){continue};$o=$ac.Occurrences.Add($parts[$item.part].FullFileName,(Matrix $item.world));$o.Name=$item.part;$b=$occ[$item.link]
  for($k=0;$k -lt 3;$k++){$ac.Constraints.AddFlushConstraint((Proxy $o $planes[$item.part][$k]),(Proxy $b $b.Definition.WorkPlanes.Item($k+1)),0)|Out-Null}
  $rows+=@{name=$o.Name;link=$item.link;local=$item.local;classification='UNMODIFIED_UPSTREAM'}
 }
 foreach($joint in $ref.joints){if($joint.parent -notin $allowed -or ($two -and $joint.name -notin @('shoulder_lift','elbow_flex'))){continue};$type=if($joint.motor -eq 'VS-S092J'){'Vstone'}else{'XL330'};$b=$occ[$joint.parent]
  foreach($suffix in @('Envelope','Cradle_HOLD')){$key="${type}_$suffix";$d=$parts[$key];$o=$ac.Occurrences.Add($d.FullFileName,(Matrix $joint.world));$o.Name="$($joint.name)_$key"
   for($k=0;$k -lt 3;$k++){$ac.Constraints.AddFlushConstraint((Proxy $o $d.ComponentDefinition.WorkPlanes.Item($k+1)),(Proxy $b $jointPlanes[$joint.name][$k]),0)|Out-Null}
   $rows+=@{name=$o.Name;link=$joint.parent;local=$joint.origin;classification=if($suffix -eq 'Envelope'){'ASSUMPTION_ENVELOPE'}else{'ORIGINAL_CUSTOM_PART'};source_part=$key}
  }
 }
 $ok=$a.Update2($true);$path="$mech/$folder/iam/$filename.iam";$a.SaveAs($path,$false)
 $mp=$ac.MassProperties
 @{inventor_version=$app.SoftwareVersion.DisplayVersion;update_ok=$ok;occurrences=$ac.Occurrences.Count;constraints=@($ac.Constraints|ForEach-Object{@{name=$_.Name;health=$_.HealthStatus.ToString()}});joint_records=$jointrecords;body_records=$rows;mass_kg=$mp.Mass;com_mm=@(($mp.CenterOfMass.X*10),($mp.CenterOfMass.Y*10),($mp.CenterOfMass.Z*10));manufacturing='HOLD: motor/horn fit, adapters fastening, sweep interference and continuous torque'}|ConvertTo-Json -Depth 15|Set-Content "$mech/$folder/analysis/assembly.json" -Encoding utf8
 Export $a "$mech/$folder/step/$filename.step" 'step'
 Write-Output "Saved $filename with $($ac.Constraints.Count) constraints"
}
BuildAssembly 'two_joint_revb' 'SO101_TwoJoint_RevB' $true
BuildAssembly 'follower_six_axis' 'SO101_Custom_Follower_RevA' $false
$app.SilentOperation=$false
