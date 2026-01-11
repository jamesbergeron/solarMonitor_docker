import subprocess
import csv
import time
from datetime import datetime 

def snmp_get(target, community, oid):
    # Construct the snmpget command
    command = [
        'snmpget',
        '-v', '2c',             # SNMP version
        '-c', community,        # Community string
        target,                 # Target IP
        oid                     # OID to retrieve
    ]

    try:
        # Execute the command
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Check for errors
        if result.returncode != 0:
            print(f"Error: {result.stderr.strip()}")
        else:
            return result.stdout.strip().rsplit(':',1)[1].strip()

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
system_list = ['10.0.70.50', '10.0.70.80', '10.0.70.90', '10.0.70.100', '10.0.70.150', '10.0.70.120', '10.0.70.140', '10.0.70.40']  # Replace with the target device's IP
community = 'cmp'    # Replace with the correct community string
oid = 'IMIMGMT::poeAdmin.2002'  # OID for sysDescr (system description)
oid_list = ['IMIMGMT::sunPower.0', 'IMIMGMT::sunCurrent.0', 'IMIMGMT::sunVoltage.0',
            'IMIMGMT::batteryVoltage.0', 'IMIMGMT::chargingCurrent.0', 'IMIMGMT::controllerOutputCurrent.0', 
            'IMIMGMT::controllerOutputVoltage.0', 'IMIMGMT::loadPower.0', 'IMIMGMT::systemTemperature.0', 'IMIMGMT::batteryTemperature.0',
            'IMIMGMT::totalSolarGeneratingCapacity.0']
# 'IMIMGMT::poeAdmin.2002'
header = "nodeIP,date,sunPower,sunCurrent,sunVoltage,batteryVoltage,chargingCurrent,outputCurrent,outputVoltage,loadPower,systemTemp,batteryTemp,totalGenerated"
# data_list.append(header)
def main():
   filePre = '/app/data/'
   cornerDict = {
                '10.0.70.40': 'corner4',
                '10.0.70.50': 'corner5',
                '10.0.70.80': 'corner8',
                '10.0.70.90': 'corner9',
                '10.0.70.100': 'corner10',
                '10.0.70.140': 'corner14',
                '10.0.70.150': 'corner15',
                '10.0.70.120': 'corner20',

                }
   while True:
      now = datetime.now()
      seconds_until_next_hour = (60 - now.minute) * 60 - now.second
      time.sleep(seconds_until_next_hour)
      for target in system_list:
           data_list = []
           readData = True
           now = datetime.now()
           readable_time = now.strftime("%Y-%m-%d %H:%M:%S")
           print(f"Polling for data at {target} now: {readable_time}")
           result_list = f'{target},{readable_time}'
           for oid in oid_list:
               snmp_result = snmp_get(target, community, oid)
               if snmp_result is None or snmp_result == "None":
                  snmp_result = "0.00W"
                  readData = False
               result_list = f'{result_list},{snmp_result}'
           
           if readData:
               data_list.append(result_list)
               csv_file = filePre+cornerDict[target]+'_data.csv'

               # Writing to CSV
               with open(csv_file, mode='a', newline='') as file:
                  # Write each line to the file
                  for line in data_list:
                      file.write(line + '\n')

main()
