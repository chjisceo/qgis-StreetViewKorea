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
"""
def name():
    return "StreetViewKorea"
def description():
    return "Importatore file CXF dell'Agenzia del Territorio"
def version():
    return "Version 0.1"
def icon():
    return "icon.png"
def classFactory(iface):
    # load StreetView class from file StreetView
    from .streetviewkorea import StreetViewKorea
    return StreetViewKorea(iface)
