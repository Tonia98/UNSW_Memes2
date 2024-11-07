import pytest
import requests
from tests.wrap_functions_test import *
from src.config import url
from src.error import AccessError
from src.error import InputError
import imaplib                              
import email
import smtplib

# given an email
# search for the secret code associated with the email in our stream email
def get_code(mail):
    imap = imaplib.IMAP4_SSL('imap.gmail.com',993)
    # access to the sent mail of our stream account
    imap.login("DODOforever2@gmail.com", "memodragon")
    res, messages = imap.select('"[Gmail]/Sent Mail"')#pylint: disable=unused-variable
    # iterate through all sent mail in our stream account from the most recent one
    num_messages = int(messages[0])
    for i in range(num_messages, 0, -1):
        res, msg = imap.fetch(str(i), "(RFC822)")     
        for response in msg:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])#pylint: disable=unsubscriptable-object
                # found the email
                # return the associated secret code
                if msg['Bcc'] == mail:
                    return msg['Subject']
    return None

@pytest.fixture
def setup():
    requests.delete(url + 'clear/v1')
    
# test the case if the user request password reset
# he or she will be logged out in all sessions
def test_logged_out(setup):
    user1 = wrap_auth_register(False, "dodoforever14@gmail.com", "123456", "Wayne", "Zhang")
    wrap_auth_passwordreset_request(False, "dodoforever14@gmail.com")
    assert wrap_channels_create(True, user1['token'], 'DODO', True) == AccessError.code
    
# test the case when the use reset the password successfully
def test_reset_successful(setup):
    wrap_auth_register(False, "dodoforever14@gmail.com", "123456", "Wayne", "Zhang")
    wrap_auth_passwordreset_request(False, "dodoforever14@gmail.com")
    code = get_code("dodoforever14@gmail.com")
    wrap_auth_passwordreset_reset(False, code, "newpassword")
    # the use should be able to login with the new password
    assert wrap_auth_login(True, "dodoforever14@gmail.com", "newpassword") == 200
    
# test the case when the use entered the wrong secret code 
def test_unvalid_code(setup):
    wrap_auth_register(False, "dodoforever14@gmail.com", "123456", "Wayne", "Zhang")
    wrap_auth_passwordreset_request(False, "dodoforever14@gmail.com")
    assert wrap_auth_passwordreset_reset(True, "wrongcode", "newpassword") == InputError.code
    
# test the case when the use wants to change to a password less than 6 characters
def test_password_less_6(setup):
    wrap_auth_register(False, "dodoforever14@gmail.com", "123456", "Wayne", "Zhang")
    wrap_auth_passwordreset_request(False, "dodoforever14@gmail.com")
    code = get_code("dodoforever14@gmail.com")
    wrap_auth_passwordreset_reset(False, code, "pass")
    assert wrap_auth_login(True, "dodoforever14@gmail.com", "pass") == InputError.code
    
# test the case when there are two users request in the same time
def test_reset_two_requests(setup):
    wrap_auth_register(False, "dodoforever14@gmail.com", "123456", "Wayne", "Zhang")
    wrap_auth_register(False, "dodoforever16@gmail.com", "37856904", "Jason", "Leo")
    # both user request in the same time
    wrap_auth_passwordreset_request(False, "dodoforever16@gmail.com")
    wrap_auth_passwordreset_request(False, "dodoforever14@gmail.com")
    # the first request user should be able to login
    code = get_code("dodoforever16@gmail.com")
    wrap_auth_passwordreset_reset(False, code, "newpassword")
    assert wrap_auth_login(True, "dodoforever16@gmail.com", "newpassword") == 200
    
    
    
    
    
    
