import sys
import filecmp
import os
from datetime import datetime

# Global static variables
global logFileName, syncInterval

def main():
  # Check if the correct number of arguments is provided
  # if len(sys.argv) < 4 or len(sys.argv) > 5:
  #   print("Usage: python folderSync.py <sourcePath> <replicaPath> <syncInterval> [logFileName]")
  #   sys.exit(1)
  global logFileName
  global syncInterval

  # Get the argument from the command line
  # syncInterval = sys.argv[3]
  # Optional argument declaration
  if len(sys.argv) == 5:
    logFileName = sys.argv[4]
  else:
    dateTimeNow = datetime.now()
    formatted_datetime = dateTimeNow.strftime("%Y-%m-%d_%H-%M-%S")
    logFileName = "replicaLog_%s" %formatted_datetime

def compareDirs(dir1Obj, dir2Obj, currentPath=''):
  for entry, content in dir1Obj.items():
    entry_path = os.path.join(currentPath, entry)
    if entry not in dir2Obj:
      print("Warning: %s exists in the first structure but not in the second." % entry_path)
    elif content != dir2Obj[entry]:
      print("Warning: %s has different type in the second structure." % entry_path)
    else:
      print("Entry %s at the same position" % entry_path)
    
    if isinstance(content, dict):
      # Recursively compare subdirectories
      sub_path = os.path.join(currentPath, entry)
      compareDirs(content, dir2Obj.get(entry, {}), currentPath=sub_path)

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
  # sourceFolder = folderInfo(sys.argv[1])
  sourceFolder = folderInfo('source')
  # replicaFolder = folderInfo(sys.argv[2])
  replicaFolder = folderInfo('replica')
  # comparison = filecmp.cmp(sourceFolder.folderPath, replicaFolder.folderPath, shallow = False)
  compareDirs(sourceFolder.files, replicaFolder.files)

  # Add this line to keep the console window open
  input("Press Enter to exit...")