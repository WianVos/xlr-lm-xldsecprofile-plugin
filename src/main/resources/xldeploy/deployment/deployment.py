#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
import re, sys
import xldeploy.exceptions
import logging
import xldeploy.exceptions

from xml.etree import ElementTree as ET
from xldeploy.decorators import log_with, timer
from xldeploy.deployment import APPLICATION_MATCH_REGEX, ENVIRONMENT_MATCH_REGEX, DEPLOYMENT_TYPE_LIST

logger = logging.getLogger(__name__)

class DeploymentSpec():
    """
    the object represents a deployment in xldeploy 
    """
    
    def __init__(self, **kwargs):
        """
        This object represents a xld deployment
        
        :state: state of the deployment
        :package_id:
        :enviromnent_id:
        :xml:
        :return:
        """
        
        try:
            self.__package_id = kwargs['package_id']
        except KeyError:
            self.__package_id = None

        try:
            self.__environment_id = kwargs['environment_id']
        except KeyError:
            self.__environment_id = None
            
        try:
            self.__ds_xml = kwargs['ds_xml']
        except KeyError:
            self.__ds_xml = None

        try:
            self.__state = kwargs['state']
        except KeyError:
            self.__state = None
            
        try:
            self.__type = kwargs['type']
        except KeyError:
            self.__type = None

        
        try:
            self.__ds_dict = kwargs['ds_dict']
        except KeyError:
            self.__ds_dict = None
        

        
        if self.__ds_xml is not None:
            self.parse_ds_xml()

    @timer(logger)
    @log_with(logger)
    def parse_ds_xml(self):
        output_dict = {}

        root = ET.fromstring(self.__ds_xml)

        output_dict[root.tag] = self.parse_subelement_to_dict(root)

        self.__ds_dict = output_dict

    # @timer(logger)
    # @log_with(logger)
    def parse_subelement_to_dict(self, element):
        output = {}

        if element.attrib is not {}:
            output.update(element.attrib)
        if element.text is not None:
            if str(element.text).strip() is not '' :
                output['@text'] = str(element.text).strip()

        for child in element.iterfind('*'):
            #TODO: this appears to not work properly
            if output.has_key(child.tag):
                if isinstance(output[child.tag], dict):
                    org_value = output[child.tag]
                    new_value = self.parse_subelement_to_dict(child)
                    output[child.tag] = [org_value, new_value]
                elif isinstance(output[child.tag], list):
                    new_value = self.parse_subelement_to_dict(child)
                    output[child.tag].append(new_value)
            else:
                output[child.tag] = self.parse_subelement_to_dict(child)

        logger.debug("parsed %s into %s" % (ET.tostring(element).strip(), output))

        return output

    # @timer(logger)
    # @log_with(logger)
    def to_xml(self):

        return ET.tostring(self.dict_to_xml(self.deployment_spec_dict))


    # @timer(logger)
    # @log_with(logger)
    def dict_to_xml(self, xml_dict):
        for k,v in xml_dict.items():

            if k == 'value':
                element = ET.Element(k)
                element.text = v['@text']
                return element

            if k == '@text':
                return v
            element = ET.Element(k)

            if isinstance(v, dict):
                for k1, v1 in v.items():

                    if isinstance(v1, str):
                        if k1 == '@text':
                            element.text = v1
                        else:
                            element.set(k1,v1)
                    elif isinstance(v1, dict):
                        sub_element = self.dict_to_xml({k1:v1})

                        if isinstance(sub_element, basestring):
                            element.text = sub_element
                        else:
                            element.append(sub_element)
                    elif isinstance(v1, list):
                        for se in v1:
                            sub_element = self.dict_to_xml({k1:se})
                            element.append(sub_element)

        logger.debug("parsed %s into %s" % (xml_dict, ET.tostring(element).strip()))

        return element


    def get_validation_messages(self):
        """
        extract the validation messages from the deployment spec dictionary
        :return:
        """
        messages = {}
        for t, v in self.__ds_dict['deployment']['deployeds'].items():
            if isinstance(v, list):
                for item in v :
                    for x in list(self.gen_dict_extract('validation-message', item)):
                        messages.setdefault(t,[]).append(x)
            else:
                messages.setdefault(t,[]).append(dict(self.gen_dict_extract('validation-message', v)))

        return messages




    def gen_dict_extract(self, key, var):
        """
        does a really fast recursive search over a large dictionary for a certain key
        :param key: key to search for
        :param var: dict to search
        :return: generator object
        """
        if hasattr(var,'iteritems'):
            for k, v in var.iteritems():
                if k == key:
                    yield v
                if isinstance(v, dict):
                    for result in self.gen_dict_extract(key, v):
                        yield result
                elif isinstance(v, list):
                    for d in v:
                        for result in self.gen_dict_extract(key, d):
                            yield result

    def update_xml(self, xml):
        self.__ds_xml = xml
        self.parse_ds_xml()

    # service methods
    def to_dict(self):
        return self.deployment_spec_dict

    #getters and setters
    @property
    def package_id(self):
        return self.__package_id

    @package_id.setter
    def package_id(self, id):
       if re.match(APPLICATION_MATCH_REGEX, id):
           self.__package_id = id
       else:
            raise xldeploy.exceptions.XldeployNameError
            sys.exit(1)

    @property
    def environment_id(self):
        return self.__environment_id

    @environment_id.setter
    def environment_id(self, id):
       if re.match(ENVIRONMENT_MATCH_REGEX, id):
           self.__environment_id = id
       else:
            raise xldeploy.exceptions.XldeployNameError
            sys.exit(1)

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, dtype):
       if dtype not in ['initial', 'update', 'rolback']:
           self.__type = dtype
       else:
            raise xldeploy.exceptions.XldeployNameError
            sys.exit(1)

    @property
    def deployment_spec_xml(self):
        return self.__ds_xml

    # TODO: might be removable
    # @deployment_spec_xml.setter
    # def deployment_spec_xml(self, ddeployment_spec_xml):
    #     self.__ds_xml = ddeployment_spec_xml
    #     self.parse_ds_xml()


    @property
    def deployment_spec_dict(self):
        if self.__ds_dict is None:
            if self.__ds_xml is not None:
                self.parse_ds_xml()

        return self.__ds_dict

    @deployment_spec_dict.setter
    def deployment_spec_dict(self, ddeployment_spec_dict):
           self.__ds_dict = ddeployment_spec_dict


   

