'''
Name:        sdeTools
Purpose:     Streamline the process of initializing and loading data into an
             SDE workspace.

Author:      Joel McCune (knu2xs@gmail.com)

Created:     15Mar2013
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

# global variables for defaults
globalDbms = 'PostgreSQL' # dbms
globalSuPswd = '' # su password
globalSdePswd = '' # sde password
globalOwnerName = 'owner' # data owner username
globalOwnerPswd = '' # data owner password

# default instance is local machine
globalInstance = gethostname()
# default authorization file location
globalAuthFile = ((r'C:\Program Files\ESRI\License{0}\sysgen\keycodes').
    format(arcpy.GetInstallInfo()['Version']))

class sdeWorkspace(object):

    def __init__(self):

        # attributes
        self.instance = None
        self.dbms = None
        self.suName = None
        self.suPswd = None
        self.sdeName = 'sde'
        self.sdePswd = None
        self.ownerName = None
        self.ownerPswd = None
        self.authFile = None

    def initialize(self, dbName):
        '''
        Initializes an SDE workspace and gets it ready for use according to best
        practices. First, the database is created. Second, a connection is
        created as the sde user. Third, through this sde connection a connection
        the user specified data owner is created in the geodatabase. Finally,
        the a connection is made as the data owner. This connection is returned
        by the function for use when this method is used as part of other
        methods.
        '''
        def createConnection(userName, pswd):
            '''
            Since connections are created twice, this method simply consolidates
            the code and only requries specifying the user name and password.
            '''
            try:
                # connection name string
                connectionName = (('{0} ({1}).sde').
                    format(dbName, userName))

                # where database connections are stored
                dbFolder = 'Database Connections'

                # create the connection
                arcpy.CreateDatabaseConnection_management(
                    out_folder_path = dbFolder,
                    out_name = connectionName,
                    database_platform = self.dbms,
                    instance = self.instance,
                    account_authentication = 'DATABASE_AUTH',
                    username = userName,
                    password = pswd,
                    save_user_pass = 'SAVE_USERNAME',
                    database = dbName)

                # return the connection path
                connection = path.join(dbFolder, connectionName)

                # return path to sde connection
                return connection

            except arcpy.ExecuteError():
                arcpy.AddMessage(arcpy.GetMessages())

        # create sde workspace
        try:
            arcpy.CreateEnterpriseGeodatabase_management(
                database_platform=self.dbms,
                instance_name=self.instance,
                database_name=dbName,
                database_admin=self.suName,
                database_admin_password=self.suPswd,
                gdb_admin_name=self.sdeName,
                gdb_admin_password=self.sdePswd,
                authorization_file=self.authFile)

        except arcpy.ExecuteError():
            arcpy.AddMessage(arcpy.GetMessages())

        # create connection as sde and store connection in variable
        sdeConnection = createConnection(self.sdeName, self.sdePswd)

        # add data owner user to database, it does not exist, will create
        try:
            arcpy.CreateDatabaseUser_management(
                input_database=sdeConnection,
                user_name=self.ownerName,
                user_password=self.ownerPswd)
            # create connection as data owner and store connection in attribute
            ownerConnection = createConnection(self.ownerName, self.sdePswd)

            # return owner connection for use in other methods
            return ownerConnection

        except arcpy.ExecuteError():
            arcpy.AddMessage(arcpy.GetMessages())

    def SdeFromXml(self, xmlWorkspaceFile):
        '''
        Create a new SDE workspace from an xml workspace file. First, extract
        the name of the xml file from the path and use it as the name of the
        geodatabase. Next, call the initialize method to create the geodatabase,
        connect as sde, add the data owner and create a connection as the data
        owner. Finally, load the xml workspace file thorugh the data owner
        connection.
        '''
        try:
            # extract database name from xml workspace file name in path
            dbName = (path.basename(xmlWorkspaceFile).lower()).rstrip('.xml')

            # initialize database with database name
            dbConnection = self.initialize(dbName)

            # load data through data owner connection
            arcpy.ImportXMLWorkspaceDocument_management(
                target_geodatabase = dbConnection,
                in_file = xmlWorkspaceFile)

            # return status
            return

        except arcpy.ExecuteError():
            arcpy.AddMessage(arcpy.GetMessages())

    def fileToSde(self, fileGeodatabase):
        '''
        Provides for one stop shopping when migrating from a file geodatabase
        to an SDE. It creates a new SDE geodatabase with the same name as the
        original file geodatabase and copies the entire schema into the SDE
        through the data owner connection created using the initialize method
        defined above.
        '''
        # get database name and use for input into initialize
        fgdbName = (path.basename(fileGeodatabase).lower()).rstrip('.gdb')

        # initialize sde
        dbName = self.initialize(fgdbName)

        # use walk to get all contents of file gdb
        for parent, child, objects in arcpy.da.Walk(fileGeodatabase):

            # iterate through every object returned by walk
            for object in objects:

                # copy from file to sde
                arcpy.Copy_management(
                    in_data = path.join(parent, object),
                    out_data = path.join(dbName, object))

def parameter(displayName, name, datatype, defaultValue=None,
    parameterType=None, direction=None):
    '''
    The parameter implementation makes it a little difficult to quickly
    create parameters with defaults. This method prepopulates some of these
    values to make life easier while also allowing setting a default vallue.
    '''
    # create parameter with a few default properties
    param = arcpy.Parameter(
        displayName = displayName,
        name = name,
        datatype = datatype,
        parameterType = 'Required',
        direction = 'Input')

    # set new parameter to a default value
    param.value = defaultValue

    # return complete parameter object
    return param

class Toolbox(object):
    def __init__(self):
        # ArcGIS required properties
        self.label='SDE Tools'
        self.alias='sdeTools'

        # List of tool classes associated with this toolbox
        self.tools=[CreateSdeTool, SdeFromXmlTool, FileToSdeTool]

class CreateSdeTool(object):

    def __init__(self):

        # ArcGIS tool properties
        self.label = 'Create SDE Workspace'
        self.canRunInBackground = False

        # list of parameters for tool
        self.parameters=[
            parameter('Database Name', 'dbName', 'GPString'),
            parameter('Instance', 'instance', 'GPString',
                globalInstance),
            parameter('Database Management System', 'dbms', 'GPString',
                globalDbms),
            parameter('Superuser Name', 'suName','GPString'),
            parameter('Superuser Password', 'suPswd', 'GPEncryptedString',
                globalSuPswd),
            parameter('SDE User Password', 'sdePswd', 'GPEncryptedString',
                globalSdePswd),
            parameter('Data Owner Name', 'ownerName', 'GPString',
                globalOwnerName),
            parameter('Data Owner Password', 'ownerPswd', 'GPEncryptedString',
                globalOwnerPswd),
            parameter('Authorization File', 'authFile', 'DEFile',
                globalAuthFile)]

        # database systems dropdown list items
        self.parameters[2].filter.list = ['Oracle', 'PostgreSQL', 'SQL_Server']

    def getParameterInfo(self):
        # send parameters to ArcGIS
        return self.parameters

    def isLicensed(self):
        # need to set this to check for ArcEditor/Standard license
        return True

    def updateParameters(self, parameters):
        '''
        The database management system is a three option dropdown menu. If
        the database is PostgreSQL or SQL Server, the superuser is set to a
        default, but can be changed. If Oracle, the superuser is set and
        cannot be changed.
        '''

        # set supersusers based on dbms
        if parameters[2].value == 'Oracle':
            parameters[3].value = 'sys'
            parameters[3].enabled = False
            parameters[0].enabled = False
        if parameters[2].value == 'PostgreSQL':
            parameters[3].value = 'postgres'
            parameters[3].enabled = True
            parameters[0].enabled = True
        if parameters[2].value == 'SQL_Server':
            parameters[3].value = 'sa'
            parameters[3].enabled = True
            parameters[0].enabled = True

        return

    def updateMessages(self, parameters):
        '''Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation.'''
        return

    def execute(self, parameters, messages):
        # call initialize method of sde
        return

class SdeFromXmlTool(CreateSdeTool):

    def __init__(self):

        # Call superclass constructor
        CreateSdeTool.__init__(self)

        # Replace ArcGIS tool properties
        self.label = 'XML to SDE Workspace'
        self.canRunInBackground = False

        # Replace first tool parameter to become xml workspace file
        self.parameters[0]=parameter('XML Workspace File', 'xmlFile', 'DEFile')

        # Set input file datatype to be only xml
        self.parameters[0].filter.list = ['xml']

        return

    def execute(self, parameters, messages):
        # call xml workspace method of sde
        return

class FileToSdeTool(CreateSdeTool):

    def __init__(self):

        # Call superclass constructor
        CreateSdeTool.__init__(self)

        # Replace ArcGIS tool properties
        self.label = 'File to SDE Workspace'
        self.canRunInBackground = False

        # Replace first tool parameter to become file geodatabase
        self.parameters[0] = parameter('File Geodatabase', 'fileGdb',
            'DEWorkspace')

        self.parameters[0].filter.list = ["Local Database"]

    def execute(self):
        # call fileToSde method of sde
        pass