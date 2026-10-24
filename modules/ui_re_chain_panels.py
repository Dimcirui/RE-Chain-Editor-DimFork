import bpy

from bpy.types import (Panel,
					   Menu,
					   Operator,
					   PropertyGroup,
					   )

from .file_re_chain import version
from .re_chain_names import propLabel,pickName

def tag_redraw(context, space_type="PROPERTIES", region_type="WINDOW"):
	for window in context.window_manager.windows:
		for area in window.screen.areas:
			if area.spaces[0].type == space_type:
				for region in area.regions:
					if region.type == region_type:
						region.tag_redraw()



def greyed(layout,active):
	"""A column drawn greyed out (still editable) when active is False: the field does nothing as things are set."""
	column = layout.column()
	column.active = bool(active)
	return column

def isChainCollision(obj):
	"""The collision is in a chain or chain2 chain collection, not a clsp one."""
	types = {collection.get("~TYPE",None) for collection in bpy.data.collections if obj.name in collection.all_objects}
	return "RE_CHAIN_COLLECTION" in types and "RE_CLSP_COLLECTION" not in types

def chainGroupOfNode(nodeObj):
	obj = nodeObj.parent
	while obj != None and obj.get("TYPE",None) != "RE_CHAIN_CHAINGROUP":
		obj = obj.parent
	return obj

class OBJECT_PT_ChainObjectModePanel(Panel):
	bl_label = "RE Chain: Object Mode Tools"
	bl_idname = "OBJECT_PT_chain_object_mode_panel"
	bl_space_type = "VIEW_3D"   
	bl_region_type = "UI"
	bl_category = "RE Chain"   
	bl_context = "objectmode"

	@classmethod
	def poll(self,context):
		return context is not None and "HIDE_RE_CHAIN_EDITOR_TAB" not in context.scene

	def draw(self, context):
		scene = context.scene
		re_chain_toolpanel = scene.re_chain_toolpanel
		layout = self.layout
		layout.operator("re_chain.create_chain_header")
		layout.label(text = "Active Chain Collection")
		#layout.prop_search(re_chain_toolpanel, "chainCollection",bpy.data,"collections",icon = "COLLECTION_COLOR_02")
		layout.prop(re_chain_toolpanel, "chainCollection",icon = "COLLECTION_COLOR_02")
		layout.prop(re_chain_toolpanel, "chainFileType")
		layout.operator("re_chain.create_chain_settings")
		layout.operator("re_chain.create_wind_settings")
		layout.operator("re_chain.create_chain_jiggle")
		layout.operator("re_chain.create_chain_link")
		layout.operator("re_chain.create_chain_link_collision")
		layout.operator("re_chain.create_sub_group")
		#layout.operator("re_chain.align_chains_to_bone")# Not needed anymore
		layout.operator("re_chain.align_frames")
		layout.operator("re_chain.apply_angle_limit_ramp")
		layout.label(text="Create new chains in Pose Mode.")
		layout.operator("re_chain.switch_to_pose")
		#Not implemented yet
		#layout.operator("re_chain.point_frame")#Not implemented yet

class OBJECT_PT_ChainClipboardPanel(Panel):
	bl_label = "RE Chain: Clipboard"
	bl_idname = "OBJECT_PT_chain_clipboard_panel"
	bl_space_type = "VIEW_3D"   
	bl_region_type = "UI"
	bl_category = "RE Chain"   
	bl_context = "objectmode"
	bl_options = {'DEFAULT_CLOSED'}
	@classmethod
	def poll(self,context):
		return context is not None and "HIDE_RE_CHAIN_EDITOR_TAB" not in context.scene

	def draw(self, context):
		layout = self.layout
		layout.label(text="Copy Chain Object Properties")
		row = layout.row()
		row.operator("re_chain.copy_chain_properties")
		row.operator("re_chain.paste_chain_properties")
		layout.label(text="Clipboard Contents:")
		layout.label(text=str(context.scene.re_chain_clipboard.re_chain_type_name))
		
class OBJECT_PT_ChainPoseModePanel(Panel):
	bl_label = "RE Chain: Pose Mode Tools"
	bl_idname = "OBJECT_PT_chain_pose_mode_panel"
	bl_space_type = "VIEW_3D"   
	bl_region_type = "UI"
	bl_category = "RE Chain"   
	bl_context = "posemode"

	@classmethod
	def poll(self,context):
		return context.active_object is not None and "HIDE_RE_CHAIN_EDITOR_TAB" not in context.scene

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		re_chain_toolpanel = scene.re_chain_toolpanel
		layout.label(text="Chain Tools")
		layout.label(text = "Active Chain Collection")
		#layout.prop_search(re_chain_toolpanel, "chainCollection",bpy.data,"collections",icon = "COLLECTION_COLOR_02")
		
		layout.prop(re_chain_toolpanel, "chainCollection",icon = "COLLECTION_COLOR_02")
		layout.label(text = "Chain Setting")
		row = layout.row()
		row.prop(re_chain_toolpanel, "chainSetting")
		row.operator("re_chain.create_chain_settings",icon='ADD', text="")
		
		chainFromBoneText = re_chain_toolpanel.chainFromBoneLabelName
		if not re_chain_toolpanel.experimentalPoseModeOptions and len(context.selected_pose_bones or []) > 1:
			chainFromBoneText = "Batch Create Chains From Bones"
		layout.operator("re_chain.chain_from_bone",text=chainFromBoneText)
		layout.label(text="Collision Tools")
		layout.prop(re_chain_toolpanel, "collisionShape")
		layout.operator("re_chain.collision_from_bone")
		layout.operator("re_chain.create_full_body_clsp")
		layout.label(text="Extra Tools")
		layout.operator("re_chain.rename_bone_chain")
		layout.operator("re_chain.create_chain_bone_group")
		layout.operator("re_chain.align_bone_tails_to_axis")
		layout.prop(re_chain_toolpanel, "experimentalPoseModeOptions")
		layout.label(text="Configure chains in Object Mode.")
		layout.operator("re_chain.switch_to_object")

