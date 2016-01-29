from xml.etree import ElementTree as ET
import logging

from xldeploy.repository import META_DATA_DICT
from xldeploy.decorators import log_with, timer

logger = logging.getLogger(__name__)

class Ci(object):
    def __init__(self, **kwargs):

        if kwargs.has_key('xml'):

            self.__xml = kwargs['xml']
            self.__type = self.xml_root().tag
            try:
                self.__metadata = META_DATA_DICT[self.__type]
                logger.info('Imported metadata for ci: %s' % self.__type)
            except:
                if kwargs.has_key('meta_data'):
                    self.__metadata = kwargs['meta_data'][self.__type]
                else:
                    logger.error('Could not find Metadata for type: %s' % self.__type)
                    raise Exception('Metadata not Found')

            self.__properties = self.properties_to_dict(self.xml_root())
            self.__attributes = self.attributes_to_dict(self.xml_root())
            self.__id = self.__attributes['id']


        else:
            self.__xml = None
            try:
                self.__type = kwargs['type']
            except KeyError:
                self._type = None

            try:
                self.__properties = kwargs['properties']
            except KeyError:
                self.__properties = {}
            try:
                self.__attributes = kwargs['attributes']
            except KeyError:
                self.__attributes = {}
            try:
                self.__id = kwargs['id']
            except KeyError:
                self.__id = None

                # trying to work around the metadata lookup
                # u can pass in metadata wich wil circumvent the lookup through the repository connection
            try:
                self.__metadata = META_DATA_DICT[self.__type]
                logger.info('Imported metadata for ci: %s' % self.__type)
            except:
                if kwargs.has_key('meta_data'):
                    self.__metadata = kwargs['meta_data'][self.__type]
                else:
                    logger.error('Could not find Metadata for type: %s' % self.__type)
                    raise Exception('Metadata not Found')

    def __str__(self):
        """
        :return: String representation of the object
        """
        return "%s: type: %r, properties: %r, attributes: %r)" % (
        self.__id, self.__type, self.__properties, self.__attributes)

    @log_with(logger)
    def xml_root(self):
        if isinstance(self.__xml, str):
            return ET.fromstring(self.__xml)
        else:
            return self.__xml

    @log_with(logger)
    def to_dict(self):
        dict = self.properties_to_dict(self.xml_root())
        return dict

    @log_with(logger)
    def attributes_to_dict(self, t):
        result = dict()

        for k, v in t.attrib.iteritems():
            result[k] = v

        return result

    @log_with(logger)
    def validate_properties(self):
        req_properties = self.get_mandatory_properties()
        actual_properties = self.__properties.keys()
        missing_properties = []

        for rp in req_properties:
            if rp not in actual_properties:
                missing_properties.append(rp)

        if missing_properties:
            return missing_properties
        else:
            return True

    @log_with(logger)
    def get_mandatory_properties(self):
        req_properties = []
        for p, v in self.__metadata['properties'].items():
            if v['required'] == 'true':
                if 'hidden' in v.keys():
                    if v['hidden'] is 'false':
                        req_properties.append(p)
                else:
                    req_properties.append(p)

        return req_properties

    @timer(logger)
    @log_with(logger)
    def properties_to_dict(self, tree):
        """
        parse the xml properties for the ci to a dictonary for further use
        :param tree: xml.etree tree object
        :return: a dict object which holds all properties for the ci
        """
        result = dict()
        for x in tree.getchildren():
            property_type = self.property_type_dict()[x.tag]

            if property_type == 'MAP_STRING_STRING':
                for e in x.getchildren():
                    result.setdefault(x.tag, {})
                    result[x.tag][e.attrib['key']] = e.text
            elif property_type == 'SET_OF_CI':
                for e in x.getchildren():
                    result.setdefault(x.tag, []).append(e.attrib['ref'])
            elif property_type == 'SET_OF_STRING':
                for e in x.getchildren():
                    result.setdefault(x.tag, []).append(e.text)
            elif property_type == "CI":

                result[x.tag] = x.attrib['ref']
            else:
                result[x.tag] = x.text
        return result

    @timer(logger)
    @log_with(logger)
    def create_xml(self):
        """
        create a xldeploy valid xml string
        :return: xml
        """

        xml = ET.Element(self.__type, {'id': self.__id})

        for k, v in self.__properties.iteritems():
            xml.append(self.create_xml_subelements(k, v))

        return xml

    @timer(logger)
    @log_with(logger)
    def create_xml_subelements(self, tag, value):
        """
        create a sub-element for the create_xml function
        :param tag: the tag for the sub-element
        :param value: the value for the sub-element
        :return: xml.etree.element object
        """
        xml = ET.Element(tag)
        property_type = self.property_type_dict()[tag]
        if value is None:
            pass
        elif property_type == 'MAP_STRING_STRING':
            for k, v in value.iteritems():
                loop_element = ET.Element('entry', attrib={'key': k})
                loop_element.text = v
                xml.append(loop_element)
        elif property_type == 'SET_OF_CI':
            for v in value:
                xml.append(ET.Element('ci', {'ref': v}))
        elif property_type == 'SET_OF_STRING':
            for v in value:
                le = ET.Element('value')
                le.text = v
                xml.append(le)
        elif property_type == 'CI':
            xml.attrib['ref']= value
        else:
            xml.text = value
        return xml

    @log_with(logger)
    def get_type(self):
        return self.__type

    @log_with(logger)
    def get_properties(self):
        return self.__properties

    @log_with(logger)
    def set_properties(self, **kwargs):
        for k, v in kwargs:
            self.__properties[k] = v

    @log_with(logger)
    def get_attributes(self):
        return self.__attributes

    @log_with(logger)
    def set_attributes(self, **kwargs):
        for k, v in kwargs:
            self.__attributes[k] = v

    @log_with(logger)
    def to_xml(self):
        """
        translates the ci to xml
        :return: String containing xml
        """
        if self.__xml is None:
            self.__xml = self.create_xml()

        return ET.tostring(self.__xml)

    @log_with(logger)
    def xml_update(self):
        self.__xml = self.create_xml()

    @log_with(logger)
    def get_id(self):
        """
        get the id of the ci
        :return: id as string
        """
        return self.__id

    @log_with(logger)
    def update_ci_properties(self, **kwargs):
        for k, v in kwargs.items():
            if self.property_valid(k) is False:
                logger.info("property %s is invalid for %s" % (k,self.__type ))

        self.__properties.update(kwargs)
        self.xml_update()

    @log_with(logger)
    def valid_properties(self):
        return self.__metadata['properties'].keys()


    def property_type_dict(self):
        output = {}
        for p in self.valid_properties():
            output[p] = self.get_property_attrib(p)
        return output


    def get_property_attrib(self, property, attrib = 'kind'):
        return self.__metadata['properties'][property][attrib]

    def property_valid(self, property_name):
        if property_name in self.property_type_dict().keys():
            return True
        else:
            return False

    @log_with(logger)
    def update_id(self, id):
        old_id = self.__id
        self.__id = id
        logger.info("updated id for %s to %s" % (old_id, id))
        return True

