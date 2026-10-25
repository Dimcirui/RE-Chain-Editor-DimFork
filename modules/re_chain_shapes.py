#Box (OBB) and plane collision objects, shared by CLSP files and chain / chain2 files
#Imports nothing else from the add-on, so the property groups can use it
import bpy
from math import radians
from mathutils import Matrix,Vector,Quaternion
from .pymmh3 import hash_wide

NO_JOINT_HASH = 2180083513#0x81F16F39, a joint field's "none": the shape hangs from its owner (the armature object)

def toSigned32(value):
	"""A uint32 as Blender's int custom properties can hold it (read back with & 0xFFFFFFFF)."""
	return value - 0x100000000 if value >= 0x80000000 else value

def boneNameHash(boneName):
	"""Joint hash of a constraint subtarget: HASH_<number> is that number, a b<digits>: prefix is dropped (as import matches them, getArmatureHashList)."""
	if "HASH_" in boneName:
		return int(boneName.split("HASH_")[1])
	return hash_wide(boneName.split(":",1)[1] if boneName.startswith("b") and ":" in boneName else boneName)

#The pair joint of a CLSP sphere or a chain box or plane, kept from the file (what the game does with it is unknown):
#a bone name (or HASH_<number>), or PAIR_IS_SELF for the object's own bone. Without it the pair joint is the file's none.
PAIR_JOINT = "pairJoint"
PAIR_IS_SELF = "<self>"
def storePairJoint(obj,jointHash,pairHash,pairName,noneHash):
	if pairHash != noneHash:
		obj[PAIR_JOINT] = PAIR_IS_SELF if pairHash == jointHash else pairName
def pairJointHash(obj,jointHash,noneHash):
	pairJoint = obj.get(PAIR_JOINT,"")
	if pairJoint == PAIR_IS_SELF:
		return jointHash
	if pairJoint == "":
		return noneHash
	return boneNameHash(pairJoint)

def gameToBlenderMatrix():
	return Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))#(x,y,z) -> (x,-z,y)

def newWireCollision(name,collection,objType,vertices,edges,faces):
	mesh = bpy.data.meshes.new(name)
	mesh.from_pydata(vertices,edges,faces)
	obj = bpy.data.objects.new(name,mesh)
	collection.objects.link(obj)
	obj["TYPE"] = objType
	obj.display_type = "WIRE"
	obj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawCollisionsThroughObjects
	obj.show_name = bpy.context.scene.re_chain_toolpanel.showCollisionNames
	obj.rotation_mode = "QUATERNION"
	return obj

def attachToJoint(collisionObj,armature,jointName,parent = None):
	"""Hang a plane or box from its bone (a BoneName Child Of whose own transform is in the bone's space), or with no joint from the armature object.
	A chain's collision objects are also parented to the chain header (parent)."""
	collisionObj.parent = parent if parent != None else (armature if jointName == None else None)
	if jointName == None:
		return
	constraint = collisionObj.constraints.new(type = "CHILD_OF")
	constraint.target = armature
	constraint.subtarget = jointName
	constraint.name = "BoneName"
	constraint.use_scale_x = False
	constraint.use_scale_y = False
	constraint.use_scale_z = False
	#A new Child Of sets its inverse on its first evaluation, which would cancel the bone; use the inverse the spheres get (alignCollisions)
	constraint.set_inverse_pending = False
	constraint.inverse_matrix = armature.matrix_world.inverted()

def collisionJointHash(collisionObj):
	"""Joint hash of a plane or box from its BoneName constraint; NO_JOINT_HASH when it has none (it hangs from the armature object)."""
	constraint = collisionObj.constraints.get("BoneName")
	if constraint == None or constraint.subtarget == "":
		return NO_JOINT_HASH
	return boneNameHash(constraint.subtarget)

