#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
import ConfigParser
import logging
import logging.config
import os


__version__ = '0.0.1'
Version = __version__  # for backwards compatibility

# get config files .. home dir takes presedence over /etc
XlDeployConfigLocations = ['/etc/.xld_config.ini','~/.xld_config.ini']

# initialize the config parser
config = ConfigParser.SafeConfigParser()
for file in XlDeployConfigLocations:
  if os.path.exists(os.path.expanduser(file)):
      config.read(os.path.expanduser(file))

# now that the config is set up , let's focus on logging
XlDLoggingConfig = {
    'version': 1,
    'disable_existing_loggers': False,  # this fixes the problem

    'formatters': {
        'simple': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        "info_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "filename": "info.log",
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        },
        "default_stream_handler": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        }
    },
    'loggers': {
        '': {
            'handlers': ['info_file_handler','default_stream_handler'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}

# configuring logging

logging.config.dictConfig(XlDLoggingConfig)


def connect_repository(url = None, username = None, password = None, **kwargs):
    """
    connect to the repository service of xld
    :param url: String: url where the xldeploy instance can be reached
    :param username: String: username to use when contacting xldeploy
    :param password: String: password to use when contaction the xldeploy instance
    :return: xldeploy.client object
    """
    from xldeploy.repository.connection import RepoConnection
    return RepoConnection(url, username, password)

def connect_deployment(url = None, username = None, password = None, **kwargs):
    """
    connect to the deployment service of xld
    :param url: String: url where the xldeploy instance can be reached
    :param username: String: username to use when contacting xldeploy
    :param password: String: password to use when contaction the xldeploy instance
    :return: xldeploy.client object
    """
    from xldeploy.deployment.connection import DeploymentConnection
    return DeploymentConnection(url, username, password)


def connect_task(url = None, username = None, password = None, **kwargs):
    """
    connect to the task service of xld
    :param url: String: url where the xldeploy instance can be reached
    :param username: String: username to use when contacting xldeploy
    :param password: String: password to use when contaction the xldeploy instance
    :return: xldeploy.client object
    """
    from xldeploy.task.connection import TaskConnection
    return TaskConnection(url, username, password)


def connect_inspection(url=None, username=None, password=None, **kwargs):
    """
    connect to the deployment service of xld
    :param url: String: url where the xldeploy instance can be reached
    :param username: String: username to use when contacting xldeploy
    :param password: String: password to use when contaction the xldeploy instance
    :return: xldeploy.client object
    """
    from xldeploy.inspection.connection import InspectionConnection
    return InspectionConnection(url, username, password)


def connect_role(url=None, username=None, password=None, **kwargs):
    """
    connect to the deployment service of xld
    :param url: String: url where the xldeploy instance can be reached
    :param username: String: username to use when contacting xldeploy
    :param password: String: password to use when contaction the xldeploy instance
    :return: xldeploy.client object
    """
    from xldeploy.role.connection import RoleConnection
    return RoleConnection(url, username, password)

def connect_security(url=None, username=None, password=None, **kwargs):
    """
    connect to the deployment service of xld
    :param url: String: url where the xldeploy instance can be reached
    :param username: String: username to use when contacting xldeploy
    :param password: String: password to use when contaction the xldeploy instance
    :return: xldeploy.client object
    """
    from xldeploy.security.connection import SecurityConnection
    return SecurityConnection(url, username, password)
# TODO make logging configurable from the config file


