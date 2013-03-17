SDE Workspace Creation Toolbox
===========================

This is an ArcGIS Python toolbox (pyt) containing tools streamlining the process of enterprise geodatabase initialization and data loading. The toolbox currently contains three tools, Create SDE Workspace, File to SDE Workspace and XML to SDE Workspace.

The Create SDE Workspace tool creates a new SDE geodatabase and gets it ready for data loading following best practices. These best practices include, creating and initializing the geodatabase, creating a connection in ArcGIS as the administrative user (sde), adding a data owner user through the administrative connection and finally creating a connection in ArcGIS as the data owner. Once finished, data can be loaded through the data owner connection.