class OBJECT_PT_ChainPresetPanel(Panel):
	bl_label = "RE Chain: Presets"
	bl_idname = "OBJECT_PT_chain_presets_panel"
	bl_space_type = "VIEW_3D"   
	bl_region_type = "UI"
	bl_category = "RE Chain"   
	bl_context = "objectmode"
	bl_options = {'DEFAULT_CLOSED'}
	@classmethod
	def poll(self,context):
		return context is not None and "HIDE_RE_CHAIN_EDITOR_TAB" not in context.scene

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		re_chain_toolpanel = scene.re_chain_toolpanel
		layout.operator("re_chain.save_selected_as_preset")
		layout.operator("re_chain.open_preset_folder")
		#layout.menu(OBJECT_MT_CustomMenu.bl_idname, text="Chain Group")
		layout.label(text="Chain Settings Preset")
		layout.prop(re_chain_toolpanel, "chainSettingsPresets")
		layout.operator("re_chain.apply_chain_settings_preset")
		layout.label(text="Chain Group Preset")
		layout.prop(re_chain_toolpanel, "chainGroupPresets")
		layout.operator("re_chain.apply_chain_group_preset")
		layout.label(text="Chain Node Preset")
		layout.prop(re_chain_toolpanel, "chainNodePresets")
		layout.prop(re_chain_toolpanel,"applyPresetToChildNodes")
		layout.operator("re_chain.apply_chain_node_preset")
		layout.label(text="Wind Settings Preset")
		layout.prop(re_chain_toolpanel, "chainWindSettingsPresets")
		layout.operator("re_chain.apply_wind_settings_preset")
		layout.label(text="Chain Preset (setting, group and node)")
		layout.prop(re_chain_toolpanel, "chainPresets")
		layout.operator("re_chain.apply_chain_preset")
"""
class OBJECT_PT_ChainUtilsPanel(Panel):
	bl_label = "Chain Tools"
	bl_idname = "OBJECT_PT_chain_utils_panel"
	bl_space_type = "VIEW_3D"   
	bl_region_type = "UI"
	bl_category = "RE Chain"   


	@classmethod
	def poll(self,context):
		return context.active_object is not None

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		re_chain_toolpanel = scene.re_chain_toolpanel
		
		layout.label(text="Copy Chain Object Properties")
		row = layout.row()
		row.operator("re_chain.copy_chain_properties")
		row.operator("re_chain.paste_chain_properties")
		layout.label(text="Clipboard Contents: "+str(re_chain_toolpanel.clipboardType))
		layout.separator()
		layout.label(text="Object Mode Tools")
		layout.operator("re_chain.create_chain_header")
		layout.operator("re_chain.create_chain_settings")
		layout.operator("re_chain.create_wind_settings")
		layout.operator("re_chain.align_chains_to_bone")
		layout.operator("re_chain.align_frames")
		layout.operator("re_chain.point_frame")
		layout.label(text="Pose Mode Tools")
		layout.operator("re_chain.chain_from_bone")
		layout.label(text="Collision Shape")
		layout.prop(re_chain_toolpanel, "collisionShape")
		layout.operator("re_chain.collision_from_bone")
		
"""
class OBJECT_PT_ChainHeaderPanel(Panel):
	bl_label = "RE Chain Header Settings"
	bl_idname = "OBJECT_PT_chain_header_panel"
	bl_space_type = "PROPERTIES"   
	bl_region_type = "WINDOW"
	bl_category = "RE Chain Header Settings"
	bl_context = "object"


	@classmethod
	def poll(self,context):
		
		return context and context.active_object and context.active_object.get and context.active_object.get("TYPE",None) == "RE_CHAIN_HEADER"

	def draw(self, context):
		layout = self.layout
		object = context.active_object
		re_chain_header = object.re_chain_header
		isChain2 = context.scene.re_chain_toolpanel.chainFileType == "chain2"
		split = layout.split(factor=0.01)
		col1 = split.column()
		col2 = split.column()
		col2.alignment='RIGHT'
		col2.use_property_split = True
		#col2.prop(re_chain_header, "version")#Set by export
		row = col2.row()
		row.prop(re_chain_header, "errFlagBits")
		row.operator("re_chain.set_bit_flags",icon='DOWNARROW_HLT', text="").target = "re_chain_header.errFlagBits"
		col2.prop(re_chain_header, "masterSize")
		col2.prop(re_chain_header, "rotationOrder")
		col2.prop(re_chain_header, "defaultSettingIdx")
		col2.prop(re_chain_header, "calculateMode")
		row = col2.row()
		row.prop(re_chain_header, "chainAttrFlags")
		row.operator("re_chain.set_bit_flags",icon='DOWNARROW_HLT', text="").target = "re_chain_header.chainAttrFlags"
		row = col2.row()
		row.prop(re_chain_header, "parameterFlag")
		row.operator("re_chain.set_bit_flags",icon='DOWNARROW_HLT', text="").target = "re_chain_header.parameterFlag"
		col2.prop(re_chain_header, "calculateStepTime")
		col2.prop(re_chain_header, "modelCollisionSearch")
		if not isChain2:
			col2.prop(re_chain_header, "legacyVersion")
		else:
			#Greyed: Restart Damping Hold off / Chain Attribute Flags without Alternative Restart Iterations
			greyed(col2,re_chain_header.wilds_unkn2 == 1).prop(re_chain_header, "highFPSCalculateMode")
			greyed(col2,re_chain_header.chainAttrFlags & 0x2).prop(re_chain_header, "restartIterationsAlt")
			col2.prop(re_chain_header, "freeLinkJoint")
			col2.prop(re_chain_header, "taperedCollideMethod")
			col2.prop(re_chain_header, "wilds_unkn1",text=propLabel(re_chain_header,"wilds_unkn1"))
			col2.prop(re_chain_header, "wilds_unkn2",text=propLabel(re_chain_header,"wilds_unkn2"))
		row = col2.row()
		row.prop(re_chain_header, "collisionFilterHitBits0")
		row.operator("re_chain.set_bit_flags",icon='DOWNARROW_HLT', text="").target = "re_chain_header.collisionFilterHitBits0"
		row = col2.row()
		row.prop(re_chain_header, "collisionFilterHitBits1")
		row.operator("re_chain.set_bit_flags",icon='DOWNARROW_HLT', text="").target = "re_chain_header.collisionFilterHitBits1"
		row = col2.row()
		row.prop(re_chain_header, "collisionFilterHitBits2")
		row.operator("re_chain.set_bit_flags",icon='DOWNARROW_HLT', text="").target = "re_chain_header.collisionFilterHitBits2"
		row = col2.row()
		row.prop(re_chain_header, "collisionFilterHitBits3")
		row.operator("re_chain.set_bit_flags",icon='DOWNARROW_HLT', text="").target = "re_chain_header.collisionFilterHitBits3"
		row = col2.row()
		row.prop(re_chain_header, "collisionFilterHitBits4")
		row.operator("re_chain.set_bit_flags",icon='DOWNARROW_HLT', text="").target = "re_chain_header.collisionFilterHitBits4"
		row = col2.row()
		row.prop(re_chain_header, "collisionFilterHitBits5")
		row.operator("re_chain.set_bit_flags",icon='DOWNARROW_HLT', text="").target = "re_chain_header.collisionFilterHitBits5"
		row = col2.row()
		row.prop(re_chain_header, "collisionFilterHitBits6")
		row.operator("re_chain.set_bit_flags",icon='DOWNARROW_HLT', text="").target = "re_chain_header.collisionFilterHitBits6"
		row = col2.row()
		row.prop(re_chain_header, "collisionFilterHitBits7")
		row.operator("re_chain.set_bit_flags",icon='DOWNARROW_HLT', text="").target = "re_chain_header.collisionFilterHitBits7"
		
