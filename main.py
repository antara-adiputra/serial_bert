import os

import settings
from nicegui import ui, binding
from serial_bert import GUI

os.environ['DEBUG'] = '1' if settings.DEBUG else '0'
binding.MAX_PROPAGATION_TIME = settings.MAX_PROPAGATION_TIME
app = GUI()


if __name__ in {"__main__", "__mp_main__"}:
	print(f'Application run on {settings.ALLOWED_HOST}:{settings.BIND_PORT}')
	ui.run(
		host=settings.ALLOWED_HOST,
		port=settings.BIND_PORT,
		title=settings.APP_TITLE,
		favicon=settings.FAVICON_PATH,
		dark=settings.DARK_MODE,
		show=settings.AUTO_SHOW,
		reload=True,
		binding_refresh_interval=settings.BINDING_REFRESH_INTERVAL,
		reconnect_timeout=settings.RECONNECT_TIMEOUT,
		language=settings.LANGUAGE,
		show_welcome_message=False
	)