import sys
import signal
from src import config
from src.config import url
from json import dumps, dump
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from src.error import *
from src.auth import *
from src.channel import *
from src.channels import *
from src.other import *
from src.user import *
from src.dm import *
from src.users import *
from src.message import *
from src.admin import *
from src.data_store import data_store
from src.search import *
from src.notifications import *
from src.standup import *
from src.stats import *
import json



def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

# if it is the first time running the server, data == {}
# if it is not, this line will get data from json file
with open('src/data_base.json', 'r') as persistent_file:
    original_data = json.load(persistent_file)
    data_store.set(original_data)

# update new data to json file
def save_updated_data_store():
    all_data = data_store.get()
    with open('src/data_base.json', 'w') as persistent_file:
        dump(all_data, persistent_file)

@APP.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('', path)

@APP.route("/auth/logout/v1", methods=['POST'])
def logout_a_user():
    user_info = request.get_json()
    save_updated_data_store()
    return dumps(auth_logout(user_info['token']))


@APP.route("/user/profile/v1", methods=['GET'])
def get_user_profile():
    data = request.args.to_dict()
    profile = user_profile(data['token'], int(data['u_id']))
    save_updated_data_store()
    return dumps(profile)

@APP.route("/user/profile/setname/v1", methods=['PUT'])
def set_user_name():
    data = request.get_json()
    user_profile_set_name(data['token'], data['name_first'], data['name_last'])
    save_updated_data_store()
    return dumps({})

@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def set_user_handle_str():
    data = request.get_json()
    user_profile_set_handle(data['token'], data['handle_str'])
    save_updated_data_store()
    return dumps({})


@APP.route("/auth/register/v2", methods=['POST'])
def register_new_user():
    user_info = request.get_json()
    user_token_id = auth_register(user_info['email'], user_info['password'], user_info['name_first'], user_info['name_last'])
    save_updated_data_store()
    return dumps(user_token_id)

@APP.route("/auth/login/v2", methods=['POST'])
def login_a_user():
    user_info = request.get_json()
    user_token_id = auth_login(user_info['email'], user_info['password'])
    save_updated_data_store()
    return dumps(user_token_id)


@APP.route("/channels/list/v2", methods=['GET'])
def list_channels():
    data = request.args.to_dict()
    channels = channels_list(data['token'])
    save_updated_data_store()
    return dumps(channels)
    
@APP.route("/channels/listall/v2", methods=['GET'])
def list_all_channels():
    data = request.args.to_dict()
    channels = channels_listall(data['token'])
    save_updated_data_store()
    return dumps(channels)

@APP.route("/users/all/v1", methods=['GET'])
def all_users():
    data = request.args.to_dict()
    users = users_all(data['token'])
    save_updated_data_store()
    return dumps(users)

@APP.route("/channels/create/v2", methods=['POST'])
def create_channel():
    data = request.get_json()
    channel_id = channels_create(data['token'],data['name'],data['is_public'])
    save_updated_data_store()
    return dumps(channel_id)

# ------------------------- < clear > ----------------------------
@APP.route("/clear/v1", methods=['DELETE'])
def clear_data():
    clear()
    save_updated_data_store()
    return dumps({})

# ------------------------- < channel_message > ----------------------------
@APP.route("/channel/messages/v2", methods = ['GET'])
def printing_list_of_messages():
    data = request.args.to_dict()
    messages = channel_messages(data['token'], int(data['channel_id']), int(data['start']))
    save_updated_data_store()
    return dumps(messages)


# ------------------------- < message send > ----------------------------
@APP.route("/message/send/v1", methods = ['POST'])
def sending_message(): 
    data = request.get_json()
    message_id = message_send(data['token'], int(data['channel_id']), data['message'])
    save_updated_data_store()
    return dumps(message_id)
    

# ------------------------- < message edit > ----------------------------
@APP.route("/message/edit/v1", methods = ['PUT'])
def edit_message():
    data = request.get_json()
    message_edit(data['token'], int(data['message_id']), data['message'])
    save_updated_data_store()
    return dumps({})