class DeploymentPlan():

    def __init__(self, **kwargs):
        """
        this object represents a deployment plan preview.
        :param xml: xml used to initialize the object
        :return:
        """
        try:
            self.__xml = kwargs['xml']
        except KeyError:
            raise xldeploy.exceptions.XldeployDeploymentPlanIllegalInvocation('no xml input secified')

        self.__dict = self.parse_xml_to_dict(self.__xml)




    @timer(logger)
    @log_with(logger)
    def parse_xml_to_dict(self, xml):
        output_dict = {}

        root = ET.fromstring(xml)

        output_dict[root.tag] = self.parse_subelement_to_dict(root)

        return output_dict

    @timer(logger)
    @log_with(logger)
    def parse_subelement_to_dict(self, element):
        output = {}

        if element.attrib is not {}:
            output.update(element.attrib)
        if element.text is not None:
            if str(element.text).strip() is not '' :
                output['@text'] = str(element.text).strip()

        for child in element.iterfind('*'):
            if output.has_key(child.tag):
                if isinstance(output[child.tag], dict):
                    org_value = output[child.tag]
                    new_value = self.parse_subelement_to_dict(child)
                    print new_value
                    output[child.tag] = [org_value, new_value]
                elif isinstance(output[child.tag], list):
                    new_value = self.parse_subelement_to_dict(child)
                    output[child.tag].append(new_value)
            else:
                output[child.tag] = self.parse_subelement_to_dict(child)

        logger.debug("parsed %s into %s" % (ET.tostring(element).strip(), output))

        return output



    @property
    def preview_dict(self):
        return self.__dict

