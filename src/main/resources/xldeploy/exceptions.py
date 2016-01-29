#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

class XldeployError(StandardError):
    """
    General Xldeploy error (error accessing Xldeploy)
    """
    def __init__(self, reason, *args):
        super(XldeployError, self).__init__(reason, *args)
        self.reason = reason

    def __repr__(self):
        return 'XldeployError: %s' % self.reason

    def __str__(self):
        return 'XldeployError: %s' % self.reason



class XldeployNameError(XldeployError):
    """
    this error is thrown when a name for a type of ci does not match requirements
    a name should start with Application for an application package, Environment for an xld environment or dictionary
    ,Infrastructure for deployment targets and Configurations for configuration ci's
    """
    pass

class XlDeployDeploymentTypeError(XldeployError):
    """
    """
    pass


class XldeployDeploymentSpecError(XldeployError):
    """
    This error is thrown whe python is unable to retrieve a deployment specifiaction for a certain environment application combination
    """
    pass

class XldeployDeploymentPlanPreview(XldeployError):
    """
    This error is thrown when the api is unable to retrieve a valid deployment plan preview
    """
    pass

class XldeployDeploymentPlanIllegalInvocation(XldeployError):
    """
    This error is thrown when the deployment plan class is invoked without xml input
    """
    pass

class XldeployUnableToValidate(XldeployError):
    """
    this error is thrown when validation of a deployment plan fails
    """
    pass

#TaskService
class XldeployTaskService(XldeployError):
    """
    this error is throw when the task service is unable to complete a request
    """
    pass


class XldeployInspectionService(XldeployError):
    """
    this error is throw when the inspection service is unable to complete a request
    """
    pass
