# RE-Chain-Editor-DimFork

A fork of [RE Chain Editor](https://github.com/NSACloud/RE-Chain-Editor), focused on Monster Hunter Wilds
chain2 and clsp. See the original repository for installation and usage.

> **AI-assisted project.** Most of the code and the file-format research in this fork were
> written with the help of an AI coding assistant (Anthropic's Claude), and reviewed, tested and
> directed by the maintainer. Format conclusions are checked against vanilla game files, but please
> report anything that looks wrong.

## What this fork changes

**Chain links**

- Node pairs follow Link Mode and Skip Group A / B as MH Wilds builds them.
- Link collisions are drawn as spheres at the middle of each node pair, with a dashed guide line.
- The link panel shows how the game builds the link and which collision switches apply.

**Angle limits**

- Cones are drawn on the parent bone at the full cone angle, shaped by Angle Mode.
- *Apply Angle Limit Ramp* has a Reverse option, ramping from the tip toward the root.

**Collisions**

- CLSP plane colliders: import and export.
- *Create Full Body CLSP* (Pose Mode panel) creates the full body CLSP of the MH Wilds player skeleton.
- CLSP Flags A of groups and links can be set by ticking body parts of that CLSP.

**Editing**

- Bit flag fields (Connection Flags, Link Attribute Flags, Error Flags, Chain Attribute Flags,
  Collision Hit Flags, CLSP Flags A) are set with tick boxes.
- Fields that another setting turns off are greyed out.
- Fields use the game's own names where it has one, otherwise names that say what they do, and their
  tooltips describe what each field does. *Preferences > Original RE Chain Editor names* brings back the
  original names.
- Chain presets: a setting, a group and a node saved and applied together.
- *Redraw All Chains* (Visibility panel) updates chains in older scenes to the current drawing.

**Files**

- MH Wilds chain2 export keeps the header and setting fields the original lost or misplaced
  (Elastic Limit, Motion Force Calc Type, the restart fields and others).
- Bone names with non-ASCII characters (e.g. Chinese) hash as the game does, matching RE Mesh Editor.
- The built-in updater is off.

## Credits

- **NSA Cloud**: the original [RE Chain Editor](https://github.com/NSACloud/RE-Chain-Editor).
- **alphaZomega**: RE2R, RE3R, RE8, RE2-3-7 RT, DMC5 and SF6 support in the original.
- **[Ridog8](https://github.com/Ridog8/RidogFork_RE-Chain-Editor)**: Onimusha: Way of the Sword support and a DD2 fix.
- **[chikichikibangbang](https://github.com/chikichikibangbang/MHWilds_Chain_Editor)** (MHWilds Chain Editor):
  the full body CLSP and the chain presets this fork carries over.
