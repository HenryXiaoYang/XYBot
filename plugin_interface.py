#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.
#
#  This program is licensed under the GNU General Public License v3.0.

# plugin_interface.py
class PluginInterface:
    def run(self, recv):
        raise NotImplementedError("Subclasses must implement the 'run' method.")
