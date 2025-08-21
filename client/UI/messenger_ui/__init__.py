# PycTalk Messenger UI Module
"""
Modular messenger UI components for PycTalk
This module provides all necessary components for a modern messenger interface
"""

from .message_bubble_widget import MessageBubble
from .chat_list_item_widget import ChatListItem
from .chat_window_widget import ChatWindow
from .messenger_main_window import MessengerMainWindow
from .friend_list_window import FriendListWindow
from .integration_helper import MessengerIntegration as IntegrationHelper

__all__ = [
    'MessageBubble',
    'ChatListItem', 
    'ChatWindow',
    'MessengerMainWindow',
    'FriendListWindow',
    'IntegrationHelper'
]

__version__ = "2.0.0"
