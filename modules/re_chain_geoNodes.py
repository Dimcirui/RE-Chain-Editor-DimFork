#Author: NSA Cloud
import bpy

CURVE_RADIUS = 1.0

def getCollisionMat():
	mat = bpy.data.materials.get("ChainCollisionMat")
	if mat == None:
		mat = bpy.data.materials.new("ChainCollisionMat")
		mat.use_nodes = True
		mat.diffuse_color = bpy.context.scene.re_chain_toolpanel.collisionColor
		mat.node_tree.nodes[0].inputs["Base Color"].default_value = bpy.context.scene.re_chain_toolpanel.collisionColor
		mat.node_tree.nodes[0].inputs["Alpha"].default_value = bpy.context.scene.re_chain_toolpanel.collisionColor[3]
		mat.blend_method = "BLEND"
		if bpy.app.version < (4,2,0):
			mat.shadow_method = "NONE"
	return mat

def getChainLinkMat():
	mat = bpy.data.materials.get("ChainLinkMat")
	if mat == None:
		mat = bpy.data.materials.new("ChainLinkMat")
		mat.use_nodes = True
		mat.diffuse_color = bpy.context.scene.re_chain_toolpanel.chainLinkColor
		mat.node_tree.nodes[0].inputs["Base Color"].default_value = bpy.context.scene.re_chain_toolpanel.chainLinkColor
		mat.node_tree.nodes[0].inputs["Alpha"].default_value = bpy.context.scene.re_chain_toolpanel.chainLinkColor[3]
		mat.blend_method = "BLEND"
		if bpy.app.version < (4,2,0):
			mat.shadow_method = "NONE"
	return mat
def getChainLinkColMat():
	mat = bpy.data.materials.get("ChainLinkColMat")
	if mat == None:
		mat = bpy.data.materials.new("ChainLinkColMat")
		mat.use_nodes = True
		mat.diffuse_color = bpy.context.scene.re_chain_toolpanel.chainLinkCollisionColor
		mat.node_tree.nodes[0].inputs["Base Color"].default_value = bpy.context.scene.re_chain_toolpanel.chainLinkCollisionColor
		mat.node_tree.nodes[0].inputs["Alpha"].default_value = bpy.context.scene.re_chain_toolpanel.chainLinkCollisionColor[3]
		mat.blend_method = "BLEND"
		if bpy.app.version < (4,2,0):
			mat.shadow_method = "NONE"
	return mat
def getConeMat():
	mat = bpy.data.materials.get("ChainConeMat")
	if mat == None:
		mat = bpy.data.materials.new("ChainConeMat")
		mat.use_nodes = True
		mat.diffuse_color = bpy.context.scene.re_chain_toolpanel.coneColor
		mat.node_tree.nodes[0].inputs["Base Color"].default_value = bpy.context.scene.re_chain_toolpanel.coneColor
		mat.node_tree.nodes[0].inputs["Alpha"].default_value = bpy.context.scene.re_chain_toolpanel.coneColor[3]
		mat.blend_method = "BLEND"
		if bpy.app.version < (4,2,0):
			mat.shadow_method = "NONE"
	return mat
def getConeSubGroupMat():
	mat = bpy.data.materials.get("ChainConeSubGroupMat")
	if mat == None:
		mat = bpy.data.materials.new("ChainConeSubGroupMat")
		mat.use_nodes = True
		mat.diffuse_color = bpy.context.scene.re_chain_toolpanel.coneSubGroupColor
		mat.node_tree.nodes[0].inputs["Base Color"].default_value = bpy.context.scene.re_chain_toolpanel.coneSubGroupColor
		mat.node_tree.nodes[0].inputs["Alpha"].default_value = bpy.context.scene.re_chain_toolpanel.coneSubGroupColor[3]
		mat.blend_method = "BLEND"
		if bpy.app.version < (4,2,0):
			mat.shadow_method = "NONE"
	return mat
def getChainGroupMat():
	mat = bpy.data.materials.get("ChainGroupMat")
	if mat == None:
		mat = bpy.data.materials.new("ChainGroupMat")
		mat.use_nodes = True
		mat.diffuse_color = bpy.context.scene.re_chain_toolpanel.chainGroupColor
		mat.node_tree.nodes[0].inputs["Base Color"].default_value = bpy.context.scene.re_chain_toolpanel.chainGroupColor
		mat.node_tree.nodes[0].inputs["Alpha"].default_value = bpy.context.scene.re_chain_toolpanel.chainGroupColor[3]
		mat.blend_method = "BLEND"
		if bpy.app.version < (4,2,0):
			mat.shadow_method = "NONE"
	return mat
