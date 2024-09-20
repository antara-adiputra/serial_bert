import difflib, os, random, string, time
from typing import Any, TypeAlias

from scipy.stats import poisson
from . import utils

BitStruct: TypeAlias = tuple[int, int, int, int]
BytesDiff: TypeAlias = dict[int, tuple[int, int]]

STRING_COLLECTION = string.ascii_letters + string.digits + '_'

def confidence_level(N: int, BER_s: float, E: float) -> float:
	"""Determine the confidence level for a BER measurement by entering the specified BER, the data rate, the measurement time, and the number of detected errors. For reference, the number of transmitted bits (N) is shown as the data rate (BPS) multiplied by the measurement time (T).

	Args :
		N		= N bits sent along test duration
		BER_s	= specified BER target value
		E		= Number of measured bit errors

	Result :
		BER confidence level
	"""
	return 1 - poisson.cdf(E, N*BER_s)

def randpattern(n: int | None = None, min: int = 1, max: int = 1024) -> bytes:
	k = random.randint(min, max) if n is None else n
	return ''.join(random.choices(STRING_COLLECTION, k=k)).encode()

def strpattern(n: int | None = None, min: int = 1, max: int = 1024) -> bytes:
	k = random.randint(min, max) if n is None else n
	mul = k // len(STRING_COLLECTION)
	mod = k % len(STRING_COLLECTION)
	i = mul + 1 if mod>0 else mul
	return (STRING_COLLECTION * i)[:k].encode()

def str2compare(data1: str, data2: str):
	diffdata = dict()
	i = 0
	flag = False
	diff_list = list()
	for s in difflib.ndiff(data1, data2):
		diff_list.append(s.replace(' ', ''))
		if s[0]==' ':
			flag = False
		elif s[0]=='-':
			# Char removed
			diffdata[i] = (s[-1], '')
			flag = True
		elif s[0]=='+':
			if flag:
				# Char is replaced
				diffdata[i-1] = (diffdata[i-1][0], s[-1])
				# i -= 1
			else:
				# Char inserted, we assume this as noises on communication link
				# Just ignore it
				diffdata[i] = ('', s[-1])
				# pass
			flag = False
			i -= 1
		i += 1
	# print(diff_list)
	return diffdata

def bytes_compare(data1: bytes, data2: bytes):
	assert len(data1)==len(data2), 'Data length differ.'
	diffdata = {i: (data1[i], data2[i]) for i in range(len(data1)) if data1[i]!=data2[i]}
	return diffdata

def bytestr_compare(data1: bytes, data2: bytes):
	str1, str2 = data1.decode(), data2.decode()
	i1, i2 = 0, 0
	diffdata = dict()
	flag = False

	for s in difflib.ndiff(str1, str2):
		if s[0]==' ':
			flag = False
			i1 += 1
			i2 += 1
		elif s[0]=='-':
			# Char removed from str1
			diffdata[i1] = (data1[i1], 0)
			flag = True
			i1 += 1
		elif s[0]=='+':
			if flag:
				# Char is substituted
				diffdata[i1-1] = (diffdata[i1-1][0], data2[i2])
				# i -= 1
			else:
				# Char inserted, this may be a noise on communication link or shifted data
				# Just ignore it
				diffdata[i1] = (0, data2[i2])
				# pass
			flag = False
			i2 += 1
		# i += 1
	return diffdata


