import os
import glob

from base import Plugin


def get_plugins():
    """
    find all files in the plugin directory and import them
    """
    #get plugin directory and add it to the path
    plugin_dir = os.path.relpath(os.path.dirname(__file__))

    #get plugin files
    plugin_files = [
        filename
        for filename in glob.glob("%s/*.py" % plugin_dir )
        if not filename.endswith("__init__.py")
    ]

    #import all plugins (except base plugin)
    for plugin_file in plugin_files:
        plugin = os.path.splitext(plugin_file)[0].replace("/", ".")
        if not plugin.endswith("base"):
            mod = __import__(plugin)

    return Plugin.__subclasses__()

