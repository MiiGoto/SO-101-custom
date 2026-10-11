$ErrorActionPreference='Stop'
. "$PSScriptRoot/../../two_joint_prototype/scripts/connect_inventor.ps1"
$root=Split-Path $PSScriptRoot -Parent
$app.SilentOperation=$true
$before=@($app.Documents|ForEach-Object{@{file=$_.FullFileName;dirty=$_.Dirty}})
$before|ConvertTo-Json|Set-Content "$root/documents_before.json" -Encoding utf8
$doc=$app.Documents.Open("$root/step/SO101 Assembly.step",$false)
$doc.SaveAs("$root/native/Official_SO101_Imported.iam",$false)
$rows=@()
foreach($o in $doc.ComponentDefinition.Occurrences){
 $b=$o.RangeBox;$m=$o.Transformation;$mp=$o.Definition.MassProperties
 $r=@{name=$o.Name;file=$o.Definition.Document.FullFileName;type=$o.DefinitionDocumentType.ToString();mass=$mp.Mass;com=@(($mp.CenterOfMass.X*10),($mp.CenterOfMass.Y*10),($mp.CenterOfMass.Z*10));min=@(($b.MinPoint.X*10),($b.MinPoint.Y*10),($b.MinPoint.Z*10));max=@(($b.MaxPoint.X*10),($b.MaxPoint.Y*10),($b.MaxPoint.Z*10));matrix=@()}
 for($i=1;$i -le 4;$i++){for($j=1;$j -le 4;$j++){$r.matrix+= $m.Cell($i,$j)}}
 $rows+=$r
}
$rows|ConvertTo-Json -Depth 8|Set-Content "$root/assembly_inventory.json" -Encoding utf8
$rows|Select-Object name,type,mass|Format-Table -AutoSize
$template='C:/Users/Public/Documents/Autodesk/Inventor 2026/Templates/ja-JP/Metric/JIS.idw'
$dr=$app.Documents.Add([Inventor.DocumentTypeEnum]::kDrawingDocumentObject,$template,$false)
$dr.StylesManager.ActiveStandardStyle|Select-Object Name,FirstAngleProjection
$dr.StylesManager.DimensionStyles|Select-Object Name
$dr.ActiveSheet|Select-Object Width,Height,Size
$dr.Close($true)
