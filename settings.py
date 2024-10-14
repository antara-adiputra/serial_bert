"""Modify parameter in this file to customize application behavior."""

# Turn On/Off debug mode
DEBUG = False

# GUI SETTINGS
# Parameters below refer to ui.run of NiceGUI, for more information https://nicegui.io/documentation/section_configuration_deployment#ui_run
# Start server with this host (defaults to '127.0.0.1 in native mode, otherwise '0.0.0.0')
ALLOWED_HOST = '127.0.0.1'

# Use this port (default: 8080 in normal mode, and an automatically determined open port in native mode)
BIND_PORT = 8080

# Time between binding updates (default: 0.1 seconds, bigger is more CPU friendly)
BINDING_REFRESH_INTERVAL = 0.1

# Maximum time the server waits for the browser to reconnect (default: 3.0 seconds)
RECONNECT_TIMEOUT = 3

# Warning will be shown on terminal if propagation time exceed this value. Useful in development state.
MAX_PROPAGATION_TIME = 0.05

# Page title (default: 'NiceGUI', can be overwritten per page)
APP_TITLE = 'Serial BER Test'

# Application description
APP_DESCRIPTION = ''

# Relative filepath, absolute URL to a favicon (default: None, NiceGUI icon will be used) or emoji (e.g. '🚀', works for most browsers)
FAVICON_PATH = 'favicon.ico'

# Whether to use Quasar's dark mode (default: False, use None for "auto" mode)
DARK_MODE = False

# Automatically open the UI in a browser tab (default: True)
AUTO_SHOW = True

# Language for Quasar elements (default: 'en-US')
LANGUAGE = 'en-US'

# Encoding type (default: 'utf-8')
ENCODING = 'utf-8'


# GENERAL SETTINGS
# Minimum serial frame limit value
FRAME_MIN_LIMIT = 1

# Maximum serial frame limit value
FRAME_MAX_LIMIT = 1024

# Default parameter of baudrate (option: 600, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200)
DEFAULT_BAUDRATE = 9600

# Default parameter of data bit length (option: 7, 8)
DEFAULT_DATA_BIT = 8

# Default parameter of stop bit length (option: 1, 2)
DEFAULT_STOP_BIT = 1

# Default parameter of parity bit (option: 'N', 'O', 'E')
DEFAULT_PARITY = 'N'

# Serial read timeout, more higher the value, more lower the baudrate can be handled
READ_TIMEOUT = 1.2


# RAW SOCKET SETTINGS
# TCP packet transmission timeout
TCP_PACKET_TIMEOUT = 3