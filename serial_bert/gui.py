import asyncio, time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Iterator, Literal, Optional, Self, TypeAlias

from nicegui import app, ui, events
from . import core, state, utils

SpinnerType: TypeAlias = Literal['audio', 'bar', 'balls', 'box', 'clock', 'comment', 'cube', 'dots', 'facebook', 'gears', 'grid', 'hearts', 'hourglass', 'infinity', 'ios', 'orbit', 'oval', 'pie', 'puff', 'radio', 'rings', 'tail']

ABOUT = """**Serial Bit Error Rate (BER) Test**

	Version		: v0.0.1
	Company		: Fasop UP2B Sistem Makassar
	Contributor	: Putu Agus Antara A.

This project is _open source_ and free to use for testing serial link purpose in various applications.\n
Read our documentation [here](/documentation) or check our source code [here](https://github.com/antara-adiputra/serial_bert).
"""

ui_item = ui.item.default_style('padding: 2px 8px;')
ui_section = ui.item_section.default_classes('align-stretch')
ui_select = ui.select.default_props('dense outlined square stack-label options-dense')
ui_input = ui.input.default_props('dense outlined square stack-label')
ui_menu_label = ui.item_label.default_classes('text-sm')
dark_mode = ui.dark_mode()

def timediff(t0: float, digit: int | None = None) -> float:
	return time.time() - t0 if digit is None else round(time.time() - t0, digit)

def timefrmt(t: float, digit: int = 3, unit: Literal['s', 'ms', 'us', 'ns'] = 's') -> str:
	unit_step = ['s', 'ms', 'us', 'ns']
	tx1 = abs(t) > 1
	tx1000 = abs(t) * 1000 > 100
	ix_unit = unit_step.index(unit)
	if t==0 or tx1 or tx1000:
		# Already specific
		return f'{round(t, digit)} {unit}'
	else:
		# Too small for current unit
		return timefrmt(t*1000, digit, unit_step[ix_unit+1])

def group_label(label: str):
	ui.label(label).classes('font-bold whitespace-nowrap')
	ui.separator().classes('w-fill')

def ip_validation(ip: str | None) -> bool:
	if ip is None or ip=='':
		# Skip validation
		return True
	else:
		return utils.validate_ip(ip)

def port_validation(port: str | None) -> bool:
	if port is None or port=='':
		# Skip validation
		return True
	else:
		try:
			int(port)
			return True
		except ValueError:
			return False


class LoadingSpinner(ui.dialog):

	def __init__(
			self,
			text: str = '',
			*,
			value: bool = False,
			spinner: SpinnerType | None = 'default',
			size: str = '10em',
			color: str = 'primary',
			thickness: int = 5,
			**kwargs
		) -> None:
		super().__init__(value=value)
		self.text = text
		self.props('persistent backdrop-filters="opacity(90%)"')
		with self:
			with UIColumn(align_items='center'):
				if spinner is not None: ui.spinner(type=spinner, size=size, color=color, thickness=thickness)
				self.message = ui.label(text=text).classes('text-2xl text-white')\
					.bind_text_from(self)


class UIRow(ui.row):

	def __init__(
			self,
			*,
			wrap: bool = False,
			align_items: Literal['start', 'end', 'center', 'baseline', 'stretch'] | None = 'center',
			overflow: Literal['auto', 'clip', 'scroll', 'hidden', 'visible'] = 'auto',
			gap: int = 1,
			**kwargs
		) -> None:
		super().__init__(wrap=wrap, align_items=align_items)
		predefined_class = {'css_gap': f'gap-x-{gap}', 'css_overflow': f'overflow-{overflow}'}

		for key, val in kwargs.items():
			if key.startswith('css_'): predefined_class[key] = val

		self.classes(' '.join(predefined_class.values()))


