#RE9 bone axes from RE-Mesh-Editor: on an armature whose data has REMeshBoneAxes = "RE9", a bone's Blender frame is its
#file frame @ C^-1, with C (row-major 3x3) in the bone's reAxisCorrection. A chain, chain2 or CLSP file stores its offsets
#and rotations in the file's bone frames, the scene in the Blender ones: o_blender = C @ o_file, q_blender = C @ q_file.
#Import converts the read file to Blender frames, export the built file back, so the scene keeps working in Blender frames.
from mathutils import Matrix,Vector,Quaternion
from .pymmh3 import hash_wide

AXIS_CORRECTION_PROP = "reAxisCorrection"
ARMATURE_AXIS_FLAG = "REMeshBoneAxes"
ARMATURE_AXIS_FLAG_RE9 = "RE9"

def fileBoneName(boneName):
	"""A bone's name as the file hashes it (a b<digits>: prefix dropped, as getArmatureHashList does)."""
	return boneName.split(":",1)[1] if boneName.startswith("b") and ":" in boneName else boneName

def boneCorrection(bone):
	value = bone.get(AXIS_CORRECTION_PROP)
	if value is None:
		return None
	values = list(value)
	if len(values) != 9:
		return None
	return Matrix((values[0:3],values[3:6],values[6:9])).normalized()

class BoneAxes():
	"""The C of each bone, by joint hash, on the RE9 armatures among the given ones (first armature wins)."""
	def __init__(self,armatures):
		self.corrections = {}
		self.parents = {}
		for armature in armatures:
			if armature is None or armature.type != "ARMATURE" or armature.data.get(ARMATURE_AXIS_FLAG) != ARMATURE_AXIS_FLAG_RE9:
				continue
			for bone in armature.data.bones:
				jointHash = hash_wide(fileBoneName(bone.name))
				if jointHash in self.parents:
					continue
				self.parents[jointHash] = hash_wide(fileBoneName(bone.parent.name)) if bone.parent is not None else None
				correction = boneCorrection(bone)
				if correction is not None:
					self.corrections[jointHash] = correction
	def __bool__(self):
		return bool(self.corrections)
	def correction(self,jointHash,toFile):
		"""(rotation matrix, quaternion) taking the bone's offsets to the other frame, or None."""
		correction = self.corrections.get(jointHash)
		if correction is None:
			return None
		#The conjugate, not the transposed matrix's quaternion, so a rotation comes back with its sign
		quaternion = correction.to_quaternion()
		return (correction.transposed(),quaternion.conjugated()) if toFile else (correction,quaternion)
	def parentHash(self,jointHash):
		return self.parents.get(jointHash)
	def boneChain(self,terminateHash,count):
		"""Joint hashes of a chain group's bones, root first: the terminate bone and its parents, count at most."""
		chain = []
		jointHash = terminateHash
		while jointHash is not None and jointHash in self.parents and len(chain) < count:
			chain.append(jointHash)
			jointHash = self.parents[jointHash]
		chain.reverse()
		return chain

def armaturesOfObjects(objects):
	"""The armatures the objects' constraints target, in the order first met."""
	armatures = []
	for obj in objects:
		for constraint in getattr(obj,"constraints",()):
			target = getattr(constraint,"target",None)
			if target is not None and target.type == "ARMATURE" and target not in armatures:
				armatures.append(target)
	return armatures

def _vector(correction,obj,names):
	if correction is None:
		return
	values = correction[0] @ Vector([getattr(obj,name) for name in names])
	for name,value in zip(names,values):
		setattr(obj,name,value)

def _quaternion(correction,obj,names):
	#names in w,x,y,z order
	if correction is None:
		return
	values = correction[1] @ Quaternion([getattr(obj,name) for name in names])
	for name,value in zip(names,values):
		setattr(obj,name,value)

POS = ("posX","posY","posZ")
PAIR_POS = ("pairPosX","pairPosY","pairPosZ")
ROT_OFFSET = ("rotOffsetW","rotOffsetX","rotOffsetY","rotOffsetZ")
ANGLE_LIMIT_DIRECTION = ("angleLimitDirectionW","angleLimitDirectionX","angleLimitDirectionY","angleLimitDirectionZ")
RANGE_OFFSET = ("rangeOffsetX","rangeOffsetY","rangeOffsetZ")
RANGE_AXIS = ("rangeAxisW","rangeAxisX","rangeAxisY","rangeAxisZ")
CHAIN_CAPSULE_SHAPES = (0,2,5)#none (drawn as a capsule), capsule, tapered capsule: pairPos on the pair joint
CHAIN_OBB_SHAPE = 3#pairPos is the half extents
CHAIN_PLANE_SHAPE = 4#pairPos is kept as the file's

def convertChainFileAxes(chainFile,axes,toFile):
	"""Chain or chain2 file data between file bone frames and Blender's (toFile: Blender -> file), in place."""
	if not axes:
		return
	for collision in chainFile.ChainCollisionList:
		correction = axes.correction(collision.jointNameHash,toFile)
		_vector(correction,collision,POS)
		_quaternion(correction,collision,ROT_OFFSET)
		shape = collision.chainCollisionShape
		if shape in (CHAIN_OBB_SHAPE,CHAIN_PLANE_SHAPE):
			continue
		pairHash = collision.pairJointNameHash
		if shape in CHAIN_CAPSULE_SHAPES or pairHash in axes.parents:
			correction = axes.correction(pairHash,toFile)
		_vector(correction,collision,PAIR_POS)
	for group in chainFile.ChainGroupList:
		bones = axes.boneChain(group.terminateNodeNameHash,len(group.nodeList))
		nodeLists = [group.nodeList] + [subGroup.nodeList for subGroup in getattr(group,"subGroupList",[])]
		for nodeList in nodeLists:
			for node,jointHash in zip(nodeList,bones):
				#The angle limit frame (and a jiggle on the node) is in the parent bone's frame
				correction = axes.correction(axes.parentHash(jointHash),toFile)
				_quaternion(correction,node,ANGLE_LIMIT_DIRECTION)
				jiggle = getattr(node,"jiggleData",None)
				if jiggle:
					_vector(correction,jiggle,RANGE_OFFSET)
					_quaternion(correction,jiggle,RANGE_AXIS)

CLSP_SPHERE_SHAPE = 0
CLSP_BOX_SHAPE = 2
CLSP_PLANE_SHAPE = 4
CLSP_POS = ("x1","y1","z1")
CLSP_END_POS = ("x2","y2","z2")

def convertCLSPFileAxes(clspFile,axes,toFile):
	"""CLSP file data between file bone frames and Blender's (toFile: Blender -> file), in place."""
	if not axes:
		return
	for entry in clspFile.clspEntryList:
		correction = axes.correction(entry.jointNameHash,toFile)
		shape = entry.chainCollisionShape
		if shape == CLSP_BOX_SHAPE:
			if correction is not None:
				rows,halfExtents = entry.getBox()
				matrix = correction[0].to_4x4() @ Matrix(rows).transposed()#The file's rows are Blender's columns
				entry.setBox([list(row) for row in matrix.transposed()],halfExtents)
			continue
		_vector(correction,entry,CLSP_POS)#A plane's normal; its d does not change with a rotation
		if shape == CLSP_PLANE_SHAPE:
			continue
		pairHash = entry.pairJointNameHash
		if shape != CLSP_SPHERE_SHAPE or pairHash in axes.parents:
			correction = axes.correction(pairHash,toFile)
		_vector(correction,entry,CLSP_END_POS)