class OBJECT_PT_WindSettingsPanel(Panel):
	bl_label = "RE Chain Wind Settings"
	bl_idname = "OBJECT_PT_wind_settings_panel"
	bl_space_type = "PROPERTIES"   
	bl_region_type = "WINDOW"
	bl_category = "RE Chain Wind Settings"
	bl_context = "object"


	@classmethod
	def poll(self,context):
		
		return context and context.object.mode == "OBJECT" and context.active_object and context.active_object.get("TYPE",None) == "RE_CHAIN_WINDSETTINGS"

	def draw(self, context):
		layout = self.layout
		object = context.active_object
		re_chain_windsettings = object.re_chain_windsettings
		
		split = layout.split(factor=0.01)
		col1 = split.column()
		col2 = split.column()
		col2.alignment='RIGHT'
		col2.use_property_split = True
		col2.prop(re_chain_windsettings, "id")
		col2.prop(re_chain_windsettings, "windDirection") 
		col2.prop(re_chain_windsettings, "windCount")
		col2.prop(re_chain_windsettings, "windType")
		col2.prop(re_chain_windsettings, "randomDamping")
		col2.prop(re_chain_windsettings, "randomDampingCycle")
		col2.prop(re_chain_windsettings, "randomCycleScaling")
		col2.separator()
		col2.prop(re_chain_windsettings, "dir0")
		col2.prop(re_chain_windsettings, "min0")
		col2.prop(re_chain_windsettings, "max0")
		col2.prop(re_chain_windsettings, "phaseShift0")
		col2.prop(re_chain_windsettings, "cycle0")
		col2.prop(re_chain_windsettings, "interval0")
		col2.separator()
		col2.prop(re_chain_windsettings, "dir1")
		col2.prop(re_chain_windsettings, "min1")
		col2.prop(re_chain_windsettings, "max1")
		col2.prop(re_chain_windsettings, "phaseShift1")
		col2.prop(re_chain_windsettings, "cycle1")
		col2.prop(re_chain_windsettings, "interval1")
		col2.separator()
		col2.prop(re_chain_windsettings, "dir2")
		col2.prop(re_chain_windsettings, "min2")
		col2.prop(re_chain_windsettings, "max2")
		col2.prop(re_chain_windsettings, "phaseShift2")
		col2.prop(re_chain_windsettings, "cycle2")
		col2.prop(re_chain_windsettings, "interval2")
		col2.separator()
		col2.prop(re_chain_windsettings, "dir3")
		col2.prop(re_chain_windsettings, "min3")
		col2.prop(re_chain_windsettings, "max3")
		col2.prop(re_chain_windsettings, "phaseShift3")
		col2.prop(re_chain_windsettings, "cycle3")
		col2.prop(re_chain_windsettings, "interval3")
		col2.separator()
		col2.prop(re_chain_windsettings, "dir4")
		col2.prop(re_chain_windsettings, "min4")
		col2.prop(re_chain_windsettings, "max4")
		col2.prop(re_chain_windsettings, "phaseShift4")
		col2.prop(re_chain_windsettings, "cycle4")
		col2.prop(re_chain_windsettings, "interval4")

