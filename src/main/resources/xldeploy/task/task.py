from xml.etree import ElementTree as ET

import logging
import xldeploy
from xldeploy.decorators import log_with, timer

logger = logging.getLogger(__name__)


class Task(object):

    def __init__(self, xml):
        self.__task_xml = xml
        self.__task_dict = self.parse_xml()
        self.__id = self.__task_dict['id']
        self.__owner = self.__task_dict['owner']
        self.__state = self.__task_dict['state']
        self.__failures = self.__task_dict['failures']
        self.__execution_plan = self.get_execution_plan()

    def get_execution_plan(self):
        """
        retrieve the execution plan into a sane dict
        :return:
        """

    def parse_xml(self):
        output_dict = {}

        root = ET.fromstring(self.__task_xml)

        output_dict = self.parse_subelement_to_dict(root)
        return output_dict


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

    def to_dict(self):
        return self.__task_dict
    
    @property
    def id(self):
        return self.__id

    @property
    def owner(self):
        return self.__owner

    @property
    def failures(self):
        return self.__failures

    @property
    def state(self):
        return self.__state

    @property
    def execution_plan(self):
        return self.__execution_plan

class TaskList(object):

    def __init__(self, xml = None, tasks = []):
        self.__tasks = tasks
        if xml is not None:
            self.__tasks = self.parse_xml_list_totasks(xml)

    @log_with(logger)
    def add_task(self, task):
        self.__tasks.append(task)

    @log_with(logger)
    def create_xml(self):
        """
        creates a xml list element containing all the tasks in the set
        :return: xml
        """
        xml = ET.Element('list')
        for task in self.__tasks:
            xml.append(task.create_xml())
        return xml

    @log_with(logger)
    def to_xml(self):
        """
        generates an xml list element containing the tasks in this set
        :return: xml list as string
        """
        xml = self.create_xml()
        return ET.tostring(xml)

    @log_with(logger)

    def parse_xml_list_totasks(self, xml):
        """
        parse an xml list from xldeploy into a set of tasks
        :param xml: xml as string
        :return: list containing tasks
        """
        tasks = []
        tasks_xml = ET.fromstring(xml)
        for task_xml in  tasks_xml.findall('task'):
            task = Task(xml = ET.tostring(task_xml))
            tasks.append(task)



        return tasks


    def __iter__(self): # Python 3: def __next__(self)
        """
        this method provides a generator to make the CiSet iterable
        :return:
        """
        c = 0
        i = len(self.__tasks)

        while c < i:
          yield self.__tasks[c]
          c+=1


    def __str__(self):
        output = ""
        for task in self.__tasks:
            output += "%s \n" % (str(task))
        return output


    def __getitem__(self,index):
        return self.__tasks[index]
    
    def __setitem__(self,index,task):
        self.__tasks[index] = task
    
    def __delitem__(self, index):
        del self.__tasks[index]