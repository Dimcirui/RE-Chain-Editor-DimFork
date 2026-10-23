# Interface for other add-ons

What other add-ons can rely on: how chain, chain2 and CLSP data is stored in the scene, and the in-memory export in `wd_api`. The names below are a stable interface. Renaming one or changing what it means raises `wd_api.API_VERSION` and is recorded under [Changes](#changes).

Current `API_VERSION`: **1**.

## Collections

Every chain, chain2 or CLSP file is one root collection. Import and *Create Chain Header* create it; its custom properties are:

| Property | Value |
|---|---|
| `~TYPE` | `RE_CHAIN_COLLECTION` for .chain and .chain2, `RE_CLSP_COLLECTION` for .clsp. Written when the collection is created and never changed. |
| `~ASSETPATH` | Game path of the imported file, without `natives/STM/` and without the version number, e.g. `Art/Model/Character/ch03/039/001/2/ch03_039_0012.chain2`. Written on import when the file is inside a `natives` folder. Collections that were created new, or imported from outside a `natives` folder (including *Create Full Body CLSP*, which imports a bundled file), don't have it. |
| `BatchExport_path` | Full path of the last export (for RE Toolbox batch export). Not part of this interface. |

The file format is told by the collection name: a name ending in `.chain2` is chain2, `.chain` is the old format, `.clsp` is CLSP (Blender's `.001` suffixes are ignored). Older versions of *Create Chain Header* typed new CLSP collections `RE_CHAIN_COLLECTION`; `wd_api` exports those as CLSP because of their name.

All data of a file is on objects in the root collection or its child collections (`collection.all_objects`); nothing is stored on the scene, world or other collections. Child collections made by the editor (`Chain Collisions - …`, `Chain Links - …`, `Node Capsules - …`) only organise objects.

## wd_api

`wd_api` is a module in the add-on package (`RE-Chain-Editor-DimFork.wd_api` as a legacy add-on). It is imported when the add-on is enabled, so it is in `sys.modules`.

```python
API_VERSION = 1
COLLECTION_TYPES = ("RE_CHAIN_COLLECTION", "RE_CLSP_COLLECTION")

class ExportError(Exception): ...   # str(err): problems, one per line; err.problems: the same as a list

def export_bytes(collection, version=None) -> bytes: ...
```

- `collection`: a `bpy.types.Collection` (or its name) typed as above.
- `version`: the number at the end of the file name. `None` gives the MH Wilds version: chain2 **14**, CLSP **3**. Old-format .chain collections need an explicit version (MH Wilds doesn't use .chain).
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
| `RE_CHAIN_COLLISION_PLANE` | Plane (CLSP only) | none or the armature | `re_chain_chaincollision` | CLSP entry, shape 4 |
| `RE_CHAIN_LINK` | Chain link | header | `re_chain_chainlink` | Link |
| `RE_CHAIN_LINK_COLLISION` | Collision of one node pair of a link | link | `re_chain_chainlink_collision` | Link node |
| `RE_CHAIN_NODE_FRAME_HELPER`, `RE_CHAIN_NODE_CAPSULE` | Display only | | | not exported |

Single collisions and capsule roots also have `re_chain_collision_subdata` (chain collision subdata).

### Bones

Objects that follow a bone have a Child Of constraint named `BoneName`; its `subtarget` is the bone. Joint hashes in the file are `pymmh3.hash_wide(bone name)`. A subtarget `HASH_<number>` (CLSP; a bone missing from the armature) is written as that number. In chain collisions a `b<digits>:` prefix on the bone name is dropped before hashing. A CLSP plane without the constraint hangs from the armature object (joint hash `0x81F16F39`).

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

A capsule whose start and end radii differ is written as a tapered capsule (shape `5`) in chain2 and .chain version 46 and later; older .chain versions get a plain capsule (shape `2`). `collisionOffset`, `radius`, `endCollisionOffset` mirror the objects for the UI; export reads the objects.

CLSP entries:

| Property / object | CLSP field |
|---|---|
| `chainCollisionShape` | `chainCollisionShape`: `"1"` sphere → 0, `"2"` capsule → 1, `"5"` tapered capsule → 3, `"4"` plane → 4; other shapes are skipped |
| `clspBitFlag0`, `clspBitFlag1` | `unknBitFlag0`, `unknBitFlag1` |
| sphere: object `location`, `scale[0]`; `endCollisionOffset` | `x1/y1/z1`, `collisionCapsuleStartRadius`; `x2/y2/z2` |
| capsule: start `location`, end `location`, start `scale[0]` | `x1/y1/z1`, `x2/y2/z2`, `collisionSphereRadius` (capsule) or `collisionCapsuleStartRadius` (tapered) |
| tapered capsule: end `scale[0]` | `collisionCapsuleEndRadius` |
| plane: object `matrix_basis` (own transform) | normal in `x1/y1/z1`, distance in `collisionCapsuleStartRadius` |

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
