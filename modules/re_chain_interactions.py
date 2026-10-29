#Highlights in the viewport what the selection collides with: the collisions a selected chain group or link collides
#with, or the chain groups and links a selected collision is hit by.
#Internal collisions (the chain's own collection) are filtered by Collision Filter Flags: node & collision in chain2,
#group & node & collision in chain. External ones (the Reference Colliders collection, a CLSP in the game) by the 64-bit
#CLSP mask (Flags A low 32 bits, B high), in chain2 and chain version 55 and above only. Chain Collisions and Scene
#Colliders switch each kind on, from the group's attribute flags or its setting's with Collision from Setting.
#chain2 only: the file's own collisions skip groups whose Exe Order is below their Min Exe Order, and Collision Group
#adds the other groups of the file whose colliding nodes share a Collision Filter Flags bit with the group's.
#With no reference collection (or the chain's own), the chain's own collisions are the external ones: most pfbs set the
#chain to collide with external colliders only.
import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from bpy.app.handlers import persistent

from .re_chain_type_sync import getOwningChainCollection,chainFileTypeForCollection
from .re_chain_propertyGroups import linkCollisionSetting

COLLISION_TYPES = ("RE_CHAIN_COLLISION_SINGLE","RE_CHAIN_COLLISION_CAPSULE_ROOT","RE_CHAIN_COLLISION_PLANE","RE_CHAIN_COLLISION_BOX")
CAPSULE_END_TYPES = ("RE_CHAIN_COLLISION_CAPSULE_START","RE_CHAIN_COLLISION_CAPSULE_END")
GROUP_TYPES = ("RE_CHAIN_CHAINGROUP","RE_CHAIN_SUBGROUP")
INTERNAL_COLOR = (1.0,0.55,0.0,1.0)
EXTERNAL_COLOR = (0.0,0.8,1.0,1.0)
HIDDEN_OPACITY = 0.35#Of the set opacity, for the parts behind other geometry

#Group attribute flags: (Collision from Setting, Chain Collisions, Collision Group, Scene Colliders) per format
COLLISION_DEFAULT = 0x8
COLLISION_MODEL = 0x20
COLLISION_GROUP = 0x100
COLLISION_CHARACTER = {"chain":0x20000,"chain2":0x10000}
FULL_MASK = (1 << 64) - 1

def clspMask(flagsA,flagsB):
	return (flagsA & 0xFFFFFFFF) | ((flagsB & 0xFFFFFFFF) << 32)

class ChainInfo():
	"""The format of a chain collection and where its internal and external collisions come from."""
	def __init__(self,collection,reference):
		self.collection = collection
		self.fileType = chainFileTypeForCollection(collection.name) or "chain"
		headers = [obj for obj in collection.all_objects if obj.get("TYPE",None) == "RE_CHAIN_HEADER"]
		try:
			version = int(getattr(headers[0].re_chain_header,"version",0)) if headers else 0
		except ValueError:
			version = 0
		self.hasCLSP = self.fileType == "chain2" or version >= 55
		ownCollisions = collisionsOf(collection)
		self.own = set(ownCollisions)
		if not self.hasCLSP:
			self.internal,self.external = ownCollisions,[]
		elif reference == None or reference == collection:
			self.internal,self.external = [],ownCollisions
		else:
			self.internal,self.external = ownCollisions,collisionsOf(reference)

def collisionsOf(collection):
	return [obj for obj in collection.all_objects if obj.get("TYPE",None) in COLLISION_TYPES]

def externalMask(colObj):
	#A chain or chain2 collision record has no CLSP mask, so one used as an external collider is not filtered
	if any(collection.get("~TYPE",None) == "RE_CLSP_COLLECTION" for collection in colObj.users_collection):
		return clspMask(colObj.re_chain_chaincollision.clspBitFlag0,colObj.re_chain_chaincollision.clspBitFlag1)
	return FULL_MASK

def switches(attrFlags,fileType):
	return bool(attrFlags & COLLISION_MODEL), bool(attrFlags & COLLISION_CHARACTER[fileType])

def groupCollisionAttr(groupObj):
	"""The attribute flags a group takes its collision switches from: its own, or its setting's with Collision from Setting."""
	attrFlags = groupObj.re_chain_chaingroup.attrFlags
	setting = groupObj.parent
	if attrFlags & COLLISION_DEFAULT and setting != None and setting.get("TYPE",None) == "RE_CHAIN_CHAINSETTINGS":
		attrFlags = setting.re_chain_chainsettings.groupDefaultAttr
	return attrFlags

def groupSwitches(groupObj,fileType):
	return switches(groupCollisionAttr(groupObj),fileType)

def nodesOf(groupObj):
	return [child for child in groupObj.children_recursive if child.get("TYPE",None) == "RE_CHAIN_NODE"]

