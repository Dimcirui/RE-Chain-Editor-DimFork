# Interface for other add-ons

What other add-ons can rely on: how chain, chain2 and CLSP data is stored in the scene, and the in-memory export in `wd_api`. The names below are a stable interface. Renaming one or changing what it means raises `wd_api.API_VERSION` and is recorded under [Changes](#changes).

Current `API_VERSION`: **2**.

## Collections

Every chain, chain2 or CLSP file is one root collection. Import and *Create Chain Header* create it; its custom properties are:

| Property | Value |
|---|---|
| `~TYPE` | `RE_CHAIN_COLLECTION` for .chain and .chain2, `RE_CLSP_COLLECTION` for .clsp. Written when the collection is created and never changed, with one exception: the CLSP fix below. |
| `~ASSETPATH` | Game path of the collection's file, without `natives/<platform>/` and without the version number, e.g. `Art/Model/Character/ch03/039/001/2/ch03_039_0012.chain2`. Written on import when the file is inside a `natives` folder. After each successful export to a file (Export RE Chain / Chain2 / CLSP, including batch exports that run these), it follows the export target: set to the target's game path when the target is inside a `natives` folder, removed when it isn't, and left alone when unchanged. `wd_api.export_bytes` never changes it. Collections that were created new and never exported, or imported from outside a `natives` folder (including *Create Full Body CLSP*, which imports a bundled file), don't have it. |
| `BatchExport_path` | Full path of the last export (for RE Toolbox batch export). Not part of this interface. |

The file format is told by the collection name: a name ending in `.chain2` is chain2, `.chain` is the old format, `.clsp` is CLSP (Blender's `.001` suffixes are ignored).

Older versions of *Create Chain Header* typed new CLSP collections `RE_CHAIN_COLLECTION`. When a .blend is opened, and once when the add-on is enabled, such collections are retyped `RE_CLSP_COLLECTION`. Only a collection that is certainly a CLSP is retyped: its name ends in `.clsp`, it has no `RE_CHAIN_HEADER` object, and it has at least one collision object (`RE_CHAIN_COLLISION_SINGLE`, `RE_CHAIN_COLLISION_CAPSULE_ROOT`, `RE_CHAIN_COLLISION_PLANE` or `RE_CHAIN_COLLISION_BOX`). Each retyped collection is printed to the console. A mistyped collection that fails these checks (for example, an empty one) keeps its type; `wd_api` still exports it as CLSP because of its name.

All data of a file is on objects in the root collection or its child collections (`collection.all_objects`); nothing is stored on the scene, world or other collections. Child collections made by the editor (`Chain Collisions - …`, `Chain Links - …`, `Node Capsules - …`) only organise objects.

## wd_api

`wd_api` is a module in the add-on package (`RE-Chain-Editor-DimFork.wd_api` as a legacy add-on). It is imported when the add-on is enabled, so it is in `sys.modules`.

```python
API_VERSION = 2
COLLECTION_TYPES = ("RE_CHAIN_COLLECTION", "RE_CLSP_COLLECTION")

class ExportError(Exception): ...   # str(err): problems, one per line; err.problems: the same as a list

def export_bytes(collection, version=None, as_format=None) -> bytes: ...
```

- `collection`: a `bpy.types.Collection` (or its name) typed as above.
- `version`: the number at the end of the file name. `None` gives the MH Wilds version: chain2 **14**, CLSP **3**. Old-format .chain collections need an explicit version (MH Wilds doesn't use .chain), unless `as_format` turns them into chain2 or CLSP.
- `as_format`: `None` writes the collection's own format. `"chain2"` writes a chain collection of either format as chain2. For an old-format .chain, the group attribute flags (each group's `attrFlags` and each chain settings' `groupDefaultAttr`) are moved to their chain2 bits: the two formats put them on different bits (Scene Colliders is `0x20000` in .chain and `0x10000` in chain2, Extra Tail Node `0x4` and `0x20000`). A flag chain2 doesn't have is dropped; a bit neither format names is kept. Fields only chain2 has take the objects' property values; fields only .chain has are left out. `"clsp"` writes the collision objects of a chain collection (either format) as a CLSP file, with each collision object's CLSP flags as its mask. A CLSP collection can't be exported as another format.
- Returns exactly the bytes *Export RE Chain2* / *Export RE CLSP* would write for the same collection.
- Writes no files and changes nothing: not the selection, active object, mode, frame, object names or properties. Export normally writes a few fixes back to the scene (unique wind/chain settings IDs, tapered capsule shapes, missing MH Wilds setting subdata, collision UI values); `export_bytes` works out the same result without writing them.
- Reads only each object's own `location`, rotation and `scale` (never constraint-driven world matrices) and its properties, so animation playback doesn't change the result.
- Raises `ExportError` when the collection can't be exported (wrong `~TYPE`, broken chain structure, missing header). A CLSP collection needs no chain header.
- Warnings that don't stop export (a skipped subgroup or unsupported CLSP shape) are not printed.
- Takes a few milliseconds for a CLSP and about 70 ms for a 600-object chain2.

## Objects

Every object the editor makes has a custom property `TYPE`. Records of the same kind are written in the order of their object names, except chain settings, which are sorted by ID afterwards.

| `TYPE` | What it is | Parent | Property group | File record |
|---|---|---|---|---|
| `RE_CHAIN_HEADER` | Chain header, one per chain collection (none in CLSP) | none | `re_chain_header` | Header |
| `RE_CHAIN_WINDSETTINGS` | Wind settings | header | `re_chain_windsettings` | Wind settings |
| `RE_CHAIN_CHAINSETTINGS` | Chain settings | header or wind settings | `re_chain_chainsettings` | Chain settings |
| `RE_CHAIN_CHAINGROUP` | Chain group | chain settings | `re_chain_chaingroup` | Chain group |
| `RE_CHAIN_SUBGROUP` | Chain subgroup | chain settings | `re_chain_chainsubgroup` | Subgroup of a chain group |
| `RE_CHAIN_NODE` | Chain node; the first is a child of the group (or subgroup), each next node a child of the previous one | group, subgroup or node | `re_chain_chainnode` | Node |
| `RE_CHAIN_NODE_FRAME` | Angle limit frame of a node, exactly one per node | node | none | Node angle limit direction |
| `RE_CHAIN_JIGGLE` | Jiggle of a node | node | `re_chain_chainjiggle` | Node jiggle data |
| `RE_CHAIN_COLLISION_SINGLE` | Single-joint collision (sphere and similar) | header (chain) / none (CLSP) | `re_chain_chaincollision` | Collision / CLSP entry |
| `RE_CHAIN_COLLISION_CAPSULE_ROOT` | Two-joint capsule, holds the properties | header (chain) / none (CLSP) | `re_chain_chaincollision` | Collision / CLSP entry |
| `RE_CHAIN_COLLISION_CAPSULE_START` | Capsule start | capsule root | none | Joint, position, radius |
| `RE_CHAIN_COLLISION_CAPSULE_END` | Capsule end | capsule root | none | Pair joint, pair position, end radius |
| `RE_CHAIN_COLLISION_PLANE` | Plane: a wire square, normal along local Z (CLSP) or local Y (chain, custom property `planeNormalAxis` = `"Y"`) | header (chain) / none or the armature (CLSP) | `re_chain_chaincollision` | Collision shape 4 / CLSP entry, shape 4 |
| `RE_CHAIN_COLLISION_BOX` | Box (OBB): a wire cube from -1 to 1 | header (chain) / none or the armature (CLSP) | `re_chain_chaincollision` | Collision shape 3 / CLSP entry, shape 2 |
| `RE_CHAIN_LINK` | Chain link | header | `re_chain_chainlink` | Link |
| `RE_CHAIN_LINK_COLLISION` | Collision of one node pair of a link | link | `re_chain_chainlink_collision` | Link node |
| `RE_CHAIN_NODE_FRAME_HELPER`, `RE_CHAIN_NODE_CAPSULE` | Display only | | | not exported |

Single collisions and capsule roots also have `re_chain_collision_subdata` (chain collision subdata).

### Bones

Objects that follow a bone have a Child Of constraint named `BoneName`; its `subtarget` is the bone. Joint hashes in the file are `pymmh3.hash_wide(bone name)`. A subtarget `HASH_<number>` (CLSP; a bone missing from the armature) is written as that number. A `b<digits>:` prefix on the bone name is dropped before hashing (chain collisions and, since API 2, CLSP shapes). A plane or box without the constraint has joint hash `0x81F16F39` (the owner): a CLSP one hangs from the armature object, a chain one from the chain header, and its transform is in that object's space, Blender z up, written y up.

### IDs and links between records

- Chain settings `windID`: the parent wind settings' `id` when parented to one, else `re_chain_chainsettings.fileWindID`.
- Chain group `settingID`: the parent chain settings' `id`. Group `windID`: `re_chain_chaingroup.fileWindID` when the object has the custom property `windIDFromFile` (set on import) or no wind settings grandparent; otherwise the grandparent wind settings' `id`.
- Subgroup: `re_chain_chainsubgroup.subGroupID`, `parentGroup` (pointer to the chain group object), `settingID` from its parent chain settings. Subgroups are written in `subGroupID` order and need as many nodes as their group.
- Group `terminateNodeNameHash`: hash of the last node's `BoneName` subtarget.
- Link `terminateNodeNameHashA/B`: the terminate hash of the group named by `re_chain_chainlink.chainGroupAObject` / `chainGroupBObject` (object names), or the number itself if the field holds digits.
- A wind or chain settings `id` used twice goes up by one until unique (the same rule export always applied).

## Property groups

Each table lists the properties export reads, with the field they become in the file (field names as in `modules/file_re_chain2.py` / `file_re_chain.py` / `file_re_clsp.py`). "Same" means the file field has the property's name. Enum properties hold the number as a string and are written as that integer. Properties not listed are editor-only (display, presets, clipboard).

### `re_chain_header` (header)

| Property | File field |
|---|---|
| `errFlagBits` | `errFlags` |
| `masterSize`, `rotationOrder`, `defaultSettingIdx`, `calculateMode`, `chainAttrFlags`, `parameterFlag`, `calculateStepTime`, `modelCollisionSearch` | same |
| `collisionFilterHitBits0` … `collisionFilterHitBits7` | `collisionFilterHit0` … `collisionFilterHit7` |
| `legacyVersion` | same (.chain only) |
| `highFPSCalculateMode`, `freeLinkJoint`, `taperedCollideMethod`, `wilds_unkn1`, `wilds_unkn2` | same (chain2 only) |
| `restartIterationsAlt` | `wilds_unkn0` (chain2 only) |

`version` is the export version and the record counts come from the objects; the `version` property is only display.

### `re_chain_windsettings` (wind settings)

| Property | File field |
|---|---|
| `id`, `windDirection`, `windCount`, `windType`, `randomDamping`, `randomDampingCycle`, `randomCycleScaling` | same |
| `dir0` … `dir4` (vectors) | `dir0X/Y/Z` … `dir4X/Y/Z` |
| `min0`…`min4`, `max0`…`max4`, `phaseShift0`…`phaseShift4`, `cycle0`…`cycle4`, `interval0`…`interval4` | same |

### `re_chain_chainsettings` (chain settings)

| Property | File field |
|---|---|
| `id`, `colliderFilterInfoPath`, `settingsAttrFlags`, `damping`, `secondDamping`, `secondDampingSpeed`, `minDamping`, `secondMinDamping`, `dampingPow`, `secondDampingPow`, `collideMaxVelocity`, `springForce`, `springLimitRate`, `springMaxVelocity`, `springCalcType`, `windDelayType`, `reduceSelfDistanceRate`, `secondReduceDistanceRate`, `secondReduceDistanceSpeed`, `friction`, `shockAbsorptionRate`, `coefOfElasticity`, `coefOfExternalForces`, `stretchInteractionRatio`, `angleLimitInteractionRatio`, `groupDefaultAttr`, `windEffectCoef`, `velocityLimit`, `hardness`, `windDelaySpeed`, `envWindEffectCoef`, `motionForce` | same |
| `gravity` (vector) | `gravityX/Y/Z` |
| `fileWindID` | `windID` when not parented to wind settings |
| `sprayParameterArc`, `sprayParameterFrequency`, `sprayParameterCurve1`, `sprayParameterCurve2`, `chainType`, `muzzleDirection`, `shootingElasticLimitRate` | same (.chain only) |
| `muzzleVelocity` (vector) | `muzzleVelocityX/Y/Z` (.chain only) |
| `motionForceCalcType`, `elasticLimit` | same (chain2 only) |
| `motionForceCalcTypeTail` | `padding` (chain2 only) |
| `unknQuaternion[0..3]`, `unknPos[0..2]` | `subDataUnkn0..3`, `subDataUnkn4..6` (chain2 only) |
| `subDataList_items[i].values` (7 ints) | subdata entry `unkn0, unkn1A, unkn1B, unkn1C, unkn1D, unkn2, unkn3` (chain2 only). Empty on a version 14 export: the two MH Wilds defaults are written. |

### `re_chain_chaingroup` (chain group)

| Property | File field |
|---|---|
| `rotationOrder`, `autoBlendCheckNodeNo`, `attrFlags`, `tag0`…`tag3`, `hierarchyHash0`…`hierarchyHash3`, `dampingNoise0`, `dampingNoise1`, `endRotConstMax`, `tagCount`, `angleLimitDirectionMode`, `clspFlags0`, `clspFlags1` | same |
| `fileWindID` | `windID` (see above) |
| `collisionFilterFlags` | same (.chain only) |
| `extraNodeLocalPos` (vector) | `extraNodeLocalPosX/Y/Z` (.chain only) |
| `interpCount`, `nodeInterpolationMode` | same (chain2 only) |

### `re_chain_chainnode` (node)

| Property | File field |
|---|---|
| `angleLimitRad`, `angleLimitDistance`, `angleLimitRestitution`, `angleLimitRestituteStopSpeed`, `collisionFilterFlags`, `capsuleStretchRate0`, `capsuleStretchRate1`, `attrFlags`, `windCoef`, `angleMode`, `collisionShape`, `attachType`, `rotationType`, `gravityCoef` | same |
| `collisionRadius` | `collisionRadius`, multiplied by the node object's `scale[0]` |
| `constraintJntName` | `constraintJntNameHash`: hashed, or the number if digits, 0 if empty |
| `jointHash` | `jointHash` the same way (chain2 only) |
| `basePos` (vector) | `basePos` (chain2 only) |
| frame object rotation | `angleLimitDirectionX/Y/Z/W`: the `RE_CHAIN_NODE_FRAME` child's rotation as a quaternion, in whatever `rotation_mode` it uses |

### `re_chain_chainjiggle` (node jiggle)

| Property | File field |
|---|---|
| `rangeShape`, `springForce`, `gravityCoef`, `damping`, `attrFlags`, `windCoef` | same |
| object `scale` | `rangeX/Y/Z` |
| object `location` | `rangeOffsetX/Y/Z` |
| object `rotation_quaternion` (w, x, y, z) | `rangeAxisW/X/Y/Z` |

### `re_chain_chaincollision` (chain collision and CLSP entry)

Chain collisions (chain and chain2):

| Property | File field |
|---|---|
| `rotationOrder`, `lerp`, `chainCollisionShape`, `subDataCount`, `collisionFilterFlags` | same |
| `endRadius` | `endRadius` (for a tapered capsule, shape `5`: the end object's `scale[0]`) |
| `endCollisionOffset` | `pairPosX/Y/Z` of a single collision |
| single: object `location`, `scale[0]`, `rotation_quaternion` | `posX/Y/Z`, `radius`, `rotOffsetX/Y/Z/W` |
| capsule: start object `location`, `scale[0]`, `rotation_quaternion`; end object `location` | `posX/Y/Z`, `radius`, `rotOffset…`; `pairPosX/Y/Z` |
| box (shape `3`): object `location`, `rotation_quaternion`, `scale` | `posX/Y/Z` (centre), `rotOffsetX/Y/Z/W`, `pairPosX/Y/Z` (half extents). `radius` and `endRadius` keep the properties' values |
| plane (shape `4`): object `location`, `rotation_quaternion`; `endCollisionOffset` | `posX/Y/Z` (a point on the plane), `rotOffsetX/Y/Z/W` (the normal is its +Y), `pairPosX/Y/Z`. A plane with `planeNormalAxis` unset (a CLSP plane object) is turned so its local Z is written as +Y |
| box, plane: custom property `pairJoint` | `pairJointNameHash`, as for CLSP spheres below; none is `0` |
| box, plane with no joint: custom property `ownerJointHash` | `jointNameHash`: `0x81F16F39` or `0` (both mean the owner in shipped files), stored as a signed 32-bit int (Blender's int properties) and written `& 0xFFFFFFFF`; missing is `0x81F16F39` |
| custom property `fileRotationOrder` | `rotationOrder` when the file's value isn't one of the enum's (shipped files have `0xFFFFFFFF`), stored signed like `ownerJointHash`; written while `rotationOrder` is left at `"0"` |

A capsule whose start and end radii differ is written as a tapered capsule (shape `5`) in chain2 and .chain version 46 and later; older .chain versions get a plain capsule (shape `2`). `collisionOffset`, `radius`, `endCollisionOffset` mirror the objects for the UI; export reads the objects.

CLSP entries:

| Property / object | CLSP field |
|---|---|
| `chainCollisionShape` | `chainCollisionShape`: `"1"` sphere → 0, `"2"` capsule → 1, `"5"` tapered capsule → 3, `"3"` box (OBB) → 2, `"4"` plane → 4; any other shape, or a shape on another kind of object (an OBB or plane `RE_CHAIN_COLLISION_SINGLE` from a chain file), is skipped |
| `clspBitFlag0`, `clspBitFlag1` | `unknBitFlag0`, `unknBitFlag1` |
| sphere: object `location`, `scale[0]`; `endCollisionOffset` | `x1/y1/z1`, `collisionCapsuleStartRadius`; `x2/y2/z2` |
| sphere: custom property `pairJoint` | `pairJointNameHash`: a bone name (or `HASH_<number>`), `"<self>"` for the sphere's own bone, missing or empty for none (`0x81F16F39`). Import sets it from the file; what the game does with a sphere's pair joint is unknown |
| capsule: start `location`, end `location`, start `scale[0]` | `x1/y1/z1`, `x2/y2/z2`, `collisionSphereRadius` (capsule) or `collisionCapsuleStartRadius` (tapered) |
| tapered capsule: end `scale[0]` | `collisionCapsuleEndRadius` |
| plane: object `matrix_basis` (own transform) | normal (local Z, or local Y with `planeNormalAxis` = `"Y"`) in `x1/y1/z1`, distance in `collisionCapsuleStartRadius` |
| box: object `matrix_basis` without its scale; its `scale` | +0x20 to +0x5f: 4x4 matrix, translation in the last row (rows 0-2 the box's axes, row 3 its centre); +0x60: half extents. Both joint fields are the box's joint |

### `re_chain_collision_subdata` (chain collision subdata, when `subDataCount` is set)

| Property | File field |
|---|---|
| `pos`, `pairPos` (vectors) | `subData.posX/Y/Z`, `subData.pairPosX/Y/Z` |
| `rotOffset` (w, x, y, z) | `subData.rotOffsetW/X/Y/Z` |
| `radius`, `id`, `unknSubCollisionData0`…`unknSubCollisionData3` | same, under `subData` |

### `re_chain_chainlink` (link)

| Property | File field |
|---|---|
| `distanceShrinkLimitCoef`, `distanceExpandLimitCoef`, `linkMode`, `linkAttrFlags`, `skipGroupA`, `skipGroupB`, `linkOrder` | same |
| `connectFlagBits` | `connectFlags` |
| `clspFlags0`, `clspFlags1` | same (chain2 only) |
| `chainGroupAObject`, `chainGroupBObject` | `terminateNodeNameHashA/B` (see above) |

Its `RE_CHAIN_LINK_COLLISION` children, in name order, are the link's node entries; with none, `nodeCount` is group A's node count.

### `re_chain_chainlink_collision` (link node)

| Property | File field |
|---|---|
| `collisionRadius`, `collisionFilterFlags` | same |

## Changes

- **1**: first version.
- **1** (same API version, no rename): `~ASSETPATH` also follows the target of each file export, and is removed when a file is exported outside a `natives` folder. Before, only import wrote it.
- **1** (same API version): bug fix, the one exception to "`~TYPE` never changes". CLSP collections that older versions of *Create Chain Header* typed `RE_CHAIN_COLLECTION` are retyped `RE_CLSP_COLLECTION` when a file is opened or the add-on is enabled (see [Collections](#collections) for the exact checks). New CLSP collections are typed correctly from the start.
- **2**: `export_bytes` takes `as_format` (`"chain2"`, `"clsp"`). Calls without it give the same bytes as before.
- **2** (same API version, addition): CLSP boxes (shape 2) are imported as `RE_CHAIN_COLLISION_BOX` objects and exported. Before, import dropped them. A sphere's pair joint is kept in `pairJoint`; before, export always wrote none. Chain and chain2 OBBs (shape 3) and planes (shape 4) are imported as `RE_CHAIN_COLLISION_BOX` / `RE_CHAIN_COLLISION_PLANE` objects too; before, they were `RE_CHAIN_COLLISION_SINGLE` spheres, or capsules when their pair joint was set. Bug fixes: a chain sphere's `pairPos` is imported into `endCollisionOffset` (export wrote 0 before), and a collision with a `rotationOrder` outside the enum no longer stops the import. CLSP joint hashes drop a `b<digits>:` bone name prefix, as import already matched them.
