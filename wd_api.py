#Exports chain, chain2 and CLSP collections to bytes in memory, for other add-ons to call
#Callers find it in sys.modules by the name ending in .wd_api and check COLLECTION_TYPES and API_VERSION
#The object types and properties these files are made from are listed in docs/wd-interface.md
import io

import bpy

from .modules.blender_re_chain import chainStructureErrors,buildChainFile
from .modules.blender_re_clsp import clspStructureErrors,buildCLSPFile
from .modules.re_chain_type_sync import chainFileTypeForCollection

API_VERSION = 1
COLLECTION_TYPES = ("RE_CHAIN_COLLECTION","RE_CLSP_COLLECTION")

#File version used when export_bytes is not given one: the version MH Wilds reads
#The old .chain format isn't used by MH Wilds, so it has none
DEFAULT_VERSIONS = {"chain2":14,"clsp":3}

class ExportError(Exception):
	"""Export failed. The message lists the problems one per line, readable as is; .problems holds them as a list."""
	def __init__(self,problems):
		if isinstance(problems,str):
			problems = [problems]
		self.problems = list(problems)
		super().__init__("\n".join(self.problems))

def collectionFormat(collection):
	#"clsp", "chain2" or "chain"
	collectionType = collection.get("~TYPE")
	if collectionType == "RE_CLSP_COLLECTION":
		return "clsp"
	if collectionType != "RE_CHAIN_COLLECTION":
		raise ExportError(f"{collection.name} is not a chain or CLSP collection (~TYPE is {collectionType!r}).")
	fileType = chainFileTypeForCollection(collection.name)
	if fileType == None:
		#Older versions of Create Chain Header typed new CLSP collections as chains; a chain collection renamed without .chain is taken as chain2
		return "clsp" if ".clsp" in collection.name else "chain2"
	return fileType

def export_bytes(collection,version = None):
	"""Export a chain, chain2 or CLSP collection and return the file's bytes.

	collection is a bpy.types.Collection (or its name) typed RE_CHAIN_COLLECTION or RE_CLSP_COLLECTION.
	version is the file version (the number at the end of the file name); None gives the MH Wilds version
	(chain2 14, CLSP 3). An old-format .chain collection needs a version.

	Writes no files and changes nothing in the scene: the file is made from the objects' own location,
	rotation and scale and their properties, not from constraint-driven world matrices, so playback doesn't
	change it. The result is what Export RE Chain2 / Export RE CLSP would write for the same collection.
	Raises ExportError with a readable list of problems when the collection can't be exported.
	"""
	if isinstance(collection,str):
		collectionName = collection
		collection = bpy.data.collections.get(collectionName)
		if collection == None:
			raise ExportError(f"There is no collection named {collectionName}.")
	if not isinstance(collection,bpy.types.Collection):
		raise ExportError(f"Expected a collection, got {type(collection).__name__}.")
	fileFormat = collectionFormat(collection)
	if version == None:
		version = DEFAULT_VERSIONS.get(fileFormat)
		if version == None:
			raise ExportError(f"{collection.name} is an old-format .chain collection, which MH Wilds doesn't use. Pass the chain version to export it.")
	try:
		version = int(version)
	except (TypeError,ValueError):
		raise ExportError(f"Invalid file version: {version!r}.") from None

	#Warnings (skipped subgroups or collisions) don't stop the export and aren't printed: this can run on every scene update
	warnings = []
	try:
		if fileFormat == "clsp":
			problems = clspStructureErrors(collection)
			if problems:
				raise ExportError(problems)
			fileData = buildCLSPFile(collection,version,fixScene = False,warn = warnings.append)[0]
		else:
			problems = chainStructureErrors(collection,warn = warnings.append)
			if problems:
				raise ExportError(problems)
			fileData = buildChainFile(collection,version,isChain2 = fileFormat == "chain2",fixScene = False,warn = warnings.append)
		stream = io.BytesIO()
		fileData.write(stream)
	except ExportError:
		raise
	except Exception as err:
		raise ExportError(f"{collection.name} could not be exported: {type(err).__name__}: {err}") from err
	return stream.getvalue()