def collidingNodeFilters(nodes):
	"""The Collision Filter Flags of the nodes that have a collision shape (MH Wilds: Sphere or Capsule, with a radius)."""
	return [node.re_chain_chainnode.collisionFilterFlags for node in nodes if node.re_chain_chainnode.collisionShape in ("1","2") and node.re_chain_chainnode.collisionRadius > 0]

def skipsGroup(colObj,groupObj,info):
	"""chain2: the file's own collision skips a group whose Exe Order is below the collision's Min Exe Order."""
	return info.fileType == "chain2" and colObj in info.own and groupObj.re_chain_chaingroup.rotationOrder < colObj.re_chain_chaincollision.minExeOrder

def groupInteractions(groupObj,info):
	"""{collision or other chain group object: "internal" or "external"} for a chain group or sub group."""
	nodes = nodesOf(groupObj)
	if groupObj.get("TYPE",None) == "RE_CHAIN_SUBGROUP":#Flags and masks are the parent group's
		groupObj = groupObj.re_chain_chainsubgroup.parentGroup
		if groupObj == None:
			return {}
	internalOn,externalOn = groupSwitches(groupObj,info.fileType)
	result = {}
	if internalOn:
		groupFilter = groupObj.re_chain_chaingroup.collisionFilterFlags if info.fileType == "chain" else -1
		nodeFilters = [groupFilter & node.re_chain_chainnode.collisionFilterFlags for node in nodes]
		for colObj in info.internal:
			if skipsGroup(colObj,groupObj,info):
				continue
			colFilter = colObj.re_chain_chaincollision.collisionFilterFlags
			if any(nodeFilter & colFilter for nodeFilter in nodeFilters):
				result[colObj] = "internal"
	if info.fileType == "chain2" and groupCollisionAttr(groupObj) & COLLISION_GROUP:
		ownFilters = collidingNodeFilters(nodes)
		for otherObj in info.collection.all_objects:
			if otherObj.get("TYPE",None) == "RE_CHAIN_CHAINGROUP" and otherObj != groupObj:
				if any(ownFilter & otherFilter for ownFilter in ownFilters for otherFilter in collidingNodeFilters(nodesOf(otherObj))):
					result[otherObj] = "internal"
	if externalOn and info.hasCLSP:
		mask = clspMask(groupObj.re_chain_chaingroup.clspFlags0,groupObj.re_chain_chaingroup.clspFlags1)
		for colObj in info.external:
			if mask & externalMask(colObj) and not skipsGroup(colObj,groupObj,info):
				result[colObj] = "external"
	return result

def linkInteractions(linkObj,info):
	"""{collision object: kind} for a chain link: its link collisions' filter flags, and in chain2 the link's CLSP mask."""
	header,setting = linkCollisionSetting(linkObj)
	internalOn,externalOn = switches(setting.re_chain_chainsettings.groupDefaultAttr,info.fileType) if setting != None else (True,True)
	result = {}
	if internalOn:
		linkFilters = [child.re_chain_chainlink_collision.collisionFilterFlags for child in linkObj.children if child.get("TYPE",None) == "RE_CHAIN_LINK_COLLISION"]
		for colObj in info.internal:
			colFilter = colObj.re_chain_chaincollision.collisionFilterFlags
			if any(linkFilter & colFilter for linkFilter in linkFilters):
				result[colObj] = "internal"
	if externalOn and info.fileType == "chain2":#A chain link has no CLSP mask
		mask = clspMask(linkObj.re_chain_chainlink.clspFlags0,linkObj.re_chain_chainlink.clspFlags1)
		for colObj in info.external:
			if mask & externalMask(colObj):
				result[colObj] = "external"
	return result

def chainSourceOf(obj):
	"""The chain group, sub group or link a selected object stands for, or None."""
	objType = obj.get("TYPE",None)
	if objType in GROUP_TYPES or objType == "RE_CHAIN_LINK":
		return obj
	if objType == "RE_CHAIN_LINK_COLLISION":
		return obj.parent
	if objType in ("RE_CHAIN_NODE","RE_CHAIN_NODE_FRAME"):
		parent = obj.parent
		while parent != None and parent.get("TYPE",None) not in GROUP_TYPES:
			parent = parent.parent
		return parent
	return None

def collisionOf(obj):
	objType = obj.get("TYPE",None)
	if objType in COLLISION_TYPES:
		return obj
	if objType in CAPSULE_END_TYPES:
		return obj.parent
	return None

def interactionsOf(sourceObj,infoCache,reference):
	collection = getOwningChainCollection(sourceObj)
	if collection == None or chainFileTypeForCollection(collection.name) == None:#Not a chain or chain2 collection
		return {}
	if collection.name not in infoCache:
		infoCache[collection.name] = ChainInfo(collection,reference)
	info = infoCache[collection.name]
	if sourceObj.get("TYPE",None) == "RE_CHAIN_LINK":
		return linkInteractions(sourceObj,info)
	return groupInteractions(sourceObj,info)

