
def getKey():
	from hwinfo import *
	return str( hash( getHarddriveSerialNo() + getMotherboardSerialNo() ) )
