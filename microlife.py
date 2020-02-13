#!/usr/bin/env python3

# Copyright (C) 2020 nbenm <nb@dagami.org>
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; see the file COPYING. If not, write to the
#    Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

# Copyright (C) 2020 nbenm <nb@dagami.org>
#     Ce programme est un logiciel libre: vous pouvez le redistribuer
#     et/ou le modifier selon les termes de la "GNU General Public
#     License", tels que publiés par la "Free Software Foundation"; soit
#     la version 2 de cette licence ou (à votre choix) toute version
#     ultérieure.
# 
#     Ce programme est distribué dans l'espoir qu'il sera utile, mais
#     SANS AUCUNE GARANTIE, ni explicite ni implicite; sans même les
#     garanties de commercialisation ou d'adaptation dans un but spécifique.
# 
#     Se référer à la "GNU General Public License" pour plus de détails.
# 
#     Vous devriez avoir reçu une copie de la "GNU General Public License"
#     en même temps que ce programme; sinon, écrivez a la "Free Software
#     Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA".

from easyhid import Enumeration
import sys
import datetime
import codecs
import getopt

usage="""
usage:
%s [-r] [-d] [-t] [-n] [-g] [-s id] [-h]
-r   : read mode. Permet d'afficher tout les mesures du tensiomètre.
-d   : delete mode. Efface toutes les mesures, mais pas l'ID.
-t   : set time. Mise à jour de la date et heure à partir de celle du Mac.
-n   : serial number. Lit le numéro de série (un doute existe sur le résultat).
-g   : get id. Lecture de l'ID enregistré sur le tensiomètre.
-s id: set id. Enregistre une nouvelle valeur de l'ID sur le tensiomètre.
               Les mesures ne sont pas effacées.
-h   : help. Affiche cette aide.
""" % sys.argv[0]

def checksum(string):
  sm=0
  for i in range(len(string)):
    sm+=ord(string[i])
  return format(sm&0xff, 'x').upper()

def getid(dev):
  # Send command (0x24) for reading data from sphygmomanometer
  send_cmd (dev, 0x24)
  # Read the response from device
  lgr,id = read_device(dev)
  # Attention, c'est de l'ascii, donc doubler la longueur
  pos = id[0:22].find(b'99')
  if pos != -1:
    id = id[0:int(pos)]
  pos = id[0:22].find(b'00')
  if pos != -1:
    id = id[0:int(pos)]
  id = id.decode('utf-8')
  return codecs.decode(id, "hex").decode('utf-8')

def setid(dev, id): # Set a new ID and remove all measures remain
  # Data to send
  request = '00010001'
  id_ascii = ''
  for i in range(len(id)):
    id_ascii += format(ord(id[i]),'x')
  id_ascii += '9' * (22 - len(id_ascii))
  request += id_ascii
  request += '0000000000000000000000000000000000'
  chk = checksum(request)
  request += chk
  # Send command (0x23) for setting ID on device. Data remain
  send_cmd (dev, 0x23)
  # Now send the data
  write_data (dev, request)

def deletedata(dev):
  # Data to send
  request = '0000000100000000000000000000000016'
  # Send command (0x23) for deleting data only on device
  send_cmd (dev, 0x23)
  # Now send the data
  write_data (dev, request)

def read_serial(dev):
  # Send command (0x3e) for reading data from sphygmomanometer
  send_cmd (dev, 0x3e)
  # Read the response from device
  lgr,serial_num = read_device(dev)
  return codecs.decode(serial_num, "hex")

def write_data(dev, data):
  nb_full_records = len(data) // 7
  last_record = len(data) % 7
  # Process first all full records (ie size=7)
  for i in range (nb_full_records):
    bytes_to_send = '\x07'
    bytes_to_send += data[i*7:i*7+7]
    bytes_to_send = bytearray(bytes_to_send.encode())
    dev.write(bytes_to_send)
  # Process now the remaining partial record, if exists
  if last_record != 0:
    i += 1
    bytes_to_send = "\\x%0.2X" % last_record
    bytes_to_send += data[i*7:i*7+7]
    bytes_to_send = bytearray(bytes_to_send.encode())
    dev.write(bytes_to_send)

def read_date(dev):
  # Send command (0x26) for reading parameters from meter
  send_cmd (dev, 0x26)
  # Read the response from device
  lgr,buffer_total = read_device(dev)
  ident = str(buffer_total[18:80], 'utf-8')
  date = str(buffer_total[0:14], 'utf-8')
  return date, ident

def build_date():
  dt=datetime.datetime.now()
  return (datetime.datetime.strftime(dt, "%m%d%Y%H%M%S"))

