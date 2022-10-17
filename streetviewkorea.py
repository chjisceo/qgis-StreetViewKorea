# -*- coding: utf-8 -*-
"""
/***************************************************************************
 StreetViewKorea
                                 A QGIS plugin
 StreetViewKorea
                             -------------------
        begin                : 2022-05-17
        copyright            : (C) 2022 by StreetViewKorea
        email                : StreetViewKorea
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
 ***************************************************************************/
"""
# Import the PyQt and QGIS libraries
from PyQt5 import Qt, QtCore, QtWidgets, QtGui, QtWebKit, QtWebKitWidgets, QtXml, QtNetwork, uic
import subprocess
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from .resources_rc import *
# Import the code for the dialog
import os.path
import math
import webbrowser
import requests
import json
import warnings
warnings.filterwarnings(action='ignore')
rb=QgsRubberBand(iface.mapCanvas(),QgsWkbTypes.PointGeometry )
rl=QgsRubberBand(iface.mapCanvas(),QgsWkbTypes.LineGeometry )
premuto= False
linea=False
point0=iface.mapCanvas().getCoordinateTransform().toMapCoordinates(0, 0)
point1=iface.mapCanvas().getCoordinateTransform().toMapCoordinates(0, 0)


class StreetViewKorea:

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        
        # locale = QtCore.QSettings().value("locale/userLocale", defaultValue="")[0:2]
        # localePath = os.path.join(self.plugin_dir, 'i18n', 'streetview_{}.qm'.format(locale))

        # if os.path.exists(localePath):
        #     self.translator = QTranslator()
        #     self.translator.load(localePath)
        #
        #     if qVersion() > '4.3.3':
        #         QCoreApplication.installTranslator(self.translator)
        
    def run(self):
        tool = PointTool(self.iface.mapCanvas())
        self.iface.mapCanvas().setMapTool(tool)

    def initGui(self):
        self.action = QtWidgets.QAction(QtGui.QIcon(os.path.join(os.path.dirname(__file__),"icon.png")),"Click and Drag on Map", self.iface.mainWindow())
        self.action.triggered.connect(self.run)

        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("StreetViewKorea", self.action)
        
    def unload(self):
        self.iface.removePluginMenu("StreetViewKorea", self.action)
        self.iface.removeToolBarIcon(self.action)


    
       
  
