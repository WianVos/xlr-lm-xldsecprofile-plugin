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
from xldeploy.security.role import PermissionSet
from xldeploy.security import POSSIBLE_PERMISSIONS

logger = logging.getLogger(__name__)


class SecurityConnection(XLDConnection):
    """
    provides a connection to xldeploy and lets the user interact with the security system
    """

    @log_with(logger)
    def __init__(self, url=None, username=None, password=None, **kwargs):

        super(SecurityConnection, self).__init__(url, username, password, **kwargs)


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

    @log_with(logger)
    def get_role_permissions(self, role):
        '''
        retrieve the granted permissions for a certain role
        :param role: str: role name
        :return: RoleObject
        '''
        # check if the role exists
        if not self.role_exists(role):
            logger.error('unable to find role: %s' % role)
        # retrieve the permissions xml
        xml = self.http_get('security/granted-permissions/%s' % role)
        set = PermissionSet(xml=xml)

        return set

    @log_with(logger)
    def role_permission_exists(self, role, permission, id='global'):
        '''
        checks whether a permission is set on an id for a certain role.
        if id is not passed it will assume global permission scope is intended
        :param role: str role name
        :param permission: str permission name
        :param id: str ci id ..
        :return: True or False
        '''

        #check if the role exists
        if not self.role_exists(role):
            logger.warning("role: %s does not exist" % role)

        #check if the permission is set

        response = ET.fromstring(self.http_get("security/permission/%s/%s/%s" % (permission, role, id)))
        if 'false' in response.text:
            logger.info("permission: %s does not exist for role: %s on ci: %s " % (permission, role, id))
            return False
        else:
            logger.debug("permission: %s does exist for role: %s on ci: %s " % (permission, role, id))
            return True

        return False

    @log_with(logger)
    def create_role_permission(self, role, permission, id= 'global'):
        '''
        creates a permission on an id for a certain role.
        if id is not passed it will assume global permission scope is intended
        :param role: str role name
        :param permission: str permission name
        :param id: str ci id ..
        :return: True or False
        '''


        #check if the role exists
        if not self.role_exists(role):
            logger.error("role: %s does not exist" % role)
            return False

        #check if the permission is set or not
        # if not proceed else respond true
        if self.role_permission_exists(role, permission, id) == True:
            logger.info("permission: %s for role: %s on id: %s already set"  % (permission, role, id) )
            return True

        #create the permission
        try:
            response = self.http_put("security/permission/%s/%s/%s" % (permission, role, id) )
        except Exception:
            logger.error("unable to create permission: %s for role: %s on ci: %s " % (permission, role, id))
            return False

        #make sure the permission exists
        if self.role_permission_exists(role, permission, id) == True:
            logger.info("permission: %s for role: %s on id: %s created"  % (permission, role, id) )
            return True
        else:
            logger.warning("permission: %s for role: %s on id: %s not created"  % (permission, role, id) )
            return False

    @log_with(logger)
    def delete_role_permission(self, role, permission, id=None):
        '''
        delete a permission on an id for a certain role.
        if id is not passed it will assume global permission scope is intended
        :param role: str role name
        :param permission: str permission name
        :param id: str ci id ..
        :return: True or False
        '''
         #check if the role exists
        if not self.role_exists(role):
            logger.error("role: %s does not exist so the permission doesn't exist" % role)
            return True

        #check if the permission is set or not
        # if it is proceed else respond true
        if self.role_permission_exists(role, permission, id) == False:
            logger.info("permission: %s for role: %s on id: %s is not set"  % (permission, role, id) )
            return True

        #delete the permission
        try:
            response = self.http_delete("security/permission/%s/%s/%s" % (permission, role, id) )
        except Exception:
            logger.error("unable to delete permission: %s for role: %s on ci: %s " % (permission, role, id))
            return False

        #make sure the permission is gone
        if self.role_permission_exists(role, permission, id) == False:
            logger.info("permission: %s for role: %s on id: %s deleted"  % (permission, role, id) )
            return True
        else:
            logger.warning("permission: %s for role: %s on id: %s not deleted"  % (permission, role, id) )
            return False

    @log_with(logger)
    def save_permission(self,role, permission, strict=True):
        '''
        save a permission, if strict is set to true all the permission for the role on the id will be removed first before implementing the ones specified
        :param role: the role to save this permission for
        :param permission: permission object
        :param strict: enforce strict permissions
        :return: True/False
        '''

        # if strict is yes .. clean up first
        if strict:
            #run cleanup
            for grant in permission.possible_grants():
                self.delete_role_permission(role, grant, permission.get_id())

        # create the stuff we want
        print str(permission)
        for grant in permission:
            print "------------------------------------"
            print grant
            response = self.create_role_permission(role, grant, permission.get_id())
            if response == False:
                logger.warning("unable to create permissions for id: %s" % permission.get_id())
                return False

        return True


        # if all goes well return True
    @log_with(logger)
    def save_permission_set(self, role, permission_set):
        '''
        save en entire permission set
        :param permission_set: permissionset object
        :return: True or false
        '''
        for permission in permission_set:
           if self.save_permission(role, permission) == False:
            logger.warning("unable to create permissionset " % permission.get_id())
            return False

        return True




#GET	/security/check/{permission}/{id:.*?}	Checks if the currently logged in user has a certain permission on a CI.
#GET	/security/granted-permissions	Gets all the permissions granted to the logged in user.
#GET	/security/granted-permissions/{role}	Gets all the permissions granted to a role.
#GET	/security/permission/{permission}/{role}/{id:.*?}	Checks if a permission is granted to a role on a CI.
#PUT	/security/permission/{permission}/{role}/{id:.*?}	Grants a permission to a role on a CI.
#DELETE	/security/permission/{permission}/{role}/{id:.*?}	Revokes the permission of a role on a CI.
#GET	/security/security/	Lists the names of all available securitys in the security system.
#GET	/security/security/securitys	Lists the securitys of the currently logged in user.
#GET	/security/security/securitys/{username}	Lists the securitys of a user.
#PUT	/security/security/{security}	Creates a new security.
#POST	/security/security/{security}	Renames a security.
#DELETE	/security/security/{security}	Removes a security from the XL Deploy security system.
#PUT	/security/security/{security}/{principal}	Assigns a security to a user or group.
#DELETE	/security/security/{security}/{principal}	Removes a security from a user or group.