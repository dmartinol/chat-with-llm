title = "Chat Client"
welcome = f"Welcome to {title}"
help_message = """
            Help / TL;DR
            - /c <host>: Connect OpenAI-compliant server host
            - /c: Print connected server host
            - /h: Print this help message
            - /s: Print system prompt
            - /s <prompt>: Initialize system prompt
            - /t: Print temperature settings
            - /t <temperature>: Configure temperature  between 0 (focused and deterministic) and 1 (more creative). If set to 0, the model will use log probability to automatically increase the temperature until certain thresholds are hit.
            - /r: Reset chat
            """
default_system_prompt = "Sei un assistente che parla italiano."
default_temperature: float = 0.2
connection_alert = "OpenAI client not connected!"
