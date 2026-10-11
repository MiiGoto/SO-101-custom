function RigidAt($o,$parent,[double]$x,[double]$z){$ac.Constraints.AddFlushConstraint((Plane $o 1),(Plane $parent 1),(-$x/10))|Out-Null;$ac.Constraints.AddFlushConstraint((Plane $o 2),(Plane $parent 2),0)|Out-Null;$ac.Constraints.AddFlushConstraint((Plane $o 3),(Plane $parent 3),(-$z/10))|Out-Null}
$sc=Occ 'Shoulder_Fixed_Support' 'Shoulder_Support_Carrier';Rigid $sc $base
$ec=Occ 'Elbow_Fixed_Support' 'Elbow_Support_Carrier';Rigid $ec $upper
$sf=Occ 'Shoulder_Output_Flange' 'Shoulder_Output_Flange';Rigid $sf $upper
$ef=Occ 'Elbow_Output_Flange' 'Elbow_Output_Flange' 90;Rigid $ef $forearm
$ss=Occ 'Shoulder_Auxiliary_Shaft' 'Shoulder_Shaft_Envelope';Rigid $ss $upper
$es=Occ 'Elbow_Auxiliary_Shaft' 'Elbow_Shaft_Envelope' 90;Rigid $es $forearm
foreach($side in @('Shoulder','Elbow')){
 $fixed=$base;$moving=$upper;$x=0;$z=0
 if($side -eq 'Elbow'){$fixed=$upper;$moving=$forearm;$x=90;$z=34}
 foreach($name in @('Bearing_625_Envelope','Bearing_Retainer','Encoder_Mount','Encoder_Board_Envelope')){$o=Occ "${side}_$name" $name $x $z;RigidAt $o $fixed $x $z}
 # Moving group origins differ by elbow X90; local magnet follows joint output.
 foreach($name in @('Magnet_Carrier','Magnet_6x2_Envelope')){$o=Occ "${side}_$name" $name $x $z;RigidAt $o $moving 0 $z}
 foreach($offset in @(-12,12)){$o=Occ "${side}_Encoder_Standoff_$offset" 'Encoder_Standoff' ($x+$offset) $z;RigidAt $o $fixed ($x+$offset) $z}
}