class PointTool(QgsMapTool):  

        
        def __init__(self, canvas):
        
            QgsMapTool.__init__(self, canvas)
            self.canvas = canvas    
            self.plugin_dir = os.path.dirname(__file__)
            chrome_path = os.path.join(self.plugin_dir, 'chrome_path.txt')
        
            # check chrome.exe path
            if os.path.isfile(chrome_path) == False:
                filepath = self.findFile("chrome.exe", "C:\\")
                with open(chrome_path,'x') as f:
                    f.write(filepath.replace("\\",'/'))
                    
            else:
                with open(chrome_path,'r') as f:
                    self.chrome_path = f.read().replace('\\','/')
                
        def findFile(self, name, path):
            for dirpath, dirname, filename in os.walk(path):
                if name in filename:
                    return os.path.join(dirpath, name)
                        
    
        def canvasPressEvent(self, event):
            x = event.pos().x()
            y = event.pos().y()
            global rb ,premuto ,point0
            if not premuto: 
              premuto=True
              rb=QgsRubberBand(iface.mapCanvas(),QgsWkbTypes.PointGeometry )
              rb.setColor ( QtCore.Qt.red )
              point0 = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
              rb.addPoint(point0)  
  
        def canvasMoveEvent(self, event):
              x = event.pos().x()
              y = event.pos().y()        
              global premuto,point0,point1,linea,rl
              if premuto:
               if not linea:              
                rl.setColor ( QtCore.Qt.red )
                point1 = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
                rl.addPoint(point0)  
                rl.addPoint(point1)
                linea=True
               else:
                if linea: 
                  point1 = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
                  rl.reset(QgsWkbTypes.LineGeometry)
                  rl.addPoint(point0)  
                  rl.addPoint(point1)
                  
                  
      
        def canvasReleaseEvent(self, event):
            event.modifiers()
            if (event.modifiers() & QtCore.Qt.ControlModifier):
                CTRLPressed = True
            else:
                CTRLPressed = None
            
        
            global premuto,linea,rb,rl,point1,point0
            angle = math.atan2(point1.x() - point0.x(), point1.y() - point0.y())
            angle = math.degrees(angle)if angle>0 else (math.degrees(angle) + 180)+180
            premuto=False
            linea=False
            actual_crs = self.canvas.mapSettings().destinationCrs()

            if CTRLPressed:  # NAVER when you drag with ctrl
                # Naver EPSG:3857
                crsDest = QgsCoordinateReferenceSystem(4326)  # NAVER
                xform = QgsCoordinateTransform(actual_crs, crsDest, QgsProject.instance())
                pt1 = xform.transform(point0)

                # Get panoid
                n_url = 'https://m.map.naver.com/viewer/panorama.naver?lng={}&lat={}'.format(str(pt1.x()), str(pt1.y()))
                response = requests.get(n_url, verify=False)
                if response.status_code != 200:
                    QgsMessageLog.logMessage(f"네이버 지도 오류 [{response.status_code} ERROR : {response.reason}]")
                else:
                    # get panorama part
                    text = response.text
                    idx = text.find('"panorama"') + 12
                    end_idx = text[idx:].find("}")
                    pano = text[idx:idx + end_idx + 1]

                    # id, pan, tilt, lng, lat, fov
                    pr = json.loads(pano)

                    # change coord as EPSG:3857
                    crsDest = QgsCoordinateReferenceSystem(3857)  # NAVER
                    xform = QgsCoordinateTransform(actual_crs, crsDest, QgsProject.instance())
                    pt2 = xform.transform(point0)

                    # change angle range 0~179 , -180~0
                    if angle > 180:
                        angle -= 360

                    # create full naver url
                    naver_url = "https://map.naver.com/v5/?c={0},{1},16,0,0,0,dha&p={2},{3},{4},80,Float".format(str(pt2.x()),str(pt2.y()),pr["id"],str(float(angle)),pr['tilt'])

                    try:
                        webbrowser.get(f"{self.chrome_path} %s").open(naver_url)

                    except:
                        QgsMessageLog.logMessage("ERROR : CANNOT FIND 'chrome.exe' file. Please install chrome first.")

            else:  # KAKAO when you drag
                crsDest = QgsCoordinateReferenceSystem(5181)  # WTM
                xform = QgsCoordinateTransform(actual_crs, crsDest, QgsProject.instance())
                pt1 = xform.transform(point0)


                # KAKAO request to get infos
                kakao_url = f'https://rv.map.kakao.com/roadview-search/v2/nodes?PX={int(pt1.x())}&PY={int(pt1.y())}&RAD=35&PAGE_SIZE=50&INPUT=wtm&TYPE=w&SERVICE=glpano'

                # send url and get Full URL
                response = requests.get(url=kakao_url, verify=False)
                if response.status_code != 200:
                    QgsMessageLog.logMessage(f"카카오맵 오류 [{response.status_code} ERROR : {response.reason}]")
                else:
                    st = json.loads(response.text)

                    rd = st['street_view']['streetList'][0]
                    k_return_url = f"https://map.kakao.com/?panoid={rd['id']}&pan={angle}&zoom=0&map_type=TYPE_MAP&map_attribute=ROADVIEW&urlX={rd['wcongx']}&urlY={rd['wcongy']}"

                    # Run on Chrome
                    try:
                        webbrowser.get(f"{self.chrome_path} %s").open(k_return_url)

                    except:
                        QgsMessageLog.logMessage("ERROR : CANNOT FIND 'chrome.exe' file. Please install chrome first.")

            rl.reset()
            rb.reset()           
            self.canvas.unsetMapTool(self)           
        def activate(self):
            pass
    
        def deactivate(self):
            pass
           
        def isZoomTool(self):
            return False
    
        def isTransient(self):
            return False
    
        def isEditTool(self):
            return True    