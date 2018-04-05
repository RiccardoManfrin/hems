#!/bin/python

from aurorapy.client import AuroraError, AuroraTCPClient, AuroraSerialClient


inverter = AuroraSerialClient(port='/dev/ttyUSB0', address=2, baudrate=19200, data_bits=8, parity='N', stop_bits=1, timeout=0.1, tries=3)
inverter.connect()
print inverter.alarms()
#print inverter.measure(1, global_measure=True)