class CiSet(object):
    """
    Object to hold a set of cis for further use . can be saved to xld at once ..
    """
    # warning: this changed

    def __init__(self, cis=None, xml=None):
        if cis is None:
            self.__cis = []
        if xml is not None:
            self.__cis = self.parse_xml_list_to_cis(xml)

    @log_with(logger)
    def add_ci(self, ci):
        self.__cis.append(ci)

    @log_with(logger)
    def create_xml(self):
        """
        creates a xml list element containing all the cis in the set
        :return: xml
        """
        xml = ET.Element('list')
        for ci in self.__cis:
            xml.append(ci.create_xml())
        return xml

    @log_with(logger)
    def to_xml(self):
        """
        generates an xml list element containing the cis in this set
        :return: xml list as string
        """
        xml = self.create_xml()
        return ET.tostring(xml)

    @log_with(logger)
    def parse_xml_list_to_cis(self, xml):
        """
        parse an xml list from xldeploy into a set of cis
        :param xml: xml as string
        :return: list containing cis
        """
        cis = []
        cis_xml = ET.fromstring(xml)
        for ci_xml in  cis_xml.findall('ci'):
            ci = Ci(xml = ci_xml)
            cis.append(ci)

        return cis


    def __iter__(self): # Python 3: def __next__(self)
        """
        this method provides a generator to make the CiSet iterable
        :return:
        """
        c = 0
        i = len(self.__cis)

        while c < i:
          yield self.__cis[c]
          c+=1


    def __str__(self):
        output = ""
        for ci in self.__cis:
            output += "%s \n" % (str(ci))
        return output

