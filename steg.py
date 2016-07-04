import cv2
import numpy as np
import sys

def setLastBit(v, x):
	""" Sets the last bit of v to x 

	Modified from http://stackoverflow.com/questions/12173774/
	modify-bits-in-an-integer-in-python """
	v &= ~1
	if x:
		v |= 1
	return v

def imgToNP(img):
	""" Converts an input image to a BGR Numpy nd-array """
	im = cv2.imread(img, 1)
	if im is None:
		raise Exception('Input image does not exist')
	return im

def msgToVec(msg):
	""" Converts msg into a bitvector that represents the
	message in ASCII

	Could definitely save memory by not using ints for each 1 and 0 """

	assert type(msg) is str

	# Make len(msg) a multiple of 4 by adding spaces to the end
	msg = msg + (' ' * (4 - (len(msg) % 4)))

	asciiArr = np.array([ord(i) for i in msg])

	return asciiArr

	#this is to try and compress 4 ints into 1 since only the last 8 bits
	#matter
	# mask = 255 # last 8 bits are 1, first 24 bits are 0

	# for i in range(0, )

def encode(img, msg):
	""" Encodes msg in img """
	assert type(msg) is str

	im = imgToNP(img)
	h, w, c = np.shape(im)
	im = np.ravel(im)

	asciiArr = [ord(i) for i in msg]

	# Write the length of the message to the first 32 bits
	msgLen = min(len(msg) * 8, len(im) - 32)
	for i in range(32):
		bit = msgLen & (1 << (31 - i))
		im[i] = setLastBit(im[i], bit)

	imPos = 32
	for i in asciiArr:
		for j in xrange(7, -1, -1):
			bit = i & (1 << j)
			try:
				im[imPos] = setLastBit(im[imPos], bit)
			except:
				print('Image too small to write entire message')
				print('Returning truncated version\n')
				im = im.reshape(h, w, c)
				cv2.imwrite('encode_' + img, im)
				return
			imPos += 1

	im = im.reshape(h, w, c)
	cv2.imwrite('encode_' + img, im)

def bitsToInt(arr):
	""" Converts the 8 1s or 0s in arrs into a single int """
	assert len(arr) == 8

	# Indexing is weird because bit pos indices goes 32 -> 0 and
	# arrs goes 0 -> 7 
	res = 0
	for i in range(7, -1, -1):
		res |= (arr[7-i]) << i
	return res

def decode(img):
	""" Decodes the message contained in img """

	im = imgToNP(img)

	# 1 x n array of the last bits of im
	im = np.ravel(im) & 1
	# Grab the message length and then remove it from im
	msgLen = 0
	for i in range(31, -1, -1):
		msgLen |= im[31-i] << i
	im = im[32:msgLen+31]
	# Make im have a length that's a multiple of 8 by adding 0s
	im = np.append(im, [0] * (8 - (len(im) % 8)))
	# Now break it into chunks of 8
	im = im.reshape((len(im) / 8, 8))

	res = [bitsToInt(i) for i in im]
	res = [chr(i) for i in res]
	return ''.join(res).strip()

if __name__ == '__main__':
	# TODO: Add command line arguments?

	action = sys.argv[1]
	if action != 'e' and action != 'd':
		print('Invalid action specified, must be encode (e) or decode (d)')
	else:
		img = raw_input("Enter your image name: ")

		if action == 'e':
			txt = raw_input("Enter your text file name: ")
			with open(txt, 'r') as f:
				encode(img, f.read())
		else:
			print(decode(img))


	# encode('black_small.png', 'hi')
	# print decode('encode_black_small.png')
	# with open('text.txt', 'r') as f:
	# 	txt = f.read()
	# #print txt
	# encode('xkcd.png', txt)
	# a = decode('encode_xkcd.png')
	# print a
