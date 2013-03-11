'''
Name:
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

# global variables to be set and reused
globalInstance=gethostname()
globalDbms='PostgreSQL' # dbms
globalSuPswd='' # su password
globalSdePswd='' # sde password
globalOwnerName='owner' # data owner username
globalOwnerPswd='' # data owner password
# authorization file
globalAuthFile=r'C:\Program Files\ESRI\License10.1\sysgen\keycodes'

# method used by all tools
def methodCreateSde(parameters):


class Toolbox(object):

    def __init__(self):
        '''Define the toolbox (the name of the toolbox is the name of the
        .pyt file).'''
        self.label='SDE Tools'
        self.alias='SDE Tools'

        # List of tool classes associated with this toolbox
        self.tools=[createSde, createSdeLoadXml]

class createSde(object):

    def __init__(self):
        '''Define the tool (tool name is the name of the class).'''
        self.label='Create SDE Workspace'
        self.description=('Calls the Create Enterprise Geodatabase tool, with '+
            'with a lot of the parameters already pre-populated to make life '+
            'a little easier.')
        self.canRunInBackground=False

    def getParameterInfo(self):
        '''Define parameter definitions'''
        param0=arcpy.Parameter(
            displayName='Database Name',
            name='dbName',
            datatype='GPString',
            parameterType='Required',
            direction='Input')
        param1=arcpy.Parameter(
            displayName='Instance',
            name='instance',
            datatype='GPString',
            parameterType='Required',
            direction='Input')
        param2=arcpy.Parameter(
            displayName='Database Management System',
            name='dbms',
            datatype='GPString',
            parameterType='Required',
            direction='Input')
        param3=arcpy.Parameter(
            displayName='Superuser Name',
            name='suName',
            datatype='GPString',
            parameterType='Required',
            direction='Input')
        param4=arcpy.Parameter(
            displayName='Superuser Password',
            name='suPswd',
            datatype='GPEncryptedString',
            parameterType='Required',
            direction='Input')
        param5=arcpy.Parameter(
            displayName='SDE User Password',
            name='sdePswd',
            datatype='GPEncryptedString',
            parameterType='Required',
            direction='Input')
        param6=arcpy.Parameter(
            displayName='Data Owner Name',
            name='dataownerName',
            datatype='GPString',
            direction='Input')
        param7=arcpy.Parameter(
            displayName='Data Owner Password',
            name='dataownerPassword',
            datatype='GPEncryptedString',
            direction='Input')
        param8=arcpy.Parameter(
            displayName='Authorization File',
            name='authFile',
            datatype='DEFile',
            parameterType='Required',
            direction='Input')

        # database options
        param2.filter.list=['Oracle', 'PostgreSQL', 'SQL_Server']

        # set parameter defaults
        param1.value=globalInstance # instance
        param2.value=globalDbms # dbms
        param4.value=globalSuPswd # su password
        param5.value=globalSdePswd # sde password
        param6.value=globalOwnerName # data owner username
        param7.value=globalOwnerPswd # data owner password
        param8.value=globalAuthFile # authorization file

        # list and return parameters
        params=[param0, param1, param2, param3, param4, param5, param6, \
            param7, param8]
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

        # import os
        from os.path import join

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
            sdeConnectionPath=join(dbFolder, sdeConnectionName)

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
            ownerConnectionPath=join(dbFolder, ownerConnectionName)
            return ownerConnectionPath

        except arcpy.ExecuteError():
            arcpy.AddMessage(('Could not create connection as data owner: {0}')\
                .format(ownerName))
            arcpy.AddMessage(arcpy.GetMessages())

            return