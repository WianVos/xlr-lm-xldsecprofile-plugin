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
from xldeploy.repository import VALID_QUERY_PARAMETERS, META_DATA_DICT
from xldeploy.repository.configuration_item import Ci, CiSet

logger = logging.getLogger(__name__)


class RepoConnection(XLDConnection):
    """
    provides a connection to xldeploy and lets the user interact with the repository
    """

    @log_with(logger)
    def __init__(self, url=None, username=None, password=None, **kwargs):

        super(RepoConnection, self).__init__(url, username, password, **kwargs)
        self.prefetch_metadata()



    @log_with(logger)
    def get_ci_by_name(self, ci_name):
        """
        retrieve a ci from the xld repository
        :param ci_name: String: Full name of the ci (eg. Infrastructure/test_ci
        :return: returns a xldeploy.configuration_type.Ci object
        """
        try:
            logger.debug('retrieving ci: %s' % ci_name)
            c =  Ci(xml=self.http_get("repository/ci/%s" % (ci_name)))
            logger.debug('ci %s retrieved' % ci_name)
            return c
        except:
            logger.debug('unable to retrieve ci: %s ' % ci_name)
            return None

    @log_with(logger)
    def create_ci(self, ci):
        """
        creates a ci in the xldrepository
        :param ci: xldeploy.configuration_type.Ci object
        :return: True or False depending on success
        """
        try:
            logger.info("creating CI: %s" % ci.get_id())
            self.http_post("repository/ci/%s" % (ci.get_id()), ci.to_xml())
            logger.info("creation of CI succesfull")
            return True
        except Exception:
            logger.info("unable to create CI: %s" % (ci.get_id()))
            return False


    @log_with(logger)
    def update_ci(self, ci):
        """
        update the parameters of a ci in the xld repository
        :param ci: xldeploy.configuration_type.Ci object
        :return: Boolean True or False
        """
        try:
            logger.info('updating ci: %s' % ci.get_id())
            self.http_put("repository/ci/%s" % (ci.get_id()), ci.to_xml())
            logger.info('updated ci: %s' % ci.get_id())
            return True
        except:
            logger.info('unable to update ci: %s' % ci.get_id())
            return False

    @timer(logger)
    @log_with(logger)
    def update_cis(self,cis):
        """
        update a set of cis in one go
        :param cis:
        :return:
        """
        cis_xml = cis.to_xml()
        try:
            logger.info('updating a set of cis')
            logger.debug('cis set xml: %s' % (str(cis_xml)))
            self.http_put("repository/cis", cis_xml)
            logger.info('update succesfull')
            return True
        except:
            logger.info('unable to update set of cis')
            return False


    @timer(logger)
    @log_with(logger)
    def create_cis(self,cis):
        """
        create a set of cis
        :param cis:
        :return:
        """
        cis_xml = cis.to_xml()
        try:
            logger.info('creating a set of cis')
            logger.debug('cis set xml: %s' % (str(cis_xml)))
            self.http_post("repository/cis", cis_xml)
            logger.info('creation succesfull')
            return True
        except Exception:
            logger.info('unable to create set of cis')
            return False

    @log_with(logger)
    def get_cis_by_query(self, **kwargs):
        """
        get all cis that match a certain query parameter
        :param kwargs: possible query parameters
                        possible parameters: 'parent', 'ancestor', 'namePattern', 'lastModifiedBefore', 'lastModifiedAfter', 'page' and 'resultsPerPage'
        :return: list of ci objects
        """
        cis = CiSet()

        for k in kwargs.iterkeys():
            if k not in VALID_QUERY_PARAMETERS:
                logger.error('"query parameter: %s not allowed" % k')
                raise IllegalQueryParameter("query parameter: %s not allowed" % k)

        if 'resultsPerPage' not in kwargs.iterkeys():
            kwargs['resultsPerPage'] = '-1'

        try:
            logger.debug('trying to retrieve a set of cis')
            root = ET.fromstring(self.http_get_query('repository/query', kwargs))
            logger.debug('retrieval succesfull')
        except Exception:
            logger.error('to retrieve cis')
            return False


        for elem in root.findall('ci'):
            logger.debug('appending; %s' % elem.attrib['ref'])
            ci = (self.get_ci_by_name(elem.attrib['ref']))
            cis.add_ci(ci)

        return cis

    @log_with(logger)
    def prefetch_metadata(self):  
        """
        loads all metadata in one go and stores it in the global META_DATA_DICT
        """
        metadata = self.http_get("metadata/type")
        xml_tree = ET.fromstring(metadata)
        for xml in xml_tree.getchildren():
            META_DATA_DICT[str(xml.attrib['type'])] = self.parse_metadata_type_xml(xml)
            logger.info('metadata for type %s found' % xml.attrib['type'])


    @log_with(logger)
    def parse_metadata_type_xml(self, xml):
        """
        xml to python dict parser for the metadata of one specific type
        :param xml: xml for a single type metadata
        :return: dict
        """
        metadata_type_dict = {'descriptor': {}, 'description': '', 'properties': {}, 'control_tasks': {}, 'interfaces': {},
                  'supertypes': {}}

        if isinstance(xml, str):
            root = ET.fromstring(xml)
        else:
            root = xml

        metadata_type_dict['descriptor'] = root.attrib
        for child in root.getchildren():
            if child.tag == "description":
                metadata_type_dict['description'] = child.text
            if child.tag == "property-descriptors":
                for sub_child in child.getchildren():
                    metadata_type_dict['properties'][sub_child.attrib['name']] = sub_child.attrib
                    for ssc in sub_child.getchildren():
                       metadata_type_dict['properties'][sub_child.attrib['name']].setdefault(ssc.tag, []).append(ssc.text)
        #TODO fix parsing of control-tasks interfaces and supertypes
        #     if child.tag == "control-tasks":
        #         for sub_child in child.getchildren():
        #           metadata_type_dict['control_tasks'].setdefault(sub_child.attrib['name'], {})
        #           metadata_type_dict['control_tasks'][sub_child.attrib['name']].update(sub_child.attrib)
        #           for ssc in sub_child.getchildren():
        #                 metadata_type_dict['control_tasks'][sub_child['name']][ssc.tag] = {}
        #                 print ssc.elements()
        #      if child.tag == "interfaces":
        #      if child.tag == "supertypes":
        #
        return metadata_type_dict


    def save_ci(self, ci):
        """
        save a ci to the database
        :param ci: xldeploy.configuration_item.Ci object
        :return: Boolean True or False depending on success
        """
        ci_id = ci.get_id()
        ci_parent = path.dirname(ci_id)

        logger.debug("attempting to save ci: %s to the repository" % (ci_id))

        # determine if we need to create or update the ci
        # check if the ci exists
        if self.ci_exists(ci_id):
            try:
                logger.info("ci exists, trying to update")
                self.update_ci(ci)
                logger.info('ci updated')
                return True
            except Exception:
                logger.info("unable to update ci: % " % (ci_id))
                return False
        else:

            # check if the parent of the ci exists
            if self.ci_exists(ci_parent):
                logger.info ('%s parent exists' % (ci_parent))
                try:
                  logger.info('attempting to create ci: %s' % (ci_id))
                  self.create_ci(ci)
                  return True
                except Exception:
                   logger.info('unable to create ci: %s' % (ci_id))
                   return False
            else:
                logger.info('trying to create ci parent %s as directory' % ci_parent)
                parent_ci = Ci(id=ci_parent,type='core.Directory' )
                self.save_ci(parent_ci)
                self.create_ci(ci)
                return True

    def save_cis(self,cis):
        """
        :param cis: a ciset object
        :return: true of false
        """
        for ci in cis:
            self.save_ci(ci)

        return True

    @log_with(logger)
    def ci_parent_name(self, name):

        """

        :type name: ci object or string
        """
        ci_parent = None
        #get the parent name depending on input . We're going to treat ci objects different than strings
        if isinstance(name, Ci):
        # get parent name
            ci_parent = path.dirname(name.get_id())
        elif isinstance(name, str):
            ci_parent = path.dirname(name)

        return ci_parent

    @log_with(logger)
    def parent_ci_exists(self, ci):
        '''

        :param ci: ci to check the parent of (could be ci object or straight string)
        :return:
        '''

        #run the parent name through the ci_exists function and return the answer
        return self.ci_exists(self.ci_parent_name(ci))


    @log_with(logger)
    def ci_exists(self, ci):
        """
        check if a ci exists
        :param ci: xldeploy.configuration_item.Ci object or a string
        :return: Boolean True or False depending on success

        """


        if isinstance(ci, str):
           ci_id = ci
        if isinstance(ci, Ci):
           ci_id = ci.get_id()

        response = ET.fromstring(self.http_get("repository/exists/%s" % (ci_id)))
        if 'false' in response.text:
            logger.info("ci: %s does not exist" % ci )
            return False
        else:
            return True