from src.data_store import data_store
import requests 
import json
from src.config import url
import os

def clear():

    '''
    Reset all data in data_store to initial stage
    
    Arguments:
        No input required
    
    Return Value:
        Returns an empty dictionary
    '''
    store = data_store.get()
    store['users'].clear()
    store['channels'].clear()
    store['dms'].clear()
    store['workspace_stats'].clear()
    store['removed_users'].clear()
    store['message_id_tracker'] = 1
    store['session_id_tracker'] = 1
    store['user_id_tracker'] = 1
    store['dm_id_tracker'] = 1
    data_store.set(store)
    
    for f in os.listdir('src/static'):
        if f != 'image.jpg':
            os.remove(os.path.join('src/static', f))
    
    return {}
