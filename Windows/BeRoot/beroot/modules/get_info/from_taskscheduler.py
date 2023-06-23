# -*- coding: utf-8 -*-
import ctypes
import os
import platform
# import pythoncom

from xml.etree.cElementTree import ElementTree

from .system_info import System
from ..checks.path_manipulation_checks import get_path_info
from ..objects.taskscheduler import Taskscheduler


class GetTaskschedulers(object):
    def __init__(self):
        self.task_directory = os.path.join(os.environ.get('systemroot'), 'system32\Tasks')
        s = System()

        self.disable_redirection = bool(s.isx64)

    def tasks_list(self):
        tasks = []

        # manage tasks for windows XP
        if platform.release() not in ['XP', '2003']:
            if self.disable_redirection:
                wow64 = ctypes.c_long(0)
                ctypes.windll.kernel32.Wow64DisableWow64FsRedirection(ctypes.byref(wow64))

            if os.path.exists(self.task_directory):
                for root, dirs, files in os.walk(self.task_directory):
                    for f in files:

                        xml_file = os.path.join(root, f)
                        try:
                            tree = ElementTree(file=xml_file)
                        except Exception:
                            continue

                        command = ''
                        arguments = ''
                        userid = ''
                        groupid = ''
                        runlevel = ''

                        xmlroot = tree.getroot()
                        for xml in xmlroot:
                            # get task information (date, author)
                            # in RegistrationInfo tag

                            # get triggers information (launch at boot, etc.)
                            # in Triggers tag

                            # get user information
                            if 'principals' in xml.tag.lower():
                                for child in xml.getchildren():
                                    if 'principal' in child.tag.lower():
                                        for principal in child.getchildren():
                                            if 'userid' in principal.tag.lower():
                                                userid = principal.text
                                            elif 'groupid' in principal.tag.lower():
                                                groupid = principal.text
                                            elif 'runlevel' in principal.tag.lower():
                                                runlevel = principal.text

                            # get all execution information (executable and arguments)
                            if 'actions' in xml.tag.lower():
                                for child in xml.getchildren():
                                    if 'exec' in child.tag.lower():
                                        for execution in child.getchildren():
                                            if 'command' in execution.tag.lower():
                                                if execution.text:
                                                    command = os.path.expandvars(execution.text)
                                            elif 'arguments' in execution.tag.lower():
                                                if execution.text:
                                                    arguments = os.path.expandvars(execution.text)

                        full_path = f'{str(command)} {str(arguments)}'
                        if full_path := full_path.strip():
                            t = Taskscheduler()
                            t.name = f
                            t.full_path = full_path
                            t.paths = get_path_info(t.full_path)

                            t.userid = 'LocalSystem' if userid == 'S-1-5-18' else userid
                            t.groupid = groupid
                            t.runlevel = runlevel

                            # append the tasks to the main tasklist
                            tasks.append(t)

            if self.disable_redirection:
                ctypes.windll.kernel32.Wow64EnableWow64FsRedirection(wow64)

        return tasks
