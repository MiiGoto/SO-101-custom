$ErrorActionPreference='Stop'
# Installed interop identity resolves to 2025 in this host. Use it for shared
# enum definitions only; the running COM server version is independently checked.
if(-not ('Inventor.DocumentTypeEnum' -as [type])){Add-Type -Path 'C:/Program Files/Autodesk/Inventor 2025/Bin/Autodesk.Inventor.Interop.dll'}
if(-not ('InvActive26' -as [type])){
Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class InvActive26 {
 [DllImport("oleaut32.dll", PreserveSig=false)] private static extern void GetActiveObject(ref Guid clsid, IntPtr reserved, [MarshalAs(UnmanagedType.IUnknown)] out object result);
 public static object Get() { var id=Type.GetTypeFromProgID("Inventor.Application",true).GUID; object o; GetActiveObject(ref id,IntPtr.Zero,out o); return o; }
}
'@
}
$app=[InvActive26]::Get()
if($app.SoftwareVersion.DisplayVersion -notlike '2026*'){throw 'Refusing non-2026 Inventor'}
$app.Visible=$true
$tg=$app.TransientGeometry
