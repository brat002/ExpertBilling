
def getKey():
	serials = ''
	import wmi
	w = wmi.WMI()
	for obj in w.Win32_BaseBoard(): # or 'Win32_MotherboardDevice' ?
		serials += obj.SerialNumber
		break
	for obj in w.Win32_DiskDrive():
		serials += obj.SerialNumber
		break
	return str( hash( serials ) )
