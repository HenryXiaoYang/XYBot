class PluginInterface:
    def run(self, recv):
        raise NotImplementedError("Subclasses must implement the 'run' method.")
