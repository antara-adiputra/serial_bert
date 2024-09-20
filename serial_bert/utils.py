import asyncio, functools, io, os, random, socket, sys, time
from typing import Any, Callable, TypeAlias, Literal, Self

import serial
import serial.serialutil
import serial.tools.list_ports

N_THREAD: int = os.cpu_count() * 2
COM_PORTS: dict[str, str] = dict()
BAUD_RATES: list[int] = [600, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]
DATA_BITS: list[int] = [7, 8]
PARITIES: dict[str, str] = {'N': 'None', 'E': 'Even', 'O': 'Odd'}
STOP_BITS: list[float] = [1, 1.5, 2]
FLOW_CONTROLS: list[str] = ['NONE', 'RTS/CTS', 'XON/XOFF']


def list_available_ports() -> dict[str, str]:
	global COM_PORTS
	COM_PORTS = {tty.device: f'{tty.name} ({tty.manufacturer if tty.manufacturer else tty.subsystem + "-" + tty.description})' for tty in serial.tools.list_ports.comports()}
	return COM_PORTS

list_available_ports()

def superscript(s: str) -> str:
	str_map = {
		"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶",
		"7": "⁷", "8": "⁸", "9": "⁹", "a": "ᵃ", "b": "ᵇ", "c": "ᶜ", "d": "ᵈ",
		"e": "ᵉ", "f": "ᶠ", "g": "ᵍ", "h": "ʰ", "i": "ᶦ", "j": "ʲ", "k": "ᵏ",
		"l": "ˡ", "m": "ᵐ", "n": "ⁿ", "o": "ᵒ", "p": "ᵖ", "q": "۹", "r": "ʳ",
		"s": "ˢ", "t": "ᵗ", "u": "ᵘ", "v": "ᵛ", "w": "ʷ", "x": "ˣ", "y": "ʸ",
		"z": "ᶻ", "A": "ᴬ", "B": "ᴮ", "C": "ᶜ", "D": "ᴰ", "E": "ᴱ", "F": "ᶠ",
		"G": "ᴳ", "H": "ᴴ", "I": "ᴵ", "J": "ᴶ", "K": "ᴷ", "L": "ᴸ", "M": "ᴹ",
		"N": "ᴺ", "O": "ᴼ", "P": "ᴾ", "Q": "Q", "R": "ᴿ", "S": "ˢ", "T": "ᵀ",
		"U": "ᵁ", "V": "ⱽ", "W": "ᵂ", "X": "ˣ", "Y": "ʸ", "Z": "ᶻ", "+": "⁺",
		"-": "⁻", "=": "⁼", "(": "⁽", ")": "⁾"}
	return ''.join([str_map[c] for c in s])

def subscript(s: str) -> str:
	str_map = {
		"0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄", "5": "₅", "6": "₆",
		"7": "₇", "8": "₈", "9": "₉", "a": "ₐ", "b": "♭", "c": "꜀", "d": "ᑯ",
		"e": "ₑ", "f": "բ", "g": "₉", "h": "ₕ", "i": "ᵢ", "j": "ⱼ", "k": "ₖ",
		"l": "ₗ", "m": "ₘ", "n": "ₙ", "o": "ₒ", "p": "ₚ", "q": "૧", "r": "ᵣ",
		"s": "ₛ", "t": "ₜ", "u": "ᵤ", "v": "ᵥ", "w": "w", "x": "ₓ", "y": "ᵧ",
		"z": "₂", "A": "ₐ", "B": "₈", "C": "C", "D": "D", "E": "ₑ", "F": "բ",
		"G": "G", "H": "ₕ", "I": "ᵢ", "J": "ⱼ", "K": "ₖ", "L": "ₗ", "M": "ₘ",
		"N": "ₙ", "O": "ₒ", "P": "ₚ", "Q": "Q", "R": "ᵣ", "S": "ₛ", "T": "ₜ",
		"U": "ᵤ", "V": "ᵥ", "W": "w", "X": "ₓ", "Y": "ᵧ", "Z": "Z", "+": "₊",
		"-": "₋", "=": "₌", "(": "₍", ")": "₎"}
	return ''.join([str_map[c] for c in s])

