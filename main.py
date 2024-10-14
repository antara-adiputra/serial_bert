import os

import settings
from nicegui import ui, binding
from serial_bert import GUI


PARAMETERS = ['APP_TITLE', 'APP_DESCRIPTION', 'DEBUG', 'FRAME_MIN_LIMIT', 'FRAME_MAX_LIMIT', 'DEFAULT_BAUDRATE', 'DEFAULT_DATA_BIT', 'DEFAULT_STOP_BIT', 'DEFAULT_PARITY', 'READ_TIMEOUT', 'TCP_PACKET_TIMEOUT']

def load_settings() -> None:
	for stt in dir(settings):
		if stt in PARAMETERS:
			if getattr(settings, stt) in (None, False):
				os.environ[stt] = '0'
			elif getattr(settings, stt)==True:
				os.environ[stt] = '1'
			else:
				os.environ[stt] = str(getattr(settings, stt))


if __name__ in {"__main__", "__mp_main__"}:
	load_settings()
	binding.MAX_PROPAGATION_TIME = settings.MAX_PROPAGATION_TIME
	app = GUI()
	print(f'Application run on {settings.ALLOWED_HOST}:{settings.BIND_PORT}')
	ui.run(
		host=settings.ALLOWED_HOST,
		port=settings.BIND_PORT,
		title=settings.APP_TITLE,
		favicon=settings.FAVICON_PATH,
		dark=settings.DARK_MODE,
		show=settings.AUTO_SHOW,
		reload=False,
		binding_refresh_interval=settings.BINDING_REFRESH_INTERVAL,
		reconnect_timeout=settings.RECONNECT_TIMEOUT,
		language=settings.LANGUAGE,
		show_welcome_message=False
	)