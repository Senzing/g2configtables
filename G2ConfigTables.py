#--python imports
import optparse
import sys
import os
import json

#--optional imports
try: import pyodbc
except: pass
try: import sqlite3
except: pass

#--project classes
import G2Exception
from G2Config import G2Config

#======================
class G2ConfigTables:
#======================


    #----------------------------------------
    def __init__(self, configFile,g2iniParams,configuredDatasourcesOnly=False):
        self.configFileName = configFile
        self.g2iniParams = g2iniParams
        self.success = True
        self.configuredDatasourcesOnly = configuredDatasourcesOnly

		
    #----------------------------------------
    #-- g2 specific calls
    #----------------------------------------

    #----------------------------------------
    def loadConfig(self, tableName):
        cfgDict = {}
        with open(self.configFileName) as data_file:
            cfgDataRoot = json.load(data_file, encoding="utf-8")
        configNode = cfgDataRoot['G2_CONFIG']
        tableNode = configNode[tableName.upper()]
        for rowNode in tableNode:
            cfgNodeEntry = {}
            if tableName.upper() == 'CFG_DSRC':
            	cfgNodeEntry['ID'] = rowNode['DSRC_ID'];
            	cfgNodeEntry['DSRC_CODE'] = rowNode['DSRC_CODE'];
            	cfgDict[cfgNodeEntry['DSRC_CODE']] = cfgNodeEntry
            elif tableName.upper() == 'CFG_ETYPE':
            	cfgNodeEntry['ID'] = rowNode['ETYPE_ID'];
            	cfgNodeEntry['ETYPE_CODE'] = rowNode['ETYPE_CODE'];
            	cfgDict[cfgNodeEntry['ETYPE_CODE']] = cfgNodeEntry
            elif tableName.upper() == 'CFG_FTYPE':
            	cfgNodeEntry['ID'] = rowNode['FTYPE_ID'];
            	cfgNodeEntry['FTYPE_CODE'] = rowNode['FTYPE_CODE'];
            	cfgNodeEntry['DERIVED'] = rowNode['DERIVED'];
            	cfgDict[cfgNodeEntry['FTYPE_CODE']] = cfgNodeEntry
            elif tableName.upper() == 'CFG_ERRULE':
            	cfgNodeEntry['ID'] = rowNode['ERRULE_ID'];
            	cfgNodeEntry['ERRULE_CODE'] = rowNode['ERRULE_CODE'];
            	cfgNodeEntry['REF_SCORE'] = rowNode['REF_SCORE'];
            	cfgNodeEntry['RTYPE_ID'] = rowNode['RTYPE_ID'];
            	cfgDict[cfgNodeEntry['ID']] = cfgNodeEntry
            elif tableName.upper() == 'CFG_ATTR':
            	cfgNodeEntry['ATTR_ID'] = rowNode['ATTR_ID'];
            	cfgNodeEntry['ATTR_CODE'] = rowNode['ATTR_CODE'];
            	cfgNodeEntry['ATTR_CLASS'] = rowNode['ATTR_CLASS'];
            	cfgNodeEntry['FTYPE_CODE'] = rowNode['FTYPE_CODE'];
            	cfgNodeEntry['FELEM_CODE'] = rowNode['FELEM_CODE'];
            	cfgNodeEntry['FELEM_REQ'] = rowNode['FELEM_REQ'];
            	cfgDict[cfgNodeEntry['ATTR_CODE']] = cfgNodeEntry
            else:
            	return None
        return cfgDict

    #----------------------------------------
    def addDataSource(self, dataSource):
        ''' adds a data source if does not exist '''
        returnCode = 0  #--1=inserted, 2=updated
        g2_config_module = G2Config()
        g2_config_module.initV2('pyG2AddDataSource', self.g2iniParams, False)

        with open(self.configFileName) as data_file:
            cfgDataRoot = data_file.read() #.decode('utf8')
            configHandle = g2_config_module.load(cfgDataRoot)
            dsrcExists = False
            dsrcListDocString = bytearray()
            ret_code = g2_config_module.listDataSources(configHandle,dsrcListDocString)
            dsrcListDoc = json.loads(dsrcListDocString.decode())
            dsrcListNode = dsrcListDoc['DSRC_CODE']
            for dsrcNode in dsrcListNode:
                if dsrcNode.upper() == dataSource:
                    dsrcExists = True
            if dsrcExists == False :
                if self.configuredDatasourcesOnly == False:
                    g2_config_module.addDataSource(configHandle,dataSource)
                    newConfig = bytearray()
                    ret_code = g2_config_module.save(configHandle,newConfig)
                    with open(self.configFileName, 'w') as data_file2:
                        json.dump(json.loads(newConfig.decode()),data_file2, indent=4)
                    returnCode = 1
                else:
                    raise G2Exception.UnconfiguredDataSourceException(dataSource)
            g2_config_module.close(configHandle)
            g2_config_module.destroy()
            del g2_config_module
        return returnCode

    #----------------------------------------
    def addEntityType(self, entityType):
        ''' adds an entity type if does not exist '''
        # For now, we just add a data source, which includes creating the entity type.
        return self.addDataSource(entityType)

    #----------------------------------------
    def verifyEntityTypeExists(self,entityType):
        etypeExists = False
        with open(self.configFileName) as data_file:
            cfgDataRoot = json.load(data_file, encoding="utf-8")
        configNode = cfgDataRoot['G2_CONFIG']
        tableNode = configNode['CFG_ETYPE']
        for rowNode in tableNode:
            if rowNode['ETYPE_CODE'] == entityType:
                etypeExists = True
        return etypeExists

