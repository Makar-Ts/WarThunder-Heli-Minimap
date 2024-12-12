# pylint: undefined-loop-variable, disable=line-too-long, invalid-name, import-error, multiple-imports, unspecified-encoding, broad-exception-caught, trailing-whitespace, no-name-in-module, unused-import


import configparser
import os

import logging
logger = logging.getLogger(__name__)


class Config:
    def __init__(self, screen_size):
        """
        Initializes the Config object with the given screen size and loads the configuration.

        Parameters:
            screen_size (tuple): A tuple containing the width and height of the screen.

        Returns:
            None
        """
        self.screen_size = screen_size

        self.dconfig = None

        self.load_config()

    
    def load_config(self):
        """
        Loads the configuration settings from the configuration file and sets the corresponding attributes.

        This function reads the configuration file specified by the `get_config_path` method and initializes
        settings. If position or size are not found in the configuration file, it attempts to 
        load default screen configuration. If where is no such configuration creates it.

        Parameters:
            None

        Returns:
            None
        """
        logger.info("Loading config")

        self.config = configparser.ConfigParser()
        self.config.read(self.get_config_path())

        self.zoom = float(self.config.get("settings", "zoom", fallback=1.0))
        self.text_size = int(self.config.get("settings", "text_size", fallback=10))
        self.bg_color = self.config.get("settings", "bg_color", fallback="00FFFF")
        self.transparent = bool(int(self.config.get("settings", "trasparent", fallback=1)))
        
        self.update_time = {
            "usual": int(self.config.get("update_time", "usual", fallback=50)),
            "not_working": int(self.config.get("update_time", "not_working", fallback=3000))
        }
        
        self.cache = {
            "max_images": int(self.config.get("cache", "max_images", fallback=300)),
            "use_cached_spawns_positions": bool(self.config.get("cache", "use_cached_spawns_positions", fallback=True)),
        }

        if self.config.has_section("position"):
            self.position = {
                "x": int(self.config.get("position", "x", fallback=0)),
                "y": int(self.config.get("position", "y", fallback=0))
            }
        else:
            logger.warning("No position specified in configuration")

            self.load_dconfig()

            self.position = {
                "x": int(self.dconfig.get("position", "x", fallback=0)),
                "y": int(self.dconfig.get("position", "y", fallback=0))
            }

        if self.config.has_section("size"):
            self.size = {
                "x": int(self.config.get("size", "x", fallback=200)),
                "y": int(self.config.get("size", "y", fallback=200))
            }
        else:
            logger.warning("No size specified in configuration")

            if not self.dconfig:
                self.load_config()

            self.size = {
                "x": int(self.dconfig.get("size", "x", fallback=200)),
                "y": int(self.dconfig.get("size", "y", fallback=200))
            }

        self.object_size = {
            "ground": {
                "x": float(self.config.get("object_ground_size", "x", fallback=1.0)),
                "y": float(self.config.get("object_ground_size", "y", fallback=1.0))
            },
            "other": {
                "x": float(self.config.get("object_other_size", "x", fallback=2.0)),
                "y": float(self.config.get("object_other_size", "y", fallback=2.0))
            }
        }

        logger.info("Config loaded successfully")

    
    def get_config_path(self):
        """
        Get the path to the configuration file.

        This function returns the full path to the 'config.ini' file, which is located
        in the same directory as the current script.

        Parameters:
            None

        Returns:
            str: The full path to the 'config.ini' file.
        """
        return os.path.join(os.path.dirname(__file__), "config.ini")
    
    def get_dconfig_path(self, name):
        """
        Get the path to a specific default configuration file.

        This function returns the full path to a default configuration file with the given name,
        located in the 'dconfigs' subdirectory of the current script's directory.

        Parameters:
            name (str): The name of the default configuration file (without the .ini extension).

        Returns:
            str: The full path to the specified default configuration file.
        """
        return os.path.join(os.path.dirname(__file__), "dconfigs", f"{name}.ini")
    
    def load_dconfig(self):
        """
        Load the default configuration (DConfig) based on the current screen size.

        This function attempts to load a default configuration file specific to the current screen size.
        If the configuration file doesn't exist, it creates a new one using the create_dconfig method.

        Parameters:
            None

        Returns:
            None
        """
        name = f"{self.screen_size[0]}x{self.screen_size[1]}"

        logger.info("Loading DConfig")
        if not os.path.exists(self.get_dconfig_path(name)):
            logger.exception("No DConfig for such screen size")

            self.create_dconfig()

        self.dconfig = configparser.ConfigParser()
        self.dconfig.read(self.get_dconfig_path(name))

        logger.info("DConfig loaded successfully")

    
    def create_dconfig(self):
        """
        Create a new default configuration file (DConfig) based on the current screen size.

        This function generates a new configuration file with default settings for the
        minimap's position and size. The file is named after the current screen resolution
        and saved in the dconfigs directory.

        Parameters:
            None

        Returns:
            None
        """
        logger.info("Creating new DConfig")

        name = f"{self.screen_size[0]}x{self.screen_size[1]}"

        size = min(self.screen_size)//3
        padding = min(self.screen_size)//100*5

        with open(self.get_dconfig_path(name), "w") as f:
            f.write(f"""[position]
x={self.screen_size[0]-size-padding}
y={self.screen_size[1]-size-padding}
[size]
x={size}
y={size}
""")

        logger.info("New DConfig %s.ini created", name)
