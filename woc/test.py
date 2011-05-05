from woc import Text2List, _unhtmlify

print _unhtmlify("Say <strong>Hi</strong> to this <br />")
print Text2List("Peter Bengtsson, change this (word)")