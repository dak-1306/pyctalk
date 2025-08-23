# PycTalk Messenger UI Module
"""
Modular messenger UI components for PycTalk
This module provides all necessary components for a modern messenger interface
"""

from .message_bubble_widget import MessageBubble
from .chat_list_item_widget import ChatListItem
from .friend_list_window import FriendListWindow
__all__ = [
    'MessageBubble',
    'ChatListItem', 
    'FriendListWindow'
]

__version__ = "2.0.0"