def chainSources():
	return [obj for obj in bpy.data.objects if obj.get("TYPE",None) in GROUP_TYPES or obj.get("TYPE",None) == "RE_CHAIN_LINK"]

def highlightedObjects(context):
	"""{object: kind} to highlight for the selection."""
	reference = context.scene.re_chain_toolpanel.referenceColliderCollection
	infoCache = {}
	result = {}
	selected = context.selected_objects
	sources = {chainSourceOf(obj) for obj in selected} - {None}
	for sourceObj in sources:
		result.update(interactionsOf(sourceObj,infoCache,reference))
	collisions = {collisionOf(obj) for obj in selected} - {None}
	if collisions:
		for sourceObj in chainSources():
			for colObj,kind in interactionsOf(sourceObj,infoCache,reference).items():
				if colObj in collisions:
					result[sourceObj] = kind
	for obj in selected:
		result.pop(obj,None)
	return result

#---DRAWING---#
drawHandle = None
batchCache = None#(selection key, [(batch, color)])

def objectLines(obj,depsgraph):
	"""World space edge vertex pairs of an object's evaluated geometry."""
	evaluated = obj.evaluated_get(depsgraph)
	try:
		mesh = evaluated.to_mesh()
	except RuntimeError:
		return []
	if mesh == None:
		return []
	matrix = evaluated.matrix_world
	coords = [matrix @ vertex.co for vertex in mesh.vertices]
	lines = [coords[index] for edge in mesh.edges for index in edge.vertices]
	evaluated.to_mesh_clear()
	return lines

def highlightLines(obj,depsgraph):
	if obj.get("TYPE",None) in GROUP_TYPES:#A group draws as a line; its nodes show the chain better
		lines = []
		for child in obj.children_recursive:
			if child.get("TYPE",None) == "RE_CHAIN_NODE" and child.parent != None and child.parent.get("TYPE",None) == "RE_CHAIN_NODE":
				lines.extend((child.parent.matrix_world.translation,child.matrix_world.translation))
		return lines or objectLines(obj,depsgraph)
	return objectLines(obj,depsgraph)

def buildBatches(context):
	shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
	depsgraph = context.evaluated_depsgraph_get()
	linesByColor = {INTERNAL_COLOR:[],EXTERNAL_COLOR:[]}
	for obj,kind in highlightedObjects(context).items():
		if obj.visible_get():
			linesByColor[INTERNAL_COLOR if kind == "internal" else EXTERNAL_COLOR].extend(highlightLines(obj,depsgraph))
	return [(batch_for_shader(shader,"LINES",{"pos":lines}),color) for color,lines in linesByColor.items() if lines]

def drawHighlights():
	global batchCache
	context = bpy.context
	toolpanel = getattr(context.scene,"re_chain_toolpanel",None)
	if toolpanel == None or not toolpanel.highlightInteractions or context.mode != "OBJECT":
		return
	key = (tuple(obj.name for obj in context.selected_objects),toolpanel.referenceColliderCollection)
	try:
		if batchCache == None or batchCache[0] != key:
			batchCache = (key,buildBatches(context))
		shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
		region = context.region
		opacity = toolpanel.highlightOpacity
		gpu.state.blend_set("ALPHA")
		gpu.state.depth_mask_set(False)
		shader.bind()
		shader.uniform_float("viewportSize",(region.width,region.height))
		shader.uniform_float("lineWidth",2.0)
		#In front of the scene at the set opacity, behind it (colliders sit inside the body) fainter
		for depthTest,alpha in (("LESS_EQUAL",opacity),("GREATER",opacity * HIDDEN_OPACITY)):
			gpu.state.depth_test_set(depthTest)
			for batch,color in batchCache[1]:
				shader.uniform_float("color",(*color[:3],alpha))
				batch.draw(shader)
		gpu.state.depth_test_set("NONE")
		gpu.state.blend_set("NONE")
	except Exception as error:#A draw callback error would repeat every redraw
		print(f"RE Chain Editor: interaction highlight failed: {error}")
		batchCache = (key,[])

@persistent
def clearHighlightCache(*args):
	global batchCache
	batchCache = None

def register():
	global drawHandle
	drawHandle = bpy.types.SpaceView3D.draw_handler_add(drawHighlights,(),"WINDOW","POST_VIEW")
	bpy.app.handlers.depsgraph_update_post.append(clearHighlightCache)
	bpy.app.handlers.load_post.append(clearHighlightCache)

def unregister():
	global drawHandle
	if drawHandle != None:
		bpy.types.SpaceView3D.draw_handler_remove(drawHandle,"WINDOW")
		drawHandle = None
	for handlers in (bpy.app.handlers.depsgraph_update_post,bpy.app.handlers.load_post):
		if clearHighlightCache in handlers:
			handlers.remove(clearHighlightCache)
