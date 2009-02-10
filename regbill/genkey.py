
import sys

def main():
	if len(sys.argv) != 3:
		raise RuntimeError, 'invalid number of paramters to script'
	import bz2, binascii, base64, md5
	for s in base64.b64decode(binascii.unhexlify(base64.b64decode(binascii.unhexlify(bz2.BZ2File(sys.argv[1], 'rb').read())))).split('\n'):
		if s.startswith('memory mapping: '):
			print md5.new (binascii.unhexlify (s.split ('memory mapping: ')[1]) + open (sys.argv[2]).read ()).hexdigest ().upper ()
			break

if __name__ == '__main__':
	try:
		main()
	except Exception, err:
		sys.stderr.write("%s: %s\n" % (sys.argv[0], str(err)))
		sys.exit(1)