"""
def getColCapsuleGeoNodeTree():
	TREENAME = "ChainCapsuleGeoNodeTreeV1"
	
	if TREENAME not in bpy.data.node_groups:
		node_group = bpy.data.node_groups.new(type="GeometryNodeTree", name=TREENAME)
		nodes = node_group.nodes
		links = node_group.links
		currentXLoc = 0
		currentYLoc = 0
		
		
		if bpy.app.version < (4,0,0):
			node_group.inputs.new("NodeSocketObject","Start Object")
			node_group.inputs.new("NodeSocketObject","End Object")
		else:
			node_group.interface.new_socket(name="Start Object",description="Do not change this value manually, set it from the chain object",in_out ="INPUT", socket_type="NodeSocketObject")
			node_group.interface.new_socket(name="End Object",description="Do not change this value manually, set it from the chain object",in_out ="INPUT", socket_type="NodeSocketObject")
		
		mat = getCollisionMat()
		inNode = nodes.new('NodeGroupInput')
		inNode.location = (currentXLoc,currentYLoc)
		
		currentXLoc += 300
		startObjInfoNode = nodes.new('GeometryNodeObjectInfo')
		startObjInfoNode.location = (currentXLoc,currentYLoc)
		#startObjInfoNode.inputs["Object"].default_value = startObj
		links.new(inNode.outputs["Start Object"],startObjInfoNode.inputs["Object"])
		
		endObjInfoNode = nodes.new('GeometryNodeObjectInfo')
		endObjInfoNode.location = (currentXLoc,currentYLoc - 300)
		#endObjInfoNode.inputs["Object"].default_value = endObj
		links.new(inNode.outputs["End Object"],endObjInfoNode.inputs["Object"])
		
		currentXLoc += 300
		
		curveLineNode = nodes.new('GeometryNodeCurvePrimitiveLine')
		curveLineNode.location = (currentXLoc,currentYLoc)
		links.new(startObjInfoNode.outputs["Location"],curveLineNode.inputs["Start"])
		links.new(endObjInfoNode.outputs["Location"],curveLineNode.inputs["End"])
		
		separateScaleXYZNode = nodes.new('ShaderNodeSeparateXYZ')
		separateScaleXYZNode.location = (currentXLoc,currentYLoc - 300)
		links.new(startObjInfoNode.outputs["Scale"],separateScaleXYZNode.inputs["Vector"])
		
		currentXLoc += 300
		
		uvSphereNode = nodes.new('GeometryNodeMeshUVSphere')
		uvSphereNode.location = (currentXLoc,currentYLoc - 150)
		uvSphereNode.inputs["Radius"].default_value = CURVE_RADIUS
		
		setCurveRadiusNode = nodes.new('GeometryNodeSetCurveRadius')
		setCurveRadiusNode.location = (currentXLoc,currentYLoc - 300)
		links.new(curveLineNode.outputs["Curve"],setCurveRadiusNode.inputs["Curve"])
		links.new(separateScaleXYZNode.outputs["X"],setCurveRadiusNode.inputs["Radius"])
		
		curveCircleNode = nodes.new('GeometryNodeCurvePrimitiveCircle')
		curveCircleNode.location = (currentXLoc,currentYLoc - 450)
		curveCircleNode.inputs["Radius"].default_value = CURVE_RADIUS + 0.005
		currentXLoc += 300
		
		instanceNode = nodes.new('GeometryNodeInstanceOnPoints')
		instanceNode.location = (currentXLoc,currentYLoc)
		links.new(curveLineNode.outputs["Curve"],instanceNode.inputs["Points"])
		links.new(uvSphereNode.outputs["Mesh"],instanceNode.inputs["Instance"])
		links.new(separateScaleXYZNode.outputs["X"],instanceNode.inputs["Scale"])
		
		curveToMeshNode = nodes.new('GeometryNodeCurveToMesh')
		curveToMeshNode.location = (currentXLoc,currentYLoc - 350)
		links.new(setCurveRadiusNode.outputs["Curve"],curveToMeshNode.inputs["Curve"])
		links.new(curveCircleNode.outputs["Curve"],curveToMeshNode.inputs["Profile Curve"])
		
		currentXLoc += 300
		
		joinGeometryNode = nodes.new('GeometryNodeJoinGeometry')
		joinGeometryNode.location = (currentXLoc,currentYLoc)
		links.new(instanceNode.outputs["Instances"],joinGeometryNode.inputs["Geometry"])
		links.new(curveToMeshNode.outputs["Mesh"],joinGeometryNode.inputs["Geometry"])
		currentXLoc += 300
		
		setMaterialNode = nodes.new('GeometryNodeSetMaterial')
		setMaterialNode.location = (currentXLoc,currentYLoc)
		setMaterialNode.inputs["Material"].default_value = mat
		links.new(joinGeometryNode.outputs["Geometry"],setMaterialNode.inputs["Geometry"])
		currentXLoc += 300
		
		setSmoothShadeNode = nodes.new('GeometryNodeSetShadeSmooth')
		setSmoothShadeNode.location = (currentXLoc,currentYLoc)
		links.new(setMaterialNode.outputs["Geometry"],setSmoothShadeNode.inputs["Geometry"])
		
		currentXLoc += 300
		outNode = nodes.new('NodeGroupOutput')
		outNode.location = (currentXLoc,currentYLoc)
		if bpy.app.version < (3,4,0):
			outNode.inputs.new('NodeSocketGeometry', 'Geometry')
		elif bpy.app.version < (4,0,0):
			node_group.outputs.new('NodeSocketGeometry', 'Geometry')
		else:
			node_group.interface.new_socket(name="Geometry",description="",in_out ="OUTPUT", socket_type="NodeSocketGeometry")
		links.new(setSmoothShadeNode.outputs["Geometry"],outNode.inputs["Geometry"])
	else:
		node_group = bpy.data.node_groups[TREENAME]
	return node_group
"""
def getColCapsuleGeoNodeTree():
	TREENAME = "ChainCapsuleGeoNodeTreeV3"
	
	if TREENAME not in bpy.data.node_groups:
		node_group = bpy.data.node_groups.new(type="GeometryNodeTree", name=TREENAME)
		nodes = node_group.nodes
		links = node_group.links
		currentXLoc = 0
		currentYLoc = 0
		
		
		if bpy.app.version < (4,0,0):
			node_group.inputs.new("NodeSocketObject","Start Object")
			node_group.inputs.new("NodeSocketObject","End Object")
		else:
			node_group.interface.new_socket(name="Start Object",description="Do not change this value manually, set it from the chain object",in_out ="INPUT", socket_type="NodeSocketObject")
			node_group.interface.new_socket(name="End Object",description="Do not change this value manually, set it from the chain object",in_out ="INPUT", socket_type="NodeSocketObject")
		
		mat = getCollisionMat()
		inNode = nodes.new('NodeGroupInput')
		inNode.location = (currentXLoc,currentYLoc)
		
		currentXLoc += 300
		startObjInfoNode = nodes.new('GeometryNodeObjectInfo')
		startObjInfoNode.location = (currentXLoc,currentYLoc)
		#startObjInfoNode.inputs["Object"].default_value = startObj
		links.new(inNode.outputs["Start Object"],startObjInfoNode.inputs["Object"])
		
		endObjInfoNode = nodes.new('GeometryNodeObjectInfo')
		endObjInfoNode.location = (currentXLoc,currentYLoc - 300)
		#endObjInfoNode.inputs["Object"].default_value = endObj
		links.new(inNode.outputs["End Object"],endObjInfoNode.inputs["Object"])
		
		currentXLoc += 300
		
		curveLineNode = nodes.new('GeometryNodeCurvePrimitiveLine')
		curveLineNode.location = (currentXLoc,currentYLoc)
		links.new(startObjInfoNode.outputs["Location"],curveLineNode.inputs["Start"])
		links.new(endObjInfoNode.outputs["Location"],curveLineNode.inputs["End"])
		
		separateScaleXYZNode = nodes.new('ShaderNodeSeparateXYZ')
		separateScaleXYZNode.location = (currentXLoc,currentYLoc - 300)
		links.new(startObjInfoNode.outputs["Scale"],separateScaleXYZNode.inputs["Vector"])
		
		separateScaleXYZEndNode = nodes.new('ShaderNodeSeparateXYZ')
		separateScaleXYZEndNode.location = (currentXLoc,currentYLoc - 450)
		links.new(endObjInfoNode.outputs["Scale"],separateScaleXYZEndNode.inputs["Vector"])
		
		currentXLoc += 300
		
		uvSphereNode = nodes.new('GeometryNodeMeshUVSphere')
		uvSphereNode.location = (currentXLoc,currentYLoc - 150)
		uvSphereNode.inputs["Radius"].default_value = 1
		
		currentXLoc += 300
		
		startEndpointNode = nodes.new('GeometryNodeCurveEndpointSelection')
		startEndpointNode.location = (currentXLoc,currentYLoc)
		startEndpointNode.inputs[0].default_value = 1
		startEndpointNode.inputs[1].default_value = 0
		
		endEndpointNode = nodes.new('GeometryNodeCurveEndpointSelection')
		endEndpointNode.location = (currentXLoc,currentYLoc - 150)
		endEndpointNode.inputs[0].default_value = 0
		endEndpointNode.inputs[1].default_value = 1
		
		currentXLoc += 300
		
		startSetCurveRadiusNode = nodes.new('GeometryNodeSetCurveRadius')
		startSetCurveRadiusNode.location = (currentXLoc,currentYLoc - 300)
		links.new(startEndpointNode.outputs["Selection"],startSetCurveRadiusNode.inputs["Selection"])
		links.new(curveLineNode.outputs["Curve"],startSetCurveRadiusNode.inputs["Curve"])
		links.new(separateScaleXYZNode.outputs["X"],startSetCurveRadiusNode.inputs["Radius"])
		
		currentXLoc += 300
		
		endSetCurveRadiusNode = nodes.new('GeometryNodeSetCurveRadius')
		endSetCurveRadiusNode.location = (currentXLoc,currentYLoc - 300)
		links.new(endEndpointNode.outputs["Selection"],endSetCurveRadiusNode.inputs["Selection"])
		links.new(startSetCurveRadiusNode.outputs["Curve"],endSetCurveRadiusNode.inputs["Curve"])
		links.new(separateScaleXYZEndNode.outputs["X"],endSetCurveRadiusNode.inputs["Radius"])
		
		curveCircleNode = nodes.new('GeometryNodeCurvePrimitiveCircle')
		curveCircleNode.location = (currentXLoc,currentYLoc - 450)
		curveCircleNode.inputs["Radius"].default_value = 1
		
		currentXLoc -= 1500
		currentYLoc += 500
		
		positionNode = nodes.new('GeometryNodeInputPosition')
		positionNode.location = (currentXLoc,currentYLoc)
		
		currentXLoc += 300
		
		separatePosXYZNode = nodes.new('ShaderNodeSeparateXYZ')
		separatePosXYZNode.location = (currentXLoc,currentYLoc)
		links.new(positionNode.outputs["Position"],separatePosXYZNode.inputs["Vector"])
		
		currentXLoc += 300
		
		addNode = nodes.new('ShaderNodeMath')
		addNode.location = (currentXLoc,currentYLoc)
		addNode.operation = "ADD"
		links.new(separatePosXYZNode.outputs["Z"],addNode.inputs[0])
		addNode.inputs[1].default_value = 0.1
		
		currentXLoc += 300
		
		multNode = nodes.new('ShaderNodeMath')
		multNode.location = (currentXLoc,currentYLoc)
		multNode.operation = "MULTIPLY"
		links.new(addNode.outputs["Value"],multNode.inputs[0])
		multNode.inputs[1].default_value = -1
		currentXLoc += 300
		
		startDeleteGeometryNode = nodes.new('GeometryNodeDeleteGeometry')
		startDeleteGeometryNode.location = (currentXLoc,currentYLoc)
		links.new(uvSphereNode.outputs["Mesh"],startDeleteGeometryNode.inputs["Geometry"])
		links.new(multNode.outputs["Value"],startDeleteGeometryNode.inputs["Selection"])
		
		endDeleteGeometryNode = nodes.new('GeometryNodeDeleteGeometry')
		endDeleteGeometryNode.location = (currentXLoc,currentYLoc - 300)
		links.new(uvSphereNode.outputs["Mesh"],endDeleteGeometryNode.inputs["Geometry"])
		links.new(separatePosXYZNode.outputs["Z"],endDeleteGeometryNode.inputs["Selection"])
		
		currentXLoc += 300
		
		vectorSubtractNode = nodes.new('ShaderNodeVectorMath')
		vectorSubtractNode.location = (currentXLoc,currentYLoc)
		vectorSubtractNode.operation = "SUBTRACT"
		links.new(endObjInfoNode.outputs["Location"],vectorSubtractNode.inputs[0])
		links.new(startObjInfoNode.outputs["Location"],vectorSubtractNode.inputs[1])
		
		currentXLoc += 300
		
		eulerAlignNode = nodes.new('FunctionNodeAlignEulerToVector')
		eulerAlignNode.location = (currentXLoc,currentYLoc)
		eulerAlignNode.axis = "Z"
		links.new(vectorSubtractNode.outputs["Vector"],eulerAlignNode.inputs["Vector"])
		currentXLoc += 300
		
		currentYLoc -= 500
		
		startInstanceNode = nodes.new('GeometryNodeInstanceOnPoints')
		startInstanceNode.location = (currentXLoc,currentYLoc + 400)
		links.new(curveLineNode.outputs["Curve"],startInstanceNode.inputs["Points"])
		links.new(startEndpointNode.outputs["Selection"],startInstanceNode.inputs["Selection"])
		#links.new(startDeleteGeometryNode.outputs["Geometry"],startInstanceNode.inputs["Instance"])
		#backwards
		links.new(endDeleteGeometryNode.outputs["Geometry"],startInstanceNode.inputs["Instance"])
		links.new(eulerAlignNode.outputs["Rotation"],startInstanceNode.inputs["Rotation"])
		links.new(separateScaleXYZNode.outputs["X"],startInstanceNode.inputs["Scale"])
		
		endInstanceNode = nodes.new('GeometryNodeInstanceOnPoints')
		endInstanceNode.location = (currentXLoc,currentYLoc)
		links.new(curveLineNode.outputs["Curve"],endInstanceNode.inputs["Points"])
		links.new(endEndpointNode.outputs["Selection"],endInstanceNode.inputs["Selection"])
		#links.new(endDeleteGeometryNode.outputs["Geometry"],endInstanceNode.inputs["Instance"])
		#backwards
		links.new(startDeleteGeometryNode.outputs["Geometry"],endInstanceNode.inputs["Instance"])
		links.new(eulerAlignNode.outputs["Rotation"],endInstanceNode.inputs["Rotation"])
		links.new(separateScaleXYZEndNode.outputs["X"],endInstanceNode.inputs["Scale"])
		
		currentXLoc += 300
		
		startRealizeInstance = nodes.new('GeometryNodeRealizeInstances')
		startRealizeInstance.location = (currentXLoc,currentYLoc + 400)
		links.new(startInstanceNode.outputs["Instances"],startRealizeInstance.inputs["Geometry"])
		
		endRealizeInstance = nodes.new('GeometryNodeRealizeInstances')
		endRealizeInstance.location = (currentXLoc,currentYLoc)
		links.new(endInstanceNode.outputs["Instances"],endRealizeInstance.inputs["Geometry"])
		
		
		curveToMeshNode = nodes.new('GeometryNodeCurveToMesh')
		curveToMeshNode.location = (currentXLoc,currentYLoc - 350)
		links.new(endSetCurveRadiusNode.outputs["Curve"],curveToMeshNode.inputs["Curve"])
		links.new(curveCircleNode.outputs["Curve"],curveToMeshNode.inputs["Profile Curve"])
		
		if bpy.app.version >= (4,5,0):
			radiusNode = nodes.new('GeometryNodeInputRadius')
			radiusNode.location = (currentXLoc,currentYLoc - 500)
			links.new(radiusNode.outputs["Radius"],curveToMeshNode.inputs["Scale"])
		
		currentXLoc += 300
		
		joinGeometryNode = nodes.new('GeometryNodeJoinGeometry')
		joinGeometryNode.location = (currentXLoc,currentYLoc)
		links.new(startRealizeInstance.outputs["Geometry"],joinGeometryNode.inputs["Geometry"])
		links.new(endRealizeInstance.outputs["Geometry"],joinGeometryNode.inputs["Geometry"])
		links.new(curveToMeshNode.outputs["Mesh"],joinGeometryNode.inputs["Geometry"])
		currentXLoc += 300
		
		minNode = nodes.new('ShaderNodeMath')
		minNode.location = (currentXLoc,currentYLoc)
		minNode.operation = "MINIMUM"
		links.new(separateScaleXYZNode.outputs["Z"],minNode.inputs[0])
		links.new(separateScaleXYZEndNode.outputs["Z"],minNode.inputs[1])
		
		currentXLoc += 300
		
		multNode2 = nodes.new('ShaderNodeMath')
		multNode2.location = (currentXLoc,currentYLoc)
		multNode2.operation = "MULTIPLY"
		links.new(minNode.outputs["Value"],multNode2.inputs[0])
		multNode2.inputs[1].default_value = 0.15
		currentXLoc += 300
		
		mergeNode = nodes.new('GeometryNodeMergeByDistance')
		mergeNode.location = (currentXLoc,currentYLoc)
		links.new(joinGeometryNode.outputs["Geometry"],mergeNode.inputs["Geometry"])
		links.new(multNode2.outputs["Value"],mergeNode.inputs["Distance"])
		
		currentXLoc += 300
		
		setMaterialNode = nodes.new('GeometryNodeSetMaterial')
		setMaterialNode.location = (currentXLoc,currentYLoc)
		setMaterialNode.inputs["Material"].default_value = mat
		links.new(mergeNode.outputs["Geometry"],setMaterialNode.inputs["Geometry"])
		currentXLoc += 300
		
		setSmoothShadeNode = nodes.new('GeometryNodeSetShadeSmooth')
		setSmoothShadeNode.location = (currentXLoc,currentYLoc)
		links.new(setMaterialNode.outputs["Geometry"],setSmoothShadeNode.inputs["Geometry"])
		
		currentXLoc += 300
		outNode = nodes.new('NodeGroupOutput')
		outNode.location = (currentXLoc,currentYLoc)
		if bpy.app.version < (3,4,0):
			outNode.inputs.new('NodeSocketGeometry', 'Geometry')
		elif bpy.app.version < (4,0,0):
			node_group.outputs.new('NodeSocketGeometry', 'Geometry')
		else:
			node_group.interface.new_socket(name="Geometry",description="",in_out ="OUTPUT", socket_type="NodeSocketGeometry")
		links.new(setSmoothShadeNode.outputs["Geometry"],outNode.inputs["Geometry"])
	else:
		node_group = bpy.data.node_groups[TREENAME]
	return node_group


