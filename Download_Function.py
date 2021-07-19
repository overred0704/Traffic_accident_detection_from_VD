import pandas as pd
import numpy as np
import gzip
import urllib
from urllib.request import urlopen
import requests
import os
from xml.dom import minidom
import zipfile

class Converter():
 
  def start(self):
    xmldoc = minidom.parse('temp.xml')
    VDID = xmldoc.getElementsByTagName('VDID')
    LinkID = xmldoc.getElementsByTagName('LinkID')
    LaneID = xmldoc.getElementsByTagName('LaneID')
    Speed = xmldoc.getElementsByTagName('Speed')
    Occupancy = xmldoc.getElementsByTagName('Occupancy')
    Volume = xmldoc.getElementsByTagName('Volume')

    #VDID+linkID
    cols1 = ["VDID", "LinkID"] 
    rows1 = []

    for i in range(len(VDID)):
      rows1.append({'VDID':VDID[i].firstChild.data,
            'LinkID':LinkID[i].firstChild.data})
    df1 = pd.DataFrame(rows1, columns=cols1)

    #Speed, occupancy, volume
    cols2 = ["Speed", "Occupancy" ,'Volume'] 
    rows2 = []

    temp_occupancy = []
    temp_speed = []
    temp_pcu = []
    count= 0

    for j in range(len(LaneID)-1):
      #計算車當量
      a,b,c = 3*j,3*j+1,3*j+2
      pcu = int(Volume[a].firstChild.data)+(int(Volume[b].firstChild.data))*1.5+(int(Volume[c].firstChild.data))*2
      
      #如果現在跟下一組都0直接輸出
      if int(LaneID[j].firstChild.data)==0 and int(LaneID[j+1].firstChild.data) == 0 :
        temp_occupancy.append(int(Occupancy[j].firstChild.data))
        temp_speed.append(int(Speed[j*4].firstChild.data))
        temp_pcu.append(pcu)

        occ , spd , vol = np.mean(temp_occupancy) , np.mean(temp_speed) , np.mean(temp_pcu)
        temp_occupancy, temp_speed, temp_pcu = [],[],[]

        #print('佔有率:' , occ , '速度:' , spd , '當量:' , vol)
        rows2.append({'Speed':spd, 'Occupancy':occ,'Volume':vol})
        count +=1

      #如果下一組比較大就加
      elif int(LaneID[j+1].firstChild.data) > int(LaneID[j].firstChild.data):
        temp_occupancy.append(int(Occupancy[j].firstChild.data))
        temp_speed.append(int(Speed[j*4].firstChild.data))
        temp_pcu.append(pcu)

      #如果下一組比較小就結束 取平均 歸零
      elif int(LaneID[j+1].firstChild.data) < int(LaneID[j].firstChild.data):
        temp_occupancy.append(int(Occupancy[j].firstChild.data))
        temp_speed.append(int(Speed[j*4].firstChild.data))
        temp_pcu.append(pcu)

        occ , spd , vol = np.mean(temp_occupancy) , np.mean(temp_speed) , np.mean(temp_pcu)
        temp_occupancy, temp_speed, temp_pcu = [],[],[]

        #print('佔有率:' , occ , '速度:' , spd , '當量:' , vol)
        rows2.append({'Speed':spd, 'Occupancy':occ,'Volume':vol})
        count +=1

    #最後一組的輸出
    j=len(LaneID)-1
    a,b,c = 3*j,3*j+1,3*j+2
    pcu = int(Volume[a].firstChild.data)+(int(Volume[b].firstChild.data))*1.5+(int(Volume[c].firstChild.data))*2
    temp_occupancy.append(int(Occupancy[j-1].firstChild.data))
    temp_speed.append(int(Speed[(j-1)*4].firstChild.data))
    temp_pcu.append(pcu)

    occ , spd , vol = np.mean(temp_occupancy) , np.mean(temp_speed) , np.mean(temp_pcu)

    temp_occupancy, temp_speed, temp_pcu = [],[],[]
    count +=1
    rows2.append({'Speed':spd, 'Occupancy':occ,'Volume':vol})
    #print('佔有率:' , occ , '速度:' , spd , '當量:' , vol)
    #print('總數:',count)

    df2 = pd.DataFrame(rows2, columns=cols2) 
    

    #concat and save csv file
    final = pd.concat([df1,df2],axis=1)
    final.to_csv(self.out,encoding="utf_8_sig")
    print('Convert is done') 
    print('-------------------------------') 
    
    
class VD_download(Converter):
  def __init__(self, year, month):
    self.year = year
    self.month = month

  def set_start_end(self, start_day ,end_day):
    self.start_day = start_day
    self.end_day = end_day

  def set_path(self, output_path):
    self.output_path = output_path

  def zip_file(self, filename):
    filename = (filename + '.zip')
    resource = self.output_path
    z = zipfile.ZipFile(filename, 'w')
    for f in os.listdir(resource):
      if f.endswith('.csv'):
        print(f, 'is zipped')
        z.write(os.path.join(resource, f), f, zipfile.ZIP_DEFLATED)
    print('-------------------------------')
    print('zip process is done!')
    z.close()
 
  def run(self):
    year = str(self.year)

    mon = str(0) + str(self.month) if self.month<10 else str(self.month)

    for k in range(self.start_day,self.end_day+1):
      day = str(0) + str(k) if k <=9 else str(k)
      for i in range(0,24):
        hours = str(0) + str(i) if i<= 9 else str(i)
        for j in range(0,60):
          min = str(0) + str(j) if j <= 9 else str(j)

          self.get_data(year, mon, day, hours, min)

  def get_data(self, year, mon, day, hours, min):

    u = 'https://tisvcloud.freeway.gov.tw/history/motc20/VD/'+ year + mon + day + '/VDLive_' + hours + min + '.xml.gz'


    try:
      urlopen(u)
    except:
      print(mon,day,hours,min,'is not found')
      print('-------------------------------')
      pass
    else:
      file_name = u.split("/")[-1]
      urllib.request.urlretrieve(u, file_name)

      f=gzip.open(file_name,'r')
      xmldata = f.read()
      f.close()
      print (mon,day,hours,min,'is downloaded')
      with open('temp' +'.xml', 'wb') as file:
          file.write(xmldata)

      self.out = self.output_path + mon + day + hours + min + '.csv'

      self.start()
