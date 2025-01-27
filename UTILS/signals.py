# UTILS/signals.py

from PySide6.QtCore import QObject, Signal

class SignalManager(QObject):
    """
    A Singleton Signal Manager to handle cross-service signals.
    """
    _instance = None

    messageSignal = Signal(str, str)
    commandSignal = Signal(str, list)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SignalManager, cls).__new__(cls)
            # Flag to ensure __init__ is only called once.
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        # Ensure we only do the real initialization once.
        if not self._initialized:
            super(SignalManager, self).__init__()
            self._initialized = True