def getColSphereGeoNodeTree():
	TREENAME = "ChainSphereGeoNodeTreeV1"
	mat = getCollisionMat()
	if TREENAME not in bpy.data.node_groups:
		node_group = bpy.data.node_groups.new(type="GeometryNodeTree", name=TREENAME)
		nodes = node_group.nodes
		links = node_group.links
		
		currentXLoc = 0
		currentYLoc = 0

		"""
		if bpy.app.version < (4,0,0):
			node_group.inputs.new("NodeSocketObject","Start Object")
		else:
			node_group.interface.new_socket(name="Start Object",description="Do not change this value manually, set it from the chain object",in_out ="INPUT", socket_type="NodeSocketObject")
		
		
		inNode = nodes.new('NodeGroupInput')
		inNode.location = (currentXLoc,currentYLoc)
		
		currentXLoc += 300
		startObjInfoNode = nodes.new('GeometryNodeObjectInfo')
		startObjInfoNode.location = (currentXLoc,currentYLoc)
		#startObjInfoNode.inputs["Object"].default_value = startObj
		links.new(inNode.outputs["Start Object"],startObjInfoNode.inputs["Object"])
		
		currentXLoc += 300
		
		separateScaleXYZNode = nodes.new('ShaderNodeSeparateXYZ')
		separateScaleXYZNode.location = (currentXLoc,currentYLoc - 300)
		links.new(startObjInfoNode.outputs["Scale"],separateScaleXYZNode.inputs["Vector"])
		
		currentXLoc += 300
		"""
		uvSphereNode = nodes.new('GeometryNodeMeshUVSphere')
		uvSphereNode.location = (currentXLoc,currentYLoc - 150)
		uvSphereNode.inputs["Radius"].default_value = CURVE_RADIUS
		
		currentXLoc += 300
		
		transformNode = nodes.new('GeometryNodeTransform')
		transformNode.location = (currentXLoc,currentYLoc)
		#links.new(startObjInfoNode.outputs["Location"],instanceNode.inputs["Translation"])
		links.new(uvSphereNode.outputs["Mesh"],transformNode.inputs["Geometry"])
		#links.new(separateScaleXYZNode.outputs["X"],transformNode.inputs["Scale"])
		
		
		currentXLoc += 300
		
		setMaterialNode = nodes.new('GeometryNodeSetMaterial')
		setMaterialNode.location = (currentXLoc,currentYLoc)
		setMaterialNode.inputs["Material"].default_value = mat
		links.new(transformNode.outputs["Geometry"],setMaterialNode.inputs["Geometry"])
		currentXLoc += 300
		
		setSmoothShadeNode = nodes.new('GeometryNodeSetShadeSmooth')
		setSmoothShadeNode.location = (currentXLoc,currentYLoc)
		links.new(setMaterialNode.outputs["Geometry"],setSmoothShadeNode.inputs["Geometry"])
		
		currentXLoc += 300
		outNode = nodes.new('NodeGroupOutput')
		outNode.location = (currentXLoc,currentYLoc)
		if bpy.app.version < (3,4,0):
			outNode.inputs.new('NodeSocketGeometry', 'Geometry')
		elif bpy.app.version < (4,0,0):
			node_group.outputs.new('NodeSocketGeometry', 'Geometry')
		else:
			node_group.interface.new_socket(name="Geometry",description="",in_out ="OUTPUT", socket_type="NodeSocketGeometry")
		links.new(setSmoothShadeNode.outputs["Geometry"],outNode.inputs["Geometry"])
	else:
		node_group = bpy.data.node_groups[TREENAME]
	return node_group

