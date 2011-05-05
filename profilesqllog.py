#!/usr/bin/python
import os, sys



zopehome = '/home/peterbe/zope272'
logfilepath = os.path.join(zopehome, 'var', 'SQLProfiling-Peterbe.log')
if not os.path.exists(logfilepath):
    raise "NoLogFile", "Log file does not exist"


try:
    from DocumentTemplate.sequence import sort
except ImportError:
    libhome = os.path.join(zopehome, 'lib','python')
    libhome = '/usr/lib/zope-2.7.2/lib/python'
    sys.path.insert(1, libhome)
    from DocumentTemplate.sequence import sort



out='''What do you want to know?

  1) Slowest performer
  2) Most common
  3) Total cumulative time
'''
print out.rstrip()
whattodo = raw_input()
try:
    whattodo = int(whattodo)
except ValueError:
    raise "Exit"


LIMIT = 50

logfile = open(logfilepath)


class SQLCall:
    def __init__(self, name, time, count):
	self.name=name
	assert type(time)==type(0.1)
	self.time=time
	self.count=count
	
    def __str__(self):
	t=round(self.time, 4)
	return "%s\t%s\t%s"%(str(t), self.count, self.name)
						
class SQLCallCount:
    def __init__(self, name, count):
	self.name=name
	assert type(count)==type(4)
	self.count=count
	
    def __str__(self):
	return "%s\t%s"%(self.count, self.name)
    
    
def sum(sequence):
    return reduce(lambda x,y: x+y, sequence)


if whattodo == 1:
    
    all = {}
    for line in logfile.readlines():
	if not line:
	    continue
	name, time = line.split('|')
	time = float(time)
	
	if all.has_key(name):
	    all[name].append(time)
	else:
	    all[name] = [time]
	
    
    
    all_calls = []
    for k, timeslist in all.items():
	average = sum(timeslist)/len(timeslist)
	all_calls.append(SQLCall(k, average, len(timeslist)))
	
    all_calls = sort(all_calls, (('time',),))
    all_calls.reverse()
    
    c=0
    for each in all_calls:
	print each
	c+=1
	if c> LIMIT:
	    print "...Only showing the first %s"%LIMIT
	    break
	
    
    
elif whattodo == 2:
    
    all = {}
    for line in logfile.readlines():
	if not line:
	    continue
	
	name, time = line.split('|')
	time = float(time)
	
	if all.has_key(name):
	    all[name] = all[name] + 1
	else:
	    all[name] = 1
	    
	    
    all_calls = []
    for k, v in all.items():
	all_calls.append(SQLCallCount(k, v))
	
    all_calls = sort(all_calls, (('count',),))
    all_calls.reverse()
    
    c=0
    for each in all_calls:
	print each
	c+=1
	if c>LIMIT:
	    print "...Only showing the first %s"%LIMIT
	    break
	
elif whattodo == 3:
    
    all = {}
    for line in logfile.readlines():
	if not line:
	    continue
	name, time = line.split('|')
	time = float(time)
	
	if all.has_key(name):
	    all[name].append(time)
	else:
	    all[name] = [time]
	
    
    def mystr__(self):
	return "%s\t%s"%(self.total, self.name)
    def roundup__(self):
	self.total = self.time*self.count

    SQLCall.__str__ = mystr__
    SQLCall.roundup = roundup__
    all_calls = []
    for k, timeslist in all.items():
	average = sum(timeslist)/len(timeslist)
	object = SQLCall(k, average, len(timeslist))
	object.roundup()
	all_calls.append(object)
	
    all_calls = sort(all_calls, (('total',),))
    all_calls.reverse()
    
    c=0
    for each in all_calls:
	print each
	c+=1
	if c> LIMIT:
	    print "...Only showing the first %s"%LIMIT
	    break
    