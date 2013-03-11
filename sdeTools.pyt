'''
Name:        SDE Workspace Tools
Purpose:

Author:      Joel McCune (knu2xs@gmail.com)

Created:     07Mar2013
Copyright:   (c) Joel McCune 2013
Licence:
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    The GNU General Public License can be found at
    <http://www.gnu.org/licenses>.
'''

# import modules
import arcpy
from socket import gethostname
from os import path

# global variables to be set and reused
globalInstance=gethostname()
globalDbms='PostgreSQL' # dbms
globalSuPswd='' # su password
globalSdePswd='' # sde password
globalOwnerName='owner' # data owner username
globalOwnerPswd='' # data owner password
# authorization file
globalAuthFile=r'C:\Program Files\ESRI\License10.1\sysgen\keycodes'

def newParamater(displayName, name,  datatype, defaultValue = None,
    filterList = None, parameterType = 'Required', direction = 'Input'):

    # initialize the parameter for ArcGIS
    param = arcpy.Parameter(
        displayName = displayName,
        name = name,
        datatype = datatype,
        parameterType = parameterType,
        direction = direction)

    # assign a default value
    if defaultValue is not None:
        param.value = defaultValue

    # apply a filter list
    if filterList is not None:
        param.filter.list = filterList

    # return ArcGIS Parameter type with propertites set
    return param

class Toolbox(object):

    def __init__(self):
        '''Define the toolbox (the name of the toolbox is the name of the
        .pyt file).'''
        self.label='SDE Tools'
        self.alias='SdeTools'

        # List of tool classes associated with this toolbox
        self.tools=[CreateSde, SdeFromXml]