class UIColumn(ui.column):

	def __init__(
			self,
			*,
			wrap: bool = False,
			align_items:Literal['start', 'end', 'center', 'baseline', 'stretch'] | None = 'stretch',
			**kwargs
		) -> None:
		super().__init__(wrap=wrap, align_items=align_items)
		predefined_class = {'css_width': 'w-full', 'css_padding': 'py-2 px-4', 'css_gap': 'gap-2'}

		for key, val in kwargs.items():
			if key.startswith('css_'): predefined_class[key] = val

		self.classes(' '.join(predefined_class.values()))


class NavButton(ui.button):

	def __init__(
			self,
			text: str = '',
			*,
			on_click: Callable[..., Any] | None = None,
			color: str | None = 'primary',
			icon: str | None = None,
			style: Literal['flat', 'outline', 'rounded', 'square', 'round'] = 'flat'
		) -> None:
		super().__init__(text, on_click=on_click, color=color, icon=icon)
		self.props(f'dense {style} no-caps size=sm')
		self.classes('px-2')


class NavDropdownButton(ui.dropdown_button):

	def __init__(
			self,
			text: str = '',
			*,
			value: bool = False,
			on_value_change: Callable[..., Any] | None = None,
			on_click: Callable[..., Any] | None = None,
			color: str | None = 'primary',
			icon: str | None = None,
			auto_close: bool | None = True,
			split: bool | None = False,
			style: Literal['flat', 'outline', 'rounded', 'square', 'round'] = 'flat',
			**kwargs
		) -> None:
		super().__init__(text, value=value, on_value_change=on_value_change, on_click=on_click, color=color, icon=icon, auto_close=auto_close, split=split)
		self.props(f'dense {style} no-caps no-icon-animation dropdown-icon=more_vert size=sm menu-anchor="bottom start" menu-self="top left"')
		predefined_class = {'css_padding': 'px-2'}

		for key, val in kwargs.items():
			if key.startswith('css_'): predefined_class[key] = val

		self.classes(' '.join(predefined_class.values()))


class ObjectDebugger(ui.expansion):
	"""Component which used to display object attributes for debug purpose only."""
	__used__: set
	excluded: list[str]

	def __init__(
		self,
		text: str = '',
		object: Optional[Any] = None,
		*,
		caption: Optional[str] = None,
		icon: Optional[str] = None,
		group: Optional[str] = None,
		value: bool = False,
		on_value_change: Optional[Callable[..., Any]] = None,
		render: bool = False,
		**contexts
	) -> None:
		title = text if text else repr(object)
		super().__init__(text=title, caption=caption, icon=icon, group=group, value=value, on_value_change=on_value_change)
		self.__used__ = set([attr for attr in dir(ui.expansion) if not (attr.startswith('_') and attr.endswith('_'))])
		self._object = object
		self.props(add='dense')
		self.classes('w-full')
		if 'excluded' not in contexts: self.excluded = list()
		# Add custom attribute
		for key in contexts:
			if not key.startswith('_') and key not in self.__used__: setattr(self, key, contexts[key])

		if render: self.render()

	def render(self) -> ui.expansion:
		with self:
			with ui.grid(columns='auto auto').classes('w-full gap-0'):
				for attr in dir(self._object):
					if not attr.startswith('_') and attr not in self.excluded:
						ui.label(attr).classes('border')
						ui.label('').classes('border').bind_text_from(self._object, attr, lambda x: repr(x) if callable(x) else str(x))
		return self

	def refresh(self) -> None:
		"""Refreshable content"""
		self.clear()
		self.render()