def getChainLinkGeoNodeTree():
	TREENAME = "ChainLinkGeoNodeTreeV2"
	if TREENAME not in bpy.data.node_groups:
		node_group = bpy.data.node_groups.new(type="GeometryNodeTree", name=TREENAME)
		nodes = node_group.nodes
		links = node_group.links
		linkmat = getChainLinkMat()
		currentXLoc = 0
		currentYLoc = 0
		
		if bpy.app.version < (4,0,0):
			node_group.inputs.new("NodeSocketObject","Start Object")
			node_group.inputs.new("NodeSocketObject","End Object")
		else:
			node_group.interface.new_socket(name="Start Object",description="Do not change this value manually, set it from the chain object",in_out ="INPUT", socket_type="NodeSocketObject")
			node_group.interface.new_socket(name="End Object",description="Do not change this value manually, set it from the chain object",in_out ="INPUT", socket_type="NodeSocketObject")
		
		inNode = nodes.new('NodeGroupInput')
		inNode.location = (currentXLoc,currentYLoc)
		
		currentXLoc += 300
		startObjInfoNode = nodes.new('GeometryNodeObjectInfo')
		startObjInfoNode.location = (currentXLoc,currentYLoc)
		#startObjInfoNode.inputs["Object"].default_value = startObj
		links.new(inNode.outputs["Start Object"],startObjInfoNode.inputs["Object"])
		
		endObjInfoNode = nodes.new('GeometryNodeObjectInfo')
		endObjInfoNode.location = (currentXLoc,currentYLoc - 300)
		#endObjInfoNode.inputs["Object"].default_value = endObj
		links.new(inNode.outputs["End Object"],endObjInfoNode.inputs["Object"])
		
		currentXLoc += 300
		
		curveLineNode = nodes.new('GeometryNodeCurvePrimitiveLine')
		curveLineNode.location = (currentXLoc,currentYLoc)
		links.new(startObjInfoNode.outputs["Location"],curveLineNode.inputs["Start"])
		links.new(endObjInfoNode.outputs["Location"],curveLineNode.inputs["End"])
		
		
		currentXLoc += 300
		
		setCurveRadiusNode = nodes.new('GeometryNodeSetCurveRadius')
		setCurveRadiusNode.location = (currentXLoc,currentYLoc - 300)
		links.new(curveLineNode.outputs["Curve"],setCurveRadiusNode.inputs["Curve"])
		setCurveRadiusNode.inputs["Radius"].default_value = 0.1
		
		curveCircleNode = nodes.new('GeometryNodeCurvePrimitiveCircle')
		curveCircleNode.location = (currentXLoc,currentYLoc - 450)
		curveCircleNode.inputs["Resolution"].default_value = 4
		curveCircleNode.inputs["Radius"].default_value = 0.1
		currentXLoc += 300
		
		
		curveToMeshNode = nodes.new('GeometryNodeCurveToMesh')
		curveToMeshNode.location = (currentXLoc,currentYLoc - 350)
		curveToMeshNode.inputs["Fill Caps"].default_value = True
		links.new(setCurveRadiusNode.outputs["Curve"],curveToMeshNode.inputs["Curve"])
		links.new(curveCircleNode.outputs["Curve"],curveToMeshNode.inputs["Profile Curve"])
		if bpy.app.version >= (4,5,0):
			curveToMeshNode.inputs["Scale"].default_value = 0.1
		currentXLoc += 300
		
		
		setMaterialNode = nodes.new('GeometryNodeSetMaterial')
		setMaterialNode.location = (currentXLoc,currentYLoc)
		setMaterialNode.inputs["Material"].default_value = linkmat
		links.new(curveToMeshNode.outputs["Mesh"],setMaterialNode.inputs["Geometry"])
		currentXLoc += 300
		
		
		currentXLoc += 300
		outNode = nodes.new('NodeGroupOutput')
		outNode.location = (currentXLoc,currentYLoc)
		
		if bpy.app.version < (3,4,0):
			outNode.inputs.new('NodeSocketGeometry', 'Geometry')
		elif bpy.app.version < (4,0,0):
			node_group.outputs.new('NodeSocketGeometry', 'Geometry')
		else:
			node_group.interface.new_socket(name="Geometry",description="",in_out ="OUTPUT", socket_type="NodeSocketGeometry")
		
		
		links.new(setMaterialNode.outputs["Geometry"],outNode.inputs["Geometry"])
	else:
		node_group = bpy.data.node_groups[TREENAME]
	return node_group

