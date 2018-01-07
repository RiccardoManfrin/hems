from aurorapy.client import AuroraError, AuroraTCPClient, AuroraSerialClient

client = AuroraSerialClient(port='/dev/ttyUSB0', address=2, baudrate=19200, data_bits=8, parity='N', stop_bits=1, timeout=1)
client.connect()
try:
	#print("Last 10s Joules: %s" % client.joules_in_last_10s())
	print("Inverter output power: %i [W]" % client.measure(3, global_measure=True))
except AuroraError as e:
	print(str(e))
client.close()