#Planes: a CLSP plane object's normal is its local Z; a chain plane's (and the file's) is its local Y, marked by PLANE_NORMAL_AXIS.
#Each format's export turns the other kind's normal into its own, so either kind of object can be written to either format.
PLANE_NORMAL_AXIS = "planeNormalAxis"
CLSP_PLANE_VERTICES = [(-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0),(0,0,0),(0,0,0.25)]
CHAIN_PLANE_VERTICES = [(-1,0,-1),(1,0,-1),(1,0,1),(-1,0,1),(0,0,0),(0,0.25,0)]
JOINT_PLANE_DISPLAY_SIZE = 0.25#A plane on a bone is drawn this big; its scale is not in the file
def planeNormal(planeObj):
	"""The plane object's normal in its own parent space (Blender's, before the game conversion)."""
	axis = Vector((0.0,1.0,0.0)) if planeObj.get(PLANE_NORMAL_AXIS) == "Y" else Vector((0.0,0.0,1.0))
	return (planeObj.matrix_basis.to_quaternion() @ axis).normalized()

#A CLSP plane (kind 4): normal n at +0x20, d at +0x2c,
#carried by its joint (or, with no joint, by the owner Transform): the plane is through n * -d along n.
#In Blender: a wire plane whose local Z is n and whose origin is n * -d, in its bone's space (Child Of, like the
#other shapes' offsets) or, with no joint, in the armature object's space (game y up -> Blender z up).
def createPlaneCollision(name,collection,armature,jointName,normal,d):
	planeObj = newWireCollision(name,collection,"RE_CHAIN_COLLISION_PLANE",CLSP_PLANE_VERTICES,[(4,5)],[(0,1,2,3)])
	n = Vector(normal)
	if jointName == None:
		n = Vector((n[0],-n[2],n[1]))
	n = n.normalized() if n.length > 0 else Vector((0.0,0.0,1.0))
	planeObj.rotation_quaternion = Vector((0.0,0.0,1.0)).rotation_difference(n)
	planeObj.location = n * -d
	if jointName != None:
		planeObj.scale = [JOINT_PLANE_DISPLAY_SIZE]*3
	attachToJoint(planeObj,armature,jointName)
	planeObj.re_chain_chaincollision.chainCollisionShape = "4"
	return planeObj

def planeCollisionData(planeObj):
	"""(joint hash, normal, d) of a plane collision object, in the CLSP file's terms."""
	n = planeNormal(planeObj)
	p = planeObj.matrix_basis.translation
	jointHash = collisionJointHash(planeObj)
	if jointHash == NO_JOINT_HASH:
		n, p = Vector((n[0],n[2],-n[1])), Vector((p[0],p[2],-p[1]))#Blender z up -> game y up
	return jointHash, n, -n.dot(p)

#A CLSP box (kind 2): a 4x4 matrix and half extents (CLSPEntry.getBox), both joint fields its joint,
#carried by that joint (or, with no joint, by the owner Transform).
#In Blender: a wire cube from -1 to 1 whose matrix_basis is the box's matrix with the half extents as its scale,
#in its bone's space (Child Of, like a plane) or, with no joint, in the armature object's space (game y up -> Blender z up).
BOX_VERTICES = [(x,y,z) for x in (-1,1) for y in (-1,1) for z in (-1,1)]
BOX_EDGES = [(0,1),(2,3),(4,5),(6,7),(0,2),(1,3),(4,6),(5,7),(0,4),(1,5),(2,6),(3,7)]
def createBoxCollision(name,collection,armature,jointName,rows,halfExtents):
	boxObj = newWireCollision(name,collection,"RE_CHAIN_COLLISION_BOX",BOX_VERTICES,BOX_EDGES,[])
	m = Matrix(rows).transposed()#The file's rows are Blender's columns
	if jointName == None:
		m = gameToBlenderMatrix() @ m
	location,rotation,scale = m.decompose()
	boxObj.location = location
	boxObj.rotation_quaternion = rotation
	boxObj.scale = halfExtents
	attachToJoint(boxObj,armature,jointName)
	boxObj.re_chain_chaincollision.chainCollisionShape = "3"
	return boxObj

