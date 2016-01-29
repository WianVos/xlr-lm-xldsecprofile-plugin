#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
import logging
from xml.etree import ElementTree as ET

from xldeploy.decorators import log_with, timer

logger = logging.getLogger(__name__)


class Xml(object):
    @timer(logger)
    @log_with(logger)
    def parse_xml(self, xml):
        output_dict = {}

        root = ET.fromstring(xml)

        output_dict[root.tag] = self.parse_subelement_to_dict(root)

        return output_dict

    # @timer(logger)
    # @log_with(logger)
    def parse_subelement_to_dict(self, element):
        output = {}

        if element.attrib is not {}:
            output.update(element.attrib)
        if element.text is not None:
            if str(element.text).strip() is not '':
                output['@text'] = str(element.text).strip()

        for child in element.iterfind('*'):
            # TODO: this appears to not work properly
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
    def _to_xml_string(self, dict):

        return ET.tostring(self.dict_to_xml(dict))

    # @timer(logger)
    # @log_with(logger)
    def dict_to_xml(self, xml_dict):
        element = None
        for k, v in xml_dict.items():

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
                            element.set(k1, v1)
                    elif isinstance(v1, dict):
                        sub_element = self.dict_to_xml({k1: v1})

                        if isinstance(sub_element, basestring):
                            element.text = sub_element
                        else:
                            element.append(sub_element)
                    elif isinstance(v1, list):
                        for se in v1:
                            sub_element = self.dict_to_xml({k1: se})
                            element.append(sub_element)

        logger.debug("parsed %s into %s" % (xml_dict, ET.tostring(element).strip()))

        return element


class Inspection(Xml):
    def __init__(self, xml=None):
        # parse the xml
        self.__xml = xml

        self.__dict = self.parse_xml(self.__xml)

        self.__inspectables = self.instanciate_inspectables()

    def __str__(self):
        return str(dict)

    def to_xml(self):
        self.update_dict()
        return self._to_xml_string(self.__dict)

    def to_dict(self):
        self.update_dict()
        print self.__dict

    def instanciate_inspectables(self):
        inspectables = self.__dict['inspection']['inspectable']
        inspectables_obj = []
        if isinstance(inspectables, list):
            for i in inspectables:
                inspectables_obj.append(Inspectable(i))

        else:
            inspectables_obj.append(Inspectable(inspectables))

        return inspectables_obj

    def update_dict(self):
        inspectables = []
        for i in self.__inspectables:
            inspectables.append(i.to_dict())
            print inspectables

        self.__dict['inspection']['inspectable'] = inspectables

    def inspectables(self):
        return self.__inspectables


class Inspectable(Xml):
    def __init__(self, dict):
        self.__type = dict.keys()[0]

        for k, v in dict[self.__type].items():
            setattr(self, k, v)

    def to_dict(self):
        d = vars(self)
        type = d.pop('_Inspectable__type')

        return {type: d}
