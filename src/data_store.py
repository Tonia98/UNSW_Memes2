'''
data_store.py

This contains a definition for a Datastore class which you should use to store your data.
You don't need to understand how it works at this point, just how to use it :)

The data_store variable is global, meaning that so long as you import it into any
python file in src, you can access its contents.

Example usage:

    from data_store import data_store

    store = data_store.get()
    print(store) # Prints { 'names': ['Nick', 'Emily', 'Hayden', 'Rob'] }

    names = store['names']

    names.remove('Rob')
    names.append('Jake')
    names.sort()

    print(store) # Prints { 'names': ['Emily', 'Hayden', 'Jake', 'Nick'] }
    data_store.set(store)
'''

## YOU SHOULD MODIFY THIS OBJECT BELOW
initial_object = {
    'users': [],
    'removed_users': [],
    'channels': [],
    'dms': [],
    'message_id_tracker': 1,
    'session_id_tracker': 1,
    'user_id_tracker': 1,
    'dm_id_tracker': 1,
    'workspace_stats': {}
}

## YOU SHOULD MODIFY THIS OBJECT ABOVE
'''
'users': [
    {
        'user_id': 1,
          'email': 'bob@gmail.com',
          'password': 'abc123',
          'name_first': 'Bob',
          'name_last': 'Smith',
          'handle': 'bobsmith',
          'permission': 1,
          'session_ids': [1, 2],
          'profile_img_url': url+'static/image.jpg',
          "user_stats": {
            "channels_joined": [
                {
                    "num_channels_joined": value (int)
                    "time_stamp": value (int)
                }
            ],
            "dms_joined": [
                {
                    "num_dms_joined": value (int),
                    "time_stamp": value (int)
                }
            ],
            "messages_sent": [
                {
                    "num_messages_sent": value (int),
                    "time_stamp": value (int)
                }
            ]
        },
        'notifications': [
            {
                'channel_id': value(int)
                'dm_id': value(int)
                'notification_message': message(string)
            }
        ]

    },
    {
        'user_id': 2,
          'email': 'amy@gmail.com',
          'password': 'abc123',
          'name_first': 'Amy',
          'name_last': 'Smith',
          'handle': 'amysmith',
          'permission': 2,
          'session_ids': [3],
          'profile_img_url': url+'static/image1.jpg',
          "user_stats": {
            "channels_joined": [
                {
                    "num_channels_joined": value (int)
                    "time_stamp": value (int)
                }
            ],
            "dms_joined": [
                {
                    "num_dms_joined": value (int),
                    "time_stamp": value (int)
                }
            ],
            "messages_sent": [
                {
                    "num_messages_sent": value (int),
                    "time_stamp": value (int)
                }
            ]
        }
    }
]
'''
'''
'removed_users': [
    {
        'user_id': 2,
          'email': 'amy@gmail.com',
          'password': 'abc123',
          'name_first': 'Removed',
          'name_last': 'user',
          'handle': 'amysmith',
          'permission': 1,
          'session_ids': [],
          'profile_img_url': url+'static/image.jpg',
          "user_stats": {
            "channels_joined": [
                {
                    "num_channels_joined": value (int)
                    "time_stamp": value (int)
                }
            ],
            "dms_joined": [
                {
                    "num_dms_joined": value (int),
                    "time_stamp": value (int)
                }
            ],
            "messages_sent": [
                {
                    "num_messages_sent": value (int),
                    "time_stamp": value (int)
                }
            ]
        }
    },
]
'''
'''
'channels': [
    {
        'channel_id': 1,
        'channel_name': 'Snake',
        'owner_members': [1],
        'all_members': [1],
        'messages': [
            {
                'message_id': 1,
                'u_id': 1,
                'message': 'Hello world',
                'time_created': 1582426789,
                'is_pinned': False
            }
        ],
        'standups': amysmith: aha
        ,
        'is_active':True,
        'time_finish':1582426789
        'is_public': True,
    },
    {
        'channel_id': 2,
        'channel_name': 'Tetris',
        'owner_members': [1],
        'all_members': [1, 2, 3],
        'messages': [
            {
                'message_id': 2,
                'u_id': 1,
                'message': 'Hello world',
                'time_created': 1582426789,
                'reacts':{
                    'react_id': 1,
                    'u_ids':[1]
                }
            }
            {
                'message_id': 3,
                'u_id': 3,
                'message': 'Hello there',
                'time_created': 1543622400,
                'is_pinned': False
            }
        ],
        'is_active':False,
        'time_finish':None
        'is_public': False,
    }
]
'''
'''
'dms': [
    {
        'dm_id': 1,
        'dm_name': 'bobsmith, amysmith'
        'creator': 1,
        'members': [1, 2],
        'messages': [
            {
                'message_id': 2,
                'u_id': 1,
                'message': 'Hello world',
                'time_created': 1582426789,
                'reacts':{
                    'react_id': 1,
                    'u_ids':[1]
                }
            }
        ],
    },
    {
        'dm_id': 2,
        'dm_name': 'bobsmith, amysmith, johnsmith'
        'creator': 1,
        'members': [1, 2, 3],
        'messages': [
            {
                'message_id': 2,
                'u_id': 1,
                'message': 'Hello world',
                'time_created': 1582426789,
                'reacts':{
                    'react_id': 1,
                    'u_ids':[1]
                }
            },
            {
                'message_id': 2,
                'u_id': 1,
                'message': 'Hello world',
                'time_created': 1582426789,
                'reacts':{
                    'react_id': 1,
                    'u_ids':[1]
                }
            }
        ],
    },
]
"workspace_stats": {
    "channels_exist": [
        {
            "num_channels_exist": value (int),
            "time_stamp": value (int)
        }
    ],
    "dms_exist": [
        {
            "num_dms_exist": value (int),
            "time_stamp": value (int)
        }
    ],
    "messages_exist": [
        {
            "num_messages_exist": value (int),
            "time_stamp": value (int)
        }
    ]
},
'''


class Datastore:
    def __init__(self):
        self.__store = initial_object

    def get(self):
        return self.__store

    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')
        self.__store = store

print('Loading Datastore...')

global data_store
data_store = Datastore()

