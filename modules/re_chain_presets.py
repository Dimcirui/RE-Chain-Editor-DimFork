#Author: NSA Cloud
import json
import os
import re
import bpy

from .gen_functions import textColors,raiseWarning
from .blender_utils import showErrorMessageBox
#from .blender_re_chain import findHeaderObj

def findHeaderObj():
	if bpy.data.collections.get("chainData",None) != None:
		objList = bpy.data.collections["chainData"].all_objects
		headerList = [obj for obj in objList if obj.get("TYPE",None) == "RE_CHAIN_HEADER"]
		if len(headerList) >= 1:
			return headerList[0]
		else:
			return None
PRESET_VERSION = 6#To be changed when there are changes to chain object variables
skipKeys = set(["subDataList_items"])

#chain and chain2 put the group attribute flags on different bits (Scene Colliders is 0x20000 in chain, 0x10000 in
#chain2, where chain has Enabled Scale Animation). Presets without chainFileType are told apart by keys only one format sets
FORMAT_KEYS = {"RE_CHAIN_CHAINSETTINGS":("muzzleDirection","motionForceCalcType"),"RE_CHAIN_CHAINGROUP":("extraNodeLocalPos","interpCount")}
GROUP_ATTR_KEYS = {"RE_CHAIN_CHAINSETTINGS":"groupDefaultAttr","RE_CHAIN_CHAINGROUP":"attrFlags"}

def presetFileType(values,objType,presetDict = None):
	"""The chain format (chain or chain2) the preset values were saved from, or None when it can't be told."""
	presetDict = presetDict if presetDict != None else values
	if presetDict.get("chainFileType",None) in ("chain","chain2"):
		return presetDict["chainFileType"]
	if "chainVersion" in presetDict:
		return "chain"
	if objType in FORMAT_KEYS:
		chainKey, chain2Key = FORMAT_KEYS[objType]
		if chainKey in values and chain2Key not in values:
			return "chain"
		if chain2Key in values and chainKey not in values:
			return "chain2"
	return None

def remapGroupAttr(value,fromType,toType):
	"""Moves each group attribute flag to its bit in the other format. A flag the other format lacks is dropped, a bit
	neither format names is kept."""
	from .re_chain_operators import chainGroupAttrFlags,chain2GroupAttrFlags
	source = (chain2GroupAttrFlags() if fromType == "chain2" else chainGroupAttrFlags()).flagDict
	target = (chain2GroupAttrFlags() if toType == "chain2" else chainGroupAttrFlags()).flagDict
	value &= 0xFFFFFFFF
	known = 0
	result = 0
	for key,flag in source.items():
		if value & flag["andFlag"]:
			known |= flag["andFlag"]
			if key in target:
				result |= target[key]["andFlag"]
	return result | (value & ~known)

def convertPresetGroupAttr(propertyGroup,objType,fromType):
	toType = bpy.context.scene.re_chain_toolpanel.chainFileType
	key = GROUP_ATTR_KEYS.get(objType,None)
	if key == None or fromType == None or fromType == toType:
		return
	value = getattr(propertyGroup,key)
	newValue = remapGroupAttr(value,fromType,toType)
	if newValue != value:
		setattr(propertyGroup,key,newValue)
		print(f"Moved {key} from the {fromType} flag layout to {toType}: {value} -> {newValue}")
def saveAsPreset(selection,presetName):
	if len(selection) > 1:
		return saveChainPreset(selection,presetName)
	if len(selection) == 1:
		activeObj = selection[0]
		chainObjType = activeObj.get("TYPE",None)
		if not re.search(r'^[\w,\s-]+\.[A-Za-z]{3}$',presetName) and not ".." in presetName:#Check that the preset name contains no invalid characters for a file name
			presetDict = {}
			folderPath = None
			variableList = []
			presetDict["presetVersion"] = PRESET_VERSION
			if chainObjType == "RE_CHAIN_WINDSETTINGS":
				folderPath = "WindSettings"
				presetDict["presetType"] = "RE_CHAIN_WINDSETTINGS"
				variableList = activeObj.re_chain_windsettings.items()
					
			elif chainObjType == "RE_CHAIN_CHAINSETTINGS":
				folderPath = "ChainSettings"
				presetDict["presetType"] = "RE_CHAIN_CHAINSETTINGS"
				variableList = activeObj.re_chain_chainsettings.items()
				presetDict["subDataValues"] = []#Manual subdata support
				for item in activeObj.re_chain_chainsettings.subDataList_items:
					presetDict["subDataValues"].append([v for v in item.values])
				
			elif chainObjType == "RE_CHAIN_CHAINGROUP":
				folderPath = "ChainGroup"
				presetDict["presetType"] = "RE_CHAIN_CHAINGROUP"
				variableList = activeObj.re_chain_chaingroup.items()
					
			elif chainObjType == "RE_CHAIN_NODE":
				folderPath = "ChainNode"
				presetDict["presetType"] = "RE_CHAIN_NODE"
				variableList = activeObj.re_chain_chainnode.items()
			else:
				showErrorMessageBox("Selected object can not be made into a preset.")
			
			if variableList != []:
				for key, value in variableList:
					if key not in skipKeys:
						if type(value).__name__ == "IDPropertyArray":
							presetDict[key] = value.to_list()
						else:
							presetDict[key] = value
				
				#Find chain header in scene and get the version
				chainHeader = findHeaderObj()
				if chainHeader != None:
					presetDict["chainVersion"] = chainHeader.re_chain_header.version
				presetDict["chainFileType"] = bpy.context.scene.re_chain_toolpanel.chainFileType
				presetDict["presetVersion"] = PRESET_VERSION
				jsonPath = os.path.join(os.path.dirname(os.path.split(os.path.abspath(__file__))[0]),"Presets",folderPath,presetName+".json")
				#print(presetDict)#debug
				try:
					os.makedirs(os.path.split(jsonPath)[0])
				except:
					pass
				with open(jsonPath, 'w', encoding='utf-8') as f:
					json.dump(presetDict, f, ensure_ascii=False, indent=4)
					print(textColors.OKGREEN+"Saved preset to " + str(jsonPath) + textColors.ENDC)
					return True
		else:
			showErrorMessageBox("Invalid preset file name. ")
	else:
		showErrorMessageBox("A chain object must be selected when saving a preset.")
		

