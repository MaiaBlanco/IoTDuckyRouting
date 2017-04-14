from ble_scanner import BLScanner

Scanner = BLScanner()

for data in Scanner.scan_all():
	print data
