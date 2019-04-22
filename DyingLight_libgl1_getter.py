import os, re
import urllib.request
import subprocess
import tarfile
import shutil

home = os.path.expanduser("~")
steam_library = None
dyingLightLocation = None

#Locate steam install by finding library file
if os.path.isfile(f"{home}/.local/share/Steam/steamapps/libraryfolders.vdf"):
    steam_library = f"{home}/.local/share/Steam/steamapps/libraryfolders.vdf"
    steamapps_dir = f"{home}/.local/share/Steam/steamapps"
    steam_dir = f"{home}/.local/share/Steam"
    print(f"Found libraryfolders.vdf: {steam_library}")
elif  os.path.isfile(f"{home}/.steam/steam/steamapps/libraryfolders.vdf"):
    steam_library = f"{home}/.steam/steam/steamapps/libraryfolders.vdf"
    steamapps_dir = f"{home}/.steam/steam/steamapps"
    steam_dir = f"{home}/.steam"
    print(f"Found libraryfolders.vdf: {steam_library}")
    
#Now to find "Dying Light"
if steam_library != None:
    libraries=[]
    
    for line in open(steam_library,'r'):
        stripline = line.lstrip()
        if stripline[1].isdigit():
            if os.path.isdir(re.findall(r'"([^"]*)"', line)[1]+"/steamapps/common"):
                libraries.append(re.findall(r'"([^"]*)"', line)[1]+"/steamapps/common")
    if not libraries:
        #user has no stored libraries, use default location
        libraries.append(steamapps_dir+"/common")
    #Search each library location looking for Dying Light
    for library in libraries:
        for game in (os.listdir(library)):
            if str(game) in "Dying Light":
                if os.path.isfile(f"{library}/{game}/DyingLightGame"):
                    dyingLightLocation = f"{library}/{game}"
                    print (f"Found game folder: {dyingLightLocation}")
                    
if dyingLightLocation == None:
    exit("No game(file) found, is it (fully) installed?")

#Download the library as a .deb package.
print("Downloading library...")

downloadURL = "http://repo.steampowered.com/steamos/pool/main/m/mesa/libgl1-mesa-glx_13.0.2-3+bsos1_amd64.deb"
downloadName = "libgl1-mesa-glx_13.0.2-3+bsos1_amd64.deb"
downloadLocation = f"{home}/Downloads/libgl1-mesa_cache"

with urllib.request.urlopen(downloadURL) as response, \
     open(f"{downloadLocation}/{downloadName}", 'wb') as out_file:
    shutil.copyfileobj(response, out_file)

#Extract just the achive from the package
print("Extracting archive...")

tarName = "data.tar.xz"
RunShell(['ar', 'x', downloandName, tarName], downloadLocation)

#Make a temporary dir and extract our archive into that
print("Extracting library...")

extractDirName = "libgl1-mesa-glx"
extractDir = f"{downloadLocation}/{extractDirName}"

os.mkdir(extractDir)

tar = tarfile.open(tarName)
tar.extractall(extractDir)
tar.close()

#Move the library into the game folder
shutil.move(f"{extractDir}/usr/lib/x86_64-linux-gnu/libGL.so.1.2.0", \
            f"{dyingLightLocation}/libGL.so.1")

#Cleanup after ourselves
shutil.rmtree(downloadLocation)

def RunShell (command: [], currentWorkingDirectory: str) -> None:
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, \
                            stderr=subprocess.PIPE, cwd=currentWorkingDirectory)

    o, e = proc.communicate()

    print('Output: ' + o.decode('ascii'))
    print('Error: '  + e.decode('ascii'))
    print('code: ' + str(proc.returncode))