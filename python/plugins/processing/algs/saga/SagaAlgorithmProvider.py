# -*- coding: utf-8 -*-

"""
***************************************************************************
    SagaAlgorithmProvider.py
    ---------------------
    Date                 : August 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from processing.core.AlgorithmProvider import AlgorithmProvider
from processing.core.ProcessingConfig import ProcessingConfig, Setting
from processing.core.ProcessingLog import ProcessingLog
from SagaAlgorithm212 import SagaAlgorithm212
from SagaAlgorithm213 import SagaAlgorithm213
from SplitRGBBands import SplitRGBBands
import SagaUtils
from processing.tools.system import *

class SagaAlgorithmProvider(AlgorithmProvider):

    supportedVersions = {"2.1.2": ("2.1.2", SagaAlgorithm212),
                          "2.1.3": ("2.1.3", SagaAlgorithm213),
                          "2.1.4": ("2.1.3", SagaAlgorithm213)}

    def __init__(self):
        AlgorithmProvider.__init__(self)
        self.activate = True

    def initializeSettings(self):
        AlgorithmProvider.initializeSettings(self)
        if isWindows() or isMac():
            ProcessingConfig.addSetting(Setting("SAGA",
                                    SagaUtils.SAGA_FOLDER, 'SAGA folder', ''))
        ProcessingConfig.addSetting(Setting("SAGA",
                                    SagaUtils.SAGA_IMPORT_EXPORT_OPTIMIZATION,
                                    'Enable SAGA Import/Export optimizations',
                                    False))
        ProcessingConfig.addSetting(Setting("SAGA",
                                    SagaUtils.SAGA_LOG_COMMANDS,
                                    'Log execution commands', True))
        ProcessingConfig.addSetting(Setting("SAGA",
                                    SagaUtils.SAGA_LOG_CONSOLE,
                                    'Log console output', True))

    def unload(self):
        AlgorithmProvider.unload(self)
        if isWindows() or isMac():
            ProcessingConfig.removeSetting(SagaUtils.SAGA_FOLDER)

        ProcessingConfig.removeSetting(SagaUtils.SAGA_LOG_CONSOLE)
        ProcessingConfig.removeSetting(SagaUtils.SAGA_LOG_COMMANDS)


    def _loadAlgorithms(self):
        self.algs = []
        version = SagaUtils.getSagaInstalledVersion(True)
        if version is None:
            ProcessingLog.addToLog(ProcessingLog.LOG_ERROR,
                        'Problem with SAGA installation: SAGA was not found or is not correctly installed')
            return
        if version not in self.supportedVersions:
            ProcessingLog.addToLog(ProcessingLog.LOG_ERROR,
                        'Problem with SAGA installation: installed SAGA version (%s) is not supported' % version)
            return

        folder = SagaUtils.sagaDescriptionPath()
        folder = os.path.join(folder, self.supportedVersions[SagaUtils.getSagaInstalledVersion()][0])
        for descriptionFile in os.listdir(folder):
            if descriptionFile.endswith('txt'):
                f = os.path.join(folder, descriptionFile)
                self._loadAlgorithm(f)
        self.algs.append(SplitRGBBands())

    def _loadAlgorithm(self, descriptionFile):
        try:
            alg = self.supportedVersions[SagaUtils.getSagaInstalledVersion()][1](descriptionFile)
            if alg.name.strip() != '':
                self.algs.append(alg)
            else:
                ProcessingLog.addToLog(ProcessingLog.LOG_ERROR,
                        'Could not open SAGA algorithm: '
                        + descriptionFile)
        except Exception, e:
            ProcessingLog.addToLog(ProcessingLog.LOG_ERROR,
                    'Could not open SAGA algorithm: '
                    + descriptionFile + '\n' + str(e))
    def getDescription(self):
        return 'SAGA (%s)' % SagaUtils.getSagaInstalledVersion()

    def getName(self):
        return 'saga'

    def getSupportedOutputVectorLayerExtensions(self):
        return ['shp']

    def getSupportedOutputRasterLayerExtensions(self):
        return ['tif']

    def getSupportedOutputTableLayerExtensions(self):
        return ['dbf']

    def getIcon(self):
        return QIcon(os.path.dirname(__file__) + '/../../images/saga.png')
