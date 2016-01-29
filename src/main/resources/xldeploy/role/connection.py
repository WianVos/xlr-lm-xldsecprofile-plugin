#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
import logging
from os import path
from xml.etree import ElementTree as ET

from xldeploy.decorators import log_with, timer
from xldeploy.client     import XLDConnection

logger = logging.getLogger(__name__)


class RoleConnection(XLDConnection):
    """
    provides a connection to xldeploy and lets the user interact with the role system
    """

    @log_with(logger)
    def __init__(self, url=None, username=None, password=None, **kwargs):

        super(RoleConnection, self).__init__(url, username, password, **kwargs)


    @log_with(logger)
    def role_exists(self, name):
        '''
        :param name: string : name of the role to confirm
        :return: True/False
        '''

        output = self.http_get("security/role")
        xml = ET.fromstring(output)
        for role in xml.iter('string'):
            print role.text
            if role.text == name:
                return True

        return False

    @log_with(logger)
    def create_role(self, name):
        '''
        creates a role
        :param name: role name
        :return: True or False
        '''

        # check if the role exists
        if not self.role_exists(name):
        #if not create it
            self.http_put("security/role/%s" % name)
        # verify that the role was created
            if self.role_exists(name):
                logger.info('role: %s created' % name)
                return True
        else:
            logger.warn('role: %s already exists' % name)

        logger.warn('unable to create role: %s' % name)
        return False

    @log_with(logger)
    def delete_role(self, name):
        '''
        delete a role by name
        :param name: role name
        :return: True or False
        '''
        if self.role_exists(name):
            logger.info("role: %s exists. proceeding to delete " % name)
            self.http_delete("security/role/%s" % name)
            if not self.role_exists(name):
                logger.info("deletion of role: %s has succeeded" % name)
                return True
            else:
                logger.error('role: %s not deleted' % name)
                return False
        else:
            logger.warn('role: %s does not exists deletion not needed' % name)
            return True



    @log_with(logger)
    def rename_role(self, name, new_name):
        '''
        rename a role
        :param name: current name of the role
        :param new_name: new name of the role
        :return: True or False
        '''
        print "not yet implemented"
        return False

#GET	/security/role/	Lists the names of all available roles in the security system.
#GET	/security/role/roles	Lists the roles of the currently logged in user.
#GET	/security/role/roles/{username}	Lists the roles of a user.
#PUT	/security/role/{role}	Creates a new role.
#POST	/security/role/{role}	Renames a role.
#DELETE	/security/role/{role}	Removes a role from the XL Deploy security system.
#PUT	/security/role/{role}/{principal}	Assigns a role to a user or group.
#DELETE	/security/role/{role}/{principal}	Removes a role from a user or group.