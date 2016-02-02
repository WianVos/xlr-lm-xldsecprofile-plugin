#XL Release Xl deploy security profile plugin

## Preface
This plugin enables configuring basic project setup in XL-Deploy using a basic template

## Overview
This plugin accomodates the setup and configuration of new projects based on preconfigurable templates stored in the XL-Release repository.

## Installation

### files
Copy the plugin JAR file into the `SERVER_HOME/plugins` directory of XL Release.

### configuration

make sure that xl-release/conf/script.policy contains the line

```
    permission  java.net.SocketPermission "*", "connect, listen, resolve";
```
pay attention to the listen directive . This really should be in that line.

### prerequisites

This plugin depends on xlr-xldeploy-plugin. (it needs the xldeploy.server config item from that plugin)

### Limitations

## Configuration items & tasks

### configuration items

+ lm.xldSecurityProfileTemplate
    * `templateJson` (a string containing json describing the template)
    * `templateVariables` (description of the variables in the template.. just there for documentation reference at this point)

### supported task

+ lm.createProjectSecurityStructure
    * `template` (choice of configured templates)
    * `inputData` (the data that will be used to resolve the template to configurable ci's in xldeploy
                    example: variable=value:variable=value1,value2,value3)
    * `xldeploy server` (the xldeploy server to execute the template on )




## Example Use Case
If u use an xl-release template to setup a new project environment this plugin will facilitate the creation of a directory structure and the setup of premission for different roles
 