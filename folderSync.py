import sys
import filecmp
import os
import shutil
import time
import logging
from datetime import datetime

def main():
  # Check if the correct number of arguments is provided
  if len(sys.argv) < 4 or len(sys.argv) > 5:
    print("Usage: python folderSync.py <sourcePath> <replicaPath> <syncInterval> [logFileName]")
    sys.exit(1)

  # Global static variables
  global logFileName, syncInterval

  # Get the argument from the command line
  try:
    syncInterval = float(sys.argv[3])
  except: 
    print("Usage: python folderSync.py <sourcePath> <replicaPath> <syncIntervalNumber> [logFileName]")
    sys.exit(1)

  # Optional argument for logFile declaration
  if len(sys.argv) == 5:
    logFileName = sys.argv[4]
  else:
    dateTimeNow = datetime.now()
    formatted_datetime = dateTimeNow.strftime("%Y-%m-%d_%H-%M-%S")
    logFileName = "replicaLog_%s" %formatted_datetime

  logging.basicConfig(filename=logFileName, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
  writeLog('Sync script initialized.')

def writeLog(textStr):
  print(textStr)
  logging.info(textStr)

def compareDirs(dir1Obj, dir2Obj):
  for entry, content in dir1Obj.files.items():
    entry_path1 = os.path.join(dir1Obj.folderPath, entry)
    entry_path2 = os.path.join(dir2Obj.folderPath, entry)
    if entry not in dir2Obj.files:
      if content != 'File':
        shutil.copytree(entry_path1, entry_path2)
        writeLog('New Source folder %s copied to Replica folder' % entry)
      else:
        shutil.copy(entry_path1, entry_path2)
        writeLog('New Source file %s copied to Replica folder' % entry)
    else:
      if content == 'File':
        comparison = filecmp.cmp(entry_path1, entry_path2, shallow=True)
        if not comparison:
          shutil.copy(entry_path1, entry_path2)
          writeLog("Source file %s is different from replica folder. Copied to Replica folder" % entry)

    if isinstance(content, dict):
      # Recursively compare subdirectories
      subDir1obj = folderInfo(entry_path1)
      subDir2obj = folderInfo(entry_path2)
      compareDirs(subDir1obj, subDir2obj)

def compareDirsRemove(dir1Obj, dir2Obj):
  for entry, content in dir1Obj.files.items():
    entry_path1 = os.path.join(dir1Obj.folderPath, entry)
    entry_path2 = os.path.join(dir2Obj.folderPath, entry)

    if entry not in dir2Obj.files:
      if content != 'File':
        try:
          shutil.rmtree(entry_path1)
          writeLog("Old directory %s removed from Replica folder." % entry)
        except OSError as e:
          writeLog("Error removing directory %s from Replica folder: %s" % (entry, e))
      else:
        try:
          os.remove(entry_path1)
          writeLog("Old file %s removed from Replica folder." % entry)
        except OSError as e:
          writeLog("Error removing file %s from Replica folder: %s" % (entry, e))
    else:
      if isinstance(content, dict):
        # Recursively compare subdirectories
        subDir1obj = folderInfo(entry_path1)
        subDir2obj = folderInfo(entry_path2)
        compareDirsRemove(subDir1obj, subDir2obj)

def build_directory_structure(directory):
  directory_structure = {}
  with os.scandir(directory) as entries:
    for entry in entries:
      entry_path = entry.path
      if entry.is_file():
        # Add file to the structure
        directory_structure[entry.name] = "File"
      elif entry.is_dir():
        # Recursively build structure for subdirectory
        subdirectory_structure = build_directory_structure(entry_path)
        # Add subdirectory structure to the main structure
        directory_structure[entry.name] = subdirectory_structure
  return directory_structure

class folderInfo:
  def __init__(self, folderPath):
    # Convert the path to an absolute path
    self.folderPath = os.path.abspath(folderPath)
    # Check if the folder exists, and create it if not
    if not os.path.exists(self.folderPath):
        os.makedirs(self.folderPath)
    self.files = build_directory_structure(self.folderPath)

if __name__ == "__main__":
  main()

  while True:
    # obj needs an update for each interval
    sourceFolder = folderInfo(sys.argv[1])
    replicaFolder = folderInfo(sys.argv[2])
    # Folder-Sync
    compareDirs(sourceFolder, replicaFolder)
    compareDirsRemove(replicaFolder, sourceFolder)
    time.sleep(syncInterval)
