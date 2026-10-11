$lib=$app.AssetLibraries | Where-Object DisplayName -eq 'Inventor Material Library' | Select-Object -First 1
# Included by build_inventor.ps1; all dimensions in mm.
NewPart 'Shoulder_Support_Carrier';Disc 0 0 10 15 8;Box 0 10 10 80 12 8;Box -38 -28 10 8 66 8;Box 38 -28 10 8 66 8
Disc 0 0 9 2.7 10 $true;Disc 0 0 13 8.1 6 $true;Holes 0 9 10;SavePart
NewPart 'Elbow_Support_Carrier';Disc 90 0 44 15 8;Box 90 10 44 62 12 8;Box 63 -7 44 8 38 8;Box 117 -7 44 8 38 8;Box 63 -25 30 8 12 22;Box 117 -25 30 8 12 22
Disc 90 0 43 2.7 10 $true;Disc 90 0 47 8.1 6 $true;Holes 90 43 10;SavePart
NewPart 'Shoulder_Output_Flange';Disc 0 0 5 15 3;Disc 0 0 4 2.6 5 $true;Holes 0 4 5;SavePart
NewPart 'Elbow_Output_Flange';Disc 0 0 38 15 3;Disc 0 0 37 2.6 5 $true;Holes 0 37 5;SavePart
NewPart 'Shoulder_Shaft_Envelope';Disc 0 0 8 2.5 12
$steel=$lib.MaterialAssets.Item('MaterialInv_003').CopyTo($doc);$doc.ActiveMaterial=$steel;SavePart
NewPart 'Elbow_Shaft_Envelope';Disc 0 0 41 2.5 13
$steel=$lib.MaterialAssets.Item('MaterialInv_003').CopyTo($doc);$doc.ActiveMaterial=$steel;SavePart
NewPart 'Bearing_625_Envelope';Disc 0 0 13 8 5;Disc 0 0 12 2.5 7 $true;SavePart .005
NewPart 'Encoder_Board_Envelope';Box 0 0 26 25 25 1.6;Box 0 0 24.5 3 3 1.5;SavePart .002
NewPart 'Magnet_6x2_Envelope';Disc 0 0 20.8 3 2;SavePart .0004
NewPart 'Bearing_Retainer';Disc 0 0 18 15 1;Disc 0 0 17 6.5 3 $true;Holes 0 17 3;SavePart
NewPart 'Encoder_Standoff';Disc 0 0 19 4 4;Disc 0 0 18 1.6 6 $true;SavePart
