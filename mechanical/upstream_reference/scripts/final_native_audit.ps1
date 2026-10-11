$ErrorActionPreference='Stop'
. "$PSScriptRoot/../../two_joint_prototype/scripts/connect_inventor.ps1"
$mech=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent;$app.SilentOperation=$true;$rows=@()
if(-not ('NativeDof' -as [type])){Add-Type -ReferencedAssemblies 'C:/Program Files/Autodesk/Inventor 2025/Bin/Autodesk.Inventor.Interop.dll' -TypeDefinition 'public static class NativeDof {public static int[] Get(object obj){var o=(Inventor.ComponentOccurrence)obj; int t,r; Inventor.ObjectsEnumerator tv,rv; Inventor.Point p; o.GetDegreesOfFreedom(out t,out tv,out r,out rv,out p);return new int[]{t,r};}}'}
$dof=@()
foreach($folder in @('follower_six_axis','adapters')){foreach($f in Get-ChildItem "$mech/$folder/ipt/*.ipt"){
 $d=$app.Documents.Open($f.FullName,$false);$d.Update2($true)|Out-Null;$mp=$d.ComponentDefinition.MassProperties;$b=$d.ComponentDefinition.RangeBox
 $rows+=@{folder=$folder;file=$f.Name;solid_bodies=@($d.ComponentDefinition.SurfaceBodies|ForEach-Object {$_.IsSolid});mass_kg=$mp.Mass;com_mm=@(($mp.CenterOfMass.X*10),($mp.CenterOfMass.Y*10),($mp.CenterOfMass.Z*10));bbox_mm=@((($b.MaxPoint.X-$b.MinPoint.X)*10),(($b.MaxPoint.Y-$b.MinPoint.Y)*10),(($b.MaxPoint.Z-$b.MinPoint.Z)*10));missing_refs=@($d.ReferencedDocumentDescriptors|Where-Object ReferenceMissing|ForEach-Object FullDocumentName);feature_health=@($d.ComponentDefinition.Features|ForEach-Object {$_.HealthStatus.ToString()})}
}}
$rows|ConvertTo-Json -Depth 8|Set-Content "$mech/release_review/native_parts_validation.json" -Encoding utf8
$assemblies=@()
foreach($folder in @('two_joint_revb','follower_six_axis')){
 $f=Get-ChildItem "$mech/$folder/iam/*.iam"|Select-Object -First 1;$a=$app.Documents.Open($f.FullName,$false);$mp=$a.ComponentDefinition.MassProperties
 foreach($o in $a.ComponentDefinition.Occurrences){if($o.Name -like 'REF_*'){$counts=[NativeDof]::Get($o);$dof+=@{assembly=$folder;occurrence=$o.Name;translation=$counts[0];rotation=$counts[1]}}}
 [double]$xx=0;[double]$yy=0;[double]$zz=0;[double]$xy=0;[double]$yz=0;[double]$xz=0;$mp.XYZMomentsOfInertia([ref]$xx,[ref]$yy,[ref]$zz,[ref]$xy,[ref]$yz,[ref]$xz)
 $assemblies+=@{assembly=$folder;mass_kg=$mp.Mass;com_mm=@(($mp.CenterOfMass.X*10),($mp.CenterOfMass.Y*10),($mp.CenterOfMass.Z*10));inertia_kg_m2=@(($xx*.0001),($yy*.0001),($zz*.0001),($xy*.0001),($yz*.0001),($xz*.0001));all_reference_files_exist=@($a.AllReferencedDocuments|ForEach-Object{@{file=$_.FullFileName;exists=(Test-Path $_.FullFileName)}})}
 $ad=$app.ApplicationAddIns.ItemById('{90AF7F40-0C01-11D5-8E83-0010B541CD80}');$ctx=$app.TransientObjects.CreateTranslationContext();$ctx.Type=[Inventor.IOMechanismEnum]::kFileBrowseIOMechanism;$opts=$app.TransientObjects.CreateNameValueMap();$ad.HasSaveCopyAsOptions($a,$ctx,$opts)|Out-Null;$opts.Value('ApplicationProtocolType')=3;$data=$app.TransientObjects.CreateDataMedium();$data.FileName="$mech/$folder/step/$($f.BaseName).step";$ad.SaveCopyAs($a,$ctx,$opts,$data)
}
$assemblies|ConvertTo-Json -Depth 8|Set-Content "$mech/release_review/assembly_mass_reference_validation.json" -Encoding utf8
$dof|ConvertTo-Json -Depth 6|Set-Content "$mech/release_review/dof_api.json" -Encoding utf8
$draws=@()
foreach($folder in @('adapters','two_joint_revb','follower_six_axis','templates')){foreach($f in Get-ChildItem "$mech/$folder" -Recurse -Filter '*.idw'|Where-Object FullName -notmatch OldVersions){
 $d=$app.Documents.Open($f.FullName,$false);$d.Update2($true)|Out-Null;$s=$d.ActiveSheet
 $draws+=@{folder=$folder;file=$f.Name;views=$s.DrawingViews.Count;associated_dimensions=$s.DrawingDimensions.GeneralDimensions.Count;standard=$d.StylesManager.ActiveStandardStyle.Name;dimension_styles=@($s.DrawingDimensions.GeneralDimensions|ForEach-Object {$_.Style.Name}|Sort-Object -Unique);first_angle=$d.StylesManager.ActiveStandardStyle.FirstAngleProjection;units=$d.UnitsOfMeasure.LengthUnits.ToString();width_mm=$s.Width*10;height_mm=$s.Height*10;title_block=[bool]$s.TitleBlock;border=[bool]$s.Border;missing_refs=@($d.ReferencedDocumentDescriptors|Where-Object ReferenceMissing|ForEach-Object FullDocumentName)};$d.Close($true)
}}
$draws|ConvertTo-Json -Depth 8|Set-Content "$mech/release_review/drawing_validation.json" -Encoding utf8
$app.SilentOperation=$false
'Native part, assembly mass, STEP and JIS IDW validation saved.'
