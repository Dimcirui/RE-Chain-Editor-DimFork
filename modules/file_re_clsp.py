#Author: NSA Cloud

import struct
from .gen_functions import textColors,raiseWarning,raiseError,getPaddingAmount,read_uint,read_int,read_uint64,read_int64,read_float,read_ushort,read_ubyte,read_unicode_string,read_byte,read_short,write_uint,write_int,write_uint64,write_int64,write_float,write_ushort,write_ubyte,write_unicode_string,write_byte,write_short

class CLSPHeader():
	def __init__(self):
		self.magic = 1347636291
		self.entryCount = 0
		self.dataOffset = 16
		
	def read(self,file):
		global version
		print("Reading Header...")
		
		self.magic = read_uint(file)
		if self.magic != 1347636291:
			raiseError("File is not a CLSP file.")
		self.entryCount = read_uint(file)#ENUM
		self.dataOffset = read_uint64(file)
		
	def write(self,file):
		write_uint(file, self.magic)
		write_uint(file, self.entryCount)#ENUM
		write_uint64(file, self.dataOffset)

	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)


class CLSPEntry():
	def __init__(self):
		self.chainCollisionShape = 0
		self.jointNameHash = 0
		self.pairJointNameHash = 0
		self.unkn3 = 0
		self.unknBitFlag0 = 0
		self.unknBitFlag1 = 0
		self.unkn9 = 0
		self.unkn10 = 0
		self.x1 = 0.0
		self.y1 = 0.0
		self.z1 = 0.0
		self.collisionCapsuleStartRadius = 0.0
		self.x2 = 0.0
		self.y2 = 0.0
		self.z2 = 0.0
		self.collisionCapsuleEndRadius = 0.0
		self.collisionSphereRadius = 0.0
		self.extraData = b'\x00'*44#+0x44 to the end of the entry, used by boxes

	def read(self,file):
		self.chainCollisionShape = read_uint(file)
		self.jointNameHash = read_uint(file)
		self.pairJointNameHash = read_uint(file)
		self.unkn3 = read_uint(file)
		self.unknBitFlag0 = read_int(file)
		self.unknBitFlag1 = read_int(file)
		self.unkn9 = read_uint(file)
		self.unkn10 = read_uint(file)
		self.x1 = read_float(file)
		self.y1 = read_float(file)
		self.z1 = read_float(file)
		self.collisionCapsuleStartRadius = read_float(file)
		self.x2 = read_float(file)
		self.y2 = read_float(file)
		self.z2 = read_float(file)
		self.collisionCapsuleEndRadius = read_float(file)
		self.collisionSphereRadius = read_float(file)
		self.extraData = file.read(44)

	#A box (shape 2): +0x20 to +0x5f is a 4x4 matrix in its joint's space, translation in the last row
	#(rows 0-2 are the box's axes, row 3 its centre), +0x60 the half extents along those axes, +0x6c padding
	def getBox(self):
		"""(4 rows of the box's matrix, half extents)"""
		values = [self.x1,self.y1,self.z1,self.collisionCapsuleStartRadius,self.x2,self.y2,self.z2,self.collisionCapsuleEndRadius,self.collisionSphereRadius]
		values += struct.unpack("<11f",self.extraData)
		return [values[row*4:row*4+4] for row in range(4)],values[16:19]
	def setBox(self,rows,halfExtents):
		values = [value for row in rows for value in row] + list(halfExtents)
		(self.x1,self.y1,self.z1,self.collisionCapsuleStartRadius,self.x2,self.y2,self.z2,self.collisionCapsuleEndRadius,self.collisionSphereRadius) = values[:9]
		self.extraData = struct.pack("<10f",*values[9:]) + self.extraData[40:]

	def write(self,file):
		write_uint(file, self.chainCollisionShape)
		write_uint(file, self.jointNameHash)
		write_uint(file, self.pairJointNameHash)
		write_uint(file, self.unkn3)
		write_int(file, self.unknBitFlag0)
		write_int(file, self.unknBitFlag1)
		write_uint(file, self.unkn9)
		write_uint(file, self.unkn10)
		write_float(file, self.x1)
		write_float(file, self.y1)
		write_float(file, self.z1)
		write_float(file, self.collisionCapsuleStartRadius)
		write_float(file, self.x2)
		write_float(file, self.y2)
		write_float(file, self.z2)
		write_float(file, self.collisionCapsuleEndRadius)
		write_float(file, self.collisionSphereRadius)
		file.write(self.extraData)

	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)


class CLSPFile():
	def __init__(self):
		self.header = CLSPHeader()
		self.clspEntryList = []
	def read(self,file):
		self.header.read(file)
		file.seek(self.header.dataOffset)
		for i in range(0,self.header.entryCount):
			entry = CLSPEntry()
			entry.read(file)
			self.clspEntryList.append(entry)
				
	def write(self,file):
		self.header.write(file)
		file.seek(self.header.dataOffset)
		for entry in self.clspEntryList:
			entry.write(file)
		
				
#---CLSP IO FUNCTIONS---#

def readRECLSP(filepath):
	print(textColors.OKCYAN + "__________________________________\nCLSP read started." + textColors.ENDC)
	print("Opening " + filepath)
	try:  
		file = open(filepath,"rb")
	except:
		raiseError("Failed to open " + filepath)
	
	clspFile = CLSPFile()
	clspFile.read(file)
	file.close()
	print(textColors.OKGREEN + "__________________________________\nCLSP read finished." + textColors.ENDC)
	return clspFile
def writeRECLSP(clspFile,filepath):
	print(textColors.OKCYAN + "__________________________________\nCLSP write started." + textColors.ENDC)
	print("Opening " + filepath)
	try:
		file = open(filepath,"wb")
	except:
		raiseError("Failed to open " + filepath)
	
	clspFile.write(file)
	file.close()
	print(textColors.OKGREEN + "__________________________________\nCLSP write finished." + textColors.ENDC)