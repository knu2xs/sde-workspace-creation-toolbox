SDE Workspace Creation Toolbox
===========================

This is an ArcGIS Python toolbox (pyt) containing tools streamlining the process of enterprise geodatabase initialization and data loading. The toolbox currently contains three tools, Create SDE Workspace, File to SDE Workspace and XML to SDE Workspace.

The Create SDE Workspace tool creates a new SDE geodatabase and gets it ready for data loading following best practices. These best practices include, creating and initializing the geodatabase, creating a connection in ArcGIS as the administrative user (sde), adding a data owner user through the administrative connection and finally creating a connection in ArcGIS as the data owner. Once finished, data can be loaded through the data owner connection.

The File to SDE Workspace tool extends the Create SDE Workspace tool. It facilitates moving all data from a file geodatabase to an enterprise (SDE) geodatabase. Using the name of the file geodatabase to name the new enterprise geodatabase, it performs all the funtions in the Create SDE Workspace tool. Using the data owner connection, it finishes by copying all data from the file to the enterprise geodatabase.

The XML to SDE Workspace tool also extends the Create SDE Workspace tool. It creates a new enterprise (SDE) geodatabase using the name of the XML Workspace file to name the new SDE workspace and loads all the data from the XML Workspace file into the new SDE workspace. Similar to the File to SDE Workspace tool, it implements the Create SDE Workspace tool, creating a new enterprise geodatabase with a data owner connection used to load the data from the XML Workspace file.
