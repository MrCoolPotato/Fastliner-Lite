# open_room_manager.py

class OpenRoomManager:
    _current_room_id = None

    @classmethod
    def set_current_room(cls, room_id: str):
        """Set the current (open) room ID."""
        cls._current_room_id = room_id

    @classmethod
    def get_current_room(cls) -> str:
        """Get the current (open) room ID."""
        return cls._current_room_id

    @classmethod
    def reset_current_room(cls):
        """Reset the current room ID to None."""
        cls._current_room_id = None