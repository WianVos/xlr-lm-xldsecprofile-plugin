#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
import logging
from xml.etree import ElementTree as ET

import xldeploy
import xldeploy.exceptions
from xldeploy.decorators import log_with
from xldeploy.client import XLDConnection
from xldeploy.inspection import META_DATA_DICT
from xldeploy.repository.configuration_item import Ci
from xldeploy.inspection.inspection import Inspection

logger = logging.getLogger(__name__)


class InspectionConnection(XLDConnection):
    """
    provides a connection to xldeploy and lets the user interact with the repository
    """

    inspection_basic_fields = ['type', 'host', 'id']

    @log_with(logger)
    def __init__(self, url=None, username=None, password=None, **kwargs):

        super(InspectionConnection, self).__init__(url, username, password, **kwargs)
        self.prefetch_metadata()

    def prepare_inspection(self, **kwargs):

        '''
        prepare's and inspection object
        '''

        # check if we got passed the nessecary fields
        for f in self.inspection_basic_fields:
            if kwargs.has_key(f) is False:
                raise xldeploy.exceptions.XldeployInspectionService(
                    "Inspectionservice failed , Missing parameter %s" % f)



        # see what parameters are mandatory for inspection and see if we can satisfy those

        for k, v in META_DATA_DICT[kwargs['type']]['properties'].items():
            # print k
            # print v['inspection']
            # print v['required']
            if v['requiredInspection'] == 'true':
                if kwargs.has_key(k) is False:
                    raise xldeploy.exceptions.XldeployInspectionService(
                        "Inspectionservice failed , Missing parameter %s" % k)


        # so we got all we need .. let's compose the ci .

        type = kwargs.pop('type')
        id = kwargs.pop('id')

        ci = Ci(type=type, id=id, properties=kwargs, meta_data=META_DATA_DICT)

        response = self.http_post('inspection/prepare', post_data=ci.to_xml())

        return Inspection(xml=response)

    ### utils
    # todo: find a way to not have these duplicate
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

    def parse_metadata_type_xml(self, xml):
        """
        xml to python dict parser for the metadata of one specific type
        :param xml: xml for a single type metadata
        :return: dict
        """
        metadata_type_dict = {'descriptor': {}, 'description': '', 'properties': {}, 'control_tasks': {},
                              'interfaces': {},
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
                        metadata_type_dict['properties'][sub_child.attrib['name']].setdefault(ssc.tag, []).append(
                            ssc.text)
        # TODO fix parsing of control-tasks interfaces and supertypes
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


'''

  <was.DeploymentManager id="Infrastructure/was test/blah">
      <host ref="Infrastructure/was test"/>
      <wasHome>/test</wasHome>
      <port>0</port>
      <updateGlobalPlugin>false</updateGlobalPlugin>
    </was.DeploymentManager>

def run_discovery(discovery_max_wait = '120')
    inspection = rest_post "inspection/prepare/", desired_xml
    task_id = rest_post "inspection/", inspection
    rest_post "task/#{task_id}/start"

    max_wait = discovery_max_wait.to_i
    while max_wait > 0
      state = get_task_state(task_id)
      case state
        when 'EXECUTED'
          break
        when 'STOPPED', 'DONE', 'CANCELLED'
          fail "Discovery of #{id} failed, invalid inspection task #{task_id} state #{state}"
        when 'EXECUTING', 'PENDING', 'QUEUED'
          p "Waiting for discovery to finish, task: #{task_id}, current state: #{state}, wait time left: #{max_wait}"
      end
      max_wait = max_wait - 1
      sleep 1
    end
    if max_wait == 0
      fail "Discovery of #{:id} failed, max wait time #{discovery_max_wait} exceeded"
    end
    rest_post "task/#{task_id}/archive"
    inspection_result = rest_get "inspection/retrieve/#{task_id}"
    if inspection_result != "No resource method found for GET, return 405 with Allow header"
      rest_post "repository/cis", inspection_result
    end
  end
'''
