import os
import datetime
import tempfile

class IpmiLogger:

	def __init__(self,	path=None, overwrite=False, echo=False ):
		
		if path!=None and  not overwrite and os.path.exists(path):
			raise Exception("The file '%s' exists." % path)

		f = open(path,'w')
		f.write("IpmiLogger: %s\n" % path )
		f.flush()
		f.close()

		self.path = path
		self.echo = echo

	def log(self, message, echo=None):

		f = open(self.path,'a')
		line = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + " -- " + message
		f.write( line  + "\n" )
		f.flush()
		f.close()

		if self.echo:
			if echo==None or echo==True: print(line)
			else: pass
		else:
			if echo==True: print(line)
			else: pass

if __name__ == "__main__":

	path = tempfile.mkstemp()[1]
	print("Created temp file %s\n" % path)

	logger = IpmiLogger( path=path, overwrite=True, echo=True )
	logger.log("test")

	f = open(path)
	contents = f.read()
	f.close()
	print("\nlog file contents->\n%s" % contents)

	os.unlink(path)
