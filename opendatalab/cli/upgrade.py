#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
import operator
import sys

import click

from opendatalab.__version__ import __version__
from opendatalab.cli.utility import ContextInfo, exception_handler


@exception_handler
def implement_upgrade(obj: ContextInfo):
    """
        check cli version compare with svc
    Args:
        obj (ContextInfo):

    Returns:

    """
    client = obj.get_client()
    odl_api = client.get_api()
    version_info = odl_api.check_version()

    latest_major_version = version_info['majorVersion']
    latest_minor_version = version_info['minorVersion']
    latest_service_version = version_info['serviceVersion']
    is_beta_latest = version_info['isBeta']

    # to discuss: if beta False, ignore beta version, set beta_version = 0
    if is_beta_latest:
        latest_beta_version = version_info['betaVersion']
        latest_res_version = latest_major_version + '.' + latest_minor_version + 'b' + str(latest_beta_version)
    else:
        latest_beta_version = 0
        latest_res_version = latest_major_version + '.' + latest_minor_version + '.' + str(latest_beta_version)

    # installed_svc = __svc__
    installed_version = __version__
    is_installed_beta = installed_version.find("b") != -1

    if is_installed_beta:
        cur_maj_min_ver = installed_version.split('b')[0]
        cur_major_ver = cur_maj_min_ver[:cur_maj_min_ver.rfind('.')]
        cur_minor_ver = cur_maj_min_ver[cur_maj_min_ver.rfind('.') + 1:]
        cur_b_ver = installed_version.split('b')[1]
    else:
        cur_major_ver = installed_version[:installed_version.rfind('.')]
        cur_minor_ver = installed_version[installed_version.rfind('.') + 1:]
        cur_b_ver = 0
        pass

    """
    version :
        released: 0.0.1.0 -> 0.0.2.0 ... -> 0.1.0.0
        beta    : 0.0.1b10 -> 0.0.1b11 .. -> 0.0.1b90...
        major_version: 0.0
        minor_version: 1
        is_beta: bool, True->b, False->''
        beta_version: released -> 0, beta -> 90
    upgrade flag
        -1: pre-check, 
        0: checked-no-need-grade, 
        1: checked-need-upgrade
    """
    # check_ret_code = -1

    if operator.gt(float(latest_major_version), float(cur_major_ver)):
        check_ret_code = 1
        click.secho(f"check version: installed :{installed_version}, latest: {latest_res_version}", fg='green')
        click.secho(f"[Fatal]: upgrade needed, please use 'pip install -U opendatalab'", fg='red')
        obj.set_check_info(latest_version=latest_res_version, check_ret=check_ret_code)
        sys.exit(-1)

    elif operator.lt(float(latest_major_version), float(cur_major_ver)):
        check_ret_code = 0
        obj.set_check_info(latest_version=latest_res_version, check_ret=check_ret_code)

    else:
        if operator.gt(float(latest_minor_version), float(cur_minor_ver)):
            check_ret_code = 1
            click.secho(f"odl version: current: {installed_version}, latest: {latest_res_version}", fg='green')
            click.secho(f"[Fatal]: upgrade needed, please use 'pip install -U opendatalab'", fg='red')
            obj.set_check_info(latest_version=latest_res_version, check_ret=check_ret_code)
            sys.exit(-1)

        elif operator.lt(float(latest_minor_version), float(cur_minor_ver)):
            check_ret_code = 0
            obj.set_check_info(latest_version=latest_res_version, check_ret=check_ret_code)

        else:
            if is_installed_beta and is_beta_latest:
                if operator.gt(float(latest_beta_version), float(cur_b_ver)):
                    check_ret_code = 1
                    click.secho(f"odl version: current: {installed_version}, latest: {latest_res_version}", fg='green')
                    click.secho(f"[Fatal]: upgrade needed, please use 'pip install -U opendatalab'", fg='red')
                    obj.set_check_info(latest_version=latest_res_version, check_ret=check_ret_code)
                    sys.exit(-1)
                else:
                    check_ret_code = 0
                    obj.set_check_info(latest_version=latest_res_version, check_ret=check_ret_code)

            elif is_beta_latest and not is_installed_beta:
                # TODO: keep latest released or beta version
                check_ret_code = 1
                click.secho(f"odl version: current: {installed_version}, latest: {latest_res_version}", fg='green')
                click.secho(f"[Fatal]: upgrade needed, please use 'pip install -U opendatalab'", fg='red')
                obj.set_check_info(latest_version=latest_res_version, check_ret=check_ret_code)
                sys.exit(-1)

            else:
                check_ret_code = 0
                obj.set_check_info(latest_version=latest_res_version, check_ret=check_ret_code)