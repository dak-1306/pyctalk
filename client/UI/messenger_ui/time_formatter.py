"""
Time formatting utility for Messenger-like timestamp display
"""
import datetime
from typing import Optional, Union


class TimeFormatter:
    """Format timestamps like Facebook Messenger"""
    
    @staticmethod
    def format_message_time(timestamp: Union[datetime.datetime, str], show_time: bool = False) -> Optional[str]:
        """
        Format timestamp for message display following Messenger logic:
        - Same day: Only show time (21:15)
        - Different day: Show date + time (28/08 21:15) 
        - Yesterday: Show "Hôm qua 21:15"
        - Far dates: Show full date (28/08/2024)
        
        Args:
            timestamp: Message timestamp
            show_time: Whether to show time (based on Messenger logic)
            
        Returns:
            Formatted time string or None if time shouldn't be shown
        """
        if not timestamp:
            return None
            
        if not show_time:
            return None
            
        # Convert string timestamp to datetime if needed
        if isinstance(timestamp, str):
            try:
                # Try parsing common formats
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']:
                    try:
                        timestamp = datetime.datetime.strptime(timestamp, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    # If parsing fails, return simple string
                    return timestamp.split('T')[1][:5] if 'T' in timestamp else timestamp
            except:
                return str(timestamp)
        
        now = datetime.datetime.now()
        today = now.date()
        msg_date = timestamp.date()
        
        # Same day - only show time
        if msg_date == today:
            return timestamp.strftime("%H:%M")
        
        # Yesterday
        elif msg_date == today - datetime.timedelta(days=1):
            return f"Hôm qua {timestamp.strftime('%H:%M')}"
        
        # Within same year - show date and time
        elif msg_date.year == today.year:
            return timestamp.strftime("%d/%m %H:%M")
        
        # Different year - show full date
        else:
            return timestamp.strftime("%d/%m/%Y")
    
    @staticmethod
    def should_show_timestamp(current_msg_time: Union[datetime.datetime, str], 
                             prev_msg_time: Optional[Union[datetime.datetime, str]], 
                             current_sender: str,
                             prev_sender: Optional[str],
                             is_first_message: bool = False) -> bool:
        """
        Determine if timestamp should be shown based on Messenger logic:
        - First message in conversation
        - Different sender than previous message
        - Time gap > 5 minutes from previous message
        
        Args:
            current_msg_time: Current message timestamp
            prev_msg_time: Previous message timestamp
            current_sender: Current message sender
            prev_sender: Previous message sender
            is_first_message: Is this the first message in conversation
            
        Returns:
            True if timestamp should be shown
        """
        # Always show for first message
        if is_first_message:
            return True
            
        # Show if different sender
        if current_sender != prev_sender:
            return True
            
        # Show if no previous message
        if not prev_msg_time:
            return True
            
        try:
            # Convert to datetime objects
            if isinstance(current_msg_time, str):
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']:
                    try:
                        current_msg_time = datetime.datetime.strptime(current_msg_time, fmt)
                        break
                    except ValueError:
                        continue
                        
            if isinstance(prev_msg_time, str):
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']:
                    try:
                        prev_msg_time = datetime.datetime.strptime(prev_msg_time, fmt)
                        break
                    except ValueError:
                        continue
            
            # Show if time gap > 5 minutes
            if isinstance(current_msg_time, datetime.datetime) and isinstance(prev_msg_time, datetime.datetime):
                time_diff = current_msg_time - prev_msg_time
                return time_diff.total_seconds() > 300  # 5 minutes
                
        except Exception as e:
            print(f"[DEBUG] Error comparing timestamps: {e}")
            
        # Default to showing timestamp if in doubt
        return True