def set_time(dev):
  # Read date from device
  date, ident = read_date(dev)
  # Build data to send
  date = build_date()
  request = date + '0000' + ident
  chk = checksum(request)
  request += chk
  # Send command (0x27) for setting time on device
  send_cmd (dev, 0x27)
  # Now send the data
  write_data (dev, request)

def display_date(date):
  date = '20' + date[0:2] + '-' + date[2:4] + '-' + date[4:6] + ' ' + date[6:8] + ':' + date[8:10]
  return date

def read_device(dev):
  # Lecture de tous les enregistrements de 8 octets
  buffer_total = bytearray([])
  while 1:
    result = dev.read(size=8, timeout=1000)
    if result == b'':
      break
    buffer_total.extend(result)
  if len(buffer_total) < 3:
    print ('le tensiomètre ne répond pas, on sort. 1.')
    sys.exit()
  ack = buffer_total[1]
  if ack != 6:
    print ('le tensiomètre ne répond pas, on sort. 2.')
    sys.exit()
  lgr_tot = 0
  lgr = buffer_total[0] - 240
  reponse = bytearray([])
  reponse.extend(buffer_total[2:lgr+1])
  i = 8
  while i < len(buffer_total):
    lgr = buffer_total[i] - 240
    lgr_tot += lgr
    reponse.extend(buffer_total[i+1:i+lgr+1])
    i += 8
  return lgr_tot - 2,reponse[:-2] #(lgr_tot and reponse without checksum)

def send_cmd(dev, cmd):
  dev.write(bytearray([0x04, 0x12, 0x16, 0x18, cmd, 0x0, 0x0, 0x0]))

def read_records(dev):
  # Send command (0x22) for reading data from sphygmomanometer
  send_cmd (dev, 0x22)
  # Read the response from device
  lgr,reponse = read_device(dev)
  nb_mesures = reponse[0:4]
  nb_mesures = int(nb_mesures, 16)
  # C'est de l'ascii, donc doubler la longueur
  pos = reponse[16:30].find(b'99')
  if pos != -1:
    id = reponse[8:int(pos)+16]
  pos = reponse[8:30].find(b'00')
  if pos != -1:
    id = reponse[8:int(pos)+16]
  id = id.decode('utf-8')
  id = codecs.decode(id, "hex").decode('utf-8')
  print ('\nDonnées pour l\'identifiant {}\n'.format(id))
  if nb_mesures == 0:
    print (u'Aucun résultat')
    sys.exit()
  print ('date pulse dia syst map mam')
  for i in range(nb_mesures):
    date = display_date(str(reponse[i*32+32:i*32+42], 'utf-8'))
    mam = str(reponse[i*32+42:i*32+44], 'utf-8')
    mam = '0' if mam == '20' else 'N'
    pulse = int(str(reponse[i*32+48:i*32+51], 'utf-8'), 16)
    dia = int(int(str(reponse[i*32+51:i*32+54], 'utf-8'), 16) / 4)
    syst = int(str(reponse[i*32+54:i*32+56], 'utf-8'), 16)
    map = int(dia + (syst - dia) / 3)
    print ('{} {} {} {} {} {}'.format(date, pulse, dia, syst, map, mam))

en = Enumeration()
devices = en.find(vid=0x04b4, pid=0x5500)
if len(devices) != 1:
  print (u'Dispositif non détecté: absent, panne...')
  sys.exit()

dev = devices[0]
dev.open()

try:
  opts, args = getopt.getopt(sys.argv[1:],"rdtngs:")
except getopt.GetoptError as err:
  sys.stderr.write(usage)
  sys.exit(1)

if len(sys.argv) == 1 or len(sys.argv) > 3:
  sys.stderr.write(usage)
  sys.exit(2)
  
for opt,arg in opts:
  if opt == '-r':
    if len(sys.argv) != 2:
      sys.stderr.write(usage)
      sys.exit(2)
    read_records(dev)
    sys.exit()
  elif opt == '-d':
    if len(sys.argv) != 2:
      sys.stderr.write(usage)
      sys.exit(2)
    deletedata(dev)
    sys.exit()
  elif opt == '-t':
    if len(sys.argv) != 2:
      sys.stderr.write(usage)
      sys.exit(2)
    set_time(dev)
    sys.exit()
  elif opt == '-n':
    if len(sys.argv) != 2:
      sys.stderr.write(usage)
      sys.exit(2)
    serial_num = read_serial(dev)
    print('serial:',serial_num.decode('utf-8'))
    sys.exit()
  elif opt == '-g':
    if len(sys.argv) != 2:
      sys.stderr.write(usage)
      sys.exit(2)
    id = getid(dev)
    print('id:',id)
    sys.exit()
  elif opt == '-s':
    if len(sys.argv) != 3:
      sys.stderr.write(usage)
      sys.exit(2)
    setid(dev, arg)
    sys.exit()
  else:
    sys.stderr.write(usage)
    sys.exit(2)
