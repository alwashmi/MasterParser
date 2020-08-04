#!/usr/bin/env python

# Copyright (c) 2015, Yahoo Inc.
# Copyrights licensed under the BSD
# See the accompanying LICENSE.txt file for terms.

"""Parser for Windows Scheduled Task files
"""

import struct
from defusedxml import ElementTree
import os
import datetime
import sys
import json

class Error(Exception):
    """Base exception."""


class FormatError(Error):
    """Error while parsing the job format."""


class XMLScheduledTask(object):

    def __init__(self, task_data=None):
        try:
            task_xml = ElementTree.fromstring(task_data, forbid_dtd=True)
        except ElementTree.ParseError:
            raise FormatError("Job file is not XML format")

        task_xml = self._strip_namespace(task_xml)

        # Load RegistrationInfo data
        self.uri = self._get_element_data(task_xml, "RegistrationInfo/URI")
        self.security_descriptor = self._get_element_data(task_xml, "RegistrationInfo/SecurityDescriptor")
        self.source = self._get_element_data(task_xml, "RegistrationInfo/Source")
        self.date = self._get_element_data(task_xml, "RegistrationInfo/Date")
        self.author = self._get_element_data(task_xml, "RegistrationInfo/Author")
        self.version = self._get_element_data(task_xml, "RegistrationInfo/Version")
        self.description = self._get_element_data(task_xml, "RegistrationInfo/Description")
        self.documentation = self._get_element_data(task_xml, "RegistrationInfo/Documentation")

        # Load Principal data
        self.principal_id = task_xml.find("Principals/Principal").get("id")
        self.user_id = self._get_element_data(task_xml, "Principals/Principal/UserId")
        self.logon_type = self._get_element_data(task_xml, "Principals/Principal/LogonType")
        self.group_id = self._get_element_data(task_xml, "Principals/Principal/GroupId")
        self.display_name = self._get_element_data(task_xml, "Principals/Principal/DisplayName")
        self.run_level = self._get_element_data(task_xml, "Principals/Principal/RunLevel")
        self.process_token_sid_type = self._get_element_data(task_xml, "Principals/Principal/ProcessTokenSidType")
        self.required_privileges = self._get_list_element_data(task_xml,
                                                               "Principals/Principal/RequiredPrivileges/Privilege")

        # Load Settings data
        self.allow_start_on_demand = self._get_element_data(task_xml, "AllowStartOnDemand")
        self.disallow_start_on_batteries = self._get_element_data(task_xml, "DisallowStartIfOnBatteries")
        self.stop_on_batteries = self._get_element_data(task_xml, "StopIfGoingOnBatteries")
        self.allow_hard_terminate = self._get_element_data(task_xml, "AllowHardTerminate")
        self.start_when_available = self._get_element_data(task_xml, "StartWhenAvailable")
        self.network_profile_name = self._get_element_data(task_xml, "NetworkProfileName")
        self.run_only_on_network = self._get_element_data(task_xml, "RunOnlyIfNetworkAvailable")
        self.wake_to_run = self._get_element_data(task_xml, "WakeToRun")
        self.enabled = self._get_element_data(task_xml, "Enabled")
        self.hidden = self._get_element_data(task_xml, "Hidden")
        self.delete_expired = self._get_element_data(task_xml, "DeleteExpiredTaskAfter")
        self.execution_time_limit = self._get_element_data(task_xml, "ExecutionTimeLimit")
        self.run_only_idle = self._get_element_data(task_xml, "RunOnlyIfIdle")
        self.unified_scheduling_engine = self._get_element_data(task_xml, "UseUnifiedSchedulingEngine")
        self.disallow_start_on_remote_app_session = self._get_element_data(task_xml, "DisallowStartOnRemoteAppSession")
        self.multiple_instances_policy = self._get_element_data(task_xml, "MultipleInstancesPolicy")
        self.priority = self._get_element_data(task_xml, "Priority")
        self.idle_duration = self._get_element_data(task_xml, "IdleSettings/Duration")
        self.idle_wait_timeout = self._get_element_data(task_xml, "IdleSettings/WaitTimeout")
        self.idle_stop_on_idle_end = self._get_element_data(task_xml, "IdleSettings/StopOnIdleEnd")
        self.idle_restart_on_idle = self._get_element_data(task_xml, "IdleSettings/RestartOnIdle")
        self.network_name = self._get_element_data(task_xml, "NetworkSettings/Name")
        self.network_id = self._get_element_data(task_xml, "NetworkSettings/Id")
        self.restart_on_fail_interval = self._get_element_data(task_xml, "RestartOnFailure/Interval")
        self.restart_on_fail_count = self._get_element_data(task_xml, "RestartOnFailure/Count")

        # Load Data data
        self.data = self._get_raw_xml(task_xml, "Data")

        # Load Triggers data
        self.triggers = self._get_triggers(task_xml)

        # Load Actions data
        self.actions = self._get_actions(task_xml)

    @staticmethod
    def _strip_namespace(data):
        if data.tag.startswith('{'):
            ns_length = data.tag.find('}')
            namespace = data.tag[0:ns_length+1]
        for element in data.getiterator():
            if element.tag.startswith(namespace):
                element.tag = element.tag[len(namespace):]
        return data

    @staticmethod
    def _get_element_data(data, path):
        try:
            return data.find(path).text
        except AttributeError:
            return ""

    @staticmethod
    def _get_list_element_data(data, path):
        values = []
        list_data = data.findall(path)
        if list_data is not None:
            for element in list_data:
                try:
                    values.append(element.text)
                except AttributeError:
                    pass
        return values

    @staticmethod
    def _get_list_tag_data(data, path):
        values = []
        list_data = data.findall(path)
        if list_data is not None:
            for element in list_data:
                values.append(element.tag)
        return values

    def _get_dict_data(self, data, path, fields):
        values = []
        value_list = data.findall(path)
        for value_element in value_list:
            value = {}
            for field in fields:
                value[field] = self._get_element_data(value_element, field)
            values.append(value)
        return values

    @staticmethod
    def _get_raw_xml(data, path):
        xml = data.find(path)
        if xml is not None:
            return ElementTree.tostring(xml, encoding="utf-8")
        else:
            return ""

    def _get_triggers(self, data):
        triggers = []
        trigger_list = data.findall("Triggers/*")
        for trigger_element in trigger_list:
            trigger = {"Type": trigger_element.tag,
                       "Enabled": self._get_element_data(trigger_element, "Enabled"),
                       "StartBoundary": self._get_element_data(trigger_element, "StartBoundary"),
                       "EndBoundary": self._get_element_data(trigger_element, "EndBoundary"),
                       "ExecutionTimeLimit": self._get_element_data(trigger_element, "ExecutionTimeLimit"),
                       "Repetition": self._get_dict_data(trigger_element, "Repetition", ["Interval", "Duration",
                                                                                         "StopAtDurationEnd"])
                       }
            if trigger["Type"] == "BootTrigger":
                trigger["Delay"] = self._get_element_data(trigger_element, "Delay")
            elif trigger["Type"] == "RegistrationTrigger":
                trigger["Delay"] = self._get_element_data(trigger_element, "Delay")
            elif trigger["Type"] == "IdleTrigger":
                pass
            elif trigger["Type"] == "TimeTrigger":
                trigger["RandomDelay"] = self._get_element_data(trigger_element, "RandomDelay")
            elif trigger["Type"] == "EventTrigger":
                trigger["Subscription"] = self._get_element_data(trigger_element, "Subscription")
                trigger["Delay"] = self._get_element_data(trigger_element, "Delay")
                trigger["PeriodOfOccurrence"] = self._get_element_data(trigger_element, "PeriodOfOccurrence")
                trigger["NumberOfOccurrences"] = self._get_element_data(trigger_element, "NumberOfOccurrences")
                trigger["MatchingElement"] = self._get_element_data(trigger_element, "MatchingElement")
                trigger["ValueQueries"] = self._get_list_element_data(trigger_element, "ValueQueries/Value")
            elif trigger["Type"] == "LogonTrigger":
                trigger["UserId"] = self._get_element_data(trigger_element, "UserId")
                trigger["Delay"] = self._get_element_data(trigger_element, "Delay")
            elif trigger["Type"] == "SessionStateChangeTrigger":
                trigger["UserId"] = self._get_element_data(trigger_element, "UserId")
                trigger["Delay"] = self._get_element_data(trigger_element, "Delay")
                trigger["StateChange"] = self._get_element_data(trigger_element, "StateChange")
            elif trigger["Type"] == "CalendarTrigger":
                trigger["RandomDelay"] = self._get_element_data(trigger_element, "RandomDelay")
                if trigger_element.find("ScheduleByDay") is not None:
                    trigger["ScheduleByDay"] = self._get_dict_data(trigger_element, "ScheduleByDay", ["DaysInterval"])
                if trigger_element.find("ScheduleByWeek") is not None:
                    trigger["ScheduleByWeek"] = self._get_schedule_by_week(trigger_element)
                if trigger_element.find("ScheduleByMonth") is not None:
                    trigger["ScheduleByMonth"] = self._get_schedule_by_month(trigger_element)
                if trigger_element.find("ScheduleByMonthDayOfWeek") is not None:
                    trigger["ScheduleByMonthDayOfWeek"] = self._get_schedule_by_month_day_of_week(trigger_element)
            triggers.append(trigger)
        return triggers

    def _get_schedule_by_week(self, data):
        schedule = {"WeeksInterval": self._get_element_data(data, "ScheduleByWeek/WeeksInterval"),
                    "DaysOfWeek": self._get_list_tag_data(data, "ScheduleByWeek/DaysOfWeek/*")
                    }
        return schedule

    def _get_schedule_by_month(self, data):
        schedule = {"DaysOfMonth": self._get_list_element_data(data, "ScheduleByMonth/DaysOfMonth/Day"),
                    "Months": self._get_list_tag_data(data, "ScheduleByMonth/Months/*")
                    }
        return schedule

    def _get_schedule_by_month_day_of_week(self, data):
        schedule = {"Weeks": self._get_list_element_data(data, "ScheduleByMonthDayOfWeek/Weeks/Week"),
                    "DaysOfWeek": self._get_list_tag_data(data, "ScheduleByMonthDayOfWeek/DaysOfWeek/*"),
                    "Months": self._get_list_tag_data(data, "ScheduleByMonthDayOfWeek/Months/*")
                    }
        return schedule

    def _get_actions(self, data):
        actions = []
        action_list = data.findall("Actions/*")
        for action_element in action_list:
            action = {"Type": action_element.tag}
            if action["Type"] == "Exec":
                action["Command"] = self._get_element_data(action_element, "Command")
                action["Arguments"] = self._get_element_data(action_element, "Arguments")
                action["WorkingDirectory"] = self._get_element_data(action_element, "WorkingDirectory")
            elif action["Type"] == "ComHandler":
                action["ClassId"] = self._get_element_data(action_element, "ClassId")
                action["Data"] = self._get_raw_xml(action_element, "Data")
            elif action["Type"] == "SendEmail":
                action["Server"] = self._get_element_data(action_element, "Server")
                action["Subject"] = self._get_element_data(action_element, "Subject")
                action["To"] = self._get_element_data(action_element, "To")
                action["Cc"] = self._get_element_data(action_element, "Cc")
                action["Bcc"] = self._get_element_data(action_element, "Bcc")
                action["ReplyTo"] = self._get_element_data(action_element, "ReplyTo")
                action["From"] = self._get_element_data(action_element, "From")
                action["Body"] = self._get_element_data(action_element, "Body")
                action["Attachments"] = self._get_element_data(action_element, "Attachments/File")
                action["Headers"] = self._get_dict_data(action_element, "Headers/HeaderField", ["Name", "Value"])
            elif action["Type"] == "ShowMessage":
                action["Title"] = self._get_element_data(action_element, "Title")
                action["Body"] = self._get_element_data(action_element, "Body")
            actions.append(action)
        return actions

    def parse(self):
        # Returns a dictionary containing all the fields of a XML task
        task = {
            "task_type": "XML",
            "uri": self.uri,
            "security_descriptor": self.security_descriptor,
            "source": self.source,
            "date": self.date,
            "author": self.author,
            "version": self.version,
            "description": self.description,
            "documentation": self.documentation,
            "principal_id": self.principal_id,
            "user_id": self.user_id,
            "logon_type": self.logon_type,
            "group_id": self.group_id,
            "display_name": self.display_name,
            "run_level": self.run_level,
            "process_token_sid_type": self.process_token_sid_type,
            "required_privileges": self.required_privileges,
            "allow_start_on_demand": self.allow_start_on_demand,
            "disallow_start_on_batteries": self.disallow_start_on_batteries,
            "stop_on_batteries": self.stop_on_batteries,
            "allow_hard_terminate": self.allow_hard_terminate,
            "start_when_available": self.start_when_available,
            "network_profile_name": self.network_profile_name,
            "run_only_on_network": self.run_only_on_network,
            "wake_to_run": self.wake_to_run,
            "enabled": self.enabled,
            "hidden": self.hidden,
            "delete_expired": self.delete_expired,
            "execution_time_limit": self.execution_time_limit,
            "run_only_idle": self.run_only_idle,
            "unified_scheduling_engine": self.unified_scheduling_engine,
            "disallow_start_on_remote_app_session": self.disallow_start_on_remote_app_session,
            "multiple_instances_policy": self.multiple_instances_policy,
            "priority": self.priority,
            "idle_duration": self.idle_duration,
            "idle_wait_timeout": self.idle_wait_timeout,
            "idle_stop_on_idle_end": self.idle_stop_on_idle_end,
            "idle_restart_on_idle": self.idle_restart_on_idle,
            "network_name": self.network_name,
            "network_id": self.network_id,
            "restart_on_fail_interval": self.restart_on_fail_interval,
            "restart_on_fail_count": self.restart_on_fail_count,
            "data": self.data,
            "triggers": self.triggers,
            "actions": self.actions
        }
        return task


