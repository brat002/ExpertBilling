
import sys

REG_FILE = 'regbill.reg'

def main():
	text = ''
	print 'GEATHERING SYSTEM INFORMATION'
	print '============================='
	import commands
	exit_code, output = commands.getstatusoutput('dmesg')
	if exit_code or not output:
		raise SystemError, "command 'dmesg' failed"
	print output
	text += output
	exit_code, output = commands.getstatusoutput('ls /dev/disk/by-id')
	if exit_code or not output:
		raise SystemError, "command 'ls' failed"
	serials = []
	for s in output.split('\n'):
		s = s.split('_')[1].split('-')[0]
		if s and s not in serials: serials.append(s)
	data = ''
	for s in serials:
		data += s
	import platform
	data += platform.platform()
	import binascii
	data = binascii.hexlify(data)
	text += '\nmemory mapping: ' + data + '\n'
	exit_code, output = commands.getstatusoutput('cat /proc/cpuinfo')
	if not exit_code:
		print output
		text += output
	exit_code, output = commands.getstatusoutput('cat /proc/bus/pci/devices')
	if not exit_code:
		print output
		text += output
	print '============================='
	import os.path, bz2, base64
	f = bz2.BZ2File(os.path.expanduser('~/%s' % REG_FILE), 'wb', 9)
	f.write(binascii.hexlify(base64.b64encode(binascii.hexlify(base64.b64encode(text)))))
	f.close()
	print "Now send a file '%s' in your home directory" % REG_FILE
	print "to ISD-studio to complete your registration."

if __name__ == '__main__':
	try:
		main()
	except Exception, err:
		sys.stderr.write("%s: %s\n" % (sys.argv[0], str(err)))
		sys.exit(1)
