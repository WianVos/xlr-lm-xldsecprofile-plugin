#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
POSSIBLE_PERMISSIONS = {'global': ['task#takeover',
                                   'task#preview_step',
                                   'report#view',
                                   'controltask#execute',
                                   'admin',
                                   'task#skip_step',
                                   'login',
                                   'task#assign',
                                   'task#move_step',
                                   'security#edit',
                                   'discovery'],
                        'Applications': ['controltask#execute',
                                         'import#initial',
                                         'repo#edit',
                                         'read',
                                         'import#remove',
                                         'import#upgrade'],
                        'Environments': ['controltask#execute',
                                         'import#initial',
                                         'deploy#initial',
                                         'deploy#upgrade',
                                         'deploy#undeploy',
                                         'repo#edit',
                                         'read',
                                         'import#remove',
                                         'import#upgrade',
                                         'task#skip_step',
                                         'task#move_step',
                                         'task#takeover'
                                         ],
                        'Infrastructure': ['controltask#execute',
                                           'repo#edit',
                                           'read', ]}

#
# <map>
#     <entry>
#         <string>global</string>
#         <set>
#             <string>task#takeover</string>
#             <string>task#preview_step</string>
#             <string>report#view</string>
#             <string>controltask#execute</string>
#             <string>admin</string>
#             <string>task#skip_step</string>
#             <string>login</string>
#             <string>task#assign</string>
#             <string>task#move_step</string>
#             <string>security#edit</string>
#             <string>discovery</string>
#         </set>
#     </entry>
#     <entry>
#         <string>Environments/Claims</string>
#         <set>
#             <string>task#takeover</string>
#             <string>controltask#execute</string>
#             <string>deploy#undeploy</string>
#             <string>deploy#initial</string>
#             <string>repo#edit</string>
#             <string>task#skip_step</string>
#             <string>read</string>
#             <string>deploy#upgrade</string>
#             <string>task#move_step</string>
#         </set>
#     </entry>
#     <entry>
#         <string>Infrastructure/Claims</string>
#         <set>
#             <string>controltask#execute</string>
#             <string>repo#edit</string>
#             <string>read</string>
#         </set>
#     </entry>
#     <entry>
#         <string>Applications/Claims/bpm</string>
#         <set>
#             <string>controltask#execute</string>
#             <string>import#initial</string>
#             <string>repo#edit</string>
#             <string>read</string>
#             <string>import#remove</string>
#             <string>import#upgrade</string>
#         </set>
#     </entry>
# </map>