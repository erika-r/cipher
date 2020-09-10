#IDEA splitting english_quadgrams file
#splitting the main loop into teo threads

import quadgrams_score as qs
import time,random,string
from copy import deepcopy
import sys,os	#used to create and write to file
import concurrent.futures
from queue import Queue

start = time.perf_counter()

#this will determine the text's closeness to comprehensive english
#this makes the dictionary of scores which we will compare the text to later
fitness = qs.quadgrams_score("english_quadgrams.txt")

#get original text from file and list of all capitals so they can be capitalised later
input_file = sys.argv[1]	#encrypted text file
with open(input_file) as holder:
	original_txt = holder.read().strip()
	lower_original = original_txt.lower()       #will be used to decrypt later 
	capitals = [index for index,letter in enumerate(original_txt) if letter.isupper()]

#get rid of all punctuation,spaces, and newlines
lower_no_punc = original_txt.lower()
for letter in set(lower_no_punc):
	if not letter.isalpha():
		lower_no_punc = lower_no_punc.replace(letter,"")
	if letter in (string.punctuation + " \n"):
		lower_no_punc = lower_no_punc.replace(letter,"")

def capitalize(text):
	text = list(text)
	for i in capitals:
		text[i] = text[i].upper()
	return "".join(text)

def decrypt(txt,active_key):
	active_key = "".join(active_key)
	table = str.maketrans(active_key,"etaoinsrhdlucmfywgpbvkxqjz")		#string.ascii_uppercase)
	text = txt.translate(table)
	return text

def frequency(text):
	frq = list("etaoinsrhdlucmfywgpbvkxqjz")

	dct = {}
	for letter in set(text):	#no repetition
		dct[letter] = text.count(letter)
	
	dct = {key: val for key, val in sorted(dct.items(), reverse=True,key=lambda item: item[1])}
	txt_frq = [key for key in dct]		#list of letters in filetxt sorted by frequencies
	
	for letter in string.ascii_lowercase:
		if letter not in txt_frq:
			txt_frq.append(letter)

	return txt_frq

def loop(lower_no_punc,max_key,max_score):
	
	print("in loop")
	
	parent_key = max_key[:]
	parent_score = max_score

	for i in range(5):		#run min 3 * 2500 times
		random.shuffle(parent_key)			#attempting to avoid the local maxima by deliberately starting at a completely different point
		dec = decrypt(lower_no_punc,parent_key)
		parent_score = fitness.get_score(dec)

		reset = 0
		while reset < 500:
			a = random.randint(0,25)
			b = random.randint(0,25)
			child_key = parent_key[:]		#randomly swap 2 letters of the key
			child_key[a],child_key[b] = child_key[b],child_key[a]
			child_score = fitness.get_score(decrypt(lower_no_punc,child_key))		#get key of newly decrypted text

			if child_score > parent_score:			#set new best key 
				parent_score = child_score
				parent_key = child_key[:]
				reset = 0				#reset counter, later frequency of the child score being higher than the parent score will decrease so counter will not be reset
			reset += 1

		if max_score < parent_score:		#reset new maximum
			max_score = parent_score
			max_key = parent_key[:]
	
	return [max_score,max_key]

def main():
	
	max_key = frequency(lower_no_punc)
	max_score = fitness.get_score(decrypt(lower_no_punc,max_key))

	#get return values from threads
	with concurrent.futures.ThreadPoolExecutor() as executor:
		t1 = executor.submit(loop,lower_no_punc,max_key,max_score)
		t2 = executor.submit(loop,lower_no_punc,max_key,max_score)
		t1_result = t1.result()
		t2_result = t2.result()

	#choose better key
	if t1_result[0] > t2_result[0]:
		max_key = t1_result[1]
	else:
		max_key = t2_result[1]

	#create and write to file
	output = "{}-decrypted.txt".format(input_file[:-4])		#get rid of the .txt
	os.system("touch {}".format(output))	
	f = open(output, "w+")
	f.write(capitalize(decrypt(lower_original,max_key)))
	finish = time.perf_counter()
	print("time taken: {} seconds".format(finish-start))

if __name__ == "__main__":
	main()