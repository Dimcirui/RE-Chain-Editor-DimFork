#Display names. A name is the game's own where MH Wilds has one, otherwise one that says what the option does when that is
#known, otherwise the original RE Chain Editor name. The add-on preference "Original RE Chain Editor names" brings back the
#original names, except where those named a different field than the one the file holds.
import bpy

ADDON = __package__.rsplit(".",1)[0]

def useLegacyNames():
	try:
		return bpy.context.preferences.addons[ADDON].preferences.legacyNames
	except Exception:
		return False

def pickName(new,legacy):
	return legacy if legacy and useLegacyNames() else new

#Attribute flag dialogs: property name -> (name, original name)
FLAG_NAMES = {
	#Chain group attribute flags (and the setting's Group Default Attribute)
	"RootRotation":("Free Root Rotation","Root Rotation"),
	"AngleLimit":("Enabled Angle Limit","Angle Limit"),
	"ScaleAnimation":("Enabled Scale Animation","Scale Animation"),
	"CollisionDefault":("Collision from Setting","Collision Default"),
	"CollisionSelf":("Self Collision","Collision Self"),
	"CollisionModel":("Chain Collisions","Collision Model"),
	"CollisionVGround":("Virtual Ground","Collision VGround"),
	"CollisionCollider":("Environment Collision","Collision Collider"),
	"CollisionGroup":("Collision Group","Collision Group"),
	"CollisionCharacter":("Scene Colliders (CLSP)","Collision Character"),
	"EnablePartBlend":("Enable Part Blend","Enable Part Blend"),
	"WindDefault":("Wind from Setting","Wind Default"),
	"TransAnimation":("Lengths from Pose","Trans Animation"),
	"AngleLimitRestitution":("Angle Limit Bounce","Angle Limit Restitution"),
	"StretchBoth":("Stretch Both","Stretch Both"),
	"EndRotConstraint":("End Rot Constraint","End Rot Constraint"),
	"EnableEnvWind":("Environment Wind","Enable Env Wind"),
	"ExtraNode":("Extra Tail Node","Extra Node"),
	"UseBitFlag":("Use Bit Flag","Use Bit Flag"),
	"StretchBothAutoScale":("Stretch Both Auto Scale","Stretch Both Auto Scale"),
	#Chain node attribute flags
	"PartMotionBlend":("Part Motion Blend","Part Motion Blend"),
	"Jiggle":("Extra Root Node","Jiggle"),
	#Chain settings attribute flags
	"Default":("Default","Default"),
	"VirtualGroundRoot":("Virtual Ground Root","Virtual Ground Root"),
	"VirtualGroundTarget":("Virtual Ground Target","Virtual Ground Target"),
	"IgnoreSameGroupCollision":("Ignore Same Setting Group Collision","Ignore Same Group Collision"),
	"UseReduceDistanceCurve":("Use Reduce Distance Curve","Use Reduce Distance Curve"),
	#Chain jiggle attribute flags
	"OverrideDamping":("Override Damping","Override Damping"),
	}

def flagLabel(key):
	new,legacy = FLAG_NAMES.get(key,(key,None))
	return pickName(new,legacy)

#Panel fields: (property group class, property) -> original name
PROP_NAMES = {
	("chainHeaderPropertyGroup","wilds_unkn1"):"Wilds Unknown",
	("chainHeaderPropertyGroup","wilds_unkn2"):"Wilds Unknown 2",
	}

def propLabel(propertyGroup,prop):
	legacy = PROP_NAMES.get((type(propertyGroup).__name__,prop))
	return pickName(propertyGroup.bl_rna.properties[prop].name,legacy)

#Link Mode: (value, name, original name)
LINK_MODE_NAMES = [("0","Root to Tip","LinkMode_TopToBottom"),("1","Tip to Root","LinkMode_BottomToTop"),("2","Off","LinkMode_Manual")]