def readPresetJSON(filepath,activeObj):
		try:
			with open(filepath) as jsonFile:
				jsonDict = json.load(jsonFile)
				if jsonDict["presetVersion"] > PRESET_VERSION:
					showErrorMessageBox("Preset was created in a newer version and cannot be used. Update to the latest version of the chain importer.")
					return False
				
		except Exception as err:
			showErrorMessageBox("Failed to read json file. \n" + str(err))
			return False
		
		if jsonDict["presetType"] != activeObj.get("TYPE",None):
			showErrorMessageBox("Preset type does not match selected object")
			return False
		propertyGroup = {}
		if jsonDict["presetType"] == "RE_CHAIN_WINDSETTINGS":
			propertyGroup = activeObj.re_chain_windsettings
				
		elif jsonDict["presetType"] == "RE_CHAIN_CHAINSETTINGS":
			if jsonDict["presetVersion"] < 6:
				#Fix keys changed in update
				if "unknChainSettingValue0" in jsonDict:
					jsonDict["windDelaySpeed"] = jsonDict["unknChainSettingValue0"]
				if "unknChainSettingValue1" in jsonDict:
					jsonDict["envWindEffectCoef"] = jsonDict["unknChainSettingValue1"]
				if "unknChainSettingValue2" in jsonDict:
					jsonDict["motionForce"] = jsonDict["unknChainSettingValue2"]
				
			
			propertyGroup = activeObj.re_chain_chainsettings
			if "subDataValues" in jsonDict:
				activeObj.re_chain_chainsettings.subDataList_items.clear()
				for entry in jsonDict["subDataValues"]:
					item = activeObj.re_chain_chainsettings.subDataList_items.add()
					for index, val in enumerate(entry[:len(item.values)]):
						if isinstance(val, int):
							item.values[index] = val
							
		elif jsonDict["presetType"] == "RE_CHAIN_CHAINGROUP":
			propertyGroup = activeObj.re_chain_chaingroup
			
		elif jsonDict["presetType"] == "RE_CHAIN_NODE":
			propertyGroup = activeObj.re_chain_chainnode
			if jsonDict["presetVersion"] < 6:
				#Fix keys changed in update
				if "unknChainNodeValue0" in jsonDict:
					jsonDict["gravityCoef"] = jsonDict["unknChainNodeValue0"]
		else:
			showErrorMessageBox("Preset type is not supported")
			return False
		print("Applying preset to " + activeObj.name)
		chainVersion = jsonDict.get("chainVersion",None)
		if chainVersion != None:
			#Find chain header in scene and get the version
			chainHeader = findHeaderObj()
			if chainHeader != None:
				if str(chainVersion) != str(chainHeader.re_chain_header.version):
					raiseWarning("Preset was created for chain version " + str(chainVersion)+ " while the current file is version " +str(chainHeader.re_chain_header.version)+".")
			else:
				raiseWarning("No chain header in scene, can't compare preset chain version to current file.")
		else:
			raiseWarning("Preset is missing the chain version.")
		for key in propertyGroup.keys():
			if key not in skipKeys:
				try:
					propertyGroup[key] = jsonDict[key]
				except:
					raiseWarning("Preset is missing key " + str(key) +", cannot set value on active object.")
		convertPresetGroupAttr(propertyGroup,jsonDict["presetType"],presetFileType(jsonDict,jsonDict["presetType"]))
		return True
