#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
import logging
import urllib2
import urllib
import base64
import sys

import xldeploy
from xldeploy.decorators import log_with, timer

logger = logging.getLogger(__name__)

class XLDConnection(object):

    def __init__(self, url = None , username = None, password = None, use_ssl=False, version="5.0.1"):
        """
        Initialize an xldeploy connection object
        :param url: url where the xldeploy instance can be reached. Where assuming the GUI url here.
        :param username: A valid xldeploy username
        :param password: A valid xldeploy password
        :param use_ssl: Are we going to use ssl. Default
        :return:
        """

        if url is None:
            try:
                self.__url = xldeploy.config.get(__name__, 'xld_url')
                logger.debug('url set to %s' % self.__url)
            except Exception:
                logger.warning('url not configured and None passed')
                sys.exit(1)
        else:
            self.__url = url

        
        if username is None:
            try:
                self.__username = xldeploy.config.get(__name__, 'xld_username')
                logger.debug('username set to %s' % self.__username)
            except Exception:
                logger.warning('username not configured and None passed')
                sys.exit(1)
        else:
            self.__username = username

        if password is None:
            try:
                self.__password = xldeploy.config.get(__name__, 'xld_password')
                logger.debug('password set to ******')
            except Exception:
                logger.warning('password not configured and None passed')
                sys.exit(1)
        else:
            self.__password = password

            
       

        self.__use_ssl = use_ssl
        self.__version = version

    @log_with(logger)
    def http_get(self, path):
        """
        fire a http get request at the xlds
        :param path: relative path in the rest interface
        :return: returns a response object
        """
        request = self.prepare_request(path)
        return self.execute_request(request)

    @log_with(logger)
    def http_get_query(self, path, query_data):
        path = "%s?%s" % (path, urllib.urlencode(query_data))
        return self.http_get(path)

    @log_with(logger)
    def http_post(self, path, post_data = None):
        """
        do a http post request to the xld server
        :param:
        :post_data:
        :return:
        """
        request = self.prepare_request(path, post_data)
        request.get_method = lambda: 'POST'
        return self.execute_request(request)

    @log_with(logger)
    def http_post_query(self, path, query_data, data=None):
        """
        post request with query
        :param path:
        :param query_data:
        :param data:
        :return:
        """
        path = "%s?%s" % (path, urllib.urlencode(query_data))
        request = self.prepare_request(path, data)
        request.get_method = lambda: 'POST'
        return self.execute_request(request)

    @log_with(logger)
    def http_put(self, path, put_data = None):
        """
        do a put request carrying data to the xlds
        :param put_data: data to be put
        :return: response string
        """
        request = self.prepare_request(path, put_data)
        request.get_method = lambda: 'PUT'
        return self.execute_request(request)

    @log_with(logger)
    def http_delete(self, path):
        """
        http delete request towards the xlds
        :param path:
        :return:
        """
        request = self.prepare_request(path)
        request.get_method = lambda: 'DELETE'
        return self.execute_request(request)

    @log_with(logger)
    def prepare_request(self, path, data=None):
        """
        prepares requests before they get executed
        :param path: path within the rest interface
        :param data: data in case where dealing with a put or post request
        :return: request object
        """
        new_url = ("%s/deployit/%s" % (self.__url, path))
        url = new_url.replace('#', '%23')
        if data is None:
            request = urllib2.Request(url)
        else:
            request = urllib2.Request(url, data=data)
        request.add_header('Content-Type', 'application/xml')

        base64string = base64.encodestring('%s:%s' % (self.__username, self.__password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)

        return request

    @timer(logger)
    @log_with(logger)
    def execute_request(self, request):
        """

        :param request: urllib2 request object
        :return: response body as string
        """

        #try:
        logger.info('executing request: %s' % (request.get_full_url()))
        response = urllib2.urlopen(request).read()
        #except urllib2.HTTPError as e:
        #    logger.info('error Http request %s returned %s: %s' % (request.get_full_url(), e.code, e.message))
        return response