class OBJECT_PT_ChainSettingsPanel(Panel):
	bl_label = "RE Chain Settings"
	bl_idname = "OBJECT_PT_chain_settings_panel"
	bl_space_type = "PROPERTIES"   
	bl_region_type = "WINDOW"
	bl_category = "RE Chain Settings"
	bl_context = "object"


	@classmethod
	def poll(self,context):
		
		return context and context.object.mode == "OBJECT" and context.active_object.get("TYPE",None) == "RE_CHAIN_CHAINSETTINGS"

	def draw(self, context):
		layout = self.layout
		object = context.active_object
		re_chain_chainsettings = object.re_chain_chainsettings
		isChain2 = context.scene.re_chain_toolpanel.chainFileType == "chain2"
		split = layout.split(factor=0.01)
		col1 = split.column()
		col2 = split.column()
		col2.alignment='RIGHT'
		col2.use_property_split = True
		col2.prop(re_chain_chainsettings, "id")
		row = col2.row()
		row.prop(re_chain_chainsettings, "colliderFilterInfoPath")
		row.operator("re_chain.set_cfil_path",icon='DOWNARROW_HLT', text="")
		if not isChain2:
			col2.prop(re_chain_chainsettings, "chainType")
			col2.prop(re_chain_chainsettings, "sprayParameterArc") 
			col2.prop(re_chain_chainsettings, "sprayParameterFrequency")
			col2.prop(re_chain_chainsettings, "sprayParameterCurve1")
			col2.prop(re_chain_chainsettings, "sprayParameterCurve2")
			col2.prop(re_chain_chainsettings, "muzzleDirection")
			col2.prop(re_chain_chainsettings, "muzzleVelocity")
			col2.prop(re_chain_chainsettings, "shootingElasticLimitRate")
			
		row = col2.row()
		row.prop(re_chain_chainsettings, "settingsAttrFlags")
		row.operator("re_chain.set_settings_attr_flags",icon='DOWNARROW_HLT', text="")
		
		col2.prop(re_chain_chainsettings, "gravity")
		
		col2.prop(re_chain_chainsettings, "damping",slider=True)
		#if version >= 24:
		col2.prop(re_chain_chainsettings, "minDamping",slider=True)
		col2.prop(re_chain_chainsettings, "dampingPow")
		#MH Wilds: each speed (or force) leads its group; at exactly 0 the rest of the group does nothing and is greyed
		secondDampingOn = not isChain2 or re_chain_chainsettings.secondDampingSpeed != 0.0
		col2.prop(re_chain_chainsettings, "secondDampingSpeed")
		greyed(col2,secondDampingOn).prop(re_chain_chainsettings, "secondDamping",slider=True)
		#if version >= 24:
		greyed(col2,secondDampingOn).prop(re_chain_chainsettings, "secondMinDamping",slider=True)
		#if version >= 24:
		greyed(col2,secondDampingOn).prop(re_chain_chainsettings, "secondDampingPow")
		col2.prop(re_chain_chainsettings, "collideMaxVelocity")
		springOn = not isChain2 or re_chain_chainsettings.springForce != 0.0
		col2.prop(re_chain_chainsettings, "springForce")
		greyed(col2,springOn).prop(re_chain_chainsettings, "springCalcType")
		greyed(col2,springOn).prop(re_chain_chainsettings, "springLimitRate")
		greyed(col2,springOn).prop(re_chain_chainsettings, "springMaxVelocity")

		col2.prop(re_chain_chainsettings, "reduceSelfDistanceRate",slider=True)
		col2.prop(re_chain_chainsettings, "secondReduceDistanceSpeed")
		greyed(col2,not isChain2 or re_chain_chainsettings.secondReduceDistanceSpeed != 0.0).prop(re_chain_chainsettings, "secondReduceDistanceRate",slider=True)
		col2.prop(re_chain_chainsettings, "friction",slider=True)
		col2.prop(re_chain_chainsettings, "shockAbsorptionRate",slider=True)
		col2.prop(re_chain_chainsettings, "coefOfElasticity",slider=True)
		col2.prop(re_chain_chainsettings, "coefOfExternalForces",slider=True)
		col2.prop(re_chain_chainsettings, "stretchInteractionRatio",slider=True)
		col2.prop(re_chain_chainsettings, "angleLimitInteractionRatio",slider=True)
		
			
		col2.prop(re_chain_chainsettings, "motionForce")
		if object.parent == None or object.parent.get("TYPE",None) != "RE_CHAIN_WINDSETTINGS":
			col2.prop(re_chain_chainsettings, "fileWindID")
		if isChain2:
			col2.prop(re_chain_chainsettings, "motionForceCalcType")
			col2.prop(re_chain_chainsettings, "elasticLimit")
		row = col2.row()
		#Greyed when nothing reads it; the line under it says what does
		from .re_chain_propertyGroups import groupDefaultAttrUses
		groups, links = groupDefaultAttrUses(object)
		links = links and isChain2
		row.active = bool(groups or links)
		row.prop(re_chain_chainsettings, "groupDefaultAttr")
		row.operator("re_chain.set_attr_flags",icon='DOWNARROW_HLT', text="")
		uses = ([f"{groups} group(s) with Collision from Setting"] if groups else []) + (["the link collisions"] if links else [])
		note = col2.row()
		note.alignment = 'RIGHT'
		note.label(text=("Read by " + " and ".join(uses)) if uses else "Not read: no group with Collision from Setting uses this setting" + (", and it is not the links' setting" if isChain2 else ""))
		col2.prop(re_chain_chainsettings, "windDelayType")
		#Greyed: only Wind Delay Type Manual reads it
		greyed(col2,not isChain2 or re_chain_chainsettings.windDelayType == "2").prop(re_chain_chainsettings, "windDelaySpeed")
		col2.prop(re_chain_chainsettings, "windEffectCoef",slider=True)
		col2.prop(re_chain_chainsettings, "envWindEffectCoef",slider=True)
		col2.prop(re_chain_chainsettings, "velocityLimit")
		col2.prop(re_chain_chainsettings, "hardness",slider=True)
class OBJECT_PT_ChainSettingsSubDataPanel(Panel):
	bl_label = "Settings Sub Data"
	bl_idname = "OBJECT_PT_chain_settings_subdata_panel"
	bl_parent_id = "OBJECT_PT_chain_settings_panel"  # Specify the ID of the parent panel
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_options = {'DEFAULT_CLOSED'}
	def draw(self, context):
		layout = self.layout
		object = context.active_object
		re_chain_chainsettings = object.re_chain_chainsettings
		
		split = layout.split(factor=0.025)#Indent list slightly to make it more clear it's a part of a sub panel
		col1 = split.column()
		col2 = split.column()
		col2.label(text = f"Chain2 version 12 (MH Wilds) and above only")
		col2.prop(re_chain_chainsettings,"unknQuaternion")
		col2.prop(re_chain_chainsettings,"unknPos")
		col2.label(text = f"Sub Data Count: {str(len(object.re_chain_chainsettings.subDataList_items))}")

		col2.template_list(
			listtype_name = "CHAIN_UL_ChainSettingsSubDataList", 
			list_id = "",
			dataptr = re_chain_chainsettings,
			propname = "subDataList_items",
			active_dataptr = re_chain_chainsettings, 
			active_propname = "subDataList_index",
			rows = 4,
			type='DEFAULT'
			)
	@classmethod
	def poll(self,context):
		
		return context and context.scene.re_chain_toolpanel.chainFileType == "chain2"