# ------------------------- < message remove > ----------------------------
@APP.route("/message/remove/v1", methods = ['DELETE'])
def remove_message():
    data = request.get_json()
    message_remove(data['token'], data['message_id'])
    save_updated_data_store()
    return dumps({})


# ------------------------- < dm message > ----------------------------
@APP.route("/dm/messages/v1", methods = ['GET'])
def message_dm():
    data = request.args.to_dict()
    dm_message_list = dm_messages(data['token'], int(data['dm_id']), int(data['start']))
    save_updated_data_store()
    return dumps(dm_message_list)
    

# ------------------------- < message send_dm > ----------------------------
@APP.route("/message/senddm/v1", methods = ['POST'])
def send_message_dm():
    data = request.get_json()
    dm_message_id = message_senddm(data['token'], int(data['dm_id']), data['message'])
    save_updated_data_store()
    return dumps(dm_message_id)

@APP.route("/message/share/v1", methods = ['POST'])
def sharing_messages():
    data = request.get_json()
    share_message_id = message_share(data['token'], int(data['og_message_id']), 
                                      data['message'], int(data['channel_id']),  int(data['dm_id']))
    save_updated_data_store()
    return dumps(share_message_id)

@APP.route("/message/react/v1", methods = ['POST'])
def reacting_message():
    data = request.get_json()
    message_react(data['token'], int(data['message_id']), int(data['react_id']))
    save_updated_data_store()
    return dumps({})

@APP.route("/message/unreact/v1", methods = ['POST'])
def unreacting_message():
    data = request.get_json()
    message_unreact(data['token'], int(data['message_id']), int(data['react_id']))
    save_updated_data_store()
    return dumps({})

@APP.route("/channel/leave/v1", methods=['POST'])
def leave_a_member():
    data = request.get_json()
    channel_leave(data['token'], data['channel_id'])
    save_updated_data_store()
    return dumps({})

@APP.route("/channel/addowner/v1", methods=['POST'])
def add_an_owner():
    data = request.get_json()
    channel_addowner(data['token'], data['channel_id'], data['u_id'])
    save_updated_data_store()
    return dumps({})

@APP.route("/channel/removeowner/v1", methods=['POST'])
def remove_an_owner():
    data = request.get_json()
    channel_removeowner(data['token'], data['channel_id'], data['u_id'])
    save_updated_data_store()
    return dumps({})

@APP.route("/channel/details/v2", methods=['GET'])
def details_of_channel():
    data = request.args.to_dict()
    channel_info = channel_details(data['token'],int(data['channel_id']))
    save_updated_data_store()
    return dumps(channel_info)
    
@APP.route("/channel/invite/v2", methods=['POST'])
def invite_a_member():
    data = request.get_json()
    channel_invite(data['token'], int(data['channel_id']), data['u_id'])
    save_updated_data_store()
    return dumps({})
    
@APP.route("/dm/create/v1", methods=['POST'])
def create_dm():
    data = request.get_json()
    dm = dm_create(data['token'], data['u_ids'])
    save_updated_data_store()
    return dumps(dm)
    
@APP.route("/channel/join/v2", methods=['POST'])
def join_a_member():
    data = request.get_json()
    channel_join(data['token'], data['channel_id'])
    save_updated_data_store()
    return dumps({})
    
@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def change_permission():
    data = request.get_json()
    userpermission_change(data['token'], data['u_id'], data['permission_id'])
    save_updated_data_store()
    return dumps({})
    
@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def remove_user():
    data = request.get_json()
    user_remove(data['token'], data['u_id'])
    save_updated_data_store()
    return dumps({})

@APP.route("/dm/list/v1", methods=['GET'])
def list_dm():
    data = request.args.to_dict()
    dms = dm_list(data['token'])
    save_updated_data_store()
    return dumps(dms)