def boxCollisionData(boxObj):
	"""(joint hash, 4 rows of the box's matrix, half extents) of a box collision object, in the CLSP file's terms."""
	location,rotation,scale = boxObj.matrix_basis.decompose()
	m = Matrix.LocRotScale(location,rotation,None)
	jointHash = collisionJointHash(boxObj)
	if jointHash == NO_JOINT_HASH:
		m = gameToBlenderMatrix().inverted() @ m#Blender z up -> game y up
	return jointHash, [list(row) for row in m.transposed()], [abs(value) for value in scale]

#A chain or chain2 OBB (shape 3): pos the centre, rotOffset its rotation, pairPos its half extents, in its joint's space.
#A chain plane (shape 4): through pos, its normal the rotOffset rotation's +Y.
#radius, endRadius and the pair joint keep the file's values (the game's use of them is unknown).
#In Blender: location = pos, rotation_quaternion = rotOffset (w first), a box's scale = pairPos; parented to the chain
#header with a BoneName Child Of, or with no joint (0x81F16F39) only parented, in the header's space (game y up -> Blender z up).
def createChainShapeCollision(name,collection,headerObj,armature,jointName,shape,location,rotation,halfExtents = None):
	if shape == "3":
		obj = newWireCollision(name,collection,"RE_CHAIN_COLLISION_BOX",BOX_VERTICES,BOX_EDGES,[])
	else:
		obj = newWireCollision(name,collection,"RE_CHAIN_COLLISION_PLANE",CHAIN_PLANE_VERTICES,[(4,5)],[(0,1,2,3)])
		obj[PLANE_NORMAL_AXIS] = "Y"
	location,rotation = Vector(location),Quaternion(rotation)
	if jointName == None:
		location,rotation = (gameToBlenderMatrix() @ Matrix.LocRotScale(location,rotation,None)).decompose()[:2]
	obj.location = location
	obj.rotation_quaternion = rotation
	if shape == "3":
		obj.scale = halfExtents
	elif jointName != None:
		obj.scale = [JOINT_PLANE_DISPLAY_SIZE]*3
	attachToJoint(obj,armature,jointName,parent = headerObj)
	obj.re_chain_chaincollision.chainCollisionShape = shape
	return obj

#Chain files also write a collision with no joint as joint hash 0 (shipped items); OWNER_JOINT_HASH keeps that value
#(signed: Blender's int custom properties are 32-bit, see toSigned32)
CHAIN_NO_JOINT_HASHES = (NO_JOINT_HASH,0)
OWNER_JOINT_HASH = "ownerJointHash"
def chainShapeData(obj):
	"""(joint hash, pos, rotOffset (w,x,y,z), half extents) of a box or plane object, in the chain file's terms."""
	location = obj.location.copy()
	rotation = obj.rotation_quaternion.copy() if obj.rotation_mode == "QUATERNION" else obj.matrix_basis.to_quaternion()
	if obj.get("TYPE") == "RE_CHAIN_COLLISION_PLANE" and obj.get(PLANE_NORMAL_AXIS) != "Y":
		rotation = rotation @ Quaternion((1.0,0.0,0.0),radians(90))#A CLSP plane object: its normal (local Z) becomes the file's +Y
	jointHash = collisionJointHash(obj)
	if jointHash == NO_JOINT_HASH:
		jointHash = obj.get(OWNER_JOINT_HASH,NO_JOINT_HASH) & 0xFFFFFFFF
		location,rotation = (gameToBlenderMatrix().inverted() @ Matrix.LocRotScale(location,rotation,None)).decompose()[:2]#Blender z up -> game y up
	return jointHash, location, rotation, [abs(value) for value in obj.scale]
