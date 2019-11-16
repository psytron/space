

import sys
import os
#print('os.getcwd: '+ os.getcwd() )
#print("SYS PATH: "+ str( sys.path) )
sys.path.append(os.getcwd())

#
#from core.models import Node
#from core.models import Link

import datetime

from decimal import *
getcontext().prec = 8



class Entity():
    key=''
    secret=''
    agenda=[]

    def __init__(self , *args , **kwargs):
        self.key = kwargs.get('key','default')
        self.secret = kwargs.get('secret','default')
        self.account_id = kwargs.get('account_id','default')
        self.passphrase = kwargs.get('passphrase','default')
        self.password = kwargs.get('password','default')

    def getAgenda(self):
        return self.agenda