def getLinkColGeoNodeTree():
	"""MH Wilds' link collision: a sphere midway between the pair's nodes, of the link node's radius (times the
	chain's scale), and a thin dashed line between the nodes."""
	TREENAME = "ChainLinkColGeoNodeTreeV5"
	if TREENAME not in bpy.data.node_groups:
		node_group = bpy.data.node_groups.new(type="GeometryNodeTree", name=TREENAME)
		nodes = node_group.nodes
		links = node_group.links
		if bpy.app.version < (4,0,0):
			node_group.inputs.new("NodeSocketObject","Start Object")
			node_group.inputs.new("NodeSocketObject","End Object")
			node_group.inputs.new("NodeSocketFloat","Radius")
		else:
			node_group.interface.new_socket(name="Start Object",description="Do not change this value manually, set it from the chain object",in_out ="INPUT", socket_type="NodeSocketObject")
			node_group.interface.new_socket(name="End Object",description="Do not change this value manually, set it from the chain object",in_out ="INPUT", socket_type="NodeSocketObject")
			node_group.interface.new_socket(name="Radius",description="Do not change this value manually, set it from the chain object",in_out ="INPUT", socket_type="NodeSocketFloat")
		mat = getChainLinkColMat()
		inNode = nodes.new('NodeGroupInput')
		inNode.location = (0,0)
		startObjInfoNode = nodes.new('GeometryNodeObjectInfo')
		startObjInfoNode.location = (300,0)
		links.new(inNode.outputs["Start Object"],startObjInfoNode.inputs["Object"])
		endObjInfoNode = nodes.new('GeometryNodeObjectInfo')
		endObjInfoNode.location = (300,-300)
		links.new(inNode.outputs["End Object"],endObjInfoNode.inputs["Object"])
		addNode = nodes.new('ShaderNodeVectorMath')
		addNode.location = (600,0)
		addNode.operation = "ADD"
		links.new(startObjInfoNode.outputs["Location"],addNode.inputs[0])
		links.new(endObjInfoNode.outputs["Location"],addNode.inputs[1])
		midNode = nodes.new('ShaderNodeVectorMath')
		midNode.location = (800,0)
		midNode.operation = "SCALE"
		links.new(addNode.outputs["Vector"],midNode.inputs[0])
		midNode.inputs["Scale"].default_value = 0.5
		uvSphereNode = nodes.new('GeometryNodeMeshUVSphere')
		uvSphereNode.location = (800,-200)
		links.new(inNode.outputs["Radius"],uvSphereNode.inputs["Radius"])
		transformNode = nodes.new('GeometryNodeTransform')
		transformNode.location = (1000,0)
		links.new(uvSphereNode.outputs["Mesh"],transformNode.inputs["Geometry"])
		links.new(midNode.outputs["Vector"],transformNode.inputs["Translation"])
		curveLineNode = nodes.new('GeometryNodeCurvePrimitiveLine')
		curveLineNode.location = (600,-300)
		links.new(startObjInfoNode.outputs["Location"],curveLineNode.inputs["Start"])
		links.new(endObjInfoNode.outputs["Location"],curveLineNode.inputs["End"])
		#The pair line, dashed: display only, the game has no line.
		#2k+1 equal segments of about DASH each (k = floor(length / (2 DASH))), every other one kept, so both ends are dashes
		DASH = 0.004
		distanceNode = nodes.new('ShaderNodeVectorMath')
		distanceNode.location = (600,-450)
		distanceNode.operation = "DISTANCE"
		links.new(startObjInfoNode.outputs["Location"],distanceNode.inputs[0])
		links.new(endObjInfoNode.outputs["Location"],distanceNode.inputs[1])
		dashCountNode = nodes.new('ShaderNodeMath')
		dashCountNode.location = (800,-450)
		dashCountNode.operation = "DIVIDE"
		links.new(distanceNode.outputs["Value"],dashCountNode.inputs[0])
		dashCountNode.inputs[1].default_value = 2.0 * DASH
		dashFloorNode = nodes.new('ShaderNodeMath')
		dashFloorNode.location = (1000,-450)
		dashFloorNode.operation = "FLOOR"
		links.new(dashCountNode.outputs["Value"],dashFloorNode.inputs[0])
		pointCountNode = nodes.new('ShaderNodeMath')
		pointCountNode.location = (1200,-450)
		pointCountNode.operation = "MULTIPLY_ADD"
		links.new(dashFloorNode.outputs["Value"],pointCountNode.inputs[0])
		pointCountNode.inputs[1].default_value = 2.0
		pointCountNode.inputs[2].default_value = 2.0
		resampleNode = nodes.new('GeometryNodeResampleCurve')
		resampleNode.location = (800,-300)
		links.new(curveLineNode.outputs["Curve"],resampleNode.inputs["Curve"])
		links.new(pointCountNode.outputs["Value"],resampleNode.inputs["Count"])
		polylineNode = nodes.new('GeometryNodeCurveToMesh')
		polylineNode.location = (1000,-300)
		links.new(resampleNode.outputs["Curve"],polylineNode.inputs["Curve"])
		indexNode = nodes.new('GeometryNodeInputIndex')
		indexNode.location = (1000,-600)
		gapNode = nodes.new('ShaderNodeMath')
		gapNode.location = (1200,-600)
		gapNode.operation = "FLOORED_MODULO"
		links.new(indexNode.outputs["Index"],gapNode.inputs[0])
		gapNode.inputs[1].default_value = 2.0
		deleteGapsNode = nodes.new('GeometryNodeDeleteGeometry')
		deleteGapsNode.location = (1200,-300)
		deleteGapsNode.domain = "EDGE"
		links.new(polylineNode.outputs["Mesh"],deleteGapsNode.inputs["Geometry"])
		links.new(gapNode.outputs["Value"],deleteGapsNode.inputs["Selection"])
		dashCurveNode = nodes.new('GeometryNodeMeshToCurve')
		dashCurveNode.location = (1400,-300)
		links.new(deleteGapsNode.outputs["Geometry"],dashCurveNode.inputs["Mesh"])
		curveCircleNode = nodes.new('GeometryNodeCurvePrimitiveCircle')
		curveCircleNode.location = (1400,-500)
		curveCircleNode.inputs["Resolution"].default_value = 8
		curveCircleNode.inputs["Radius"].default_value = 0.0005
		curveToMeshNode = nodes.new('GeometryNodeCurveToMesh')
		curveToMeshNode.location = (1600,-300)
		links.new(dashCurveNode.outputs["Curve"],curveToMeshNode.inputs["Curve"])
		links.new(curveCircleNode.outputs["Curve"],curveToMeshNode.inputs["Profile Curve"])
		joinGeometryNode = nodes.new('GeometryNodeJoinGeometry')
		joinGeometryNode.location = (1200,0)
		links.new(transformNode.outputs["Geometry"],joinGeometryNode.inputs["Geometry"])
		links.new(curveToMeshNode.outputs["Mesh"],joinGeometryNode.inputs["Geometry"])
		setMaterialNode = nodes.new('GeometryNodeSetMaterial')
		setMaterialNode.location = (1400,0)
		setMaterialNode.inputs["Material"].default_value = mat
		links.new(joinGeometryNode.outputs["Geometry"],setMaterialNode.inputs["Geometry"])
		setSmoothShadeNode = nodes.new('GeometryNodeSetShadeSmooth')
		setSmoothShadeNode.location = (1600,0)
		links.new(setMaterialNode.outputs["Geometry"],setSmoothShadeNode.inputs["Geometry"])
		outNode = nodes.new('NodeGroupOutput')
		outNode.location = (1800,0)
		if bpy.app.version < (3,4,0):
			outNode.inputs.new('NodeSocketGeometry', 'Geometry')
		elif bpy.app.version < (4,0,0):
			node_group.outputs.new('NodeSocketGeometry', 'Geometry')
		else:
			node_group.interface.new_socket(name="Geometry",description="",in_out ="OUTPUT", socket_type="NodeSocketGeometry")
		links.new(setSmoothShadeNode.outputs["Geometry"],outNode.inputs["Geometry"])
		return node_group
	return bpy.data.node_groups[TREENAME]

