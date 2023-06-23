# -*- coding: utf-8 -*-
from ..objects.winstructures import try_empty_login


def check_empty_passwords(u):
    '''
    Local users have empty password
    '''
    return [user['name'] for user in u.users if try_empty_login(user['name'])]


def check_passwordreq_option(u):
    '''
    Check if password is not required
    if the user has been created with the option /passwordreq:no
    '''
    return [user['name'] for user in u.users if not user['password_required']]