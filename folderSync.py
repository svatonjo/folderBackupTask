import sys
import filecmp
import os
import shutil
from datetime import datetime

# Global static variables
global logFileName, syncInterval

def main():
  # Check if the correct number of arguments is provided
  if len(sys.argv) < 4 or len(sys.argv) > 5:
    print("Usage: python folderSync.py <sourcePath> <replicaPath> <syncInterval> [logFileName]")
    sys.exit(1)
  global logFileName
  global syncInterval

  # Get the argument from the command line
  syncInterval = sys.argv[3]
  # Optional argument declaration
  if len(sys.argv) == 5:
    logFileName = sys.argv[4]
  else:
    dateTimeNow = datetime.now()
    formatted_datetime = dateTimeNow.strftime("%Y-%m-%d_%H-%M-%S")
    logFileName = "replicaLog_%s" %formatted_datetime

def compareDirs(dir1Obj, dir2Obj):
  for entry, content in dir1Obj.files.items():
    entry_path1 = os.path.join(dir1Obj.folderPath, entry)
    entry_path2 = os.path.join(dir2Obj.folderPath, entry)
    if entry not in dir2Obj.files:
      print("Warning: %s exists in the first structure but not in the second." % entry_path1)
      if content != 'File':
        shutil.copytree(entry_path1, entry_path2)
      else:
        shutil.copy(entry_path1, entry_path2)
    else:
      print("Entry %s at the same position" % entry_path1)
      if content == 'File':
        comparison = filecmp.cmp(entry_path1, entry_path2, shallow=True)

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
      print("Warning: %s exists in the first structure but not in the second." % entry_path1)
      if content != 'File':
        try:
          shutil.rmtree(entry_path1)
          print(f"Directory '{entry_path1}' removed successfully.")
        except OSError as e:
            print(f"Error removing directory '{entry_path1}': {e}")
      else:
        try:
          os.remove(entry_path1)
          print(f"File '{entry_path1}' removed successfully.")
        except OSError as e:
          print(f"Error removing file '{entry_path1}': {e}")

    if isinstance(content, dict):
      # Recursively compare subdirectories
      subDir1obj = folderInfo(entry_path1)
      subDir2obj = folderInfo(entry_path2)
      compareDirs(subDir1obj, subDir2obj)

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
    self.files = build_directory_structure(self.folderPath)

if __name__ == "__main__":
  main()
  sourceFolder = folderInfo(sys.argv[1])
  replicaFolder = folderInfo(sys.argv[2])
  compareDirs(sourceFolder, replicaFolder)
  compareDirsRemove(replicaFolder, sourceFolder)
