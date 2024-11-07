selected assumptions:
1. assume a user can log in as many times as he/she wants without log out (auth_log_in_v1)
2. assume channel_id and auth_user_id are positive integers (general)
3. assume 1 user can register as many accounts as he/she wants with differnet email address. (auth_register_v1)
4. assume start is positive integer (channel_message_v1)
5. assume if there is no channel being created, an empty list will be returned (channels_listall_v1)
6. assume global owner's id is 1 (channel_join_v1)

assumption for auth_log_in_v1 function:
  assume two users can not have the same email 
  assume a user can log in as many times as he/she wants without log out

assumption for auth_register_v1 function:
  assume 1 user can register as many accounts as he/she wants with differnet email address.
  assume 2 users can have the same password for their accounts

assumption for channels_create_v1 function:
  assume no channel can be an empty channel

assumption for channels_list_v1 function:
  assume if the authorised user is not part of any channels, an empty list will be returned.

assumption for channels_listall_v1 function:
  assume if there is no channel being created, an empty list will be returned

assumption for channel_join_v1 function:
  assume channel_id are positive integers
  assume global owner's id is 1

assumption for channel_invite_v1 function:
  assume auth_user_id are positive integers

assumption for channel_message_v1 function:
  assume there's no existing message in the list of dictionaries as there're no founctions to create message in the channel -- (1)
  base on (1), the return for 'messages' in the output dictionary will be a empty list
  base on (1), the return value for 'end' in the output dictionary will always be -1


assumption for clear_v1 function
  assume the input of the function is always correct e.g. will not put extra variable in the function bracket 
  the return of this function will always be a empty dictionary only
  assume there's only 'users' and 'channels' in data_store that needs to be reset into initial stage