def getNodeCapsuleGeoNodeTree():
	"""A Capsule node's collision capsule: from the node toward the next node, its ends pulled in by the stretch
	rates (next + rate0 x (node - next) and node + rate1 x (next - node)). Positions are taken relative to the
	drawing object, so it draws right whatever that object's transform."""
	TREENAME = "ChainNodeCapsuleGeoNodeTreeV1"
	if TREENAME in bpy.data.node_groups:
		return bpy.data.node_groups[TREENAME]
	node_group = bpy.data.node_groups.new(type="GeometryNodeTree", name=TREENAME)
	nodes = node_group.nodes
	links = node_group.links
	for name, socketType in (("Node Object","NodeSocketObject"),("Next Node Object","NodeSocketObject"),("Radius","NodeSocketFloat"),("Rate 0","NodeSocketFloat"),("Rate 1","NodeSocketFloat")):
		if bpy.app.version < (4,0,0):
			node_group.inputs.new(socketType,name)
		else:
			node_group.interface.new_socket(name=name,description="Do not change this value manually, set it from the chain node",in_out="INPUT",socket_type=socketType)
	inNode = nodes.new('NodeGroupInput')
	nodeInfo = nodes.new('GeometryNodeObjectInfo')
	nodeInfo.transform_space = 'RELATIVE'
	links.new(inNode.outputs["Node Object"],nodeInfo.inputs["Object"])
	nextInfo = nodes.new('GeometryNodeObjectInfo')
	nextInfo.transform_space = 'RELATIVE'
	links.new(inNode.outputs["Next Node Object"],nextInfo.inputs["Object"])
	def lerpEnd(base, other, rate):
		#base + rate x (other - base)
		sub = nodes.new('ShaderNodeVectorMath')
		sub.operation = "SUBTRACT"
		links.new(other,sub.inputs[0])
		links.new(base,sub.inputs[1])
		scale = nodes.new('ShaderNodeVectorMath')
		scale.operation = "SCALE"
		links.new(sub.outputs["Vector"],scale.inputs[0])
		links.new(rate,scale.inputs["Scale"])
		add = nodes.new('ShaderNodeVectorMath')
		add.operation = "ADD"
		links.new(scale.outputs["Vector"],add.inputs[0])
		links.new(base,add.inputs[1])
		return add.outputs["Vector"]
	end0 = lerpEnd(nextInfo.outputs["Location"],nodeInfo.outputs["Location"],inNode.outputs["Rate 0"])
	end1 = lerpEnd(nodeInfo.outputs["Location"],nextInfo.outputs["Location"],inNode.outputs["Rate 1"])
	lineNode = nodes.new('GeometryNodeCurvePrimitiveLine')
	links.new(end0,lineNode.inputs["Start"])
	links.new(end1,lineNode.inputs["End"])
	circleNode = nodes.new('GeometryNodeCurvePrimitiveCircle')
	circleNode.inputs["Resolution"].default_value = 16
	links.new(inNode.outputs["Radius"],circleNode.inputs["Radius"])
	tubeNode = nodes.new('GeometryNodeCurveToMesh')
	links.new(lineNode.outputs["Curve"],tubeNode.inputs["Curve"])
	links.new(circleNode.outputs["Curve"],tubeNode.inputs["Profile Curve"])
	joinNode = nodes.new('GeometryNodeJoinGeometry')
	links.new(tubeNode.outputs["Mesh"],joinNode.inputs["Geometry"])
	for end in (end0,end1):
		sphereNode = nodes.new('GeometryNodeMeshUVSphere')
		sphereNode.inputs["Segments"].default_value = 16
		sphereNode.inputs["Rings"].default_value = 8
		links.new(inNode.outputs["Radius"],sphereNode.inputs["Radius"])
		moveNode = nodes.new('GeometryNodeTransform')
		links.new(sphereNode.outputs["Mesh"],moveNode.inputs["Geometry"])
		links.new(end,moveNode.inputs["Translation"])
		links.new(moveNode.outputs["Geometry"],joinNode.inputs["Geometry"])
	materialNode = nodes.new('GeometryNodeSetMaterial')
	materialNode.inputs["Material"].default_value = getCollisionMat()
	links.new(joinNode.outputs["Geometry"],materialNode.inputs["Geometry"])
	#A radius of 0 (no collision) draws nothing
	compareNode = nodes.new('FunctionNodeCompare')
	compareNode.data_type = 'FLOAT'
	compareNode.operation = 'GREATER_THAN'
	links.new(inNode.outputs["Radius"],compareNode.inputs[0])
	compareNode.inputs[1].default_value = 0.0
	switchNode = nodes.new('GeometryNodeSwitch')
	switchNode.input_type = 'GEOMETRY'
	links.new(compareNode.outputs["Result"],switchNode.inputs["Switch"])
	links.new(materialNode.outputs["Geometry"],switchNode.inputs["True"])
	outNode = nodes.new('NodeGroupOutput')
	if bpy.app.version < (3,4,0):
		outNode.inputs.new('NodeSocketGeometry','Geometry')
	elif bpy.app.version < (4,0,0):
		node_group.outputs.new('NodeSocketGeometry','Geometry')
	else:
		node_group.interface.new_socket(name="Geometry",description="",in_out="OUTPUT",socket_type="NodeSocketGeometry")
	links.new(switchNode.outputs[0],outNode.inputs["Geometry"])
	return node_group