class LoopBackData:
	_error_bytes: BytesDiff
	_error_bits: int

	def __init__(self, sent: bytes, received: bytes, time_delta: float, bits_struct: BitStruct, **kwargs) -> None:
		self._sent = sent
		self._received = received
		self.bits_structure = bits_struct
		self.time_delta = time_delta
		self._error_bytes = bytes_compare(sent, received) if len(sent)==len(received) else bytestr_compare(sent, received)
		self._error_bits = sum(map(self._count_bit_errors, self._error_bytes.values()))

		if os.environ.get('DEBUG'):
			if len(sent)!=len(received): print('Warning! Data length differed.')

	def __str__(self) -> str:
		return f'tx >> {self._sent}\r\n' +\
			f'rx >> {self._received}\r\n' +\
			f'bytes={self.total_bytes} bits={self.total_bits} error_bytes={self.total_error_frames} error_bits={self.total_error_bits}'
	
	def _count_bit_errors(self, pairs: tuple[int, int]) -> int:
		ctx, crx = pairs
		if ctx>0 and crx>0:
			# Byte differed/replaced
			return (ctx ^ crx).bit_count()
		elif ctx>0 or crx>0:
			# Byte missed or inserted, so all bits are wrong
			return sum(self.bits_structure)
		else:
			# Impossible state
			return 0

	def to_dict(self) -> dict[str, Any]:
		attrs = ['sent', 'received', 'frame_size', 'time_delta', 'total_frames', 'total_bytes', 'total_error_frames', 'total_bits', 'total_error_bits', 'error_bytes']
		return {attr: getattr(self, attr) for attr in attrs}

	@property
	def sent(self):
		return self._sent.decode()

	@property
	def received(self):
		return self._received.decode()

	@property
	def frame_size(self):
		return sum(self.bits_structure)

	@property
	def error_bytes(self):
		return dict(map(lambda i: (i, (chr(self._error_bytes[i][0]), chr(self._error_bytes[i][1]))), self._error_bytes.keys()))

	@property
	def total_frames(self):
		return self.total_bytes

	@property
	def total_bytes(self):
		return len(self._sent)

	@property
	def total_bits(self):
		return self.total_frames * self.frame_size

	@property
	def total_error_frames(self):
		return len(self._error_bytes)

	@property
	def total_error_bits(self):
		return self._error_bits

	@property
	def data_rate(self):
		return len(self._received) / self.time_delta


class LoopBackTest:
	_results: list[LoopBackData]

	def __init__(self, port: utils.SerialPort, data: list[tuple] = [], **kwargs) -> None:
		self._rawdata = data
		self._calc_baudrate: int = None
		self.port = port
		self.is_running: bool = False
		self.progress: float = 0.0
		self.due_time: float = 0.0
		# Process data if any
		self._results = self.process_all() if data else list()

	def __getitem__(self, item):
		return self.results[item]

	def _reinitalize(self) -> None:
		self._rawdata = list()
		self._results = list()
		self.progress = 0.0
		self.due_time = 0.0

	async def _run(self, once: bool, duration: float, frame_length: int | None, timeout: float, **kwargs) -> None:
		self._reinitalize()
		dkwargs = dict()
		if 'min_length' in kwargs: dkwargs['min'] = utils.pop_dict(kwargs, 'min_length')
		if 'max_length' in kwargs: dkwargs['max'] = utils.pop_dict(kwargs, 'max_length')

		t0 = time.time()
		# Executor may defined in kwargs
		while time.time() - t0 <= duration:
			sr = await utils.async_serial_sendrcv(port=self.port, data=strpattern(frame_length, **dkwargs), timeout=timeout, **kwargs)
			self.process(*sr)
			self._rawdata.append(sr)
			self.progress = (time.time() - t0) / duration
			self.due_time = round(duration - time.time() + t0, 1)
			if once: break
		return self.results

	def process_all(self) -> list[LoopBackData]:
		results = [LoopBackData(*data, self.bits_structure) for data in self._rawdata]
		return results

	def process(self, tx_data: bytes, rx_data: bytes, t_delta: float) -> LoopBackData:
		result = LoopBackData(tx_data, rx_data, t_delta, self.bits_structure)
		self._results.append(result)

		if self.avg_data_rate>0 and self._calc_baudrate is None:
			# Set calculated baudrate based on transmission data rate
			self._calc_baudrate = utils.guess_baudrate(self.avg_data_rate, self.frame_size)
		return result

	@utils.toggle_attr(name='is_running')
	async def run_once(self, frame_length: int | None = None, timeout: float = 3, **kwargs) -> None:
		return await self._run(once=True, duration=3, frame_length=frame_length, timeout=timeout, **kwargs)

	@utils.toggle_attr(name='is_running')
	async def run_for(self, duration: float, frame_length: int | None = None, timeout: float = 3, **kwargs) -> None:
		return await self._run(once=False, duration=duration, frame_length=frame_length, timeout=timeout, **kwargs)

	@property
	def results(self):
		return self._results

	@property
	def counter(self):
		return len(self.results)

	@property
	def start_bits(self):
		return 1

	@property
	def data_bits(self):
		return self.port.bytesize

	@property
	def parity_bits(self):
		return 1 if self.port.parity in ('E', 'O') else 0

	@property
	def stop_bits(self):
		return self.port.stopbits

	@property
	def frame_size(self):
		return self.start_bits + self.port.bytesize + self.parity_bits + self.port.stopbits

	@property
	def bits_structure(self):
		return (self.start_bits, self.data_bits, self.parity_bits, self.port.stopbits)

	@property
	def total_frames_transmitted(self):
		return sum(map(lambda d: d.total_frames, self.results)) if self.results else 0

	@property
	def total_frames_received(self):
		return sum(map(lambda d: len(d.received), self.results)) if self.results else 0

	@property
	def total_frames_lost(self):
		return self.total_frames_transmitted - self.total_frames_received

	@property
	def total_bits(self):
		return sum(map(lambda d: d.total_bits, self.results)) if self.results else 0

	@property
	def total_error_frames(self):
		return sum(map(lambda d: d.total_error_frames, self.results)) if self.results else 0

	@property
	def total_error_bits(self):
		return sum(map(lambda d: d.total_error_bits, self.results)) if self.results else 0

	@property
	def bit_error_rate(self):
		if self.total_error_bits>0:
			return self.total_error_bits / self.total_bits
		else:
			if self.total_bits>0:
				# Find the nearest greater, so we assume that the next bit is error
				return 1 / (self.total_bits + 1)
			else:
				return 0

	@property
	def avg_propagation_time(self):
		return sum(map(lambda d: d.time_delta, self.results)) / self.counter if self.counter else 0

	@property
	def avg_data_rate(self):
		return sum(map(lambda d: d.data_rate, self.results)) / self.counter if self.counter else 0

	@property
	def avg_frames_received(self):
		return self.total_frames_received / self.counter if self.counter else 0

	@property
	def avg_travel_time(self):
		if self._calc_baudrate is None:
			return 0
		else:
			return self.avg_propagation_time - (self.avg_frames_received / self._calc_baudrate * self.frame_size)


