#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
import logging
from os import path
from xml.etree import ElementTree as ET

import xldeploy
import xldeploy.exceptions
from xldeploy.decorators import log_with, timer
from xldeploy.client     import XLDConnection
from xldeploy.deployment.deployment import DeploymentSpec, DeploymentPlan

logger = logging.getLogger(__name__)


class DeploymentConnection(XLDConnection):

    """
    provides a connection to xldeploy and lets the user interact with the repository
    """
    @timer(logging)
    @log_with(logger)
    def __init__(self, url=None, username=None, password=None, **kwargs):

        super(DeploymentConnection, self).__init__(url, username, password, **kwargs)

    @timer(logging)
    @log_with(logger)
    def get_deployment_spec(self, environment_id, package_id):
        logger.info("retieving deployment specification for %s onto %s" % (package_id, environment_id))

        # does the deployment exist?
        application_id = path.dirname(package_id)
        response = self.http_get_query("deployment/exists",
                                       {'environment': environment_id, 'application': application_id})
        root = ET.fromstring(response)
        answer = root.text()

        if answer == 'false':
            self.get_initial_deployment_spec(environment_id, package_id)
        if answer == 'true':
            # todo figure out what i intended here
            self.get_update()

    @timer(logging)
    @log_with(logger)
    def get_initial_deployment_spec(self,environment_id, package_id):
        logger.debug("retrieving initial deployment spec for %s onto %s" % (package_id, environment_id))
        try:
            deployment_spec = self.http_get("deployment/prepare/initial?environment=%s&version=%s" % (environment_id, package_id))
        except Exception:
            raise xldeploy.exceptions.XldeployDeploymentSpecError("unable to obtain deployment specification")

        deployment = DeploymentSpec(environment_id = environment_id, package_id = package_id , ds_xml = deployment_spec, type = "initial")
        logger.debug("created deployment object")
        return deployment


    @timer(logging)
    @log_with(logger)
    def get_deployment_plan_preview(self,deployment_spec):
        try:
            deployment_plan = self.http_post("deployment/previewblock", deployment_spec.to_xml())
        except Exception:
            raise xldeploy.exceptions.XldeployDeploymentPlanPreview("unable to obtain deployment plan preview")

        logger.debug("succesfully retrieved deployment plan preview")
        deploymentplan = DeploymentPlan(xml = deployment_plan)
        return deploymentplan

    @timer(logging)
    @log_with(logger)
    def get_deployment_mapping(self, deployment_spec):
        try:
            output = self.http_post("deployment/prepare/deployeds", deployment_spec.to_xml())
            deployment_spec.update_xml(output)
        except Exception:
            raise xldeploy.exceptions.XldeployDeploymentSpecError("unable to obtain deployment specification")

        return deployment_spec

    @timer(logging)
    @log_with(logger)
    def validate_deployment_spec(self, deployment_spec):
        """
        validate if a deployment spec can be validated
        :param deployment_spec:
        :return:
        """
        try:
            output = self.http_post("deployment/validate", deployment_spec.to_xml())
            return True
        except Exception:
            raise xldeploy.exceptions.XldeployUnableToValidate("unable to validate deployment")

    @timer(logging)
    @log_with(logger)
    def create_deployment_task(self, deployment_spec):
        """
        create a deployment task if the deployment_spec can be validated
        :param deployment_spec:
        :return:
        """
        if self.validate_deployment_spec(deployment_spec):
            logger.info("deploymentspec validated, moving on to task creation")
            try:
                output = self.http_post("deployment", deployment_spec.to_xml())
                return output
            except Exception:
                raise xldeploy.exceptions.XldeployUnableToValidate("unable to validate deployment")
        else:
            logger.error("unable to validate deployment, task not created")
            return None



#TODO: make generation more specific
#TODO: add posibility of generating single deployments
#TODO: add update deployments



