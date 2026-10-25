#Collider Filter Info (.cfil) paths per game. A chain setting's cfil is a game file: a path the game doesn't have
#keeps the character loading forever, so export warns when the path is another game's
import json
import os
import re

#cfil_paths.json: for each game, the chain / chain2 versions and .cfil files of its file list, and the paths vanilla
#chains reference (known for RE4, MH Wilds, Onimusha and DMC5)
CFIL_TABLE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),"cfil_paths.json")
#Versions no file list has: the games the add-on names for them
VERSION_ALIASES = {("chain",35):["MHR"],("chain",54):["DD2"]}
_table = None

def cfilGames():
	global _table
	if _table is None:
		with open(CFIL_TABLE_PATH,encoding="utf-8") as file:
			_table = json.load(file)["games"]
	return _table

def normalizeCfilPath(path):
	"""Lowercase, forward slashes, without natives/<platform>/ and the file version, as the table stores them."""
	path = path.strip().replace("\\","/").lower()
	path = re.sub(r"^natives/[^/]+/","",path)
	return re.sub(r"(\.cfil)\.\d+$",r"\1",path)

def gamesForVersion(version,isChain2):
	fileType = "chain2" if isChain2 else "chain"
	games = [key for key,game in cfilGames().items() if version in game[fileType]]
	return games or VERSION_ALIASES.get((fileType,version),[])

def gamesWithCfil(path):
	path = normalizeCfilPath(path)
	return [key for key,game in cfilGames().items() if path in game["files"]]

def gameNames(keys):
	return ", ".join(cfilGames()[key]["name"] for key in keys)

def cfilWarnings(settingObjs,version,isChain2):
	"""One message per cfil path that is another game's file and not one of the games this version is for."""
	targets = gamesForVersion(version,isChain2)
	if not targets:
		return []
	byPath = {}
	for obj in settingObjs:
		path = obj.re_chain_chainsettings.colliderFilterInfoPath
		if path.strip():
			byPath.setdefault(path,[]).append(obj.name)
	messages = []
	for path,names in byPath.items():
		owners = gamesWithCfil(path)
		if owners and not set(owners) & set(targets):
			messages.append(f"{', '.join(names)}: Collider Filter Info {path} is a {gameNames(owners)} file, not {gameNames(targets)}. The game will keep loading forever; clear it or pick one with Set CFIL Path")
	return messages