#Bit flag fields of re_chain.set_bit_flags: (bit, name, original name)
HIT_FLAG_NAMES = [(0x1,"Unknown 1",None),(0x2,"Self","HitFlags_Self"),(0x4,"Model","HitFlags_Model"),(0x8,"Collider","HitFlags_Collider"),
	(0x10,"Angle","HitFlags_Angle"),(0x20,"Group","HitFlags_Group"),(0x40,"VGround","HitFlags_VGround"),(0x80,"Unknown 128",None)]
BIT_FLAG_NAMES = {
	"re_chain_chainlink.connectFlagBits":[(0x1,"Straight A - B","ConnectionFlags_Neighbour"),(0x2,"Diagonal A - next B","ConnectionFlags_Upper"),(0x4,"Diagonal next A - B","ConnectionFlags_Bottom")],
	"re_chain_chainlink.linkAttrFlags":[(0x1,"Stretch Range","AttrFlags_EnableStretch")],
	"re_chain_header.errFlagBits":[(0x1,"Empty","ErrFlags_Empty"),(0x2,"Not Found Ref Asset","ErrFlags_NotFoundRefAsset"),(0x4,"Not Found Include Asset","ErrFlags_NotFoundIncludeAsset")],
	"re_chain_header.chainAttrFlags":[(0x1,"Model Collision Preset","ChainAttrFlags_ModelCollisionPreset"),(0x2,"Alternative Restart Iterations","ChainAttrFlags_UNKN2"),(0x4,"Restart Wind Gate","ChainAttrFlags_UNKN4")],
	"re_chain_header.parameterFlag":[(0x1,"Reflect Environmental","ChainParamFlags_ReflectEnviromental")],
	}
for _i in range(8):
	BIT_FLAG_NAMES[f"re_chain_header.collisionFilterHitBits{_i}"] = HIT_FLAG_NAMES

#CLSP Flags A of groups and links: one bit per shape of the full body CLSP that Create Full Body CLSP makes
#(Presets/ClspPresets/full_body.clsp.3, MH Wilds player skeleton). Other CLSP files may use other bits
FULL_BODY_CLSP_NAMES = [(0x1,"Hip_HJ_00",None),(0x2,"Spine_0",None),(0x4,"Spine_1",None),(0x8,"Spine_2",None),
	(0x10,"Neck_0 > L_UpperArm",None),(0x20,"Neck_0 > R_UpperArm",None),(0x40,"L_UpperArm > L_Forearm",None),(0x80,"R_UpperArm > R_Forearm",None),
	(0x100,"L_Forearm > L_Hand",None),(0x200,"R_Forearm > R_Hand",None),(0x400,"L_Hand > L_MiddleF1",None),(0x800,"R_Hand > R_MiddleF1",None),
	(0x1000,"Neck_0 > Head",None),(0x2000,"Head",None),(0x4000,"L_Thigh > L_Knee",None),(0x8000,"R_Thigh > R_Knee",None),
	(0x10000,"L_Shin > L_Foot",None),(0x20000,"R_Shin > R_Foot",None),(0x40000,"L_Foot > L_Toe",None),(0x80000,"R_Foot > R_Toe",None),
	(0x800000,"Hip_HJ_00 (second shape)",None)]
BIT_FLAG_NAMES["re_chain_chaingroup.clspFlags0"] = FULL_BODY_CLSP_NAMES
BIT_FLAG_NAMES["re_chain_chainlink.clspFlags0"] = FULL_BODY_CLSP_NAMES

#Collision Filter Flags: the bits have no fixed meaning (a file picks its own), so each is listed by number
FILTER_BIT_NAMES = [(1 << _i,f"bit{_i}",None) for _i in range(32)]
for _target in ("re_chain_chaingroup","re_chain_chainnode","re_chain_chaincollision","re_chain_chainlink_collision"):
	BIT_FLAG_NAMES[f"{_target}.collisionFilterFlags"] = FILTER_BIT_NAMES