if __name__=='__main__':
	bits_struct = (1, 8, 0, 1)
	char = b'$'

	def sub(s: bytes, ix: list[int], x: bytes | list[bytes]):
		out = s
		n = 0
		if isinstance(x, list):
			for i in range(len(ix)):
				out = out.replace(chr(out[ix[i]+n]).encode(), x[i], 1)
				n += len(x[i]) - 1
		else:
			for i in ix:
				out = out.replace(chr(out[i]+n).encode(), x, 1)
				n += len(x) - 1
		return out
	
	def run(b1, b2):
		t0 = time.time_ns()
		res = LoopBackData(b1, b2, 0.0, bits_struct)
		t1 = time.time_ns()
		dt = (t1-t0)/1000
		print('', res, sep='\n')
		print(res.error_bytes)
		# print(f't_total={dt}us', f'count={res.total_error_frames}', f'error={res.total_error_bits}')

	def rand_index(n: int, max: int):
		gen = list()
		while len(gen)<n:
			x = random.randint(0, max)
			if x not in gen: gen.append(x)
		return gen

	length = 100
	n_err = 3
	# x = randpattern(40)
	x = strpattern(length)
	ixs = rand_index(n_err, 100)
	y1 = sub(x, ixs, char)
	y2 = sub(x, ixs, b'')
	y3 = sub(x, ixs, char*2)
	# print(x)
	# print(y)
	# x = b'NDVplmCsYNITnMXBy3QzIdkuQ9fS9h4PJ3waTueAuxpxAGnAyNmbXNWisiltGf6qe0lUqZooALlGQSGYKqoCvKSPYddUVkVQ2DAeI8oOFPQTMEFEdaEeXl7hOOAUAqmba952yv20iivTy8BodsLwJrm5qOOTgnU3XECipQ2nySHSa6E5qn1NjvISXJh7xbclwR2V8BTFtBFcCENGaRQRch4s62DiMtK2eO99LdoUAec8tpGh6xyIwZtZDugZM4e'
	# y = b'NDVppmCsYNITnMBy3Q#zIdkuQ9fS9h4PJ3waTueAuxpxAGnAyNmbNWisiptGf6qe0pUqZooALpGQSGYKqoCvKSPYddUVkVQ2DAeI8oOFPQTMEFEdaEep7hOOAUAqmba952yv20iivTy8BodsLwJrm5qOOTgnU3ECipQ2nySHSa6E5qn1NjvISJh7xbcpwR2V8BTFtBFcCENGaRQRch4s62DiMtK2eO99LdoUAec8tpGh6xyIwZtZDugZM4e'

	for y in [y1, y2, y3]:
		run(x, y)