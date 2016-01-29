#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
import logging
from os import path
import urllib2, urllib, base64
from xml.etree import ElementTree as ET

import xldeploy
import xldeploy.exceptions

from xldeploy.decorators import log_with, timer
from xldeploy.client     import XLDConnection
from xldeploy.repository import VALID_QUERY_PARAMETERS, META_DATA_DICT
from xldeploy.task.task  import Task, TaskList



logger = logging.getLogger(__name__)

class TaskConnection(XLDConnection):

    @timer(logging)
    @log_with(logger)
    def __init__(self, url=None, username=None, password=None, **kwargs):

        super(TaskConnection, self).__init__(url, username, password, **kwargs)
        logger.debug("task service succesfully initialized")

    @timer(logging)
    def get_all_tasks(self):
        """
        returns a TaskList object containing all currently activly tasks in the system
        :return: xldeploy.task.task.TaskList
        """
        logger.info("fetching all currently active tasks")
        try:
            return TaskList(xml = self.http_get('tasks/v2/current/all'))
        except Exception:
            logger.error("unable to fetch all active tasks")
            raise xldeploy.exceptions.XldeployTaskService("unable to fetch all currently active tasks")
        
    @timer(logging)
    def get_all_tasks_export(self, **kwargs):
        """
        searches the system for all tasks and returns them with step info included.
        Date parameters can be ommited
        :begindate: begin date of the query format: yyyy-MM-dd.
        :enddate: end date of the query format: yyyy-MM-dd.
        :return:
        """
        logger.info("fetching all tasks in the system ")
        if kwargs.has_key('startdate'):
            logger.debug("start date: %s") % kwargs['startdate']
        if kwargs.has_key('enddate'):
            logger.debug("end date: %s" % kwargs['enddate'])
        try:
            return TaskList(self.http_get_query('tasks/v2/export', kwargs))
            return output
        except Exception:
            logger.debug("unable to export tasks")
            raise xldeploy.exceptions.XldeployTaskService("unable to export tasks")



    @timer(logging)
    def get_task_by_id(self,id):
        """
        get a single task by id
        :param id: xldeploy task id
        :return: Task object
        """
        logger.info("fetching task %s" % id)
        try:
            return Task(self.http_get("tasks/v2/%s" % id))
        except Exception:
            logger.debug("unable to fetch task: %s" % id)
            raise xldeploy.exceptions.XldeployTaskService("unable to fetch task by id")



    @timer(logging)
    def start_task(self, task):
        """
        start a task in xld
        :param task: task
        :return:
        """

        return self.start_task_by_id(task.id)


    @timer(logging)
    def start_task_by_id(self, id):
        """
        start a task in xld by id
        :param id: task id
        :return:
        """
        # try:
        #     self.http_post('task/v2/%s' % id)
        #     return True
        # except Exception:
        #     return False


        logger.info("starting task %s" % id)
        try:
            self.http_post('tasks/v2/%s/start' % id)
            return True
        except Exception:
            logger.debug("unable to start task: %s" % id )
            raise xldeploy.exceptions.XldeployTaskService("unable to start task")
        
    @timer(logging)
    def stop_task(self, task):
        """
        stop a task in xld
        :param task: task
        :return: bool
        """
        return self.stop_task_by_id(task.id)

    @timer(logging)
    def stop_task_by_id(self, id):
        """
        stop a task in xld by id
        :param id: task id
        :return: bool
        """
        logger.info("stoping task %s" % id)
        try:
            self.http_post('tasks/v2/%s/stop' % id)
            return True
        except Exception:
            logger.debug("unable to stop task: %s" % id )
            raise xldeploy.exceptions.XldeployTaskService("unable to stop task")

    @timer(logging)
    def abort_task(self, task):
        """
        abort a task in xld
        :param task: task
        :return: bool
        """
        return self.abort_task_by_id(task.id)

    @timer(logging)
    def abort_task_by_id(self, id):
        """
        abort a task in xld by id
        :param id: task id
        :return: bool
        """
        logger.info("aborting task %s" % id)
        try:
            self.http_post('tasks/v2/%s/abort' % id)
            return True
        except Exception:
            logger.debug("unable to abort task: %s" % id )
            raise xldeploy.exceptions.XldeployTaskService("unable to abort task")

    @timer(logging)
    def abort_task(self, task):
        """
        cancela task in xld
        :param task: task
        :return: bool
        """
        return self.abort_task_by_id(task.id)

    @timer(logging)
    def abort_task_by_id(self, id):
        """
        cancela task in xld by id
        :param id: task id
        :return: bool
        """
        logger.info("aborting task %s" % id)
        try:
            self.http_delete('tasks/v2/%s' % id)
            return True
        except Exception:
            logger.debug("unable to canceltask: %s" % id )
            raise xldeploy.exceptions.XldeployTaskService("unable to canceltask")

#TODO     GET	/tasks/v2/current	Returns the active tasks of the logged in user.
#GET	/tasks/v2/current/all	Returns all active tasks for all users. : DONE
# GET	/tasks/v2/export	Searches for tasks with detailed step information. DOING
#TODO GET	/tasks/v2/query	Searches for tasks without step information.
# GET	/tasks/v2/{taskid}	Returns a task by ID.
# DELETE	/tasks/v2/{taskid}	Cancels a stopped task.
# POST	/tasks/v2/{taskid}/abort	Aborts an active task.
#TODO POST	/tasks/v2/{taskid}/add-pause/{stepPath}	Add a pause step at the specified position.
#TODO POST	/tasks/v2/{taskid}/archive	Archive an executed task.
#TODO POST	/tasks/v2/{taskid}/assign/{owner}	Assigns a task to a different user.
#TODO GET	/tasks/v2/{taskid}/block/{blockPath}	Returns a block by ID.
#TODO GET	/tasks/v2/{taskid}/block/{blockPath}/step	Returns a block with steps by ID.
#TODO POST	/tasks/v2/{taskid}/schedule	Schedules a task.
#TODO POST	/tasks/v2/{taskid}/skip	Indicates that one or more steps should be skipped.
# POST	/tasks/v2/{taskid}/start	Starts a task.
#TODO GET	/tasks/v2/{taskid}/step/{stepPath}	Retrieves information about a step.
#TODO POST	/tasks/v2/{taskid}/stop	Gracefully stops an active task.
#TODO POST	/tasks/v2/{taskid}/takeover/{owner}	Takeover a task from the owner.
#TODO POST	/tasks/v2/{taskid}/unskip	Indicates that one or more steps should no longer be skipped, but executed.
