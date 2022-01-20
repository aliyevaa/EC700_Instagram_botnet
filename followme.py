from adb import adb
import os, argparse, time
from datetime import datetime
import xml.etree.ElementTree as ET

phone = adb()


def parse_layout():
        xml_string = phone.dump_layout()
        try:
            root = ET.fromstring(xml_string)
        except Exception as e:
            print("error reading layout: %s" % str(e))
            return None
        return root

def find_coordinates(root, attribute, text):
	for i in root.iter("node"):
		if i.attrib[attribute] and i.attrib[attribute] == text:
			bounds = i.get("bounds")
			a = bounds.split("[")
			x = int(a[1].split(",")[0])
			a = bounds.split("]")
			y = int(a[0].split(",")[1])
			return (x,y)
	return (-1, -1)

def follow_account(account):
	#press Seach and Explore to find the account
	root = parse_layout()
	if (root == None):
		return False
	if root:
		(x, y) = find_coordinates(root, "content-desc", "Search and Explore")
		if (x==-1 or y==-1):
			return False
		phone.tap(x,y)

	#press Search and enter account
	root = parse_layout()
	if (root == None):
		return False
	if root:
		(x, y) = find_coordinates(root, "text", "Search")
		if (x==-1 or y==-1):
                        return False			
		phone.tap(x,y)
		phone.input_text(account)
		phone.input_keyevent(66)	
			
	#select the account
	root = parse_layout()
	if (root == None):
		return False
	if root:
		(x, y) = find_coordinates(root, "text", account)
		if (x==-1 or y==-1):
			return False
		phone.tap(x,y)

	# follow the account
	root = parse_layout()
	if (root == None):
		return False
	if root:
		(x, y) = find_coordinates(root, "text", "Follow")
		if (x==-1 or y==-1):
			return False
		phone.tap(x,y)
		
	return True

def comment_on_photo(account, photo_n, comment):
	photo_n = int(photo_n)
	root = parse_layout()
	if (root == None):
		return False
	if root:
		#assuming 3*3
		column = photo_n % 3
		row = photo_n//3 + 1
		(x, y) = find_coordinates(root, "content-desc", "Photo by A. at Row %d, Column %d" % (row, column))
		phone.tap(x,y)
		time.sleep(1)	
	print("tapped on the photo")
	root = parse_layout()
	if (root == None):
		return False
	if root:
		(x, y) = find_coordinates(root, "content-desc", "Comment")
		if (x==-1 or y==-1):
			return False
		phone.tap(x,y)
		phone.input_text(comment)
	root = parse_layout()
	if (root == None):
		return False
	if root:
		(x, y) = find_coordinates(root, "resource-id", "com.instagram.android:id/layout_comment_thread_post_button")	
		if (x==-1 or y==-1):
			return False
		phone.tap(x,y)
		time.sleep(3)
	return True
	
if (__name__ == '__main__'):
	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--follow", help="An account to follow", required=True)  
	parser.add_argument("-p", "--photo_number", help="Photo to be commented")
	parser.add_argument("-c", "--comment", help="Comment to be posted") 
	args = vars(parser.parse_args())
	if phone.check_package("com.instagram.android"):
		if phone.check_if_off():
			print("Starting evil things")
			phone.unlock()
			phone.open("com.instagram.android")
			time.sleep(2)
			if (follow_account(args["follow"]) and comment_on_photo(args["follow"], args["photo_number"], args["comment"])):
				print("Success")
			else:
				print("try again")
			phone.close("com.instagram.android")
			phone.lock()	
		else:
			print("User can see the phone")
	else:
		print("Instagram is not installed")
