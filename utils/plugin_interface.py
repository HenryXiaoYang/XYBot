class PluginInterface:
    def run(self, bot, recv):
        raise NotImplementedError("Subclasses must implement the 'run' method.")
