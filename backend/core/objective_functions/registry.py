import os
import importlib
import inspect
from .base_objective import ObjectiveFunction

class ObjectiveFunctionRegistry:
    def __init__(self):
        self._registry = {}
        self.load_all()

    def load_all(self):
        """Automatically scan and load all ObjectiveFunction subclasses in this directory."""
        current_dir = os.path.dirname(__file__)
        for filename in os.listdir(current_dir):
            if filename.endswith(".py") and not filename.startswith("__") and filename != "base_objective.py" and filename != "registry.py":
                module_name = filename[:-3]
                module = importlib.import_module(f"core.objective_functions.{module_name}")
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, ObjectiveFunction) and obj is not ObjectiveFunction:
                        # Instantiate the objective function and register it by its class name or predefined key
                        instance = obj()
                        self._registry[module_name] = instance

    def get_objective(self, name):
        """Retrieve an objective function by its module name identifier."""
        if name not in self._registry:
            # Fallback to default
            return self._registry.get('default_objective')
        return self._registry[name]


    def get_all_info(self):
        """Return a list of available objective functions for the frontend."""
        return [
            {"id": key, "name": obj.name, "description": obj.description}
            for key, obj in self._registry.items()
        ]

# Singleton registry
registry = ObjectiveFunctionRegistry()
