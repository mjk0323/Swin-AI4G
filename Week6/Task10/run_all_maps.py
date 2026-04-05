import os
import subprocess

# maps location
MAP_FOLDER = "./maps"

# players name
PLAYERS = ["Simple", "Complex"]  

# PlanetWars script
SCRIPT = "main.py"  

for filename in os.listdir(MAP_FOLDER):
    if filename.endswith(".json"):
        map_name = filename[:-5]  # Delete .json 
        print(f"Running map: {map_name}")

        # PlanetWars command
        cmd = [
            "python", SCRIPT,
            "-m", map_name,
            "-p", *PLAYERS,
            "--logscript", "Logger.py"  
        ]
        subprocess.run(cmd)

print("Finished")