class GUI(ui.card):

	def __init__(self, *, align_items: Literal['start', 'end', 'center', 'baseline', 'stretch'] | None = None) -> None:
		super().__init__(align_items=align_items)
		self.props('square bordered')
		self.classes('w-full md:max-w-xl mx-0 md:mx-auto mt-3 p-0 text-sm md:text-base gap-1')
		self.config = state.SerialConfig()
		self.state = state.MainState()
		self.loop = asyncio.get_event_loop()
		self.test: core.LoopBackTest | None = None
		self.loading_spinner = LoadingSpinner()
		self.dialog_prompt = self._render_dialog_prompt()
		self.about = self._render_about()

		with self:
			with UIColumn(align_items='center'):
				ui.label('Serial BER Test').classes('p-2 text-3xl font-extrabold')
			ui.separator()
			with UIRow(overflow='scroll', gap=0).classes('w-full px-4'):
				with NavDropdownButton('', css_padding='px-1')\
					.props(add='dropdown-icon=power_settings_new', remove='dropdown-icon=more_vert'):
					ui.item('Restart', on_click=self.restart_application).props('dense').classes('text-xs')
					ui.item('Shutdown', on_click=self.prompt_shutdown).props('dense').classes('text-xs')
				ui.separator().props('vertical')
				ui.space()
				NavButton('Reset', icon='restart_alt', on_click=self.reset_parameter)\
					.tooltip('Reset parameter to default')
				ui.separator().props('vertical')
				NavButton('', icon='', on_click=lambda: dark_mode.toggle())\
					.bind_icon_from(dark_mode, 'value', backward=lambda dark: 'light_mode' if dark else 'dark_mode')\
					.bind_text_from(dark_mode, 'value', backward=lambda dark: 'Light' if dark else 'Dark')\
					.tooltip('Switch to Dark/Light mode')
				ui.separator().props('vertical')
				NavButton('Doc', icon='description', on_click=lambda: ui.navigate.to('/documentation', new_tab=True))\
					.tooltip('Documentation')
				ui.separator().props('vertical')
				NavButton('', icon='info', on_click=self.about.open)\
					.tooltip('About')
			self._render_serial_param()
			self._render_test_param()
			self._render_test_result()
			self._render_test_control()

		self._render_debugger()

	def _render_serial_param(self) -> None:
		def raw_socket_verified(obj: state.MainState):
			return obj.host_checked and obj.host_available

		def available_to_check(obj: state.MainState):
			return not (obj.host_checked and obj.host_available or obj.checking_host)

		def host_defined(cfg: state.SerialConfig):
			return cfg.remote_ip is not None and cfg.remote_port is not None

		with UIColumn():
			self.ui_group_label(text='Serial Parameter', group_name='serial_param', can_toggle=False)
			with ui.list().bind_visibility_from(self.state, 'serial_param_visible').props('dense'):
				with ui_item():
					with ui_section():
						with UIRow(overflow='visible'):
							sradio = ui.radio(options={'serial_com': 'Serial COM', 'virtual_com': 'Raw Socket'})\
								.bind_value(self.state, 'mode')\
								.props('dense inline')\
								.classes('text-sm')
							ui.element('div').classes('h-10')
				with ui_item()\
					.bind_visibility_from(sradio, 'value', value='serial_com')\
					.classes('h-16'):
					with ui_section().classes(add='justify-start', remove='align-stretch'):
						with UIRow():
							def refresh_coms():
								com_select.options = utils.list_available_ports()
								com_select.update()

							com_select = ui_select(options=utils.COM_PORTS, label='Serial Port')\
								.bind_value(self.config, 'com_port')\
								.on('click', refresh_coms)\
								.classes('w-full')
					with ui_section()\
						.props('side')\
						.classes(add='w-2/5 ml-1 justify-start', remove='align-stretch')\
						.style('padding-left: 0;'):
						pass
				with ui_item()\
					.bind_visibility_from(sradio, 'value', value='virtual_com')\
					.classes('h-16'):
					with ui_section():
						with UIRow(align_items='start'):
							ui_input(label='Remote IP', on_change=self._change_host, validation={'Invalid IP Address': ip_validation})\
								.bind_value(self.config, 'remote_ip')\
								.props('clearable')\
								.classes('w-2/3')
							ui_input(label='Port', on_change=self._change_host, validation={'Invalid Port Number': port_validation})\
								.bind_value(self.config, 'remote_port')\
								.props('clearable')\
								.classes('w-1/3')
					with ui_section()\
						.props('side')\
						.classes(add='w-2/5 ml-1 justify-start', remove='align-stretch')\
						.style('padding-left: 0;'):
						with UIRow().classes('w-full h-10'):
							ui.icon('verified', size='sm', color='positive')\
								.bind_visibility_from(self, 'state', raw_socket_verified)\
								.tooltip('Host is available')
							ui.button(icon='sync', on_click=self.check_raw_socket)\
								.bind_visibility_from(self, 'state', available_to_check)\
								.bind_enabled_from(self, 'config', host_defined)\
								.props('dense flat rounded')\
								.tooltip('Check')
							ui.spinner('ios').bind_visibility_from(self.state, 'checking_host')
				with ui_item():
					with ui_section():
						with UIRow():
							ui_select(options=utils.BAUD_RATES, label='Baud Rate')\
								.bind_value(self.config, 'baudrate')\
								.classes('w-2/5')
							ui_select(options=utils.DATA_BITS, label='Data Bit')\
								.bind_value(self.config, 'data_bit')\
								.classes('w-1/5')
							ui_select(options=utils.PARITIES, label='Parity')\
								.bind_value(self.config, 'parity')\
								.classes('w-1/5')
							ui_select(options=utils.STOP_BITS, label='Stop Bit')\
								.bind_value(self.config, 'stop_bit')\
								.classes('w-1/5')
							ui_select(options=utils.FLOW_CONTROLS, label='Flow Control')\
								.bind_value(self.config, 'flow_control')\
								.props('disable')\
								.classes('w-full')\
								.set_visibility(False)

	def _render_test_param(self) -> None:
		def fw_timeout(input: str | int | float):
			try:
				i = float(input)
				output = abs(i)
				if output==0 or output>10: raise ValueError
			except ValueError:
				ui.notify('Error! Value must be within range 0.1-10.', color='negative')
				output = 1	# default
			finally:
				return output

		def fw_max_frame_length(input: str | int):
			try:
				i = int(input)
				if i<self.state.frame_min_limit:
					ui.notify(f'Error! Acceptable value between {self.state.frame_min_limit}-{self.state.frame_max_limit}.', color='negative')
					output = self.state.frame_min_limit
				elif i>=self.state.frame_min_limit and i<=self.state.frame_max_limit:
					output = i
				else:
					ui.notify(f'Error! Acceptable value between {self.state.frame_min_limit}-{self.state.frame_max_limit}.', color='negative')
					output = self.state.frame_max_limit
			except ValueError:
				ui.notify('Error! Value must be positif integer.', color='negative')
				output = 255	# default
			finally:
				return output

		def fw_test_duration(input: str | int | float):
			try:
				i = int(input)
				output = abs(i)
				if output==0: raise ValueError
			except ValueError:
				ui.notify('Error! Value must be positif integer.', color='negative')
				output = 1	# default
			finally:
				return output

		with UIColumn():
			self.ui_group_label(text='Test Parameter', group_name='test_param')
			with ui.list().bind_visibility_from(self.state, 'test_param_visible').props('dense').classes('w-full'):
				with ui_item():
					with ui_section():
						ui_menu_label('Data Timeout')
					with ui_section():
						with UIRow():
							ui_input()\
								.bind_value(self.state, 'data_timeout', forward=fw_timeout, backward=lambda x: float(x))\
								.props('dense outlined square type=number step=0.1 input-class=text-center')\
								.classes('w-1/2')
							ui_select(options={'s': 'seconds'}, value='s')\
								.classes('w-1/2')
				with ui_item():
					with ui_section():
						ui_menu_label('Max Frame Length')
					with ui_section():
						with UIRow(overflow='visible'):
							ui.slider(min=self.state.frame_min_limit, max=self.state.frame_max_limit)\
								.bind_value(self.state, 'max_frame_length', forward=lambda x: int(x), backward=lambda x: int(x))\
								.props('dense label')
							ui_input()\
								.bind_value(self.state, 'max_frame_length', forward=fw_max_frame_length, backward=lambda x: int(x))\
								.props('hide-bottom-space type=number input-class=text-center')\
								.classes('w-36 ml-2')
				with ui_item():
					with ui_section():
						ui_menu_label('Desired BER (BERs)')
					with ui_section():
						ui_select(options={pow(10, x): f'10{utils.superscript(str(x))}' for x in range(-1, -13, -1)})\
							.bind_value(self.state, 'desired_ber')
				with ui_item():
					with ui_section():
						ui_menu_label('Test Duration (T)')
					with ui_section():
						with UIRow():
							ui_input()\
								.bind_value(self.state, 'test_duration', forward=fw_test_duration, backward=lambda x: float(x))\
								.props('dense outlined square type=number input-class=text-center')\
								.classes('w-1/2')
							ui_select(options={'s': 'seconds', 'm': 'minutes'})\
								.bind_value(self.state, 'test_duration_unit')\
								.classes('w-1/2')
				with ui_item():
					with ui_section():
						ui_menu_label('Frame Transmission')
					with ui_section():
						with UIRow(overflow='visible'):
							ui.radio(options={'fixed': 'Fixed Length', 'diverse': 'Diversed Length'})\
								.bind_value(self.state, 'frame_transmission')\
								.props('dense inline')\
								.classes('text-sm')
							ui.element('div').classes('h-10')

	def _render_test_result(self) -> None:
		def calculate_cl(test: core.LoopBackTest):
			try:
				cl = core.confidence_level(getattr(test, 'total_bits', 0), self.state.desired_ber, getattr(test, 'total_error_bits', 0))
				return f"{cl*100:.2f}%"
			except Exception:
				return '0%'

		params = [
			('Frames Transmitted', lambda tst: getattr(tst, 'total_frames_transmitted', '-')),
			('Frames Received', lambda tst: getattr(tst, 'total_frames_received', '-')),
			('Tx/Rx Counter', lambda tst: getattr(tst, 'counter', '-')),
			('Error Frames', lambda tst: getattr(tst, 'total_error_frames', '-')),
			('Error Bits', lambda tst: getattr(tst, 'total_error_bits', '-')),
			('Bits Transmitted (N)', lambda tst: getattr(tst, 'total_bits', '-')),
			('Bit Error Rate (BER)', lambda tst: f"{getattr(tst, 'bit_error_rate', 0):.1e}"),
			('Confidence Level (CL)', calculate_cl),
			('Avg. Propagation Time', lambda tst: timefrmt(getattr(tst, 'avg_propagation_time', 0), 3)),
			('Avg. Link Latency', lambda tst: timefrmt(getattr(tst, 'avg_travel_time', 0), 3))
		]
		with UIColumn(css_gap='gap-0').bind_visibility_from(self.state, 'tested'):
			self.ui_group_label(text='Test Result', group_name='test_result')
			with UIRow(align_items='start'):
				rows = len(params)//2 + len(params)%2
				for x in range(2):
					with ui.list().bind_visibility_from(self.state, 'test_result_visible').props('dense').classes('w-full'):
						for param in params[rows*x:rows*(x+1)]:
							with ui.item():
								with ui_section():
									ui_menu_label(param[0])
								with ui_section().props('side').classes('w-1/3 border border-solid').style('padding-left: 0;'):
									ui_menu_label('0')\
										.bind_text_from(self, 'test', param[1])\
										.classes('px-2')

	def _render_test_control(self) -> None:
		def ready_to_test(state: state.MainState):
			return (self.config.com_port!=None or getattr(state, 'host_available')) and not getattr(state, 'test_running')

		with UIColumn():
			with ui.list().props('dense').classes('w-full'):
				with ui_item():
					with ui_section().classes('gap-1'):
						ui.button('Simple Loop Test', on_click=self.simple_loop_test)\
							.bind_enabled_from(self, 'state', ready_to_test)\
							.props('dense square')\
							.classes('w-full')
						ui.button('BER Test', on_click=self.character_test)\
							.bind_enabled_from(self, 'state', ready_to_test)\
							.props('dense square')

	def _render_debugger(self) -> None:
		def close_me():
			debug.close()
			for dbg in (debug_state, debug_config, debug_test):
				dbg.close()

		with ui.dialog() as debug, ui.card().classes('w-1/2 md:w-full p-0 gap-y-0'):
			with ui.element('div').classes('w-full border overflow-y-auto') as container:
				debug_state = ObjectDebugger('state', self.state, render=True)
				debug_config = ObjectDebugger('config', self.config, render=True)
				debug_test = ObjectDebugger('test', self.test, render=True, excluded=['results'])
				# debug_utils = ObjectDebugger('utils', utils).render()
			with ui.row(align_items='center').classes('w-full p-2 gap-1'):
				ui.space()
				ui.button(icon='close', on_click=close_me).props('dense size=sm')
		ui.button(icon='open_in_full', on_click=debug.open).props('dense size=xs').classes('absolute top-1.5 right-1.5')
		debug.on_value_change(lambda e: close_me() if not e.value else None)

	def _render_dialog_prompt(self) -> ui.dialog:
		with ui.dialog() as dialog, ui.card(align_items='center').props('square').classes('p-2'):
			with UIColumn(css_padding='p-1'):
				ui.label('Shutdown application?').classes('mb-4')
				with UIRow():
					ui.space()
					ui.button('Yes', on_click=lambda: dialog.submit('yes')).props('dense').classes('w-8')
					ui.button('No', on_click=lambda: dialog.submit('no')).props('dense').classes('w-8')
		return dialog

	def _render_about(self) -> ui.dialog:
		with ui.dialog() as dialog, ui.card(align_items='stretch').props('square').classes('p-2 gap-1'):
			ui.label('About').classes('text-bold text-center')
			ui.separator()
			with UIColumn(css_padding='p-1'):
				ui.markdown(content=ABOUT)
				ui.separator()
				with UIRow():
					ui.space()
					ui.button('OK', on_click=dialog.close).props('dense size=sm').classes('w-8')
		return dialog

	def reset_parameter(self) -> None:
		self.config.reset()
		self.state.reset()

	def ui_group_label(self, text: str, group_name: str, can_toggle: bool = True) -> ui.element:
		attr = group_name + '_visible'
		with UIRow(overflow='hidden', gap=2).classes('py-1') as glabel:
			ui.label(text).classes('font-bold whitespace-nowrap')
			if can_toggle:
				ui.button(icon='visibility_off', color='grey', on_click=lambda: self.state.update(**{attr: not getattr(self.state, attr)}))\
					.bind_icon_from(self.state, attr, lambda vis: 'visibility_off' if vis else 'visibility')\
					.props('dense flat rounded')\
					.tooltip(f'Show/hide {text.lower()}')
			ui.separator().classes('w-fill')
		return glabel
	
	def get_port(self) -> utils.SerialPort | None:
		maps = {'com_port': 'port', 'data_bit': 'bytesize', 'stop_bit': 'stopbits'}
		exclude = ['flow_control']

		if self.state.mode=='serial_com':
			exclude += ['remote_ip', 'remote_port']
		elif self.state.mode=='virtual_com':
			exclude += ['com_port']
		else:
			return None

		config = self.config.to_dict(exclude=exclude, maps=maps)
		# if settings.DEBUG: print(config)
		try:
			port = utils.serial_port_factory(**config)
		except RuntimeError as err:
			port = None
			ui.notify(f'Error occured. ({". ".join(err.args)})', color='negative')
		finally:
			return port

	async def _change_host(self, e: events.ValueChangeEventArguments) -> None:
		self.state.host_checked = False
		self.state.host_available = False

	async def restart_application(self, e: events.ClickEventArguments) -> None:
		self.loading_spinner.open()
		for i in range(3, 0, -1):
			self.loading_spinner.text = f'Restart in {i} seconds'
			await asyncio.sleep(1)

		self.loading_spinner.text = 'Restarting...'
		await asyncio.sleep(1)
		utils.restart_application()
		self.loading_spinner.close()

	async def prompt_shutdown(self, e: events.ClickEventArguments) -> None:
		result = await self.dialog_prompt
		if result=='yes':
			self.clear()
			with self: ui.label('Application stopped.').classes('w-full text-xl text-center')
			await asyncio.sleep(1)
			app.shutdown()

	@utils.toggle_attr(name='state.checking_host')
	async def check_raw_socket(self) -> None:
		t0 = time.time()
		with ThreadPoolExecutor(utils.N_THREAD) as tpe:
			self.state.host_available = await utils.async_tcp_ping(self.config.remote_ip, self.config.remote_port, timeout=self.config.tcp_timeout, executor=tpe)
		if self.state.host_available:
			ui.notify('Remote host is available.', color='positive')
		else:
			ui.notify(f'Remote host is unavailable. ({timefrmt(timediff(t0), 3)})', color='negative')
		self.state.host_checked = True

	@utils.toggle_attr(name='state.test_running')
	async def simple_loop_test(self, e: events.ClickEventArguments) -> None:
		e.sender.props(add='loading')
		t0 = time.time()
		try:
			# Refers to PySerial Documentation, creating serial instance with defined port will always return opened port
			port = self.get_port()
			with ThreadPoolExecutor(utils.N_THREAD) as tpe:
				send, recv, dt = await utils.async_serial_sendrcv(port=port, data=b'loop', timeout=self.state.data_timeout, executor=tpe)
				self.test = core.LoopBackTest(port=port, data=[(send, recv, dt)])
				if recv==b'':
					ui.notify(f'Loop failed/timeout. ({timefrmt(timediff(t0), 3)})', color='negative')
				elif send==recv:
					self.state.tested = True
					ui.notify(f'Loop test succeed. ({timefrmt(timediff(t0), 3)})', color='positive')
		except Exception as err:
			ui.notify(f'Error occured. ({". ".join(err.args)}) [{timefrmt(timediff(t0), 3)}]', color='negative')
		finally:
			if port is not None: port.close()
		e.sender.props(remove='loading')

	@utils.toggle_attr(name='state.test_running')
	async def character_test(self, e: events.ClickEventArguments) -> None:
		def test_due_time(test: core.LoopBackTest | None):
			return f"[ {getattr(test, 'due_time', 0.0)//60:02.0f}:{getattr(test, 'due_time', 0.0)%60:04.1f} ]"

		with e.sender.add_slot('loading'):
			with UIRow(gap=2):
				ui.spinner(type='clock', color='white')
				ui.label().bind_text_from(self, 'test', test_due_time)
				ui.label('Test Ongoing...')

		e.sender.props(add='loading')
		t0 = time.time()
		try:
			# Refers to PySerial Documentation, creating serial instance with defined port will always return opened port
			port = self.get_port()
			test_duration = self.state.test_duration * 60 if self.state.test_duration_unit=='m' else self.state.test_duration
			frame_length = self.state.max_frame_length if self.state.frame_transmission=='fixed' else None
			self.test = core.LoopBackTest(port=port)
			with ThreadPoolExecutor(utils.N_THREAD) as tpe:
				results = await self.test.run_for(
					duration=test_duration,
					frame_length=frame_length,
					timeout=self.state.data_timeout,
					min_length=self.state.frame_min_limit,
					max_length=self.state.max_frame_length,
					executor=tpe
				)
				if results:
					self.state.tested = True
					ui.notify(f'Test completed. ({timefrmt(timediff(t0), 3)})', color='positive')
				else:
					ui.notify(f'Test completed with errors. ({timefrmt(timediff(t0), 3)})', color='negative')
		except Exception as err:
			ui.notify(f'Error occured. ({". ".join(err.args)}) [{timefrmt(timediff(t0), 3)}]', color='negative')
		finally:
			if port is not None: port.close()
		e.sender.props(remove='loading')


@ui.page('/documentation', title='Serial BER Test (Documentation)')
def view_documentation():
	with open('DOCUMENTATION.md', 'r') as readme:
		text = readme.readlines()

	ui.markdown('\n'.join(text))