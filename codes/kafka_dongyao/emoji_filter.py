import emoji
import copy


# Input a tweet message in dictionary format
# Grab emojis from 'text'
# Number of emojis we got is the number of message dics we are creating
# Assgin each emoji to each message dic with key='emoji'
# Return the list of this message dics
def parse_emoji_and_divide_into_seperate_messages(message_dic):

	emojis = extract_emojis(message_dic['text'])
	if len(emojis) > 0:
		list_of_message_dic = []
		for emoji in emojis:
			new_message = copy.deepcopy(message_dic)
			new_message['emoji'] = emoji
			list_of_message_dic.append(new_message)
		return list_of_message_dic
	else:
		return []


# Grab emojis from a string
# And store the into a list
def extract_emojis(str):
	
	emojis = []
	for c in str:
		if c in emoji.UNICODE_EMOJI:
			emojis.append(c)
	return emojis