@APP.route("/dm/details/v1", methods=['GET'])
def details_dm():
    data = request.args.to_dict()
    dmdetails = dm_details(data['token'], int(data['dm_id']))
    save_updated_data_store()
    return dumps(dmdetails)
    
@APP.route("/dm/leave/v1", methods=['POST'])
def leave_dm():
    data = request.get_json()
    dm_leave(data['token'], data['dm_id'])
    save_updated_data_store()
    return dumps({})

@APP.route("/dm/remove/v1", methods = ['DELETE'])
def remove_dm():
    data = request.get_json()
    dm_remove(data['token'], data['dm_id'])
    save_updated_data_store()
    return dumps({})

@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def set_user_email():
    data = request.get_json()
    user_profile_set_email(data['token'], data['email'])
    save_updated_data_store()
    return dumps({})
    
@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def request_password():
    data = request.get_json()
    auth_passwordreset_request(data['email'])
    save_updated_data_store()
    return dumps({})
    
@APP.route("/auth/passwordreset/reset/v1", methods=['POST'])
def reset_password():
    data = request.get_json()
    auth_passwordreset_reset(data['reset_code'], data['new_password'])
    save_updated_data_store()
    return dumps({})
    
@APP.route("/user/profile/uploadphoto/v1", methods=['POST'])
def upload_photo():
    data = request.get_json()
    uploadphoto(data['token'], data['img_url'], data['x_start'], data['y_start'], data['x_end'], data['y_end'])
    save_updated_data_store()
    return dumps({})
##
@APP.route("/standup/start/v1", methods=['POST'])
def start_standup():
    data = request.get_json()
    timefinish = standup_start(data['token'], int(data['channel_id']),int(data['length']))
    save_updated_data_store()
    return dumps(timefinish)

@APP.route("/standup/active/v1", methods=['GET'])
def active_standup():
    data = request.args.to_dict()
    standup_info = standup_active(data['token'],int(data['channel_id']))
    save_updated_data_store()
    return dumps(standup_info)

@APP.route("/standup/send/v1", methods=['POST'])
def send_standup():
    data = request.get_json()
    standup_send(data['token'], data['channel_id'],data['message'])
    return dumps({})

@APP.route("/message/pin/v1", methods=['POST'])
def pin_the_message():
    data = request.get_json()
    message_pin(data['token'], data['message_id'])
    save_updated_data_store()
    return dumps({})

@APP.route("/message/unpin/v1", methods=['POST'])
def unpin_the_message():
    data = request.get_json()
    message_unpin(data['token'], data['message_id'])
    save_updated_data_store()
    return dumps({})

@APP.route("/message/sendlater/v1", methods=['POST'])
def send_later_message():
    data = request.get_json()
    message_id_dict = message_sendlater(data['token'], data['channel_id'], data['message'], data['time_sent'])
    save_updated_data_store()
    return dumps(message_id_dict)

@APP.route("/message/sendlaterdm/v1", methods=['POST'])
def send_laterdm_message():
    data = request.get_json()
    message_id_dict = message_sendlaterdm(data['token'], data['dm_id'], data['message'], data['time_sent'])
    save_updated_data_store()
    return dumps(message_id_dict)

@APP.route("/user/stats/v1", methods=['GET'])
def print_user_stats():
    data = request.args.to_dict()
    user = user_stats(data['token'])
    save_updated_data_store()
    return dumps(user)

@APP.route("/users/stats/v1", methods=['GET'])
def print_users_stats():
    data = request.args.to_dict()
    users = users_stats(data['token'])
    save_updated_data_store()
    return dumps(users)

@APP.route("/search/v1", methods=['GET'])
def search_string():
    data = request.args.to_dict()
    messages = search(data['token'], data['query_str'])
    save_updated_data_store()
    return dumps(messages)

@APP.route("/notifications/get/v1", methods=['GET'])
def print_notification():
    data = request.args.to_dict()
    notifications = notifications_get(data['token'])
    save_updated_data_store()
    return dumps(notifications)
#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port


