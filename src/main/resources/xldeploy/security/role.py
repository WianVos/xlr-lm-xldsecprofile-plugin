import logging
from xml.etree import ElementTree as ET

import xldeploy
from xldeploy.decorators import log_with, timer
from xldeploy.security import POSSIBLE_PERMISSIONS

logger = logging.getLogger(__name__)


class Role(object):
    
    @log_with(logger)
    def __init__(self, **kwargs):
        '''
        initialization method for the Role object
        :param name: str: name of the role
        :param permission_xml: str: string representation of the permissions of this role 
        :param permissions: list: list containing permissions objects             
        :return: Role Object Instance
        '''
        
        # cold variable initialization
        self.__name = None
        self.__xml = None
        self.__permissions = []
        
        try:
            self.__name = kwargs['name']
        except KeyError:
            self.__name = None
        
        try:
            self.__xml = kwargs['permission_xml']
        except KeyError:
            self.__xml = None
        
        
        try:
            self.__permissions = kwargs['permission']
        except KeyError:
            self.__permissions = []
        
        

    def parse_xml(self, xml):
        '''
        parse the xml as handed to the object at initialization
        :param xml:
        :return:
        '''
        print "not yet implemented"

class Permission(object):
    from os import path

    def __init__(self, **kwargs):
        '''
        Permission object initialization method
        :param Id: the id of the object to grant permissions on
        :param permissions: list of permissions to grant
        :param type: str: Global/Applications/Environments/Infrastructure
        :return: permission instance object
        '''

        self.__id = None
        self.__granted = []
        self.__type = None


        try:
            self.__id = kwargs['id']
        except KeyError:
            self.__id = 'global'

        try:
            self.__granted = kwargs['granted']
        except KeyError:
            self.__granted = []

        try:
            self.__type = kwargs['type']
        except KeyError:
            self.__type = None

        if self.__id is not None:
            self.__type = self.get_type_from_id()

    def __str__(self):
        return "%s: %s" % (self.__id, str(self.__granted) )

    def get_type_from_id(self):
        if not self.__id == 'global':
            return self.__id.split('/')[0]
        return 'global'

    def add_grant(self, grant):
        if self.validate_grant(grant):
            self.__granted.append(grant)
        else:
            logger.error("invalid grant: %s for permission type: %s" % (grant, self.__type))

    def validate_grant(self, grant):
        if grant in POSSIBLE_PERMISSIONS[self.__type]:
            return True
        else:
            return False
        
    def get_id(self):
        return self.__id

    def __iter__(self): # Python 3: def __next__(self)
        """
        this method provides a generator to make the PermissionSet iterable
        :return:
        """
        c = 0
        i = len(self.__granted)

        while c < i:
          yield self.__granted[c]
          c+=1

    def possible_grants(self):
        return POSSIBLE_PERMISSIONS[self.__type]

class PermissionSet(object):
    
    def __init__(self, **kwargs):

        try:
            self.__permissions = kwargs['permissions']
        except KeyError:
            self.__permissions = []



        try:
            self.parse_permission_xml(kwargs['xml'])
        except KeyError:
            pass

    def __str__(self):

        l = []

        for perm in self.__permissions:
            l.append('%s\n' % (str(perm)))

        s = ''.join(l)
        return s

    def add_permission(self, permission):
        
        self.__permissions.append(permission)
        

    def parse_permission_xml(self, xml):
        # get the root element from the string object
        xml_root = ET.fromstring(xml)

        # loop over the xml looking for entries
        for x in xml_root.iter('entry'):
            #get the id
            id =  x.find('string').text
            # instantiate a net permission
            permission = Permission(id = id)
            set = x.find('set')
            for i in set.iter('string'):

                permission.add_grant(i.text)

            self.add_permission(permission)

    def __iter__(self): # Python 3: def __next__(self)
        """
        this method provides a generator to make the PermissionSet iterable
        :return:
        """
        c = 0
        i = len(self.__permissions)

        while c < i:
          yield self.__permissions[c]
          c+=1
