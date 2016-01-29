#!/usr/bin/env python

import xldeploy
import com.xhaus.jyson.JysonCodec as json
from xldeploy.repository.configuration_item import Ci, CiSet
from xldeploy.security.role import Permission, PermissionSet
from urlparse import urlparse

# data = {'cis': {'core.Directory' :['Applications/<project>/<sub_project>',
#                                   'Environments/<project>/<sub_project>',
#                                   'Environments/<project>/<sub_project>/dictionaries',
#                                   'Infrastructure/<project>' ]},
#         'roles': {'<project>_test_role1' : {'Applications/<project>/<sub_project>' : ['controltask#execute'],
#                                             'Environments/<project>/<sub_project>': ['repo#edit']},
#                   '<project>_test_role2' : {'global': ['discovery']}
#                                     }
#         }
#
# dictionary = {}

#setup xld connection
#repo = xldeploy.connect_repository(url = "http://localhost:4516", username="admin", password="admin1")
#security= xldeploy.connect_security(url = "http://localhost:4516", username="admin", password="admin1")


#functions

def connect(username, password, hostname, port):
    global repo
    global security
    repo = xldeploy.connect_repository(url = "http://%s:%s" % (hostname, port), username=username, password=password)
    security = xldeploy.connect_security(url = "http://%s:%s" % (hostname, port), username=username, password=password)

def byteify(input):
    if isinstance(input, dict):
        return {byteify(key):byteify(value) for key,value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def load_data_from_variable(value):
    print "template input: %s " % value

    return byteify(json.loads(str(value)))


def handle_directory_data(data, project_name, sub_projects):

    ciset = CiSet()

    for type, ids in data.items():
        for id in ids:
           for i in get_id_list(id, project_name, sub_projects):
                    ci = create_ci(i, type)
                    ciset.add_ci(ci)
    repo.save_cis(ciset)

def get_id_list(id, project_name, sub_projects):

    lst = []
    print project_name

    for sub_project in sub_projects:
        new_id = ""
        new_id = id.replace('<project>', project_name)
        new_id = new_id.replace('<sub_project>', sub_project)
        lst.append(new_id)
    return lst

def get_id_dict_list(id, dictionary):

    single = []
    multi = []
    lst = []
    flst = []

    for key, value in dictionary.items():
        if len(value) > 1:
            multi.append(key)
        else:
            single.append(key)

    for k in single:
        if id.find('<%s>' % k ):
            value = dictionary[k][0]
            lst.append(id.replace("<%s>" % (k), value))

    for k in multi:
        if id.find('<%s>' % k ):
            for v in dictionary[k]:
                for i in lst:
                    flst.append(i.replace("<%s>" % k, v))

    return flst

def handle_role_data(data, project_name, sub_projects):

    permission_set = PermissionSet()

    for name_str, permissions in data.items():
        name_lst = get_id_list(name_str, project_name, sub_projects)
        for name in name_lst:
            security.create_role(name)
            permission_set = PermissionSet()
            for ids, grants in permissions.items():

                  ids_list = get_id_list(ids, project_name, sub_projects)
                  for id in ids_list:
                      permission = Permission(id = id, granted = grants)
                      permission_set.add_permission(permission)

            security.save_permission_set(name, permission_set)



def create_ci(id, type):

    return Ci(id = id, type = type)


def handle_template(data, project_name, sub_projects):
    if data.has_key('cis'):
        handle_directory_data(data['cis'], project_name, sub_projects)
    if data.has_key('roles'):
        handle_role_data(data['roles'], project_name, sub_projects)

def input_data_to_hash(inputData):
    output = {}
    fields = inputData.split(':')
    for field in fields:
        key, values = field.split('=')
        value_list = values.split(',')
        output[key] = value_list

    return output



# parse the nessacery input
p = urlparse(XlDeployServer['url'])
xld_username = XlDeployServer['username']
xld_password = XlDeployServer['password']
xld_hostname = p.hostname
xld_port = p.port

#setup the needed xld connection objects
connect(xld_username, xld_password, xld_hostname, xld_port)

# parse the input field
input_dict = input_data_to_hash(str(inputData))

# check if we have the correct fields (for now only portfolio and projects allowed
if input_dict.has_key('portfolio') == False:
    print "input does not specify the portfolio key, this is unacceptable"
if input_dict.has_key('projects') == False:
    print "input does not specify the projects key, this is unacceptable"

#load the template data
data = load_data_from_variable(template['templateJson'])
# handle the template based on input
handle_template(data,input_dict['portfolio'][0], input_dict['projects'])
