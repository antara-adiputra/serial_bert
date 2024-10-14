import settings


class State:
	"""Abstract class of State"""

	def __init__(self) -> None:
		pass

	def _attr_from_dict(self, **kwargs) -> None:
		for key, val in kwargs.items():
			if hasattr(self, key): setattr(self, key, val)

	def reset(self) -> None:
		pass

	def update(self, **kwargs) -> None:
		self._attr_from_dict(**kwargs)


class SerialConfig(State):
	__parameter__ = ['com_port', 'baudrate', 'data_bit', 'stop_bit', 'parity', 'flow_control', 'remote_ip', 'remote_port', 'timeout']

	def __init__(self) -> None:
		super().__init__()
		self.com_port: str = None
		self.baudrate: int = getattr(settings, 'DEFAULT_BAUDRATE', 9600)
		self.data_bit: int = getattr(settings, 'DEFAULT_DATA_BIT', 8)
		self.stop_bit: int = getattr(settings, 'DEFAULT_STOP_BIT', 1)
		self.parity: str = getattr(settings, 'DEFAULT_PARITY', 'N')
		self.flow_control: str = 'NONE'
		self.timeout: float = getattr(settings, 'READ_TIMEOUT', 1)
		self.remote_ip: str = None
		self.remote_port: int = None
		self.tcp_timeout: float = getattr(settings, 'TCP_PACKET_TIMEOUT', 3)

	def reset(self) -> None:
		self.__init__()

	def to_dict(self, exclude: str | list = [], maps: dict = {}, **kwargs) -> dict:
		exc = exclude.split(' ') if isinstance(exclude, str) else exclude
		output = dict()

		for attr in dir(self):
			if attr in self.__parameter__ and attr not in exc:
				if attr in maps:
					output[maps[attr]] = getattr(self, attr)
				else:
					output[attr] = getattr(self, attr)
		return output


class MainState(State):
	serial_param_visible: bool = True
	test_param_visible: bool = True
	test_result_visible: bool = True
	frame_min_limit: int = getattr(settings, 'FRAME_MIN_LIMIT', 1)
	frame_max_limit: int = getattr(settings, 'FRAME_MAX_LIMIT', 1024)

	def __init__(self) -> None:
		super().__init__()
		self.mode = 'serial_com'
		self.max_frame_length: int = 255
		self.data_timeout: float = 3
		self.desired_ber: float = 1e-6
		self.test_duration: int = 10
		self.test_duration_unit: str = 's'
		self.frame_transmission: str = 'fixed'
		self.checking_host: bool = False
		self.host_available: bool = False
		self.host_checked: bool = False
		self.tested: bool = False
		self.test_running: bool = False

	def reset(self) -> None:
		self.__init__()