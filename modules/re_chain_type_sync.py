#Keeps the scene-wide chainFileType and chainCollection on the chain collection of the active object
import re
import bpy
from bpy.app.handlers import persistent

from .re_chain_propertyGroups import filterChainCollection

#Blender's duplicate suffix, as in "name.chain2.001"
DUPLICATE_SUFFIX = re.compile(r"\.\d{3,}$")
#Owner of the msgbus subscription; reading a .blend clears every subscription, so load_post subscribes again
subscriptionOwner = object()

def chainFileTypeForCollection(collectionName):
	#None for .clsp, which sits beside a chain of either format
	baseName = DUPLICATE_SUFFIX.sub("",collectionName)
	if baseName.endswith(".clsp") or ".chain" not in baseName:
		return None
	return "chain2" if baseName.endswith(".chain2") else "chain"

def getOwningChainCollection(obj):
	#Collisions and links live in child collections, so walk up to the chain collection
	parentDict = {}
	for collection in bpy.data.collections:
		for child in collection.children:
			parentDict[child.name] = collection
	for collection in obj.users_collection:
		visited = set()
		while collection is not None and collection.name not in visited:
			visited.add(collection.name)
			if filterChainCollection(None,collection):
				return collection
			collection = parentDict.get(collection.name)
	return None

def syncChainFileType(*args):
	#Runs from msgbus, where an exception would reach the UI event loop
	try:
		toolpanel = getattr(bpy.context.scene,"re_chain_toolpanel",None)
		obj = getattr(bpy.context,"active_object",None)
		if toolpanel is None or obj is None:
			return
		#An object outside every chain collection leaves both values as they are
		collection = getOwningChainCollection(obj)
		if collection is None:
			return
		#Both move together so create operators never put one format's objects in the other format's collection
		if toolpanel.chainCollection != collection:
			toolpanel.chainCollection = collection
		fileType = chainFileTypeForCollection(collection.name)
		if fileType is not None and toolpanel.chainFileType != fileType:
			toolpanel.chainFileType = fileType
	except Exception as err:
		print(f"RE Chain Editor: chain file type sync failed: {err}")

def subscribeChainFileTypeSync():
	#Background mode has no selection to follow
	if bpy.app.background:
		return
	bpy.msgbus.clear_by_owner(subscriptionOwner)
	bpy.msgbus.subscribe_rna(
		key=(bpy.types.LayerObjects, "active"),
		owner=subscriptionOwner,
		args=(),
		notify=syncChainFileType,
		)

@persistent
def re_chain_resubscribe_type_sync(dummy):
	subscribeChainFileTypeSync()

def register():
	subscribeChainFileTypeSync()
	if re_chain_resubscribe_type_sync not in bpy.app.handlers.load_post:
		bpy.app.handlers.load_post.append(re_chain_resubscribe_type_sync)

def unregister():
	if re_chain_resubscribe_type_sync in bpy.app.handlers.load_post:
		bpy.app.handlers.load_post.remove(re_chain_resubscribe_type_sync)
	bpy.msgbus.clear_by_owner(subscriptionOwner)
