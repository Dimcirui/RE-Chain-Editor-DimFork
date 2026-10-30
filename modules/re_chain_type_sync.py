#Keeps the scene-wide chainFileType and chainCollection on the chain collection of the active object
import re
import bpy
from bpy.app.handlers import persistent

from .re_chain_propertyGroups import getOwningChainCollection

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

#Links name their chain groups (Chain Group A / B are strings), so a renamed group would leave its links pointing at
#nothing. Each group keeps the name it had last time; a group whose name changed while no object has the old name
#any more was renamed (not duplicated), and its links follow it
GROUP_NAME_KEY = "~groupName"

def syncChainGroupNames(*args):
	#Runs from msgbus as well, where an exception would reach the UI event loop
	try:
		links = None
		for groupObj in bpy.data.objects:
			if groupObj.get("TYPE",None) != "RE_CHAIN_CHAINGROUP":
				continue
			oldName = groupObj.get(GROUP_NAME_KEY,None)
			if oldName == groupObj.name:
				continue
			if oldName and oldName not in bpy.data.objects:
				if links is None:
					links = [obj for obj in bpy.data.objects if obj.get("TYPE",None) == "RE_CHAIN_LINK"]
				for linkObj in links:
					link = linkObj.re_chain_chainlink
					if link.chainGroupAObject == oldName:
						link.chainGroupAObject = groupObj.name
					if link.chainGroupBObject == oldName:
						link.chainGroupBObject = groupObj.name
			groupObj[GROUP_NAME_KEY] = groupObj.name
	except Exception as err:
		print(f"RE Chain Editor: chain group rename sync failed: {err}")

@persistent
def re_chain_group_name_sync(scene,depsgraph = None):
	#Records the names of new groups (import, Create Chain) and catches renames msgbus doesn't report (from Python)
	syncChainGroupNames()

def stampChainGroupNames():
	#From a timer: while the add-on registers at startup bpy.data can't be read
	syncChainGroupNames()
	return None

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
	bpy.msgbus.subscribe_rna(
		key=(bpy.types.Object, "name"),
		owner=subscriptionOwner,
		args=(),
		notify=syncChainGroupNames,
		)

@persistent
def re_chain_resubscribe_type_sync(dummy):
	subscribeChainFileTypeSync()
	syncChainGroupNames()

def register():
	subscribeChainFileTypeSync()
	if re_chain_resubscribe_type_sync not in bpy.app.handlers.load_post:
		bpy.app.handlers.load_post.append(re_chain_resubscribe_type_sync)
	if re_chain_group_name_sync not in bpy.app.handlers.depsgraph_update_post:
		bpy.app.handlers.depsgraph_update_post.append(re_chain_group_name_sync)
	bpy.app.timers.register(stampChainGroupNames,first_interval = 0.0)

def unregister():
	if re_chain_resubscribe_type_sync in bpy.app.handlers.load_post:
		bpy.app.handlers.load_post.remove(re_chain_resubscribe_type_sync)
	if re_chain_group_name_sync in bpy.app.handlers.depsgraph_update_post:
		bpy.app.handlers.depsgraph_update_post.remove(re_chain_group_name_sync)
	if bpy.app.timers.is_registered(stampChainGroupNames):
		bpy.app.timers.unregister(stampChainGroupNames)
	bpy.msgbus.clear_by_owner(subscriptionOwner)