class OBJECT_PT_ChainGroupPanel(Panel):
	bl_label = "RE Chain Group Settings"
	bl_idname = "OBJECT_PT_chain_group_panel"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_category = "RE Chain Group Settings"
	bl_context = "object"


	@classmethod
	def poll(self,context):
		
		return context and context.object.mode == "OBJECT" and context.active_object.get("TYPE",None) == "RE_CHAIN_CHAINGROUP"

	def draw(self, context):
		layout = self.layout
		object = context.active_object
		re_chain_chaingroup = object.re_chain_chaingroup
		
		split = layout.split(factor=0.01)
		col1 = split.column()
		col2 = split.column()
		col2.alignment='RIGHT'
		col2.use_property_split = True
		
		col2.prop(re_chain_chaingroup, "rotationOrder")
		if object.get("windIDFromFile",False) or object.parent == None or object.parent.parent == None or object.parent.parent.get("TYPE",None) != "RE_CHAIN_WINDSETTINGS":
			#Greyed: Wind from Setting takes the setting's wind ID
			isChain2 = context.scene.re_chain_toolpanel.chainFileType == "chain2"
			greyed(col2,not (isChain2 and re_chain_chaingroup.attrFlags & 0x400)).prop(re_chain_chaingroup, "fileWindID")
		row = col2.row()
		row.prop(re_chain_chaingroup, "attrFlags")
		row.operator("re_chain.set_attr_flags",icon='DOWNARROW_HLT', text="")
		
		col2.prop(re_chain_chaingroup, "dampingNoise0")
		col2.prop(re_chain_chaingroup, "dampingNoise1")
		col2.prop(re_chain_chaingroup, "endRotConstMax")
		col2.prop(re_chain_chaingroup, "angleLimitDirectionMode")
		
		if context.scene.re_chain_toolpanel.chainFileType == "chain":
			col2.prop(re_chain_chaingroup, "extraNodeLocalPos")
			col2.prop(re_chain_chaingroup, "collisionFilterFlags")
		else:#chain2
			col2.prop(re_chain_chaingroup, "interpCount")
			col2.prop(re_chain_chaingroup, "nodeInterpolationMode")
		
		col2.prop(re_chain_chaingroup, "colliderQualityLevel")
		row = col2.row()
		row.prop(re_chain_chaingroup, "clspFlags0")
		row.operator("re_chain.set_bit_flags",icon='DOWNARROW_HLT', text="").target = "re_chain_chaingroup.clspFlags0"
		col2.prop(re_chain_chaingroup, "clspFlags1")
		if context.scene.re_chain_toolpanel.chainFileType == "chain":
			note = col2.row()
			note.alignment = 'RIGHT'
			note.label(text="CLSP Flags: only games with CLSP files (Dragon's Dogma 2, Pragmata); RE4 and older have none")

		col2.prop(re_chain_chaingroup, "autoBlendCheckNodeNo")
		col2.prop(re_chain_chaingroup, "tagCount")
		col2.prop(re_chain_chaingroup, "tag0")
		col2.prop(re_chain_chaingroup, "tag1")
		col2.prop(re_chain_chaingroup, "tag2")
		col2.prop(re_chain_chaingroup, "tag3")
		
		col2.prop(re_chain_chaingroup, "hierarchyHash0")
		col2.prop(re_chain_chaingroup, "hierarchyHash1")
		col2.prop(re_chain_chaingroup, "hierarchyHash2")
		col2.prop(re_chain_chaingroup, "hierarchyHash3")

class OBJECT_PT_ChainSubGroupPanel(Panel):
	bl_label = "RE Chain Sub Group Settings"
	bl_idname = "OBJECT_PT_chain_sub_group_panel"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_category = "RE Chain Sub Group Settings"
	bl_context = "object"


	@classmethod
	def poll(self,context):
		
		return context and context.object.mode == "OBJECT" and context.active_object.get("TYPE",None) == "RE_CHAIN_SUBGROUP"

	def draw(self, context):
		layout = self.layout
		object = context.active_object
		re_chain_chainsubgroup = object.re_chain_chainsubgroup
		
		split = layout.split(factor=0.01)
		col1 = split.column()
		col2 = split.column()
		col2.alignment='RIGHT'
		col2.use_property_split = True
		
		col2.prop(re_chain_chainsubgroup, "subGroupID")
		col2.prop(re_chain_chainsubgroup, "parentGroup")
		