# See https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-objects
def rsetattr(obj, attr: str, val):
	pre, _, post = attr.rpartition('.')
	return setattr(rgetattr(obj, pre) if pre else obj, post, val)

# using wonder's beautiful simplification: https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-objects/31174427?noredirect=1#comment86638618_31174427
def rgetattr(obj, attr: str, *args):
	def _getattr(obj, attr):
		return getattr(obj, attr, *args)
	return functools.reduce(_getattr, [obj] + attr.split('.'))

def pop_dict(d: dict, key: int | str | list, copy: bool = False) -> Any:
	_dict = d.copy() if copy else d
	if isinstance(key, list):
		out = dict()
		for k in key:
			out[k] = _dict[k]
			del _dict[k]
	else:
		out = _dict[key]
		del _dict[key]
	return out

def toggle_attr(name: str, *value):
	val0 = value[0] if len(value)>0 else True
	val1 = value[1] if len(value)>1 else None
	def wrapper(func):
		@functools.wraps(func)
		async def wrapped(self, *args, **kwargs):
			rsetattr(self, name, val0)
			result = await func(self, *args, **kwargs)
			rsetattr(self, name, val1)
			return result
		return wrapped
	return wrapper

def validate_ip(ip: str) -> bool:
	try:
		socket.inet_aton(ip)
		return True
	except socket.error:
		return False
	except Exception:
		pass

def restart_application() -> None:
	# Trigger changes on main.py and only affect if autoreload is True
	os.utime('main.py')

async def run_in_thread(executor, func: Callable[..., Any], *fnargs, **fnkwargs):
	loop = asyncio.get_event_loop()
	result = await loop.run_in_executor(executor, func, *fnargs, **fnkwargs)
	return result


class TCPRawSocket:
	_serial_param_: list[str] = ['baudrate', 'bytesize', 'parity', 'stopbits']

	def __init__(self, target: tuple[str, str | int], tcp_timeout: float = 3, auto_connect: bool = False, **kwargs) -> None:
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._sock.settimeout(tcp_timeout)
		self._target: tuple = socket.getaddrinfo(*target)[0][-1]
		self._sockname: tuple[str, int] = None
		self._peername: tuple[str, int] = None
		self._connected: bool = False

		for cfg in kwargs:
			if cfg in self._serial_param_: setattr(self, cfg, kwargs[cfg])

		if auto_connect: self.connect()

	def __enter__(self) -> Self:
		self.connect()
		return self

	def __exit__(self, *_) -> None:
		self.close()

	def connect(self) -> None:
		self._sock.connect(self._target)
		self._sockname = self._sock.getsockname()
		self._peername = self._sock.getpeername()
		self._connected = True
		if os.environ.get('DEBUG'): print('Raw socket connected.')

	def close(self) -> None:
		self._sock.close()
		self._sockname = None
		self._peername = None
		self._connected = False

	def write(self, data: bytes, /) -> int:
		return self._sock.send(data)

	def read(self, size: int = -1, /) -> bytes:
		return self._sock.recv(size)

	def sendrecv(self, data: bytes, timeout: float = 10, *args, **kwargs) -> None:
		buff = bytearray()
		t0 = time.time()
		w = self.write(data)

		while data!=buff and time.time()-t0<timeout:
			r = self.read(w)
			buff += r

		t1 = time.time()
		dt = t1 - t0
		if os.environ.get('DEBUG'):
			print(f'[{self.sockname}] tx >> ' + data.decode('ascii'))
			print(f'[{self.peername}] rx << ' + buff.decode('ascii'))
			print(f'Travel time : {dt*1000:.2f} ms')
		return data, buff, dt

	async def async_sendrecv(self, data: str, executor = None, **kwargs):
		return await run_in_thread(executor, self.sendrecv, data, **kwargs)

	@property
	def name(self):
		return f'{str(self._target[0]).rjust(16)}:{str(self._target[1]).ljust(6)}'

	@property
	def sockname(self):
		return '' if self._sockname is None else f'{str(self._sockname[0]).rjust(16)}:{str(self._sockname[1]).ljust(6)}'

	@property
	def peername(self):
		return '' if self._peername is None else f'{str(self._peername[0]).rjust(16)}:{str(self._peername[1]).ljust(6)}'


