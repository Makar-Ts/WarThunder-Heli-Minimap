# War Thunder Minimap

This program will improve your gaming experience with War Thunder with a real-time, dynamic minimap that displays game objects in real-time. By utilizing **War Thunder's localhost API (port 8111)**, this tool shows important information like player position and orientation, ground objects, airfields, and so on.

I did this for easier helicopter orintation in TRB, but the minimap will work in other modes as well.

---
## Features
- **Real-Time Object Tracking**:
    - Shows the position of your player and its orientation.
    - Highlights critical objects such as airfields, spawn points, ground vehicles, and more.
    - Accurate positioning and visualization of static and dynamic objects.
    
- **User-Friendly Interface:**
    - Resizable, customizable minimap to fit your screen dimensions.
    - Toggle visibility on/off without having to stop the game.
- **Customization Options**:
    - Zoom levels, background transparency, and object marker text sizes.
    - Dynamic generation of configuration based on your screen resolution.

---

## How It Works

It polls in **real time data** from the local instance API of War Thunder - http://127.0.0.1:8111 - and then processes it in such a way that in one minimized window, a minimap showing all the following could pop up: current position; all the static elements airfield or respawn points; moving items-tanks, planes, helis, etc.

The visualization logic is done with the Python library tkinter, offering a lightweight, interactive canvas to represent the War Thunder in-game world.

---
## Installation and Usage

### Prerequisites
- **War Thunder**: Make sure War Thunder is running (and you are in-game) and the localhost API is working - http://127.0.0.1:8111.
- **Python 3.8+**: This program is written in Python, so make sure Python is installed on your system.

### Installation
1. Download code from Releases tab or main page
2. Run the `main.py`
 
### Configuration
The program will automatically generate (or use pre-generated configuration) a **default configuration** for your screen resolution. Screen configuration files are located in the `/local/dconfigs`.

To change the settings, use the `config.ini` file located in the `/local` folder.

---
## Interface Overview
 
The following will be displayed on the minimap UI when the program is running:
* **Player Marker**: Triangular icon indicating player position and rotation.
- **Objects**: Terrain objects, airfields and other players, marked with color-coded icons.
- **Text Labels**: Significant annotations include distances to airfield and current zoom.

Further **controls** can be done in the UI by:
- **Visibility Toggle:** Dynamically hide / show the minimap.
- **Zoom Control:** Change zoom factor with the slider.

---
## Troubleshooting

If you encounter any issues:
1. Ensure War Thunder is running and the localhost API is working.
2. Verify your Python installation and dependencies.
3. Check the `logs` directory for detailed error information.

If you need more assistance or have feature requests, just open an issue in this repository, or contact me (attach `.log` file when you write about the bug, this will help fix it).

---
## File Structure

- `main.py`: Entry point of program controlling the main application loop and also UI toggles.
- `thunder_reader.py`: Responsible for fetching real-time data from the localhost API of War Thunder, parsing of object information and player metrics.
- `geom.py`: Auxiliary geometric utilities to perform various kinds of calculations related to determination of object headings, intersections, and positioning.
- `objects.py`: Classes and functions to create and update objects on the canvas, such as the player marker, airfields, etc.
- `local/config.py`: Responsible for dynamically loading configurations and creating screen-specific default configurations if no previous configuration has been saved.
- `local/config.ini`: Holds user configured settings: zoom, text sizes, colours and update rates.

---
## Contributing

If you'd like to improve the program or add new features:
1. Fork this repository.
2. Create a new branch and make your changes.
3. Submit a pull request.

---
## License

This project is licensed under the **MIT License**.

---
Thanks for using the War Thunder Minimap!
Feedback appreciated, let me know how to make this better!