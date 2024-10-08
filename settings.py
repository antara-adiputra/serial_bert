"""
"""

# GUI settings
DEBUG = True
ALLOWED_HOST = '127.0.0.1'  # 0.0.0.0
BIND_PORT = 8080
BINDING_REFRESH_INTERVAL = 0.1
RECONNECT_TIMEOUT = 3
MAX_PROPAGATION_TIME = 0.05
APP_TITLE = 'Serial BER Test'
APP_DESCRIPTION = ''
FAVICON_PATH = 'favicon.ico'
DARK_MODE = False
AUTO_SHOW = True
LANGUAGE = 'en-US'
ENCODING = 'utf-8'


# General settings
FRAME_MIN_LIMIT = 1
FRAME_MAX_LIMIT = 1024
DEFAULT_BAUDRATE = 9600
DEFAULT_DATA_BIT = 8
DEFAULT_STOP_BIT = 1
DEFAULT_PARITY = 'N'
READ_TIMEOUT = 1.2    # more higher the value, more lower the baudrate can be handled

# Raw Socket settings
TCP_PACKET_TIMEOUT = 3