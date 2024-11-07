import pytest
import math
from src.config import url
import json
import requests
from tests.wrap_functions_test import *
from datetime import datetime, timezone
from time import sleep
from src.error import AccessError

@pytest.fixture
def clear_data():
    requests.delete(url + 'clear/v1')

def test_token(clear_data):
    assert wrap_user_stats(True, '312312') == AccessError.code
    assert wrap_users_stats(True, '312312') == AccessError.code
    user1 = wrap_auth_register(False, "451842120@qq.com", "111111", "Wu", "Jiameng")
    wrap_auth_logout(False, user1['token'])
    assert wrap_user_stats(True, user1['token']) == AccessError.code
    assert wrap_users_stats(True, user1['token']) == AccessError.code

def test_no_channel_dm(clear_data):
    sleep(1)
    need_status_code = False
    # Create two valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")

    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())

    # Check user_stats
    assert wrap_user_stats(need_status_code, user1['token']) == {
        "user_stats": {
            "channels_joined": [
                {
                    "num_channels_joined": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "dms_joined": [
                {
                    "num_dms_joined": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "messages_sent": [
                {
                    "num_messages_sent": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "involvement_rate": 0.0
        }
    }
    # Check users_stats
    assert wrap_users_stats(need_status_code, user1['token']) == {
        "workspace_stats": {
            "channels_exist": [
                {
                    "num_channels_exist": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "dms_exist": [
                {
                    "num_dms_exist": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "messages_exist": [
                {
                    "num_messages_exist": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "utilization_rate": 0.0
        }
    }
    


def test_channels_stats(clear_data):
    need_status_code = False
    # Create two valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")

    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())

    sleep(1)
    dt = datetime.now()
    ch1_time = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    wrap_channels_create(need_status_code,user1['token'], "Snake", True)

    sleep(1)
    dt = datetime.now()
    ch2_time = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    wrap_channels_create(need_status_code,user2['token'], "Pig", True)

    sleep(1)
    dt = datetime.now()
    ch3_time = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    channel3 = wrap_channels_create(need_status_code,user1['token'], "Emu", True)
    
    wrap_channel_join(True, user2['token'], channel3['channel_id'])

    assert wrap_user_stats(need_status_code, user1['token']) == {
        "user_stats": {
            "channels_joined": [
                {
                    "num_channels_joined": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                },
                {
                    "num_channels_joined": 1, 
                    "time_stamp": pytest.approx(ch1_time, abs=2)
                },
                {
                    "num_channels_joined": 2, 
                    "time_stamp": pytest.approx(ch3_time, abs=2)
                }
            ],
            "dms_joined": [
                {
                    "num_dms_joined": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "messages_sent": [
                {
                    "num_messages_sent": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "involvement_rate": 2/3
        }
    }

    assert wrap_user_stats(need_status_code, user2['token']) == {
        "user_stats": {
            "channels_joined": [
                {
                    "num_channels_joined": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                },
                {
                    "num_channels_joined": 1, 
                    "time_stamp": pytest.approx(ch2_time, abs=2)
                },
                {
                    "num_channels_joined": 2, 
                    "time_stamp": pytest.approx(ch3_time, abs=2)
                }
            ],
            "dms_joined": [
                {
                    "num_dms_joined": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "messages_sent": [
                {
                    "num_messages_sent": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "involvement_rate": 2/3
        }
    }

    assert wrap_users_stats(need_status_code, user1['token']) == {
        "workspace_stats": {
            "channels_exist": [
                {
                    "num_channels_exist": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                },
                {
                    "num_channels_exist": 1, 
                    "time_stamp": pytest.approx(ch1_time, abs=2)
                },
                {
                    "num_channels_exist": 2, 
                    "time_stamp": pytest.approx(ch2_time, abs=2)
                },
                {
                    "num_channels_exist": 3, 
                    "time_stamp": pytest.approx(ch3_time, abs=2)
                }
            ],
            "dms_exist": [
                {
                    "num_dms_exist": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "messages_exist": [
                {
                    "num_messages_exist": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "utilization_rate": 1.0
        }
    }


def test_dms_states(clear_data):
    need_status_code = False
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "222222", "Zhou", "Yanting")
    user3 = wrap_auth_register(need_status_code,"z5293213@unsw.edu.au", "333333", "li", "Yunzheng")

    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())

    sleep(1)
    dt = datetime.now()
    dm1_time = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    wrap_dm_create(False, user1['token'], [user2['auth_user_id']])

    sleep(1)
    dt = datetime.now()
    dm2_time = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    wrap_dm_create(False, user1['token'], [user2['auth_user_id']])

    sleep(1)
    dt = datetime.now()
    dm3_time = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    wrap_dm_create(False, user1['token'], [user2['auth_user_id'], user3['auth_user_id']])

    assert wrap_user_stats(need_status_code, user1['token']) == {
        "user_stats": {
            "channels_joined": [
                {
                    "num_channels_joined": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "dms_joined": [
                {
                    "num_dms_joined": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                },
                {
                    "num_dms_joined": 1, 
                    "time_stamp": pytest.approx(dm1_time, abs=2)
                },
                {
                    "num_dms_joined": 2, 
                    "time_stamp": pytest.approx(dm2_time, abs=2)
                },
                {
                    "num_dms_joined": 3, 
                    "time_stamp": pytest.approx(dm3_time, abs=2)
                }
            ],
            "messages_sent": [
                {
                    "num_messages_sent": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "involvement_rate": 1
        }
    }

    assert wrap_user_stats(need_status_code, user2['token']) == {
        "user_stats": {
            "channels_joined": [
                {
                    "num_channels_joined": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "dms_joined": [
                {
                    "num_dms_joined": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                },
                {
                    "num_dms_joined": 1, 
                    "time_stamp": pytest.approx(dm1_time, abs=2)
                },
                {
                    "num_dms_joined": 2, 
                    "time_stamp": pytest.approx(dm2_time, abs=2)
                },
                {
                    "num_dms_joined": 3,
                    "time_stamp": pytest.approx(dm3_time, abs=2)
                }
            ],
            "messages_sent": [
                {
                    "num_messages_sent": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "involvement_rate": 1.0
        }
    }


    assert wrap_users_stats(need_status_code, user1['token']) == {
        "workspace_stats": {
            "channels_exist": [
                {
                    "num_channels_exist": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)},
            ],
            "dms_exist": [
                {
                    "num_dms_exist": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                },
                {
                    "num_dms_exist": 1, 
                    "time_stamp": pytest.approx(dm1_time, abs=2)
                },
                {
                    "num_dms_exist": 2, 
                    "time_stamp": pytest.approx(dm2_time, abs=2)
                },
                {
                    "num_dms_exist": 3, 
                    "time_stamp": pytest.approx(dm3_time, abs=2)
                }
            ],
            "messages_exist": [
                {
                    "num_messages_exist": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "utilization_rate": 1.0
        }
    }


def test_messages_stats(clear_data):
    need_status_code = False
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "222222", "Zhou", "Yanting")
    user3 = wrap_auth_register(need_status_code,"z5293213@unsw.edu.au", "333333", "li", "Yunzheng")
    
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())

    sleep(1)
    dt = datetime.now()
    dm1_time = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    dm1 = wrap_dm_create(False, user1['token'], [user2['auth_user_id']])

    sleep(1)
    dt = datetime.now()
    cha1_time = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    channel1 = wrap_channels_create(need_status_code,user3['token'], "Snake", True)

    sleep(1)
    dt = datetime.now()
    msg1_time = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    wrap_message_senddm(True, user1['token'], dm1['dm_id'], 'something')

    sleep(1)
    dt = datetime.now()
    msg2_time = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    wrap_message_send(need_status_code, user3['token'], channel1['channel_id'], 'hello')

    assert wrap_users_stats(need_status_code, user1['token']) == {
        "workspace_stats": {
            "channels_exist": [
                {
                    "num_channels_exist": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                },
                {
                    "num_channels_exist": 1, 
                    "time_stamp": pytest.approx(cha1_time, abs=2)
                }
            ],
            "dms_exist": [
                {
                    "num_dms_exist": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                },
                {
                    "num_dms_exist": 1, 
                    "time_stamp": pytest.approx(dm1_time, abs=2)
                },
            ],
            "messages_exist": [
                {
                    "num_messages_exist": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                },
                {
                    "num_messages_exist": 1, 
                    "time_stamp": pytest.approx(msg1_time, abs=2)
                },
                {
                    "num_messages_exist": 2, 
                    "time_stamp": pytest.approx(msg2_time, abs=2)
                }
            ],
            "utilization_rate": 1.0
        }
    }

    assert wrap_user_stats(need_status_code, user1['token']) == {
        "user_stats": {
            "channels_joined": [
                {
                    "num_channels_joined": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "dms_joined": [
                {
                    "num_dms_joined": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                },
                {
                    "num_dms_joined": 1, 
                    "time_stamp": pytest.approx(dm1_time, abs=2)
                },
            ],
            "messages_sent": [
                {
                    "num_messages_sent": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                },
                {
                    "num_messages_sent": 1, 
                    "time_stamp": pytest.approx(msg1_time, abs=2)
                }
            ],
            "involvement_rate": 1 / 2
        }
    }

    assert wrap_user_stats(need_status_code, user3['token']) == {
        "user_stats": {
            "channels_joined": [
                {
                    "num_channels_joined": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                },
                {
                    "num_channels_joined": 1, 
                    "time_stamp": pytest.approx(msg1_time, abs=2)
                }
            ],
            "dms_joined": [
                {
                    "num_dms_joined": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                },
            ],
            "messages_sent": [
                {
                    "num_messages_sent": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                },
                {
                    "num_messages_sent": 1, 
                    "time_stamp": pytest.approx(msg2_time, abs=2)
                }
            ],
            "involvement_rate": 1 / 2
        }
    }


def test_involvement_capped_1(clear_data):
    need_status_code = False
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "222222", "Zhou", "Yanting")
    
    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())

    sleep(1)
    dt = datetime.now()
    dm1_time = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    dm1 = wrap_dm_create(False, user1['token'], [user2['auth_user_id']])

    sleep(1)
    dt = datetime.now()
    cha1_time = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    channel1 = wrap_channels_create(need_status_code,user1['token'], "Snake", True)

    sleep(1)
    dt = datetime.now()
    msg1_time = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    msg1 = wrap_message_senddm(need_status_code, user1['token'], dm1['dm_id'], 'something')

    sleep(1)
    dt = datetime.now()
    msg2_time = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    wrap_message_send(need_status_code, user1['token'], channel1['channel_id'], 'hello')

    wrap_message_remove(need_status_code, user1['token'], msg1['message_id'])
    
    assert wrap_user_stats(need_status_code, user1['token']) == {
        "user_stats": {
            "channels_joined": [
                {
                    "num_channels_joined": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                },
                {
                    "num_channels_joined": 1, 
                    "time_stamp": pytest.approx(cha1_time, abs=2)
                }
            ],
            "dms_joined": [
                {
                    "num_dms_joined": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                },
                {
                    "num_dms_joined": 1, 
                    "time_stamp": pytest.approx(dm1_time, abs=2)
                },
            ],
            "messages_sent": [
                {
                    "num_messages_sent": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                },
                {
                    "num_messages_sent": 1, 
                    "time_stamp": pytest.approx(msg1_time, abs=2)
                },
                {
                    "num_messages_sent": 2, 
                    "time_stamp": pytest.approx(msg2_time, abs=2)
                }
            ],
            "involvement_rate": 1
        }
    }

def test_leave_channels_stats(clear_data):
    need_status_code = False
    # Create two valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")


    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    channel1 = wrap_channels_create(need_status_code,user1['token'], "Snake", True)

    wrap_channel_invite(False, user1['token'], channel1['channel_id'], user2['auth_user_id'])
    assert wrap_user_stats(need_status_code, user2['token']) == {
        "user_stats": {
            "channels_joined": [
                {
                    "num_channels_joined": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                },
                {
                    "num_channels_joined": 1, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                },
            ],
            "dms_joined": [
                {
                    "num_dms_joined": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "messages_sent": [
                {
                    "num_messages_sent": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "involvement_rate": 1
        }
    }
    wrap_channel_leave(True, user2['token'], channel1['channel_id'])
    assert wrap_user_stats(need_status_code, user2['token']) == {
        "user_stats": {
            "channels_joined": [
                {
                    "num_channels_joined": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                },
                {
                    "num_channels_joined": 1, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                },
                {
                    "num_channels_joined": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "dms_joined": [
                {
                    "num_dms_joined": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "messages_sent": [
                {
                    "num_messages_sent": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "involvement_rate": 0
        }
    }

def test_leave_dm_stats(clear_data):
    need_status_code = False
    # Create two valid users
    user1 = wrap_auth_register(need_status_code,"451842120@qq.com", "111111", "Wu", "Jiameng")
    user2 = wrap_auth_register(need_status_code,"z5291515@unsw.edu.au", "123456", "Zhou", "Yanting")

    dt = datetime.now()
    timestamp = math.floor(dt.replace(tzinfo=timezone.utc).timestamp())
    dm1 = wrap_dm_create(False, user1['token'], [user2['auth_user_id']])

    assert wrap_user_stats(need_status_code, user2['token']) == {
        "user_stats": {
            "channels_joined": [
                {
                    "num_channels_joined": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                },
            ],
            "dms_joined": [
                {
                    "num_dms_joined": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                },
                {
                    "num_dms_joined": 1, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "messages_sent": [
                {
                    "num_messages_sent": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "involvement_rate": 1
        }
    }
    wrap_dm_remove(True, user1['token'], dm1['dm_id'])
    assert wrap_user_stats(need_status_code, user2['token']) == {
        "user_stats": {
            "channels_joined": [
                {
                    "num_channels_joined": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                },
            ],
            "dms_joined": [
                {
                    "num_dms_joined": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                },
                {
                    "num_dms_joined": 1, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                },
                {
                    "num_dms_joined": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "messages_sent": [
                {
                    "num_messages_sent": 0, 
                    "time_stamp": pytest.approx(timestamp, abs=2)
                }
            ],
            "involvement_rate": 0
        }
    }
