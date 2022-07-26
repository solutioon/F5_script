# This Python file uses the following encoding: utf-8
# Import the proper python modules we'll need
import datetime
import time
import requests
import sys
import json
from f5.bigip import ManagementRoot
from f5.bigip import BigIP
import time
import os
 
#Escribir fichero de log
f = open ('pool_f5.log','a')
f.write(time.ctime(time.time()) + ' Ejecutado script desde ' +os.getenv("USER")+'\n' )
 
 
# Connect to the BIG-IP
lf = open ('listabalan.txt','r')
listabalantexto=lf.read()
listabalantexto=listabalantexto.rstrip('\n')
listabalan=listabalantexto.split(",")
lf.close()
 
print('')
print ('SELECCIONA EL BALANCEADOR SOBRE EL QUE ACTUAR O SALIR')
for i in range(0, len(listabalan)):
      print()
      print(str(i)+'.-      '+listabalan[i])
print()
print(str(i+1)+'.-      SALIR')
opcionb=input('¿Cual es la opción deseada 0-'+str(i+1)+'?')
 
if (opcionb==str(i+1)):
      print ('Gracias por usar este programa, que tengas un buen día')
 
else :
 
 
      #balan='f5000a.labalm'
      balan=listabalan[int(opcionb)]
      #userbalan=input('Cual es tu usuario ')
      userbalan='admin'
      #pwdbalan=input('Cual es tu pwd ')
      pwdbalan='*******'
      #print('ofidona\\'+userbalan)
 
      print ('Te vas a conectar al nodo ' + balan + ' con usuario ' + userbalan)
      f.write(time.ctime(time.time()) + ' Conectado a nodo '+ balan+'\n')
      print ('')
      print ('SELECCIONA EL NODO QUE QUIERES SACAR/METER DE BALANCEADOR O SALIR')
      print('')
 
      mgmt = ManagementRoot(balan, userbalan, pwdbalan)
      bigip = BigIP(balan, userbalan, pwdbalan)
 
      # Get a list of all pools on the BigIP and print their name and their
      # members' name
      pools = mgmt.tm.ltm.pools.get_collection()
 
      # https://devcentral.f5.com/s/feed/0D51T00006i7bPVSAY
      contadornodos=0
      nombrenodo=[] # creo una lista de nodos vacia
      particionnodo=[]
      ipnodo=[] # lista para IPs
      dnslist=[]
      for pool in pools:
      #    print(pool.name)
          for member in pool.members_s.get_collection():
              if (member.name.find("3389")>=0 or member.name.find("443")>=0):
      #            print (member.raw)
                  s = member.name #para coger el nombre hasta los dos puntos
                  m = s.index(':')
                  l = s[:m]
                  addr = member.address #para coger la IP del nodo
                  nombrenodo.append(l)
                  ipnodo.append(addr)
                  particionnodo.append(member.partition)
#                 print('El nodo ' + str(contadornodos)+' se llama ' + str(nombrenodo[contadornodos]))
                  n = bigip.ltm.nodes.node.load(partition=member.partition, name=l)
                  print (str(contadornodos)+'.-     En el pool ' + pool.name+' está el nodo '+ member.name+' estado ' + n.state)
                  print('La IP del nodo es ' + str(ipnodo[contadornodos]))
                  query = os.system("nslookup " + addr + " | grep name " + " | awk -F 'name = ' '{print $2}'")
                  contadornodos=contadornodos+1
      #            print (n.raw)
                  print()
      #            n.session="user-disabled" # Pasa a Disabled
      #            n.state="user-down" # Pasa a forced offline
      #            n.session="user-enabled"
      #            n.update()
      print(str(contadornodos)+ '.-     SALIR')
      opcionn=input('¿Cual es la opción deseada 0-'+str(contadornodos)+'?')
 
      if (opcionn==str(contadornodos)):
            print ('Gracias por usar este programa, que tengas un buen día')
      else :
            print('')
            print('SELECCION DE ACCIÓN SOBRE EL NODO')
            print('0.-      Habilitar nodo')
            print()
            print('1.-      Deshabilitar nodo')
            accion=input('¿Cual es la opción deseada 0-1?')
            n=bigip.ltm.nodes.node.load(partition=particionnodo[int(opcionn)], name=nombrenodo[int(opcionn)]) # ya no asumo todo en misma particion
            if accion=='0':
                  print ('Habilitado nodo ' + nombrenodo[int(opcionn)])
                  f.write(time.ctime(time.time()) + ' Habilitado nodo ' + nombrenodo[int(opcionn)] +'\n')
                  n.state="user-up"
 
            if accion=='1':
                  print ('Deshabilitado nodo ' + nombrenodo[int(opcionn)])
                  f.write(time.ctime(time.time()) + ' Deshabilitado nodo ' + nombrenodo[int(opcionn)] +'\n')
                  n.state="user-down"
            n.update()
            #status = mgmt.tm.cm.sync_status.load()
            #statusstr=str(status.raw)
            #print(status.raw)
            #numletraCommon = statusstr.find("to group")
            #print('Aquí empieza debug')
            #print(statusstr)
            print('Grupo de sincronización de '+balan+':')
            response = requests.get("https://"+balan+"/mgmt/tm/cm/device-group",auth=(userbalan,pwdbalan),verify=False)
            for group in response.json()['items']:
                  if group['type'] == "sync-failover":
                        group_name = group['name']
                  #print(statusstr[numletraCommon+9:numletraCommon+30])
            print (group_name)
            f.write(time.ctime(time.time()) + ' Sincronizado grupo ' + group_name +'\n')
            mgmt.tm.cm.exec_cmd('run', utilCmdArgs='config-sync to-group ' + group_name)
            #mgmt.tm.cm.exec_cmd('run', utilCmdArgs='device-group show')
 
 f.close()
