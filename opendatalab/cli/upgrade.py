#
# Copyright 2022 Shanghai AI Lab. Licensed under MIT License.
#
import sys
import operator
import click

from opendatalab.__version__ import __version__
from opendatalab.cli.utility import ContextInfo, exception_handler


@exception_handler
def implement_upgrade(obj: ContextInfo):
    """
    check cli version compare with svc
    Args:
        obj: context
    Returns:

    """
    client = obj.get_client()
    odl_api = client.get_api()
    version_info = odl_api.check_version()

    major_version = version_info['majorVersion']
    minor_version = version_info['minorVersion']
    service_version = version_info['serviceVersion']
    is_beta = version_info['isBeta']

    # if beta False, ignore beta version, set beta_version = 0
    if is_beta:
        beta_version = version_info['betaVersion']
        res_version = major_version + '.' + minor_version + 'b' + beta_version
    else:
        beta_version = 0
        res_version = major_version + '.' + minor_version + '.' + beta_version

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

    is_major_upgrade = operator.eq(float(major_version), float(cur_major_ver))
    is_minor_upgrade = operator.eq(float(minor_version), float(cur_minor_ver))
    is_beta_upgrade = operator.eq(float(beta_version), float(cur_b_ver))

    # click.echo(f"check version: installed :{installed_version}, latest: {res_version}")

    check_ret_code = 0
    if is_major_upgrade:
        if is_minor_upgrade:
            if is_beta_upgrade:
                check_ret_code = 0
                # click.secho(f"Yea! check completed, no need upgrade current version.", fg='blue')
            else:
                if operator.gt(beta_version, cur_b_ver):
                    pass
                else:
                    check_ret_code = 1
                    click.secho(f"[Error]: upgrade needed, please use 'pip install -U opendatalab'", fg='red')
                    sys.exit(-1)
        else:
            if operator.gt(minor_version, cur_minor_ver):
                pass
            else:
                check_ret_code = 1
                click.secho(f"[Error]: upgrade needed, please use 'pip install -U opendatalab'", fg='red')
                sys.exit(-1)
    else:
        if not operator.gt(major_version, cur_major_ver):
            check_ret_code = 1
            click.secho(f"[Error]: upgrade needed, please use 'pip install -U opendatalab'", fg='red')
            sys.exit(-1)
        else:
            pass

    obj.set_check_info(latest_version=res_version, check_ret=check_ret_code)
    # return installed_version, res_version, check_ret_code