class OBJECT_PT_ChainNodePanel(Panel):
	bl_label = "RE Chain Node Settings"
	bl_idname = "OBJECT_PT_chain_node_panel"
	bl_space_type = "PROPERTIES"   
	bl_region_type = "WINDOW"
	bl_category = "RE Chain Node Settings"
	bl_context = "object"


	@classmethod
	def poll(self,context):
		
		return context and context.object.mode == "OBJECT" and context.active_object.get("TYPE",None) == "RE_CHAIN_NODE"

	def draw(self, context):
		layout = self.layout
		object = context.active_object
		re_chain_chainnode = object.re_chain_chainnode
		split = layout.split(factor=0.01)
		col1 = split.column()
		col2 = split.column()
		col2.alignment='RIGHT'
		col2.use_property_split = True
		#MH Wilds: greyed when the group's switches or the node's modes keep a field from doing anything
		isChain2 = context.scene.re_chain_toolpanel.chainFileType == "chain2"
		group = chainGroupOfNode(object)
		groupAttr = group.re_chain_chaingroup.attrFlags if group != None else 0x2
		mode = re_chain_chainnode.angleMode
		angleOn = not isChain2 or (groupAttr & 0x2 and not groupAttr & 0x2000 and mode != "0")
		greyed(col2,angleOn).prop(re_chain_chainnode, "angleLimitRad")
		greyed(col2,angleOn and (not isChain2 or mode in ("3","4"))).prop(re_chain_chainnode, "angleLimitDistance",slider = True)
		bounceOn = angleOn and (not isChain2 or (mode == "2" and groupAttr & 0x1000))
		greyed(col2,bounceOn).prop(re_chain_chainnode, "angleLimitRestitution")
		greyed(col2,bounceOn).prop(re_chain_chainnode, "angleLimitRestituteStopSpeed")
		col2.prop(re_chain_chainnode, "collisionRadius")
		col2.prop(re_chain_chainnode, "collisionFilterFlags")
		capsuleOn = not isChain2 or re_chain_chainnode.collisionShape == "2"
		greyed(col2,capsuleOn).prop(re_chain_chainnode, "capsuleStretchRate0",slider = True)
		greyed(col2,capsuleOn).prop(re_chain_chainnode, "capsuleStretchRate1",slider = True)
		row = col2.row()
		row.prop(re_chain_chainnode, "attrFlags")
		row.operator("re_chain.set_node_attr_flags",icon='DOWNARROW_HLT', text="")
		col2.prop(re_chain_chainnode, "windCoef",slider = True)
		greyed(col2,not isChain2 or (groupAttr & 0x2 and not groupAttr & 0x2000)).prop(re_chain_chainnode, "angleMode")
		col2.prop(re_chain_chainnode, "collisionShape")
		col2.prop(re_chain_chainnode, "attachType")
		col2.prop(re_chain_chainnode, "rotationType")
		#col2.prop(re_chain_chainnode, "jiggleData")
		col2.prop(re_chain_chainnode, "gravityCoef")
		col2.prop(re_chain_chainnode, "constraintJntName")
		#if version >= 35:
		
		if context.scene.re_chain_toolpanel.chainFileType == "chain2":
			col2.prop(re_chain_chainnode, "jointHash")
			col2.prop(re_chain_chainnode, "basePos")


class OBJECT_PT_ChainJigglePanel(Panel):
	bl_label = "RE Chain Jiggle Settings"
	bl_idname = "OBJECT_PT_chain_jiggle_panel"
	bl_space_type = "PROPERTIES"   
	bl_region_type = "WINDOW"
	bl_category = "RE Chain Jiggle Settings"
	bl_context = "object"


	@classmethod
	def poll(self,context):
		
		return context and context.object.mode == "OBJECT" and context.active_object.get("TYPE",None) == "RE_CHAIN_JIGGLE"

	def draw(self, context):
		layout = self.layout
		object = context.active_object
		re_chain_chainjiggle = object.re_chain_chainjiggle
		split = layout.split(factor=0.01)
		col1 = split.column()
		col2 = split.column()
		col2.alignment='RIGHT'
		col2.use_property_split = True
		#col2.prop(re_chain_chainjiggle, "range")
		#col2.prop(re_chain_chainjiggle, "rangeOffset") 
		#col2.prop(re_chain_chainjiggle, "rangeAxis")
		col2.prop(re_chain_chainjiggle, "rangeShape")
		col2.prop(re_chain_chainjiggle, "springForce",slider = True)
		col2.prop(re_chain_chainjiggle, "gravityCoef",slider = True)
		col2.prop(re_chain_chainjiggle, "windCoef",slider = True)
		col2.prop(re_chain_chainjiggle, "damping",slider = True)
		row = col2.row()
		row.prop(re_chain_chainjiggle, "attrFlags")
		row.operator("re_chain.set_jiggle_attr_flags",icon='DOWNARROW_HLT', text="")
		