class BinaryScheduledTask(object):
    PRODUCT_VERSIONS = {
        0x0400: "Windows NT 4.0",
        0x0500: "Windows 2000",
        0x0501: "Windows XP",
        0x0600: "Windows Vista",
        0x0601: "Windows 7",
        0x0602: "Windows 8",
        0x0603: "Windows 8.1"
    }

    FILE_VERSIONS = {
        0x0001: "Ver. 1"
    }

    PRIORITY = {
        0b100000: "NORMAL_PRIORITY_CLASS",
        0b1000000: "IDLE_PRIORITY_CLASS",
        0b10000000: "HIGH_PRIORITY_CLASS",
        0b100000000: "REALTIME_PRIORITY_CLASS"
    }

    STATUS = {
        0x00041300: "SCHED_S_TASK_READY",
        0x00041301: "SCHED_S_TASK_RUNNING",
        0x00041305: "SCHED_S_TASK_NOT_SCHEDULED"
    }

    TASK_FLAGS = {
        0b1: "TASK_FLAG_INTERACTIVE",
        0b10: "TASK_FLAG_DELETE_WHEN_DONE",
        0b100: "TASK_FLAG_DISABLED",
        0b10000: "TASK_FLAG_START_ONLY_IF_IDLE",
        0b100000: "TASK_FLAG_KILL_ON_IDLE_END",
        0b1000000: "TASK_FLAG_DONT_START_IF_ON_BATTERIES",
        0b10000000: "TASK_FLAG_KILL_IF_GOING_ON_BATTERIES",
        0b100000000: "TASK_FLAG_RUN_ONLY_IF_DOCKED",
        0b1000000000: "TASK_FLAG_HIDDEN",
        0b10000000000: "TASK_FLAG_RUN_IF_CONNECTED_TO_INTERNET",
        0b100000000000: "TASK_FLAG_RESTART_ON_IDLE_RESUME",
        0b1000000000000: "TASK_FLAG_SYSTEM_REQUIRED",
        0b10000000000000: "TASK_FLAG_RUN_ONLY_IF_LOGGED_ON",
        0b1000000000000000000000000: "TASK_APPLICATION_NAME"
    }

    EXITCODE = {
        0x0: "S_OK",
        0x1: "S_FALSE",
        0x80000002: "E_OUTOFMEMORY",
        0x80000009: "E_ACCESSDENIED",
        0x80000003: "E_INVALIDARG",
        0x80000008: "E_FAIL",
        0x8000FFFF: "E_UNEXPECTED",
        0x00041300: "SCHED_S_TASK_READY",
        0x00041301: "SCHED_S_TASK_RUNNING",
        0x00041302: "SCHED_S_TASK_DISABLED",
        0x00041303: "SCHED_S_TASK_HAS_NOT_RUN",
        0x00041304: "SCHED_S_TASK_NO_MORE_RUNS",
        0x00041305: "SCHED_S_TASK_NOT_SCHEDULED",
        0x00041306: "SCHED_S_TASK_TERMINATED",
        0x00041307: "SCHED_S_TASK_NO_VALID_TRIGGERS",
        0x00041308: "SCHED_S_EVENT_TRIGGER",
        0x80041309: "SCHED_E_TRIGGER_NOT_FOUND",
        0x8004130A: "SCHED_E_TASK_NOT_READY",
        0x8004130B: "SCHED_E_TASK_NOT_RUNNING",
        0x8004130C: "SCHED_E_SERVICE_NOT_INSTALLED",
        0x8004130D: "SCHED_E_CANNOT_OPEN_TASK",
        0x8004130E: "SCHED_E_INVALID_TASK",
        0x8004130F: "SCHED_E_ACCOUNT_INFORMATION_NOT_SET",
        0x80041310: "SCHED_E_ACCOUNT_NAME_NOT_FOUND",
        0x80041311: "SCHED_E_ACCOUNT_DBASE_CORRUPT",
        0x80041312: "SCHED_E_NO_SECURITY_SERVICES",
        0x80041313: "SCHED_E_UNKNOWN_OBJECT_VERSION",
        0x80041314: "SCHED_E_UNSUPPORTED_ACCOUNT_OPTION",
        0x80041315: "SCHED_E_SERVICE_NOT_RUNNING",
        0x80041316: "SCHED_E_UNEXPECTEDNODE",
        0x80041317: "SCHED_E_NAMESPACE",
        0x80041318: "SCHED_E_INVALIDVALUE",
        0x80041319: "SCHED_E_MISSINGNODE",
        0x8004131A: "SCHED_E_MALFORMEDXML",
        0x0004131B: "SCHED_S_SOME_TRIGGERS_FAILED",
        0x0004131C: "SCHED_S_BATCH_LOGON_PROBLEM",
        0x8004131D: "SCHED_E_TOO_MANY_NODES",
        0x8004131E: "SCHED_E_PAST_END_BOUNDARY",
        0x8004131F: "SCHED_E_ALREADY_RUNNING",
        0x80041320: "SCHED_E_USER_NOT_LOGGED_ON",
        0x80041321: "SCHED_E_INVALID_TASK_HASH",
        0x80041322: "SCHED_E_SERVICE_NOT_AVAILABLE",
        0x80041323: "SCHED_E_SERVICE_TOO_BUSY",
        0x80041324: "SCHED_E_TASK_ATTEMPTED",
        0x00041325: "SCHED_S_TASK_QUEUED",
        0x80041326: "SCHED_E_TASK_DISABLED",
        0x80041327: "SCHED_E_TASK_NOT_V1_COMPAT",
        0x80041328: "SCHED_E_START_ON_DEMAND"
    }

    TRIGGER_FLAGS = {
        0b1: "TASK_TRIGGER_FLAG_HAS_END_DATE",
        0b10: "TASK_TRIGGER_FLAG_KILL_AT_DURATION_END",
        0b100: "TASK_TRIGGER_FLAG_DISABLED"
    }

    def __init__(self, task_data=None):
        # Load fixed length sections
        self.product_version = struct.unpack("<H", task_data[0:2])[0]
        self.file_version = struct.unpack("<H", task_data[2:4])[0]

        if self.product_version not in BinaryScheduledTask.PRODUCT_VERSIONS:
            raise FormatError("Job file is not binary format")

        if self.file_version not in BinaryScheduledTask.FILE_VERSIONS:
            raise FormatError("Job file is not binary format")

        self.uuid = self._get_uuid(task_data)
        self.application_name_offset = struct.unpack("<H", task_data[20:22])[0]
        self.trigger_offset = struct.unpack("<H", task_data[22:24])[0]
        self.error_retry_count = struct.unpack("<H", task_data[24:26])[0]
        self.error_retry_interval = struct.unpack("<H", task_data[26:28])[0]
        self.idle_deadline = struct.unpack("<H", task_data[28:30])[0]
        self.idle_wait = struct.unpack("<H", task_data[30:32])[0]
        self.priority = struct.unpack("<I", task_data[32:36])[0]
        self.maximum_run_time = struct.unpack("<I", task_data[36:40])[0]
        self.exitcode = struct.unpack("<i", task_data[40:44])[0]
        self.status = struct.unpack("<I", task_data[44:48])[0]
        self.flags = struct.unpack("<I", task_data[48:52])[0]
        self.lastrun = self._get_last_run(task_data[52:68])

        # Load variable length section
        self.running_instance_count = struct.unpack("<H", task_data[68:70])[0]

        self.read_offset = self.application_name_offset
        self.application_name = self._get_offset_length_data(task_data, unicode_string=True)
        self.parameters = self._get_offset_length_data(task_data, unicode_string=True)
        self.working_dir = self._get_offset_length_data(task_data, unicode_string=True)
        self.author = self._get_offset_length_data(task_data, unicode_string=True)
        self.comment = self._get_offset_length_data(task_data, unicode_string=True)
        self.user_data = self._get_offset_length_data(task_data)
        self.reserved_data = self._get_offset_length_data(task_data)
        self.triggers = self._get_triggers(task_data)

        # Load optional signature
        try:
            self.signature = self._get_signature(task_data)
        except struct.error:
            self.signature = None

    @staticmethod
    def _get_uuid(data):
        return data[4:20]

    @staticmethod
    def _get_last_run(data):
        year = struct.unpack("<H", data[0:2])[0]
        month = struct.unpack("<H", data[2:4])[0]
        day = struct.unpack("<H", data[6:8])[0]
        hour = struct.unpack("<H", data[8:10])[0]
        minute = struct.unpack("<H", data[10:12])[0]
        second = struct.unpack("<H", data[12:14])[0]
        milliseconds = struct.unpack("<H", data[14:16])[0]
        return datetime.datetime(year, month, day, hour, minute, second, milliseconds * 1000)

    def _get_offset_length_data(self, data, unicode_string=False):
        # Read the 2 byte length of data and then return the data from offset, for unicode strings the length is the
        # number of characters so it
        value = ""
        value_begin = self.read_offset + 2
        value_length = int(struct.unpack("<H", data[self.read_offset:value_begin])[0])
        if value_length:
            if unicode_string:
                value_length *= 2
            value_end = value_begin + value_length
            value = data[value_begin:value_end]
        self.read_offset += value_length + 2
        if value and unicode_string:
            value = value[0:value_length-2]
        return value

    def _get_triggers(self, data):
        triggers = []
        triggers_begin = self.trigger_offset + 2
        triggers_length = struct.unpack("<H", data[self.trigger_offset:triggers_begin])[0]
        self.read_offset = triggers_begin
        for _ in range(0, triggers_length):
            trigger = {}
            trigger_data = data[self.read_offset:self.read_offset + 48]
            trigger["trigger_size"] = struct.unpack("<H", trigger_data[0:2])[0]
            trigger["reserved"] = struct.unpack("<H", trigger_data[2:4])[0]
            trigger["begin_year"] = struct.unpack("<H", trigger_data[4:6])[0]
            trigger["begin_month"] = struct.unpack("<H", trigger_data[6:8])[0]
            trigger["begin_day"] = struct.unpack("<H", trigger_data[8:10])[0]
            trigger["end_year"] = struct.unpack("<H", trigger_data[10:12])[0]
            trigger["end_month"] = struct.unpack("<H", trigger_data[12:14])[0]
            trigger["end_day"] = struct.unpack("<H", trigger_data[14:16])[0]
            trigger["start_hour"] = struct.unpack("<H", trigger_data[16:18])[0]
            trigger["start_minute"] = struct.unpack("<H", trigger_data[18:20])[0]
            trigger["minutes_duration"] = struct.unpack("<I", trigger_data[20:24])[0]
            trigger["minutes_interval"] = struct.unpack("<I", trigger_data[24:28])[0]
            trigger["flags"] = struct.unpack("<I", trigger_data[28:32])[0]
            trigger["trigger_type"] = struct.unpack("<I", trigger_data[32:36])[0]
            trigger["trigger_specific0"] = struct.unpack("<H", trigger_data[36:38])[0]
            trigger["trigger_specific1"] = struct.unpack("<H", trigger_data[38:40])[0]
            trigger["trigger_specific2"] = struct.unpack("<H", trigger_data[40:42])[0]
            trigger["padding"] = struct.unpack("<H", trigger_data[42:44])[0]
            trigger["reserved2"] = struct.unpack("<H", trigger_data[44:46])[0]
            trigger["reserved3"] = struct.unpack("<H", trigger_data[46:48])[0]
            triggers.append(trigger)
            self.read_offset += trigger["trigger_size"]
        return triggers

    def _get_signature(self, data):
        signature = {"version": struct.unpack("<H", data[self.read_offset:self.read_offset + 2])[0],
                     "min_client_version": struct.unpack("<H", data[self.read_offset + 2:self.read_offset + 4])[0],
                     "data": data[self.read_offset + 4:self.read_offset + 64]
                     }
        return signature

    def parse(self):
        # Returns a dictionary containing all the fields of a binary task
        flags = []
        for flag in self.TASK_FLAGS:
            if flag & self.flags:
                flags.append(self.TASK_FLAGS[flag])

        triggers = self.triggers
        for trigger in triggers:
            flags = []
            for flag in self.TRIGGER_FLAGS:
                if flag & trigger["flags"]:
                    flags.append(self.TRIGGER_FLAGS[flag])
            trigger["flags"] = flags

        data1 = struct.unpack("<I", self.uuid[0:4])[0]
        data2 = struct.unpack("<H", self.uuid[4:6])[0]
        data3 = struct.unpack("<H", self.uuid[6:8])[0]
        data4 = struct.unpack(">HHHH", self.uuid[8:16])

        uuid = "%08X-%04X-%04X-%04X-%04X%04X%04X" % (data1, data2, data3,
                data4[0], data4[1], data4[2], data4[3])

        task = {
            "task_type": "Binary",
            "application_name": self.application_name.decode('utf-16'),
            "author": self.author.decode('utf-16'),
            "comment": self.comment.decode('utf-16'),
            "error_retry_count": self.error_retry_count,
            "error_retry_interval": self.error_retry_interval,
            "exitcode": self.EXITCODE[self.exitcode],
            "file_version": self.FILE_VERSIONS[self.file_version],
            "flags": flags,
            "idle_deadline": self.idle_deadline,
            "idle_wait": self.idle_wait,
            "lastrun": str(self.lastrun),
            "maximum_run_time": self.maximum_run_time,
            "parameters": self.parameters.decode('utf-16'),
            "priority": self.PRIORITY[self.priority],
            "product_version": self.PRODUCT_VERSIONS[self.product_version],
            "reserved_data": self.reserved_data,
            "running_instance_count": self.running_instance_count,
            "signature": self.signature,
            "status": self.STATUS[self.status],
            "triggers": triggers,
            "user_data": self.user_data,
            "uuid": uuid,
            "working_dir": self.working_dir.decode('utf-16')
        }
        return task


def read_task(file_data):
    # Returns a task object based on file data provided
    try:
        task_object = XMLScheduledTask(file_data)
    except FormatError:
        try:
            task_object = BinaryScheduledTask(file_data)
        except FormatError:
            return None
    return task_object

if __name__ == "__main__":
    # Enables command line usage.
    if len(sys.argv) <= 1:
        print("Usage: %s <file>" % sys.argv[0])
        sys.exit(-1)

    filename = sys.argv[1]

    if os.path.isfile(filename):
        fd = open(filename, "rb")
        file_data = fd.read()
        fd.close()
        try:
            task = XMLScheduledTask(file_data)
        except FormatError:
            try:
                task = BinaryScheduledTask(file_data)
            except FormatError:
                print("File is not XML or Binary job format")
                sys.exit(-1)
        print(json.dumps(task.parse(), indent=2))