class CreateSde(object):

    def __init__(self):
        '''Define the tool (tool name is the name of the class).'''
        self.label='Create SDE Workspace'
        self.canRunInBackground=False

    def getParameterInfo(self):
        '''Define parameter definitions'''

        # arguments for tool parameters
        param0 = newParamater('Database Name', 'dbName', 'GPString')
        param1 = newParamater('Database Management System', 'dbms', 'GPString',
            globalDbms, ['Oracle', 'PostgreSQL', 'SQL_Server'])
        param2 = newParamater('Instance', 'instance', 'GPString',
            globalInstance)
        param3 = newParamater('Superuser Name', 'suName', 'GPString')
        param4 = newParamater('Superuser Password', 'suPswd', 'GPString',
            globalSuPswd)
        param5 = newParamater('SDE User Password', 'sdePswd',
            'GPEncryptedString', globalSdePswd)
        param6 = newParamater('Data Owner Name', 'dataownerName',
            'GPString', globalOwnerName)
        param7 = Param('Data Owner Password', 'dataownerPassword',
            'GPEncryptedString', globalOwnerPswd)
        param8 = newParamater('Authorization File', 'authFile', 'DEFile',
            globalAuthFile)

        params = [param0, param1, param2, param3, param4, param5, param6,
            param7, param8]

        # return parameters
        return params

    def isLicensed(self):
        '''Set whether tool is licensed to execute.'''
        return True

    def updateParameters(self, parameters):
        '''This fuction is called whenever a parameter changes.'''
        '''The database management system is a three option dropdown menu. If
        the database is PostgreSQL or SQL Server, the superuser is set to a
        default, but can be changed. If Oracle, the superuser is set and
        cannot be changed.'''

        # set supersusers based on dbms
        if parameters[2].value=='Oracle':
            parameters[3].value='sys'
            parameters[3].enabled=False
            parameters[0].enabled=False
        if parameters[2].value=='PostgreSQL':
            parameters[3].value='postgres'
            parameters[3].enabled=True
            parameters[0].enabled=True
        if parameters[2].value=='SQL_Server':
            parameters[3].value='sa'
            parameters[3].enabled=True
            parameters[0].enabled=True

        return

    def updateMessages(self, parameters):
        '''Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation.'''
        return

    def execute(self, parameters, messages):
        '''The source code of the tool.'''
        # assign parameters to variables
        dbName=parameters[0].valueAsText
        instance=parameters[1].valueAsText
        dbms=parameters[2].valueAsText
        suName=parameters[3].valueAsText
        suPswd=parameters[4].value
        sdeName='sde'
        sdePswd=parameters[5].value
        ownerName=parameters[6].valueAsText
        ownerPswd=parameters[7].value
        authFile=parameters[8].value

        # testing message
        for parameter in parameters:
            arcpy.AddMessage(parameter)

        # assign parameters to variables
        dbName=parameters[0]
        instance=parameters[1]
        dbms=parameters[2]
        suName=parameters[3]
        suPswd=parameters[4]
        sdeName='sde'
        sdePswd=parameters[5]
        ownerName=parameters[6]
        ownerPswd=parameters[7]
        authFile=parameters[8]

        # set up some other variables
        dbFolder='Database Connections'

        # account for Oracle not accepting a database name
        if dbms=='Oracle':
            dbName=''

        # create sde workspace
        try:
            arcpy.CreateEnterpriseGeodatabase_management (
                database_platform=dbms,
                instance_name=instance,
                database_name=dbName,
                database_admin=suName,
                database_admin_password=suPswd,
                gdb_admin_name=sdeName,
                gdb_admin_password=sdePswd,
                authorization_file=authFile)
            arcpy.AddMessage(
                ('Successfully created {0} geodatabase').format(dbName))
        except arcpy.ExecuteError():
            arcpy.AddMessage('Could not create geodatabase.')
            arcpy.AddMessage(arcpy.GetMessages())

        # add connection as sde user
        try:
            # connection name string
            sdeConnectionName=('{0} ({1}).sde').format(dbName, sdeName)

            arcpy.CreateDatabaseConnection_management(
                out_folder_path=dbFolder,
                out_name=sdeConnectionName,
                database_platform=dbms,
                instance=instance,
                account_authentication='DATABASE_AUTH',
                username=sdeName,
                password=sdePswd,
                save_user_pass='SAVE_USERNAME',
                database=dbName)
            arcpy.AddMessage('Successfully created connection as sde user.')

            # full connection path
            sdeConnectionPath=path.join(dbFolder, sdeConnectionName)

        except arcpy.ExecuteError():
            arcpy.AddMessage('Unable to connect as sde user.')
            arcpy.AddMessage(arcpy.GetMessages())

        # create data owner user
        try:
            arcpy.CreateDatabaseUser_management(
                input_database=sdeConnectionPath,
                user_name=ownerName,
                user_password=ownerPswd)
            arcpy.AddMessage(('Successfully created data owner user: {0}').
                format(ownerName))

        except arcpy.ExecuteError():
            arcpy.AddMessage(
                ('Could not create data owner user: {0}').format(ownerName))
            arcpy.AddMessage(arcpy.GetMessages())

        # add dataowner connection
        try:
            # connection name string
            ownerConnectionName=('{0} ({1}).sde').format(dbName, ownerName)

            arcpy.CreateDatabaseConnection_management(
                out_folder_path=dbFolder,
                out_name=ownerConnectionName,
                database_platform=dbms,
                instance=instance,
                account_authentication='DATABASE_AUTH',
                username=ownerName,
                password=ownerPswd,
                save_user_pass='SAVE_USERNAME',
                database=dbName)
            arcpy.AddMessage(('Successfully created connection as data owner: '+
                '{0}').format(ownerName))

            # full connection path
            ownerConnectionPath=path.join(dbFolder, ownerConnectionName)
            return [ownerConnectionPath]

        except arcpy.ExecuteError():
            arcpy.AddMessage(('Could not create connection as data owner: {0}')\
                .format(ownerName))
            arcpy.AddMessage(arcpy.GetMessages())

class SdeFromXml(CreateSde):

    def __init__(self):
        '''Define the tool (tool name is the name of the class).'''
        self.label='Create SDE from XML Workspace File'
        self.canRunInBackground=False

    def getParameterInfo(self):
        '''Define parameter definitions'''

        # don't work so hard, get parameters from CreateSde
        params=CreateSde.getParameterInfo()

        # replace first parameter in list, param0, with name of xml file
        params[0] = newParamater('XML Workspace File', 'xmlFile',  'DEFile')

        # return parameters
        return params

    def execute(self, parameters, messages):

        # intercept param[0], the path to the xml file
        xmlFile = parameters[0]

        # extract filename, make lowercase, and strip xml extension
        parameters[0] = ((path.basename(xmlFile)).lower()).rstrip('.xml')

        # execute CreateSde and get path to dataowner connection
        ownerConnection = CreateSde.execute(self, parameters, messages)

        # load xml through dataowner connection
        try:
            arcpy.ImportXMLWorkspaceDocument_management(
                target_geodatabase = ownerConnection,
                in_file = xmlFile,
                import_type = 'DATA')

        except arcpy.ExecuteError:
            arcpy.AddMessage(('Data load failed from {0}').format(xmlFile))
            arcpy.AddMessage(arcpy.GetMessages())


# testing
if __name__ == '__main__':
    database = CreateSde()

    xmlDb = SdeFromXml()