#Kept per folder: Blender shows garbage for dynamic enum strings Python has freed (non-ASCII preset names)
PRESET_LISTS = {}
def reloadPresets(folderPath):
	presetsPath = os.path.join(os.path.dirname(os.path.split(os.path.abspath(__file__))[0]),"Presets")
	presetList = []
	PRESET_LISTS[folderPath] = presetList
	relPathStart = os.path.join(presetsPath,folderPath)
	if os.path.exists(relPathStart):
		for entry in os.scandir(relPathStart):
			if entry.name.endswith(".json") and entry.is_file():
				presetList.append((os.path.relpath(os.path.join(relPathStart,entry),start = presetsPath),os.path.splitext(entry.name)[0],""))
	#print("Loading " + folderPath + " presets...")
	#print("DEBUG:" + str(presetList)+"\n")#debug
	return presetList


#Chain presets: a chain setting, a chain group and a chain node saved together (Presets/Chain), each applied to the
#selected objects of its type. Files saved by MHWilds Chain Editor (Presets/ChainPresets, no presetType) read the same
CHAIN_PRESET_GROUPS = {"RE_CHAIN_CHAINSETTINGS":"re_chain_chainsettings","RE_CHAIN_CHAINGROUP":"re_chain_chaingroup","RE_CHAIN_NODE":"re_chain_chainnode"}

def _presetValues(propertyGroup):
	values = {}
	for key, value in propertyGroup.items():
		if key not in skipKeys:
			values[key] = value.to_list() if type(value).__name__ == "IDPropertyArray" else value
	return values

def saveChainPreset(selection,presetName):
	if re.search(r'^[\w,\s-]+\.[A-Za-z]{3}$',presetName) or ".." in presetName:
		showErrorMessageBox("Invalid preset file name. ")
		return False
	presetDict = {"presetVersion":PRESET_VERSION,"presetType":"RE_CHAIN_CHAIN","chainFileType":bpy.context.scene.re_chain_toolpanel.chainFileType}
	for obj in selection:
		objType = obj.get("TYPE",None)
		if objType in CHAIN_PRESET_GROUPS and objType not in presetDict:
			presetDict[objType] = _presetValues(getattr(obj,CHAIN_PRESET_GROUPS[objType]))
			if objType == "RE_CHAIN_CHAINSETTINGS":
				presetDict[objType]["subDataValues"] = [[v for v in item.values] for item in obj.re_chain_chainsettings.subDataList_items]
			#A chain group alone also gives its first node
			if objType == "RE_CHAIN_CHAINGROUP" and "RE_CHAIN_NODE" not in presetDict:
				node = next((child for child in obj.children if child.get("TYPE",None) == "RE_CHAIN_NODE"),None)
				if node != None and not any(o.get("TYPE",None) == "RE_CHAIN_NODE" for o in selection):
					presetDict["RE_CHAIN_NODE"] = _presetValues(node.re_chain_chainnode)
	if not any(key in presetDict for key in CHAIN_PRESET_GROUPS):
		showErrorMessageBox("Select a chain setting, a chain group or a chain node to save a chain preset.")
		return False
	chainHeader = findHeaderObj()
	if chainHeader != None:
		presetDict["chainVersion"] = chainHeader.re_chain_header.version
	jsonPath = os.path.join(os.path.dirname(os.path.split(os.path.abspath(__file__))[0]),"Presets","Chain",presetName+".json")
	os.makedirs(os.path.split(jsonPath)[0],exist_ok=True)
	with open(jsonPath, 'w', encoding='utf-8') as f:
		json.dump(presetDict, f, ensure_ascii=False, indent=4)
	print(textColors.OKGREEN+"Saved chain preset to " + str(jsonPath) + textColors.ENDC)
	return True

def readChainPresetJSON(filepath,selection):
	try:
		with open(filepath, encoding='utf-8') as jsonFile:
			jsonDict = json.load(jsonFile)
	except Exception as err:
		showErrorMessageBox("Failed to read json file. \n" + str(err))
		return False
	if jsonDict.get("presetVersion",0) > PRESET_VERSION:
		showErrorMessageBox("Preset was created in a newer version and cannot be used. Update to the latest version of the chain importer.")
		return False
	applied = 0
	for obj in selection:
		objType = obj.get("TYPE",None)
		if objType not in CHAIN_PRESET_GROUPS or objType not in jsonDict:
			continue
		values = jsonDict[objType]
		propertyGroup = getattr(obj,CHAIN_PRESET_GROUPS[objType])
		if objType == "RE_CHAIN_CHAINSETTINGS" and "subDataValues" in values:
			propertyGroup.subDataList_items.clear()
			for entry in values["subDataValues"]:
				item = propertyGroup.subDataList_items.add()
				for index, val in enumerate(entry[:len(item.values)]):
					if isinstance(val, int):
						item.values[index] = val
		print("Applying chain preset to " + obj.name)
		for key in propertyGroup.keys():
			if key not in skipKeys:
				if key in values:
					propertyGroup[key] = values[key]
				else:
					raiseWarning("Preset is missing key " + str(key) + ", cannot set value on " + obj.name + ".")
		convertPresetGroupAttr(propertyGroup,objType,presetFileType(values,objType,jsonDict))
		applied += 1
	if applied == 0:
		showErrorMessageBox("The preset has nothing for the selected objects (chain settings, chain groups or chain nodes).")
		return False
	return True