class OBJECT_PT_ChainCollisionPanel(Panel):
	bl_label = "RE Chain Collision Settings"
	bl_idname = "OBJECT_PT_chain_collision_panel"
	bl_space_type = "PROPERTIES"   
	bl_region_type = "WINDOW"
	bl_category = "RE Chain Collision Settings"
	bl_context = "object"


	@classmethod
	def poll(self,context):
		
		return context and context.object.mode == "OBJECT" and (context.active_object.get("TYPE",None) == "RE_CHAIN_COLLISION_SINGLE" or context.active_object.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_ROOT")

	def draw(self, context):
		layout = self.layout
		object = context.active_object
		re_chain_chaincollision = object.re_chain_chaincollision
		
		split = layout.split(factor=0.01)
		col1 = split.column()
		col2 = split.column()
		col2.alignment='RIGHT'
		col2.use_property_split = True
		#if version >= 48:
		col2.prop(re_chain_chaincollision, "rotationOrder")
		col2.prop(re_chain_chaincollision, "radius")
		col2.prop(re_chain_chaincollision, "collisionOffset")
		col2.prop(re_chain_chaincollision, "endCollisionOffset")	
		col2.prop(re_chain_chaincollision, "endRadius")
		#if version >= 48:
		col2.prop(re_chain_chaincollision, "lerp") 
		col2.prop(re_chain_chaincollision, "chainCollisionShape")
		col2.prop(re_chain_chaincollision, "subDataCount")
		col2.prop(re_chain_chaincollision, "collisionFilterFlags")
		#col2.prop(re_chain_chaincollision, "subDataFlag")
		
		#A chain or chain2 collision record has no CLSP mask: these are written only by the clsp export
		inChain = isChainCollision(object)
		greyed(col2,not inChain).prop(re_chain_chaincollision, "clspBitFlag0")
		greyed(col2,not inChain).prop(re_chain_chaincollision, "clspBitFlag1")
		if inChain:
			note = col2.row()
			note.alignment = 'RIGHT'
			note.label(text="CLSP Flags only available on clsp")
		
class OBJECT_PT_ChainCollisionSubDataPanel(Panel):
	bl_label = "RE Chain Collision Subdata Settings"
	bl_idname = "OBJECT_PT_chain_collision_subdata_panel"
	bl_space_type = "PROPERTIES"   
	bl_region_type = "WINDOW"
	bl_category = "RE Chain Collision Subdata Settings"
	bl_context = "object"


	@classmethod
	def poll(self,context):
		
		return context and context.object.mode == "OBJECT" and ((context.active_object.get("TYPE",None) == "RE_CHAIN_COLLISION_SINGLE" or context.active_object.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_ROOT") and context.active_object.re_chain_chaincollision.subDataCount == 1)

	def draw(self, context):
		layout = self.layout
		object = context.active_object
		re_chain_collision_subdata = object.re_chain_collision_subdata
		
		split = layout.split(factor=0.01)
		col1 = split.column()
		col2 = split.column()
		col2.alignment='RIGHT'
		col2.use_property_split = True
		col2.prop(re_chain_collision_subdata, "pos")
		col2.prop(re_chain_collision_subdata, "pairPos")
		col2.prop(re_chain_collision_subdata, "rotOffset")	
		col2.prop(re_chain_collision_subdata, "radius")
		col2.prop(re_chain_collision_subdata, "id")
		col2.prop(re_chain_collision_subdata, "unknSubCollisionData0")
		col2.prop(re_chain_collision_subdata, "unknSubCollisionData1")
		col2.prop(re_chain_collision_subdata, "unknSubCollisionData2")
		col2.prop(re_chain_collision_subdata, "unknSubCollisionData3")
		
class OBJECT_PT_ChainLinkPanel(Panel):
	bl_label = "RE Chain Link Settings"
	bl_idname = "OBJECT_PT_chain_link_panel"
	bl_space_type = "PROPERTIES"   
	bl_region_type = "WINDOW"
	bl_category = "RE Chain Link Settings"
	bl_context = "object"


	@classmethod
	def poll(self,context):
		
		return context and context.object.mode == "OBJECT" and context.active_object.get("TYPE",None) == "RE_CHAIN_LINK"

	def draw(self, context):
		layout = self.layout
		object = context.active_object
		re_chain_chainlink = object.re_chain_chainlink
		
		split = layout.split(factor=0.01)
		col1 = split.column()
		col2 = split.column()
		col2.alignment='RIGHT'
		col2.use_property_split = True
		col2.prop_search(re_chain_chainlink, "chainGroupAObject",bpy.context.scene,"objects")
		col2.prop_search(re_chain_chainlink, "chainGroupBObject",bpy.context.scene,"objects")
		#Greyed: Link Mode Off builds no link; the coefficients need Stretch Range in Link Attribute Flags
		isChain2 = context.scene.re_chain_toolpanel.chainFileType == "chain2"
		linkOn = not isChain2 or re_chain_chainlink.linkMode in ("0","1")
		stretchOn = not isChain2 or (linkOn and re_chain_chainlink.linkAttrFlags & 0x1)
		greyed(col2,stretchOn).prop(re_chain_chainlink, "distanceShrinkLimitCoef")
		greyed(col2,stretchOn).prop(re_chain_chainlink, "distanceExpandLimitCoef")
		col2.prop(re_chain_chainlink, "linkMode")
		from .re_chain_propertyGroups import linkCollisionNodePairs,linkCollisionObjects,linkCollisionSetting,LINK_COLLISION_FLAGS
		linkCol = greyed(col2,linkOn)
		row = linkCol.row()
		row.prop(re_chain_chainlink, "connectFlagBits")
		row.operator("re_chain.set_bit_flags",icon='DOWNARROW_HLT', text="").target = "re_chain_chainlink.connectFlagBits"
		row = linkCol.row()
		row.prop(re_chain_chainlink, "linkAttrFlags")
		row.operator("re_chain.set_bit_flags",icon='DOWNARROW_HLT', text="").target = "re_chain_chainlink.linkAttrFlags"
		linkCol.prop(re_chain_chainlink, "skipGroupA")
		linkCol.prop(re_chain_chainlink, "skipGroupB")
		linkCol.prop(re_chain_chainlink, "linkOrder")
		if bpy.context.scene.re_chain_toolpanel.chainFileType == "chain2":
			#Greyed: the setting's Scene Colliders switch is off, so the CLSP mask is not used
			header, setting = linkCollisionSetting(object)
			sceneOn = setting == None or setting.re_chain_chainsettings.groupDefaultAttr & 0x10000
			row = greyed(linkCol,sceneOn).row()
			row.prop(re_chain_chainlink, "clspFlags0")
			row.operator("re_chain.set_bit_flags",icon='DOWNARROW_HLT', text="").target = "re_chain_chainlink.clspFlags0"
			greyed(linkCol,sceneOn).prop(re_chain_chainlink, "clspFlags1")
		box = layout.box()
		from .re_chain_names import flagLabel
		box.label(text="As MH Wilds builds this link (read only):")
		pairs = linkCollisionNodePairs(object)
		colCount = len(linkCollisionObjects(object))
		if re_chain_chainlink.linkMode not in ("0","1"):
			box.label(text="Link Mode Off: the game builds no link", icon="ERROR")
		else:
			box.label(text=f"{len(pairs)} straight pairs, {colCount} link collisions")
			if colCount == 0:
				box.label(text="No link collisions: the link only keeps the node distances")
			elif colCount < len(pairs):
				box.label(text=f"Only the first {colCount} pairs are used (one per link collision)")
		if not re_chain_chainlink.connectFlagBits & 1:
			box.label(text="No straight pairs in Connection Flags: the link collisions do nothing", icon="ERROR")
		if bpy.context.scene.re_chain_toolpanel.chainFileType == "chain2":
			header, setting = linkCollisionSetting(object)
			if setting == None:
				box.label(text="No chain setting at the header's Default Setting Index", icon="ERROR")
			else:
				attr = setting.re_chain_chainsettings.groupDefaultAttr
				box.label(text=f"Collision switches, from {setting.name} (the header's Default Setting Index):")
				for bit,key in LINK_COLLISION_FLAGS:
					row = box.split(factor=0.6)
					row.label(text=f"    {flagLabel(key)}")
					row.label(text="On" if attr & bit else "Off")
				box.label(text=f"Change them in the Group Default Attribute of {setting.name}")

class OBJECT_PT_ChainLinkCollisionPanel(Panel):
	bl_label = "RE Chain Link Collision Settings"
	bl_idname = "OBJECT_PT_chain_link_collision_panel"
	bl_space_type = "PROPERTIES"   
	bl_region_type = "WINDOW"
	bl_category = "RE Chain Link Collision Settings"
	bl_context = "object"


	@classmethod
	def poll(self,context):
		
		return context and context.object.mode == "OBJECT" and context.active_object.get("TYPE",None) == "RE_CHAIN_LINK_COLLISION"

	def draw(self, context):
		layout = self.layout
		object = context.active_object
		re_chain_chainlink = object.re_chain_chainlink_collision
		
		split = layout.split(factor=0.01)
		col1 = split.column()
		col2 = split.column()
		col2.alignment='RIGHT'
		col2.use_property_split = True
		col2.prop(re_chain_chainlink, "collisionRadius")
		col2.prop(re_chain_chainlink, "collisionFilterFlags") 

class OBJECT_PT_ChainVisibilityPanel(Panel):
	bl_label = "RE Chain: Visibility"
	bl_idname = "OBJECT_PT_chain_visibility_panel"
	bl_space_type = "VIEW_3D"   
	bl_region_type = "UI"
	bl_category = "RE Chain"   
	bl_context = "objectmode"
	bl_options = {'DEFAULT_CLOSED'}
	@classmethod
	def poll(self,context):
		return context is not None and "HIDE_RE_CHAIN_EDITOR_TAB" not in context.scene

	def draw(self, context):
		re_chain_toolpanel = context.scene.re_chain_toolpanel
		layout = self.layout
		layout.operator("re_chain.redraw_all_chains",icon = "FILE_REFRESH")
		layout.operator("re_chain.hide_non_nodes")
		layout.operator("re_chain.hide_non_angle_limits")
		layout.operator("re_chain.hide_non_collisions")
		layout.operator("re_chain.unhide_all")
		layout.operator("re_chain.refresh_link_collisions")
		
		
class OBJECT_PT_NodeVisPanel(Panel):
	bl_label = "Chain Node Settings"
	bl_idname = "OBJECT_PT_chain_node_vis_panel"
	bl_parent_id = "OBJECT_PT_chain_visibility_panel"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_options = {'DEFAULT_CLOSED'}
	def draw(self, context):
		layout = self.layout
		obj = context.active_object
		re_chain_toolpanel = context.scene.re_chain_toolpanel
		layout.prop(re_chain_toolpanel, "showRelationLines")
		layout.prop(re_chain_toolpanel, "showNodeNames")
		layout.prop(re_chain_toolpanel, "drawNodesThroughObjects")
		layout.prop(re_chain_toolpanel, "drawChainGroupsThroughObjects")
		layout.prop(re_chain_toolpanel, "groupDisplaySize")
		
class OBJECT_PT_CollisionVisPanel(Panel):
	bl_label = "Collision Settings"
	bl_idname = "OBJECT_PT_chain_collision_vis_panel"
	bl_parent_id = "OBJECT_PT_chain_visibility_panel"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_options = {'DEFAULT_CLOSED'}
	def draw(self, context):
		layout = self.layout
		obj = context.active_object
		re_chain_toolpanel = context.scene.re_chain_toolpanel
		
		layout.prop(re_chain_toolpanel, "showCollisionNames")
		layout.prop(re_chain_toolpanel, "drawCollisionsThroughObjects")
		layout.prop(re_chain_toolpanel, "drawCapsuleHandlesThroughObjects")
		layout.prop(re_chain_toolpanel, "drawLinkCollisionsThroughObjects")
		
class OBJECT_PT_AngleLimitVisPanel(Panel):
	bl_label = "Angle Limit Settings"
	bl_idname = "OBJECT_PT_chain_angle_limit_vis_panel"
	bl_parent_id = "OBJECT_PT_chain_visibility_panel"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_options = {'DEFAULT_CLOSED'}
	def draw(self, context):
		layout = self.layout
		obj = context.active_object
		re_chain_toolpanel = context.scene.re_chain_toolpanel
		layout.prop(re_chain_toolpanel, "showAngleLimitCones")
		layout.prop(re_chain_toolpanel, "drawConesThroughObjects")
		layout.prop(re_chain_toolpanel, "hideLastNodeAngleLimit")
		layout.prop(re_chain_toolpanel, "angleLimitDisplaySize")
		layout.prop(re_chain_toolpanel, "coneDisplaySize")
		layout.operator("re_chain.fix_angle_limit_frames")
		
class OBJECT_PT_ColorVisPanel(Panel):
	bl_label = "Color Settings"
	bl_idname = "OBJECT_PT_chain_color_vis_panel"
	bl_parent_id = "OBJECT_PT_chain_visibility_panel"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_options = {'DEFAULT_CLOSED'}
	def draw(self, context):
		layout = self.layout
		obj = context.active_object
		re_chain_toolpanel = context.scene.re_chain_toolpanel
		
		layout.prop(re_chain_toolpanel, "collisionColor")
		layout.prop(re_chain_toolpanel, "chainLinkColor")
		layout.prop(re_chain_toolpanel, "chainLinkCollisionColor")
		layout.prop(re_chain_toolpanel, "coneColor")
		layout.prop(re_chain_toolpanel, "coneSubGroupColor")
		layout.prop(re_chain_toolpanel, "chainGroupColor")