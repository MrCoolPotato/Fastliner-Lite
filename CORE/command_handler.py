# CORE/command_handler.py

from PySide6.QtCore import QObject

from UTILS.signals import SignalManager

from UI.settings_window import SettingsWindow

from CORE.matrix_client import MatrixClient

import platform, os

import asyncio

class CommandHandler(QObject):
    def __init__(self, main_window=None, parent=None, matrix_client=None):
        super().__init__(parent)
        self.signals = SignalManager()
        
        self.settings_window = None
        
        self.main_window = main_window

        self.matrix_client = matrix_client
        
        self.logged_in = False

    def handle_command(self, command: str, args: list):
        
        cmd_lower = command.lower()

        if cmd_lower == "/help":
            self.signals.messageSignal.emit((
                "Available commands:\n"
                "  /help\n"
                "  /blank\n"
                "  /settings\n"
                "  /exit\n"
                "  /minimize\n"
                "  /fullscreen\n"
                "  /clear\n"
                "  /sidebar\n"
                "  /call\n"
                "  -\n"
                "  /login <username> <password>\n"
                "  /logout\n"
                "  -\n"
                "  /whoami\n"
                "  /myevents\n"
                "  /myrooms\n"
                "  /create_room <name> [--public|--private] [--space]\n"
                "  /leaveroom <id>\n"
                "  /invite <room_id> <user_id>\n"
                "  /myinvites [accept/reject] [<room_id>]\n"
                "  /pin [--list|--unpin] <event_id>\n"
            ), "system")

        elif cmd_lower == "/settings":
            if not self.logged_in:
                self.signals.messageSignal.emit("You are not logged in.", "warning")
            else:
                self._handle_settings()

        elif cmd_lower == "/exit":
            self._handle_exit()

        elif cmd_lower == "/minimize":
            self._handle_minimize()

        elif cmd_lower == "/fullscreen":
            self._handle_fullscreen()

        elif cmd_lower == "/clear":
            self._handle_clear() 

        elif cmd_lower == "/blank":
            self._handle_blank()     

        elif cmd_lower == "/whoami":
            asyncio.create_task(self._handle_whoami())

        elif cmd_lower == "/myevents":
            asyncio.create_task(self._handle_myevents())   
            
        elif cmd_lower == "/myrooms":
            asyncio.create_task(self._handle_myrooms())  

        elif cmd_lower == "/invite":
            
            if len(args) != 2:
                self.signals.messageSignal.emit("Usage: /invite <room_id> <user_id>", "warning")
            else:
                room_id = args[0]
                user_id = args[1]
                self.signals.messageSignal.emit(
                    f"Inviting {user_id} to room {room_id}...", "system"
                )
                asyncio.create_task(self._handle_invite(room_id, user_id))     

        elif cmd_lower == "/myinvites":
            if not self.matrix_client:
                self.signals.messageSignal.emit("Not logged in.", "warning")
                return
    
            if len(args) == 0:
                asyncio.create_task(self._handle_list_invites())
           
            elif len(args) >= 2:
                action = args[0].lower()
                room_id = args[1]
                if action == "accept":
                    asyncio.create_task(self._handle_accept_invite(room_id))
                elif action == "reject":
                    asyncio.create_task(self._handle_reject_invite(room_id))
                else:
                    self.signals.messageSignal.emit("Usage: /myinvites [accept|reject] <room_id>", "warning")
            else:
                self.signals.messageSignal.emit("Usage: /myinvites [accept|reject] <room_id>", "warning")    

        elif cmd_lower == "/leaveroom":
            if not args:
                self.signals.messageSignal.emit("Usage: /deleteroom <room_id>|<room_id2>|...", "warning")
            else:
                room_ids = args[0]
                self.signals.messageSignal.emit(f"Leaving room(s): {room_ids}", "system")
                asyncio.create_task(self._handle_leave_room(room_ids))       

        elif cmd_lower == "/create_room":
            if not args:
                self.signals.messageSignal.emit(
                    "Usage: /create_room <name> [--public|--private] [--space]",
                    "warning"
                )
                return

            name = args[0]
            visibility = "private"
            is_space = False

            
            for arg in args[1:]:
                arg = arg.lower()
                if arg == "--public":
                    visibility = "public"
                elif arg == "--private":
                    visibility = "private"
                elif arg == "--space":
                    is_space = True

            self.signals.messageSignal.emit(
                f"Creating {'space' if is_space else 'room'} '{name}' with visibility '{visibility}'.",
                "system"
            )

            asyncio.create_task(self.matrix_client.create_room(name, visibility, is_space))

        elif cmd_lower == "/sidebar":
            if self.main_window:
                self.main_window.toggle_sidebar()
            else:
                self.signals.messageSignal.emit("No main window reference. Cannot toggle sidebar.", "error")

        elif cmd_lower == "/call":
            if self.main_window:
                self.main_window.toggle_callwidget()
            else:
                self.signals.messageSignal.emit("No main window reference. Cannot toggle call.", "error")             

        elif cmd_lower == "/login":
            if len(args) != 2:
                self.signals.messageSignal.emit("Usage: /login <username> <password>", "warning")
            elif self.logged_in:
                self.signals.messageSignal.emit("You are already logged in.", "warning")
            else:
                username, password = args
                self.signals.messageSignal.emit(f"Logging in as {username}...", "system")
                asyncio.create_task(self._handle_login(username, password))  

        elif cmd_lower == "/logout":
            asyncio.create_task(self._handle_logout())      

        elif cmd_lower == "/pin":
            
            current_room = self.matrix_client.current_room_id
            if not current_room:
                self.signals.messageSignal.emit("No room open for pin operations.", "warning")
                return

            if not args:
                self.signals.messageSignal.emit("Usage: /pin --list | --unpin <event_id> | <event_id>", "warning")
            else:
                action = args[0].lower()
                if action == "--list":
                    asyncio.create_task(self._handle_list_pinned())
                elif action == "--unpin":
                    if len(args) < 2:
                        self.signals.messageSignal.emit("Usage: /pin --unpin <event_id>", "warning")
                    else:
                        asyncio.create_task(self._handle_unpin_event(args[1]))
                else:
                    
                    asyncio.create_task(self._handle_pin_event(args[0]))

        else:
            self.signals.messageSignal.emit(f"Unknown command: {command}", "error")

    async def _handle_list_pinned(self):
        current_room = self.matrix_client.current_room_id
        if not current_room:
            self.signals.messageSignal.emit("No room open to list pinned events.", "warning")
            return
        pinned = await self.matrix_client.list_pinned_events(current_room)
        if pinned:
            for event_id in pinned:
                self.signals.messageSignal.emit(f"Pinned event: {event_id}", "system")
        else:
            self.signals.messageSignal.emit("No pinned events.", "system")

    async def _handle_pin_event(self, event_id: str):
        current_room = self.matrix_client.current_room_id
        if not current_room:
            self.signals.messageSignal.emit("No room open to pin an event.", "warning")
            return
        result = await self.matrix_client.pin_event(current_room, event_id)
        if result:
            self.signals.messageSignal.emit(f"Event {event_id} pinned in room {current_room}.", "success")
        else:
            self.signals.messageSignal.emit(f"Failed to pin event {event_id}.", "error")

    async def _handle_unpin_event(self, event_id: str):
        current_room = self.matrix_client.current_room_id
        if not current_room:
            self.signals.messageSignal.emit("No room open to unpin an event.", "warning")
            return
        result = await self.matrix_client.unpin_event(current_room, event_id)
        if result:
            self.signals.messageSignal.emit(f"Event {event_id} unpinned in room {current_room}.", "success")
        else:
            self.signals.messageSignal.emit(f"Failed to unpin event {event_id}.", "error")  

    async def _handle_create_room(self, name: str, visibility: str, room_type: str):
        room_id = await self.matrix_client.create_room(name, visibility, room_type)
        if room_id:
            self.signals.messageSignal.emit(f"{room_type.capitalize()} created successfully: {room_id}", "success")
        else:
            self.signals.messageSignal.emit(f"{room_type.capitalize()} creation failed.", "error")         

    async def _handle_whoami(self):

        await self.matrix_client.whoami() 

    async def _handle_myevents(self):
        
        await self.matrix_client.list_my_events()  

    async def _handle_myrooms(self):
        
        await self.matrix_client.list_my_rooms()              

    async def _handle_login(self, username: str, password: str):

        success = await self.matrix_client.login(username, password)
        if success:
            self.logged_in = True
            self.signals.messageSignal.emit("Login successful.", "success")
        else:
            self.signals.messageSignal.emit("Login failed. Check your credentials.", "error")

    async def _handle_logout(self):

        success = await self.matrix_client.logout()
        if success:
            self.logged_in = False
            self.signals.messageSignal.emit("Logout successful.", "success")
        else:
            self.signals.messageSignal.emit("Logout failed.", "error")                

    def _handle_settings(self):
    
        if self.settings_window is None or not self.settings_window.isVisible():
            self.settings_window = SettingsWindow()
            self.settings_window.show()
        else:
            self.settings_window.activateWindow()

    def _handle_exit(self):

        if self.main_window:
            self.signals.messageSignal.emit("Exiting application...", "success")
            self.main_window.close()
        else:
            self.signals.messageSignal.emit("No main window reference. Cannot exit.", "error")

    def _handle_minimize(self):
        
        if self.main_window:
            self.signals.messageSignal.emit("Minimizing window...", "success")
            self.main_window.showMinimized()
        else:
            self.signals.messageSignal.emit("No main window reference. Cannot minimize.", "error")

    def _handle_fullscreen(self):

        if self.main_window:
            if self.main_window.isFullScreen():
                self.signals.messageSignal.emit("Restoring window from fullscreen...", "success")
                self.main_window.showNormal()
            else:
                self.signals.messageSignal.emit("Entering fullscreen mode...", "success")
                self.main_window.showFullScreen()
        else:
            self.signals.messageSignal.emit("No main window reference. Cannot fullscreen.", "error")

    def _handle_clear(self):

        if platform.system().lower().startswith("win"):
            os.system("cls")
        else:
            os.system("clear")

        if self.main_window and hasattr(self.main_window, "cli_widget"):
            self.main_window.cli_widget.clear()
        else:
            self.signals.messageSignal.emit("No main window reference. Cannot clear local screen.", "error") 

    async def _handle_list_invites(self):
        invites = self.matrix_client.pending_invites
        if invites:
            for room_id, data in invites.items():
                room_name = data.get("room_name", room_id)
                inviter = data.get("inviter", "unknown")
                self.signals.messageSignal.emit(
                    f"Invite from {inviter}: {room_name} ({room_id})", "system"
                )
        else:
            self.signals.messageSignal.emit("No pending invites found.", "system")

    async def _handle_accept_invite(self, room_id: str):
        result = await self.matrix_client.accept_invite(room_id)
        if result:
            self.signals.messageSignal.emit(f"Invite accepted for room {room_id}.", "success")
        else:
            self.signals.messageSignal.emit(f"Failed to accept invite for room {room_id}.", "error")

    async def _handle_reject_invite(self, room_id: str):
        result = await self.matrix_client.reject_invite(room_id)
        if result:
            self.signals.messageSignal.emit(f"Invite rejected for room {room_id}.", "success")
        else:
            self.signals.messageSignal.emit(f"Failed to reject invite for room {room_id}.", "error")     

    async def _handle_invite(self, room_id: str, user_id: str):
        
        result = await self.matrix_client.invite_user(room_id, user_id)
        if result:
            self.signals.messageSignal.emit(
                f"Invitation sent to {user_id} for room {room_id}.", "success"
            )
        else:
            self.signals.messageSignal.emit(
                f"Failed to invite {user_id} to room {room_id}.", "error"
            )           

    def _handle_blank(self):

        self.signals.blankSignal.emit()

    async def _handle_leave_room(self, room_ids: str):
        
        await self.matrix_client.leave_room(room_ids)
     