def getLinkColGeoNodeTreeV2():
	"""The previous link collision drawing (a tube along the pair), kept for scenes that still use it; Redraw All
	Chains replaces it."""
	TREENAME = "ChainLinkColGeoNodeTreeV2"
	
	if TREENAME not in bpy.data.node_groups:
		node_group = bpy.data.node_groups.new(type="GeometryNodeTree", name=TREENAME)
		nodes = node_group.nodes
		links = node_group.links
		currentXLoc = 0
		currentYLoc = 0
		
		
		if bpy.app.version < (4,0,0):
			node_group.inputs.new("NodeSocketObject","Start Object")
			node_group.inputs.new("NodeSocketObject","End Object")
			node_group.inputs.new("NodeSocketFloat","Radius")
		else:
			node_group.interface.new_socket(name="Start Object",description="Do not change this value manually, set it from the chain object",in_out ="INPUT", socket_type="NodeSocketObject")
			node_group.interface.new_socket(name="End Object",description="Do not change this value manually, set it from the chain object",in_out ="INPUT", socket_type="NodeSocketObject")
			node_group.interface.new_socket(name="Radius",description="Do not change this value manually, set it from the chain object",in_out ="INPUT", socket_type="NodeSocketFloat")
		
		mat = getChainLinkColMat()
		inNode = nodes.new('NodeGroupInput')
		inNode.location = (currentXLoc,currentYLoc)
		
		currentXLoc += 300
		startObjInfoNode = nodes.new('GeometryNodeObjectInfo')
		startObjInfoNode.location = (currentXLoc,currentYLoc)
		#startObjInfoNode.inputs["Object"].default_value = startObj
		links.new(inNode.outputs["Start Object"],startObjInfoNode.inputs["Object"])
		
		endObjInfoNode = nodes.new('GeometryNodeObjectInfo')
		endObjInfoNode.location = (currentXLoc,currentYLoc - 300)
		#endObjInfoNode.inputs["Object"].default_value = endObj
		links.new(inNode.outputs["End Object"],endObjInfoNode.inputs["Object"])
		
		currentXLoc += 300
		
		curveLineNode = nodes.new('GeometryNodeCurvePrimitiveLine')
		curveLineNode.location = (currentXLoc,currentYLoc)
		links.new(startObjInfoNode.outputs["Location"],curveLineNode.inputs["Start"])
		links.new(endObjInfoNode.outputs["Location"],curveLineNode.inputs["End"])
		
		currentXLoc += 300
		
		multNode = nodes.new('ShaderNodeMath')
		multNode.location = (currentXLoc,currentYLoc)
		multNode.operation = "MULTIPLY"
		links.new(inNode.outputs["Radius"],multNode.inputs[0])
		multNode.inputs[1].default_value = 3.5#The collision radius seems a bit too small so scale up to make it more visible
		
		currentXLoc += 300
		
		uvSphereNode = nodes.new('GeometryNodeMeshUVSphere')
		uvSphereNode.location = (currentXLoc,currentYLoc - 150)
		links.new(multNode.outputs["Value"],uvSphereNode.inputs["Radius"])
		
		setCurveRadiusNode = nodes.new('GeometryNodeSetCurveRadius')
		setCurveRadiusNode.location = (currentXLoc,currentYLoc - 300)
		links.new(curveLineNode.outputs["Curve"],setCurveRadiusNode.inputs["Curve"])
		links.new(multNode.outputs["Value"],setCurveRadiusNode.inputs["Radius"])
		
		addNode = nodes.new('ShaderNodeMath')
		addNode.location = (currentXLoc,currentYLoc - 450)
		addNode.operation = "ADD"
		links.new(multNode.outputs["Value"],addNode.inputs[0])
		addNode.inputs[1].default_value = 0.0023
		
		curveCircleNode = nodes.new('GeometryNodeCurvePrimitiveCircle')
		curveCircleNode.location = (currentXLoc,currentYLoc - 650)
		links.new(addNode.outputs["Value"],curveCircleNode.inputs["Radius"])
		currentXLoc += 300
		
		instanceNode = nodes.new('GeometryNodeInstanceOnPoints')
		instanceNode.location = (currentXLoc,currentYLoc)
		links.new(curveLineNode.outputs["Curve"],instanceNode.inputs["Points"])
		links.new(uvSphereNode.outputs["Mesh"],instanceNode.inputs["Instance"])
		links.new(multNode.outputs["Value"],instanceNode.inputs["Scale"])
		
		curveToMeshNode = nodes.new('GeometryNodeCurveToMesh')
		curveToMeshNode.location = (currentXLoc,currentYLoc - 350)
		links.new(setCurveRadiusNode.outputs["Curve"],curveToMeshNode.inputs["Curve"])
		links.new(curveCircleNode.outputs["Curve"],curveToMeshNode.inputs["Profile Curve"])
		if bpy.app.version >= (4,5,0):
			links.new(multNode.outputs["Value"],curveToMeshNode.inputs["Scale"])
		currentXLoc += 300
		
		joinGeometryNode = nodes.new('GeometryNodeJoinGeometry')
		joinGeometryNode.location = (currentXLoc,currentYLoc)
		links.new(instanceNode.outputs["Instances"],joinGeometryNode.inputs["Geometry"])
		links.new(curveToMeshNode.outputs["Mesh"],joinGeometryNode.inputs["Geometry"])
		currentXLoc += 300
		
		setMaterialNode = nodes.new('GeometryNodeSetMaterial')
		setMaterialNode.location = (currentXLoc,currentYLoc)
		setMaterialNode.inputs["Material"].default_value = mat
		links.new(joinGeometryNode.outputs["Geometry"],setMaterialNode.inputs["Geometry"])
		currentXLoc += 300
		
		setSmoothShadeNode = nodes.new('GeometryNodeSetShadeSmooth')
		setSmoothShadeNode.location = (currentXLoc,currentYLoc)
		links.new(setMaterialNode.outputs["Geometry"],setSmoothShadeNode.inputs["Geometry"])
		
		currentXLoc += 300
		outNode = nodes.new('NodeGroupOutput')
		outNode.location = (currentXLoc,currentYLoc)
		if bpy.app.version < (3,4,0):
			outNode.inputs.new('NodeSocketGeometry', 'Geometry')
		elif bpy.app.version < (4,0,0):
			node_group.outputs.new('NodeSocketGeometry', 'Geometry')
		else:
			node_group.interface.new_socket(name="Geometry",description="",in_out ="OUTPUT", socket_type="NodeSocketGeometry")
		links.new(setSmoothShadeNode.outputs["Geometry"],outNode.inputs["Geometry"])
	else:
		node_group = bpy.data.node_groups[TREENAME]
	return node_group

