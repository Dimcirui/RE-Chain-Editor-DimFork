#Keeps chain objects' bone constraints and hooks on an armature that has their bone.
#Joining or separating armatures, or deleting bones, leaves other objects' constraints on an armature without the
#bone; Blender then prints a failed relation for each one on every depsgraph rebuild, which slows everything down.
#Export only reads the bone names, so a reference is moved to the one armature that has its bone, or, when none
#or several do, detached (no target) with the armature it had kept to put back when the bone turns up.
import bpy
from collections import Counter
from bpy.app.handlers import persistent

#{"constraint:<name>" or "hook:<name>": armature name} on the owner of a detached constraint or hook
DETACHED_KEY = "~detachedBoneTargets"

def detachedKey(item):
	return ("hook:" if isinstance(item,bpy.types.Modifier) else "constraint:") + item.name

def detachedArmatureName(obj,item):
	detached = obj.get(DETACHED_KEY,None)
	return detached.get(detachedKey(item),None) if detached != None else None

def hasBoneTarget(constraint):
	"""Whether a bone constraint names its bone: on an armature, or detached from one that lacks the bone."""
	if constraint.subtarget == "":
		return False
	return constraint.target != None or detachedArmatureName(constraint.id_data,constraint) != None

def setDetached(obj,item,armatureName):
	detached = obj.get(DETACHED_KEY,None)
	if armatureName != None:
		if detached == None:
			obj[DETACHED_KEY] = {}
			detached = obj[DETACHED_KEY]
		detached[detachedKey(item)] = armatureName
	elif detached != None and detachedKey(item) in detached:
		del detached[detachedKey(item)]
		if len(detached) == 0:
			del obj[DETACHED_KEY]

def boneReferences(obj):
	"""(item, target attribute) of an object's constraints and hooks that name a bone."""
	for constraint in obj.constraints:
		if hasattr(constraint,"subtarget") and hasattr(constraint,"target"):
			yield constraint,"target"
	for modifier in obj.modifiers:
		if modifier.type == 'HOOK':
			yield modifier,"object"

def repairBoneTargets():
	"""Move or detach the bone references of chain objects whose armature lacks the bone, and put detached ones back
	once an armature has it. Prints what changed; returns whether anything did."""
	armatures = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']
	#Bones of an armature in Edit Mode are only updated when it leaves
	if any(arm.mode == 'EDIT' for arm in armatures):
		return False
	boneOwners = {}
	for arm in armatures:
		for bone in arm.data.bones:
			boneOwners.setdefault(bone.name,[]).append(arm)
	moved = Counter()#(old armature, new armature)
	detached = {}#old armature: bone names
	reattached = 0
	for obj in bpy.data.objects:
		if not str(obj.get("TYPE","")).startswith("RE_CHAIN") or obj.library != None:
			continue
		for item,attribute in boneReferences(obj):
			target = getattr(item,attribute)
			bone = item.subtarget
			if target != None:
				if target.type != 'ARMATURE' or bone == "":
					continue
				if bone in target.data.bones:
					setDetached(obj,item,None)#Set back by hand
					continue
				owners = boneOwners.get(bone,[])
				if len(owners) == 1:
					setattr(item,attribute,owners[0])
					moved[(target.name,owners[0].name)] += 1
				else:
					setattr(item,attribute,None)
					setDetached(obj,item,target.name)
					detached.setdefault(target.name,set()).add(bone)
			else:
				armatureName = detachedArmatureName(obj,item)
				if armatureName == None or bone == "":
					continue
				original = bpy.data.objects.get(armatureName)
				owners = boneOwners.get(bone,[])
				if original != None and original in owners:
					newTarget = original
				elif len(owners) == 1:
					newTarget = owners[0]
				else:
					continue
				setattr(item,attribute,newTarget)
				setDetached(obj,item,None)
				reattached += 1
	for (oldName,newName),count in moved.items():
		print(f"RE Chain Editor: {count} chain bone references were on {oldName}, which lacks their bones; moved to {newName}.")
	for oldName,bones in detached.items():
		names = sorted(bones)
		shown = ", ".join(names[:5]) + (f" and {len(names) - 5} more" if len(names) > 5 else "")
		print(f"RE Chain Editor: {oldName} lacks the bones {shown}, and no single other armature has them; "
			"the chain objects on them were detached from it. Export still uses the bone names.")
	if reattached:
		print(f"RE Chain Editor: {reattached} detached chain bone references were put back on an armature that has their bones.")
	return bool(moved or detached or reattached)

@persistent
def re_chain_bone_target_repair(scene,depsgraph = None):
	#Bones only change with the armature data (Edit Mode, join, separate)
	if depsgraph != None and not depsgraph.id_type_updated('ARMATURE'):
		return
	try:
		repairBoneTargets()
	except Exception as err:
		print(f"RE Chain Editor: bone target repair failed: {err}")

@persistent
def re_chain_bone_target_repair_on_load(dummy):
	re_chain_bone_target_repair(None)

def repairBoneTargetsOnEnable():
	#From a timer: while the add-on registers at startup bpy.data can't be read
	re_chain_bone_target_repair(None)
	return None

def register():
	if re_chain_bone_target_repair not in bpy.app.handlers.depsgraph_update_post:
		bpy.app.handlers.depsgraph_update_post.append(re_chain_bone_target_repair)
	if re_chain_bone_target_repair_on_load not in bpy.app.handlers.load_post:
		bpy.app.handlers.load_post.append(re_chain_bone_target_repair_on_load)
	bpy.app.timers.register(repairBoneTargetsOnEnable,first_interval = 0.0)

def unregister():
	if re_chain_bone_target_repair in bpy.app.handlers.depsgraph_update_post:
		bpy.app.handlers.depsgraph_update_post.remove(re_chain_bone_target_repair)
	if re_chain_bone_target_repair_on_load in bpy.app.handlers.load_post:
		bpy.app.handlers.load_post.remove(re_chain_bone_target_repair_on_load)
	if bpy.app.timers.is_registered(repairBoneTargetsOnEnable):
		bpy.app.timers.unregister(repairBoneTargetsOnEnable)