SerialPort: TypeAlias = serial.serialutil.SerialBase | TCPRawSocket

def serial_port_factory(
		port: str | None = None,
		remote_ip: str | None = None,
		remote_port: int | str | None = None,
		baudrate: int = 9600,
		bytesize: int = 8,
		parity: Literal['N', 'E', 'O'] = 'N',
		stopbits: float = 1,
		timeout: float = 1,
		**extras
	) -> SerialPort:
	is_serialcom = port is not None
	is_rawsocket = not (remote_ip is None or remote_port is None)

	if is_serialcom:
		return serial.Serial(
			port,
			baudrate=baudrate,
			bytesize=bytesize,
			parity=parity,
			stopbits=stopbits,
			timeout=timeout,
			**extras
		)
	elif is_rawsocket:
		return TCPRawSocket(
			(remote_ip, remote_port),
			tcp_timeout=extras.get('tcp_timeout', 3),
			auto_connect=extras.get('auto_connect', True),
			baudrate=baudrate,
			bytesize=bytesize,
			parity=parity,
			stopbits=stopbits,
			**extras
		)
	else:
		raise RuntimeError('Serial / Raw Socket not properly configured.')

def tcp_ping(ip: str, port: str | int, timeout: float = 3) -> bool:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(timeout)
	target = socket.getaddrinfo(ip, port)[0][-1]
	try:
		s.connect(target)
		result = True
	except socket.error:
		result = False
	except Exception:
		result = None
	finally:
		s.close()
	return result

async def async_tcp_ping(ip: str, port: int, timeout: float = 3, executor = None) -> bool:
	return await run_in_thread(executor, tcp_ping, ip, port, timeout)

def serial_sendrcv(port: SerialPort, data: bytes, timeout: float = 10) -> tuple[bytes, bytes, float]:
	buff = bytearray()
	t0 = time.time()
	w = port.write(data)

	while data!=buff and (time.time() - t0)<timeout:
		# port.read() is blocking function which affected by port read timeout / socket timeout
		# Using high port read timeout / socket timeout value can cause the execution duration exceed the data timeout
		r = port.read(w)
		buff += r

	t1 = time.time()
	dt = t1 - t0
	if os.environ.get('DEBUG') and False:
		tx_iface = getattr(port, 'sockname', port.name)
		rx_iface = getattr(port, 'peername', port.name)
		print(f'[{tx_iface}] tx >> ' + data.decode('ascii'))
		print(f'[{rx_iface}] rx << ' + buff.decode('ascii'))
		print(f'Travel time : {dt*1000:.2f} ms')
	return data, buff, dt

async def async_serial_sendrcv(port: SerialPort, data: str, timeout: float = 10, executor = None, **kwargs):
	return await run_in_thread(executor, serial_sendrcv, port, data, timeout, **kwargs)

def guess_baudrate(data_rate: float, frame_size: int) -> int:
	if data_rate==0: return None
	baudrate = sorted(BAUD_RATES)
	bps = data_rate * frame_size
	i2 = len(baudrate) // 2
	i1 = i2 - 1
	while True:
		if bps>baudrate[i1] and bps<=baudrate[i2]:
			return baudrate[i2]
		elif bps<=baudrate[i1]:
			i2 = i1
			if i1-1>=0:
				# Shift left
				i1 -= 1
			else:
				# i1 is first index
				return baudrate[i1]
		elif bps>baudrate[i2]:
			i1 = i2
			if i2+1<len(baudrate):
				# Shift right
				i2 += 1
			else:
				# i2 is last index
				return baudrate[i2]
		else:
			# Impossible
			pass


if __name__=='__main__':
	with TCPRawSocket(target=('192.168.127.254', 4004), timeout=1) as ss:
		print(asyncio.run(ss.async_sendrecv(b'Looooppp')))

	# ss = TCPRawSocket(target=('192.168.127.254', 4004), timeout=1)
	# ss.connect()
	# print(asyncio.run(ss.async_tcp_sendrecv(b'Looooppp')))
	# ss.close()