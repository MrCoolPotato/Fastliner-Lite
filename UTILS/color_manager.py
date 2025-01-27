# UTILS/color_manager.py
import re
from UTILS.config_manager import ConfigManager

class ColorManager:
  
    @classmethod
    def colorize(cls, raw_text: str, role: str = None) -> str:
        """
        Convert raw_text into colored HTML. 
        - If 'role' is 'system', use the system color from config.
        - Otherwise, use the default text color.
        """
        # 1) Get color config
        colors_config = ConfigManager.get("colors", {})
        default_color = colors_config.get("text_general", "#282828") 
        system_color = colors_config.get("text_system", "#458588")
        error_color = colors_config.get("text_error", "#cc241d")   
        success_color = colors_config.get("text_success", "#98971a")
        warning_color = colors_config.get("text_warning", "#d79921")

        # 2) Escape HTML special characters
        safe_text = cls.escape_html(raw_text)

        # 3) Convert newlines to <br>
        safe_text = safe_text.replace("\n", "<br>")

        # 4) Pick the color based on role
        if role == "system":
            chosen_color = system_color
        elif role == "error":
            chosen_color = error_color 
        elif role == "user":
            chosen_color = default_color
        elif role == "success":
            chosen_color = success_color  
        elif role == "warning":
            chosen_color = warning_color      
        else:
            chosen_color = default_color

        # 5) Wrap the text in a <span> with the chosen color
        colored_html = f"<span style='color:{chosen_color};'>{safe_text}</span>"
        return colored_html

    @staticmethod
    def escape_html(text: str) -> str:
        """
        Replace <, >, & with HTML entities to avoid breaking HTML markup.
        """
        return (text.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;"))