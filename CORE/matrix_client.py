from nio import (
    AsyncClient, 
    LoginResponse, 
    LogoutResponse,
    SyncResponse,
    SyncError,
)
import nio

from CONFIG.env import HOMESERVER

from UTILS.open_room_manager import OpenRoomManager

import asyncio
import aiohttp
from datetime import datetime


class MatrixClient:
    def __init__(self, signals):
        self.homeserver = HOMESERVER
        self.client = None
        self.signals = signals

        #sync control
        self.running = False
        self.next_batch = None


    async def login(self, username, password):
      
        try:
            self.client = AsyncClient(self.homeserver, username)

            response = await self.client.login(password)
            self.signals.messageSignal.emit(f"Raw response: {response}", "server")
            if isinstance(response, LoginResponse):
                self.client.user_id = response.user_id
                self.client.access_token = response.access_token
                self.signals.messageSignal.emit(
                    f"Login successful as {self.client.user_id}.", "success"
                )
                asyncio.create_task(self.sync_forever())
                asyncio.create_task(self.fetch_rooms_and_spaces())
                return True
            else:
                self.signals.messageSignal.emit(
                    f"Login failed: {response.message}", "error"
                )
                return False
        except Exception as e:
            self.signals.messageSignal.emit(f"Login error: {str(e)}", "error")
            return False
        
    async def logout(self):

        if not self.client or not self.client.access_token:
            self.signals.messageSignal.emit("You are not logged in.", "warning")
            return False

        try:
            response = await self.client.logout()
            
            if isinstance(response, LogoutResponse):
                self.client.user_id = None
                self.client.access_token = None
                self.signals.messageSignal.emit("Logged out successfully.", "success")
                await self.stop()
                self.signals.roomSignal.emit([])
                self.signals.logoutSignal.emit()
                return True
            else:
                self.signals.messageSignal.emit(
                    f"Logout failed: {response.message if hasattr(response, 'message') else 'Unknown error'}",
                    "error",
                )
                return False

        except Exception as e:
            self.signals.messageSignal.emit(f"Logout error: {str(e)}", "error")
            return False    

    async def sync_forever(self):
    
        if not self.client or not self.client.access_token:
            self.signals.messageSignal.emit("Client is not initialized or logged in. Cannot start syncing.", "error")
            return

        self.running = True
        self.signals.messageSignal.emit("Starting batch sync...", "system")

        try:
            while self.running:
                try:
                    response = await self.client.sync(timeout=5000, since=self.next_batch, full_state=False)

                    if isinstance(response, SyncResponse):
                        self.next_batch = response.next_batch

                        await self.process_sync_response(response)

                    elif isinstance(response, SyncError):
                        self.signals.messageSignal.emit(f"Sync error occurred: {response.message}", "error")
                        await asyncio.sleep(5)

                    else:
                        self.signals.messageSignal.emit("Unexpected sync response type.", "error")

                except aiohttp.ClientError as e:

                    self.signals.messageSignal.emit(f"HTTP error during sync: {e}", "error")
                    await asyncio.sleep(5)

                except Exception as e:

                    self.signals.messageSignal.emit(f"Unexpected error during sync: {e}", "error")
                    await asyncio.sleep(5)

        except asyncio.CancelledError:

            self.signals.messageSignal.emit("Sync task was cancelled.", "warning")

        except Exception as e:

            self.signals.messageSignal.emit("Critical error in sync_forever.", "error")

        finally:

            self.running = False


    async def process_sync_response(self, response: SyncResponse):
       
        open_room_id = OpenRoomManager.get_current_room()
      
        
        
        if response.rooms and hasattr(response.rooms, "join"):
            for room_id, joined_room in response.rooms.join.items():
                
               
                if room_id != open_room_id:
                    continue

                timeline = joined_room.timeline
                if timeline and timeline.events:
                    for event in timeline.events:
                        # Process standard text messages.
                        if isinstance(event, nio.RoomMessageText):
                            sender = event.sender
                            ts = event.server_timestamp
                            message = event.body
                            time_str = (
                                datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M:%S")
                                if ts else "unknown"
                            )
                            formatted_message = f"{sender} [{time_str}] : {message}"
                            self.signals.messageSignal.emit(formatted_message, "user")
                        else:
                            # Process the event as an audit log entry.
                            sender = getattr(event, "sender", "server")
                            ts = getattr(event, "server_timestamp", None)
                            time_str = (
                                datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M:%S")
                                if ts else "unknown"
                            )
                            # Try getting event_type; if not present, use the class name.
                            event_type = getattr(event, "event_type", None)
                            if not event_type:
                                event_type = event.__class__.__name__
                            
                            # If the event type is UnknownEvent, pull extra details from the event content.
                            if event_type == "UnknownEvent":
                                content = getattr(event, "content", {})
                                # Create a short summary from content (if available)
                                extra_info = ""
                                if isinstance(content, dict) and content:
                                    extra_info = ": " + ", ".join(f"{k}={v}" for k, v in content.items())
                                formatted_audit = f"{sender} [{time_str}] {event_type}{extra_info}"
                            else:
                                formatted_audit = f"{sender} [{time_str}] {event_type}"
                            self.signals.messageSignal.emit(formatted_audit, "server")

    async def stop_syncing(self):

        self.signals.messageSignal.emit("Stopping sync process...", "system")
        self.running = False    

    async def fetch_rooms_and_spaces(self):
        if not self.client or not self.client.access_token:
            self.signals.messageSignal.emit("Cannot fetch rooms: Not logged in.", "warning")
            return

        try:
            response = await self.client.joined_rooms()

            if hasattr(response, "rooms"):
                joined_rooms = response.rooms
                room_details = []

            
                for room_id in joined_rooms:
                    
                    room_info = {"room_id": room_id, "is_space": False, "name": room_id}
                    
                    state_response = await self.client.room_get_state(room_id)

                    if hasattr(state_response, "events"):
                        for event in state_response.events:
                            event_type = event.get("type")
                            content = event.get("content", {})

                            
                            if event_type == "m.room.create" and content.get("type") == "m.space":
                                room_info["is_space"] = True

                            elif event_type == "m.room.name":
                                room_name = content.get("name")
                                if room_name:
                                    room_info["name"] = room_name

                            elif event_type == "m.space.child":
    
                                child_room_id = event.get("state_key")
                                if child_room_id:
                            
                                    room_info.setdefault("children", []).append(child_room_id)

                    room_details.append(room_info)

            
                room_mapping = {room["room_id"]: room for room in room_details}

                
                for room in room_details:
                    if room.get("is_space") and "children" in room:
                        updated_children = []
                        for child_id in room["children"]:
                            if child_id in room_mapping:
                                child_info = room_mapping[child_id]
                                updated_children.append({
                                    "room_id": child_info["room_id"],
                                    "name": child_info["name"]
                                })
                            else:
                                updated_children.append({"room_id": child_id, "name": child_id})
                        room["children"] = updated_children

                self.signals.roomSignal.emit(room_details)
                self.signals.messageSignal.emit(
                    f"Fetched {len(room_details)} rooms/spaces.", "system"
                )
            else:
                self.signals.messageSignal.emit("Failed to retrieve room list.", "error")

        except Exception as e:
            self.signals.messageSignal.emit(f"Error fetching rooms: {str(e)}", "error")

    async def fetch_room_messages(self, room_id, limit=1000):
        
        if not self.client or not self.client.access_token:
            self.signals.messageSignal.emit("Cannot fetch room contexts: Not logged in.", "warning")
            return
    
        try:
            response = await self.client.room_messages(
                room_id,
                start="",
                limit=limit,
                direction="f"
            )
    
            if isinstance(response, nio.RoomMessagesResponse):
                for event in response.chunk:
                    if isinstance(event, nio.RoomMessageText):
                        sender = event.sender
                        ts = event.server_timestamp
                        message = event.body
    
                        time_str = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M:%S") if ts else "unknown"
    
                        formatted_message = f"{sender} [{time_str}] : {message}"

                        self.signals.messageSignal.emit(formatted_message, "user")
            else:
                self.signals.messageSignal.emit(f"Error: {response.message}", "error")
        except Exception as e:
            self.signals.messageSignal.emit(f"Error fetching room contexts: {str(e)}", "error")   

    async def send_message(self, room_id: str, message_content: str):
        
        if not self.client or not self.client.access_token:
            self.signals.messageSignal.emit("Cannot send message: Not logged in.", "warning")
            return

        try:

            response = await self.client.room_send(
                room_id,
                message_type="m.room.message",
                content={
                    "msgtype": "m.text",
                    "body": message_content
                }
            )
            
            if hasattr(response, "event_id") and response.event_id:
                pass
            else:
                self.signals.messageSignal.emit(
                    f"Failed to send message: {getattr(response, 'message', 'Unknown error')}", "error"
                )
        except Exception as e:
            self.signals.messageSignal.emit(f"Error sending message: {str(e)}", "error")            

    async def stop(self):
        
        await self.stop_syncing()
        await self.client.close()