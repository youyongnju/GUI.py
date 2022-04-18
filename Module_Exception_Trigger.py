#!/usr/bin/env python

import inspect
import os
import sys
import time
import threading
import traceback
import sharedata
from functools import wraps

import Module_Error_Code as m_err


def try_except(func):
    """
    This decorator is use for catch exception for function interface.
    :param func: Function handler.
    :return: Inner function handler.
    """
    @wraps(func)
    def handle_problems(obj_instance, *args, **kwargs):
        try:
            res = func(obj_instance, *args, **kwargs)
            return res
        except Exception:
            date_stamp = time.strftime("%Y%m%d")

            exc_folder = "./exception"
            if not os.path.exists(exc_folder):
                os.makedirs(exc_folder)
            exc_log = exc_folder + "\\" + r"exception_" + date_stamp + r".log"

            traceback.print_exc(file=open(exc_log, 'a+'))

            exc_type, exc_instance, exc_traceback = sys.exc_info()
            formatted_traceback = ''.join(traceback.format_tb(exc_traceback))
            detail_exc_info = ("\n%s\n%s: %s" % (formatted_traceback, exc_type.__name__, exc_instance))

            logger_info = (r"%d,Exception <%s> Catched!\n(Check .\exception\exception.log for more detail.),%s" %
                           (m_err.Err_fail, exc_instance, m_err.Err_exception_code))
            if hasattr(obj_instance, "logger") and obj_instance.logger:
                obj_instance.logger.debug(logger_info)
                obj_instance.logger.debug("-*-" * 30)
                obj_instance.logger.debug(detail_exc_info)
            else:
                print(logger_info)
                sharedata.content.append(logger_info)
                print(detail_exc_info)
                sharedata.content.append(detail_exc_info)
            # input("Exception detected, press <enter> to exit...")
            press_key = input("Exception detected, press Y to exit, other keys to continue, ...")
            if 'y' == press_key.lower():
                sys.exit()
        finally:
            pass

    return handle_problems


def timeout_set(time_interval):
    """
    This decorator is use for set timeout for function interface.
    :param time_interval: Timeout seconds.
    :return: Inner function handler.
    """
    def wrapper(func):
        def time_out(obj_instance):
            obj_instance.time_out_queue.put(1)
            if obj_instance.logger:
                obj_instance.logger.debug("Timeout Error: function not responded in %d seconds, exit automatically!" %
                                          time_interval)

        @wraps(func)
        def deco(obj_instance, *args, **kwargs):
            timer = threading.Timer(time_interval, time_out, args=(obj_instance,))
            timer.start()
            res = func(obj_instance, *args, **kwargs)
            timer.cancel()
            obj_instance.time_out_queue.queue.clear()
            return res

        return deco

    return wrapper


def type_assert(*type_args, **type_kwargs):
    """
    This decorator is use for inspect function interface parameters type.
    :param type_args: Positional parameters type for parameters.
    :param type_kwargs: Key word parameters type for parameters.
    :return: Inner function handler.
    """
    def decorate(func):
        obj_sig = inspect.signature(func)
        dict_bind_types = obj_sig.bind_partial(*type_args, **type_kwargs).arguments

        @wraps(func)
        def wrapper(obj_instance, *args, **kwargs):
            dict_bind_values = obj_sig.bind(*args, **kwargs).arguments

            for obj_param_name, obj_param_value in dict_bind_values.items():
                if obj_param_name in dict_bind_types:
                    if not isinstance(obj_param_value, dict_bind_types[obj_param_name]):
                        raise TypeError("Argument {} value {!r} type must be {}".format(
                            obj_param_name, obj_param_value, dict_bind_types[obj_param_name]))
            return func(obj_instance, *args, **kwargs)

        return wrapper

    return decorate
