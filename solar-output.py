#!/usr/bin/env python
import os
import subprocess, datetime, logging
import requests
import pymysql
import pytz
import schedule
import time

def get_inverter_data(): # may raise exception
  retry = 2
  while retry:
    ip = os.environ['IP_ADDRESS']
    if not ip:
      raise Exception('Unable to get inverter IP address')
    logging.info('Trying to get data xml from %s' % ip)
    try:
      resp = requests.get('http://%s/real_time_data.xml' % ip, timeout=10)
    except Exception as e:
      retry -= 1
      if retry:
        continue # while retry
      raise e
    retry = 0
  pac1 = ''
  e_today = ''
  v_pv1 = ''
  temperature = ''
  timezone = pytz.timezone("Europe/Brussels")
  time_stamp = timezone.localize(datetime.datetime.now())
  for line in resp.text.splitlines():
    if '<pac1>' in line:
      pac1 = int(line.split('>')[1].split('<')[0])
    if '<e-today>' in line:
      e_today = float(line.split('>')[1].split('<')[0])
    if '<v-pv1>' in line:
      v_pv1 = float(line.split('>')[1].split('<')[0])
    if '<temp>' in line:
      temperature = float(line.split('>')[1].split('<')[0])
  if '' in (pac1, e_today, v_pv1, temperature):
    raise Exception('Unable to extract all data from inverter response:\n%s' % resp.text)
  logging.info('Got data: pac1=%d e_today=%.3f v_pv1=%.3f temperature=%.3f' % (pac1, e_today, v_pv1, temperature))
  return dict(time_stamp=time_stamp, pac1=pac1, e_today=e_today, v_pv1=v_pv1, temperature=temperature)

def post_pvoutput(data): # may raise exceptions
  if not os.environ['PVOUTPUT_SYSTEM_ID']:
    logging.info('Skipping pvoutput post')
    return
  url = 'https://pvoutput.org/service/r2/addstatus.jsp'
  headers = {
    'X-Pvoutput-SystemId': os.environ['PVOUTPUT_SYSTEM_ID'],
    'X-Pvoutput-Apikey': os.environ['PVOUTPUT_API_KEY']
  }
  params = {
    'd': data['time_stamp'].strftime('%Y%m%d'),
    't': data['time_stamp'].strftime('%H:%M'),
    'v1': int(1000*data['e_today']), #kWh to Wh
    'v2': data['pac1'],
    'v5': data['temperature'],
    'v6': data['v_pv1']
  }
  logging.info(data['time_stamp'])
  logging.info('Posting data to pvoutput')
  logging.info(params)
  resp = requests.post(url, headers=headers, data=params, timeout=10)
  if resp.status_code != 200:
    logging.error('Pvoutput returned code %d' % resp.status_code)
    logging.debug(resp.text)
  return

#main
def main():
  global next_run_yes
  try:
    dt_now = datetime.datetime.now()
    data = get_inverter_data()
    post_pvoutput(data)
  except Exception as e:
    logging.error('%s : %s' % (type(e).__name__, str(e)))
  next_run_yes = 1

global next_run_yes

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logging.info('Started saj-monitor')

schedule.every(5).minutes.at(':00').do(main).run()
while True:
  if next_run_yes == 1:
    next_run = schedule.next_run().strftime('%d/%m/%Y %H:%M:%S')
    logging.info('Next run is scheduled at %s' % next_run)
    next_run_yes = 0
  schedule.run_pending()
  time.sleep(1)