def getConeGeoNodeTree(isSubGroup = False):
	"""The angle limit cone as MH Wilds clamps it: the
	input is the FULL opening angle, the swing is half of it; tip at the node, axis +X, length 10 before the helper's
	scale. Over 90 degrees half angle the cone opens backwards."""
	if isSubGroup:
		TREENAME = "ChainConeSubGroupGeoNodeTreeV2"
		mat = getConeSubGroupMat()
	else:
		TREENAME = "ChainConeGeoNodeTreeV2"
		mat = getConeMat()
	if TREENAME not in bpy.data.node_groups:
		node_group = bpy.data.node_groups.new(type="GeometryNodeTree", name=TREENAME)
		nodes = node_group.nodes
		links = node_group.links
		if bpy.app.version < (4,0,0):
			node_group.inputs.new("NodeSocketFloat","AngleLimitRadius")
		else:
			node_group.interface.new_socket(name="AngleLimitRadius",description="Do not change this value manually, set it from the chain object",in_out ="INPUT", socket_type="NodeSocketFloat")
		LENGTH = 10.0
		inNode = nodes.new('NodeGroupInput')
		inNode.location = (0,0)
		def math(operation,a,b = None,location = (0,0)):
			node = nodes.new('ShaderNodeMath')
			node.operation = operation
			node.location = location
			for index,value in enumerate((a,b)):
				if value is None:
					continue
				if isinstance(value,(int,float)):
					node.inputs[index].default_value = value
				else:
					links.new(value,node.inputs[index])
			return node.outputs[0]
		half = math("MULTIPLY",inNode.outputs["AngleLimitRadius"],0.5,(200,0))
		sine = math("SINE",half,None,(400,100))
		cosine = math("COSINE",half,None,(400,-100))
		radius = math("MULTIPLY",math("ABSOLUTE",sine,None,(600,100)),LENGTH,(800,100))
		depth = math("MULTIPLY",math("ABSOLUTE",cosine,None,(600,-100)),LENGTH,(800,-100))
		side = math("SIGN",cosine,None,(800,-300))
		coneNode = nodes.new('GeometryNodeMeshCone')
		coneNode.location = (1000,0)
		coneNode.inputs["Vertices"].default_value = 24
		coneNode.inputs["Radius Top"].default_value = 0.0
		links.new(radius,coneNode.inputs["Radius Bottom"])
		links.new(depth,coneNode.inputs["Depth"])
		offset = nodes.new('ShaderNodeCombineXYZ')
		offset.location = (1000,-250)
		links.new(depth,offset.inputs["X"])
		placeNode = nodes.new('GeometryNodeTransform')#the Mesh Cone stands on z = 0 with its tip at z = depth: tip to the origin, axis along +X
		placeNode.location = (1200,0)
		placeNode.inputs["Rotation"].default_value = (0.0,-1.570796,0.0)
		links.new(coneNode.outputs["Mesh"],placeNode.inputs["Geometry"])
		links.new(offset.outputs["Vector"],placeNode.inputs["Translation"])
		flip = nodes.new('ShaderNodeCombineXYZ')
		flip.location = (1200,-250)
		links.new(side,flip.inputs["X"])
		flip.inputs["Y"].default_value = 1.0
		flip.inputs["Z"].default_value = 1.0
		flipNode = nodes.new('GeometryNodeTransform')#a half angle over 90 degrees opens backwards
		flipNode.location = (1400,0)
		links.new(placeNode.outputs["Geometry"],flipNode.inputs["Geometry"])
		links.new(flip.outputs["Vector"],flipNode.inputs["Scale"])
		setMaterialNode = nodes.new('GeometryNodeSetMaterial')
		setMaterialNode.location = (1600,0)
		setMaterialNode.inputs["Material"].default_value = mat
		links.new(flipNode.outputs["Geometry"],setMaterialNode.inputs["Geometry"])
		outNode = nodes.new('NodeGroupOutput')
		outNode.location = (1800,0)
		if bpy.app.version < (3,4,0):
			outNode.inputs.new('NodeSocketGeometry', 'Geometry')
		elif bpy.app.version < (4,0,0):
			node_group.outputs.new('NodeSocketGeometry', 'Geometry')
		else:
			node_group.interface.new_socket(name="Geometry",description="",in_out ="OUTPUT", socket_type="NodeSocketGeometry")
		links.new(setMaterialNode.outputs["Geometry"],outNode.inputs["Geometry"])
		return node_group
	return bpy.data.node_groups[TREENAME]

def getConeGeoNodeTreeV1(isSubGroup = False):
	"""The previous angle limit cone, kept for scenes that still use it; Redraw All Chains replaces it."""
	if isSubGroup:
		TREENAME = "ChainConeSubGroupGeoNodeTreeV1"
		mat = getConeSubGroupMat()
	else:
		TREENAME = "ChainConeGeoNodeTreeV1"
		mat = getConeMat()
	
	if TREENAME not in bpy.data.node_groups:
		node_group = bpy.data.node_groups.new(type="GeometryNodeTree", name=TREENAME)
		nodes = node_group.nodes
		links = node_group.links
		
		currentXLoc = 0
		currentYLoc = 0
		if bpy.app.version < (4,0,0):
			node_group.inputs.new("NodeSocketFloat","AngleLimitRadius")
		else:
			node_group.interface.new_socket(name="AngleLimitRadius",description="Do not change this value manually, set it from the chain object",in_out ="INPUT", socket_type="NodeSocketFloat")
		
		
		inNode = nodes.new('NodeGroupInput')
		inNode.location = (currentXLoc,currentYLoc)
		
		currentXLoc += 300
		"""
		startObjInfoNode = nodes.new('GeometryNodeObjectInfo')
		startObjInfoNode.location = (currentXLoc,currentYLoc)
		#startObjInfoNode.inputs["Object"].default_value = startObj
		links.new(inNode.outputs["Start Object"],startObjInfoNode.inputs["Object"])
		
		currentXLoc += 300
		
		separateScaleXYZNode = nodes.new('ShaderNodeSeparateXYZ')
		separateScaleXYZNode.location = (currentXLoc,currentYLoc - 300)
		links.new(startObjInfoNode.outputs["Scale"],separateScaleXYZNode.inputs["Vector"])
		
		currentXLoc += 300
		"""
		coneNode = nodes.new('GeometryNodeMeshCone')
		coneNode.location = (currentXLoc,currentYLoc - 150)
		coneNode.inputs["Vertices"].default_value = 18
		#Passing the angle limit in radians directly to the bottom size isn't correct, but it's close enough to the correct value that it doesn't really matter
		links.new(inNode.outputs["AngleLimitRadius"],coneNode.inputs["Radius Bottom"])
		currentXLoc += 300
		
		transformNode = nodes.new('GeometryNodeTransform')
		transformNode.location = (currentXLoc,currentYLoc)
		transformNode.inputs["Translation"].default_value = (10.0,0.0,0.0)#Set x to 10 to line up the tip of the cone with the bone head
		transformNode.inputs["Rotation"].default_value = (0.0,-1.570796,0.0)#Rotate -90 to make the cone face the correct way
		transformNode.inputs["Scale"].default_value = (5.0,5.0,5.0)#Scale up to make it more visible
		#links.new(startObjInfoNode.outputs["Location"],instanceNode.inputs["Translation"])
		links.new(coneNode.outputs["Mesh"],transformNode.inputs["Geometry"])
		#links.new(separateScaleXYZNode.outputs["X"],transformNode.inputs["Scale"])
		
		
		currentXLoc += 300
		
		setMaterialNode = nodes.new('GeometryNodeSetMaterial')
		setMaterialNode.location = (currentXLoc,currentYLoc)
		setMaterialNode.inputs["Material"].default_value = mat
		links.new(transformNode.outputs["Geometry"],setMaterialNode.inputs["Geometry"])
		"""
		currentXLoc += 300
		
		
		setSmoothShadeNode = nodes.new('GeometryNodeSetShadeSmooth')
		setSmoothShadeNode.location = (currentXLoc,currentYLoc)
		links.new(setMaterialNode.outputs["Geometry"],setSmoothShadeNode.inputs["Geometry"])
		"""
		currentXLoc += 300
		outNode = nodes.new('NodeGroupOutput')
		outNode.location = (currentXLoc,currentYLoc)
		if bpy.app.version < (3,4,0):
			outNode.inputs.new('NodeSocketGeometry', 'Geometry')
		elif bpy.app.version < (4,0,0):
			node_group.outputs.new('NodeSocketGeometry', 'Geometry')
		else:
			node_group.interface.new_socket(name="Geometry",description="",in_out ="OUTPUT", socket_type="NodeSocketGeometry")
		links.new(setMaterialNode.outputs["Geometry"],outNode.inputs["Geometry"])
	else:
		node_group = bpy.data.node_groups[TREENAME]
	return node_group