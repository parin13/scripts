import sys, os 
import json
import requests
import datetime
import dateutil.relativedelta

payload = {"jsonrpc":1,"id":"curltext"}
btc_prefix = 'http://uname:password@localhost:8332/'

def exception_trace(sys, e):  
    exc_type, exc_obj, exc_tb = sys.exc_info()  
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]  
    return "%s || %s || %s || %s" %(exc_type, fname, exc_tb.tb_lineno,e)  


def get_block_hash(block_no):
    try:
        payload['method'] = 'getblockhash'
        payload['params'] = [int(block_no)]
        response = requests.post(btc_prefix,data=json.dumps(payload))        
        if response.status_code == 200:
            result = json.loads(response.text)
            return result['result']
    except Exception as e:
        print (exception_trace(sys,e))
    

def get_block_by_hash(block_hash):
    try:
        payload['method'] = 'getblock'
        payload['params'] = [block_hash]
        response = requests.post(btc_prefix,data=json.dumps(payload))
        if response.status_code == 200:
            result = json.loads(response.text)
            return result['result']
    except Exception as e:
        print (exception_trace(sys,e))

def get_raw_transaction(txid):
    try:
        payload['method'] = 'getrawtransaction'
        payload['params'] = [txid,1]
        response = requests.post(btc_prefix,data=json.dumps(payload))
        if response.status_code == 200:
            result = json.loads(response.text)
            return result['result']        
    except Exception as e:
        print (exception_trace(sys,e))



def calculate_bdd(in_time,out_time,value):
    try:
        in_date = datetime.datetime.fromtimestamp(in_time)
        out_date = datetime.datetime.fromtimestamp(out_time)
        day_diff = (out_date-in_date).days
        bdd = float(day_diff*value)
        if bdd > 0:
            print('days : {} value: {}'.format(str(day_diff),str(value)))
        return bdd

    except Exception as e:
        print (exception_trace(sys,e))



def crawler():
    try:        
        start_block = 230005
        end_block = 1500000
        while end_block > start_block:
            bdd_in_a_block = 0
            block_hash = get_block_hash(start_block)
            block = get_block_by_hash(block_hash)
            for transaction in block.get('tx'):
                tx_details = get_raw_transaction(transaction)
                btc_out_time = int(tx_details.get('time'))
                vins = tx_details['vin']
                for vin in vins:
                    vinTxid = vin.get('txid', 'na')
                    if not vinTxid == 'na':
                        vout_index = int(vin.get('vout'))
                        vinTxInfo = get_raw_transaction(vinTxid)
                        early_vout = vinTxInfo.get('vout')[vout_index]
                        value = float(early_vout.get('value'))
                        btc_in_time = int(vinTxInfo.get('time'))
                        bdd = calculate_bdd(btc_in_time,btc_out_time,value)
                        bdd_in_a_block = bdd_in_a_block + bdd
                
            print('bdd in block : {} is : {} '.format(str(start_block),str(bdd_in_a_block)))
            start_block = start_block + 1

    except Exception as e:
        print (exception_trace(sys,e))



if __name__ == "__main__":
    crawler()
