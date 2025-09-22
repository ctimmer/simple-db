#
################################################################################
# The MIT License (MIT)
#
# Copyright (c) 2025 Curt Timmerman
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
################################################################################
#
## SimpleDBClient
#
# Notes:
#   o 
#
################################################################################

import requests
import json

class SimpleDBClient :
    def __init__ (self, hostname = "localhost", port = 8080) :
        self.id = 0
        self.url = "http://" + hostname + ":" + str (port)
        self.post_headers = {'Content-Type': 'application/json'}

    ## writes/rewrites table row from row_data
    def write_row (self,table_name,pk,row_data) :
        #print ("w_r:", table_name,pk)
        request_dict = {
            "table_name" : table_name ,
            "pk" : pk ,
            "row_data" : row_data
            }
        return self.send_rpc_request ("write_row", request_dict)
    ## rewrites updated table row from update_data
    def rewrite_row (self,table_name,key,update_data) :
        #print ("w_r:", table_name,pk)
        request_dict = {
            "table_name" : table_name ,
            "key" : key ,
            "update_data" : update_data
            }
        return self.send_rpc_request ("rewrite_row", request_dict)

    ## read row from table/key, returns None if not found
    def read_row (self,table_name,key) :
        request_dict = {
            "table_name" : table_name ,
            "key" : key
            }
        return self.send_rpc_request ("read_row", request_dict)

    ## read next table indexed row, or first row if key is not provided
    def first_row (self,table_name,key = "") :
        request_dict = {
            "table_name" : table_name ,
            "key" : key
            }
        reply = self.send_rpc_request ("first_row", request_dict)
        return (reply)

    ## read next table indexed row, or first row if key is not provided
    def next_row (self,table_name,key = "") :
        request_dict = {
            "table_name" : table_name ,
            "key" : key
            }
        reply = self.send_rpc_request ("next_row", request_dict)
        return (reply)

    ## Return True if this key is in table_name
    def row_exists (self,table_name,key) :
        request_dict = {
            "table_name" : table_name ,
            "key" : key
            }
        return self.send_rpc_request ("row_exists", request_dict)
    ## Delete row from table
    def delete_row (self,table_name,key) :
        request_dict = {
            "table_name" : table_name ,
            "key" : key
            }
        return self.send_rpc_request ("delete_row", request_dict)
    ## Returns list of keys in table
    def get_table_keys (self,table_name,start_key=None,end_key=None,limit=999999) :
        request_dict = {
            "table_name" : table_name ,
            "start_key" : start_key ,
            "end_key" : end_key ,
            "limit" : limit
            }
        return self.send_rpc_request ("get_table_keys", request_dict)

    ## Returns list of rows in a table
    def get_table_rows (self,table_name,start_key=None,end_key=None,limit=999999) :
        request_dict = {
            "table_name" : table_name ,
            "start_key" : start_key ,
            "end_key" : end_key ,
            "limit" : limit
            }
        return self.send_rpc_request ("get_table_rows", request_dict)

    ## Returns list of rows in a table
    def get_table_items (self,table_name,start_key=None,end_key=None,limit=999999) :
        request_dict = {
            "table_name" : table_name ,
            "start_key" : start_key ,
            "end_key" : end_key ,
            "limit" : limit
            }
        return self.send_rpc_request ("get_table_items", request_dict)

    ## dump_all
    def dump_all (self, file_path = "db_dump.txt") :
        request_dict = {
            "file_path" : file_path
            }
        return self.send_rpc_request ("dump_all", request_dict)
    ## load
    def load (self, file_path = "db_dump.txt") :
        request_dict = {
            "file_path" : file_path
            }
        return self.send_rpc_request ("load", request_dict)

    ## commit updates(s), if autocommit is not set
    def commit (self) :
        request_dict = {}
        return self.send_rpc_request ("commit", request_dict)

    def send_rpc_request (self, method, params) :
        self.id += 1
        rpc_dict = {
            "jsonrpc" : "2.0" ,
            "method" : method ,
            "params" : params ,
            "id" : str (self.id)
            }
        #print ("send_rpc: request:", self.url, rpc_dict)
        response = None
        try :
            response = requests.post (self.url,
                                        json = rpc_dict,
                                        headers = self.post_headers)
            #print ("send_rpc: reply:",response.json())
            reply = response.json ()
            if "result" in reply :
                return reply ["result"]
        except Exception as e :
            print ("req.post:", e)
        finally :
            if response is not None :
                response.close ()
        ## report error here
        return None

    def close (self) :
        pass

# end SimpleDBClient  #


def main () :
    import os
    #print (os.uname())
    my_db = SimpleDBClient ("127.0.0.1", 8080)
    #
    my_db.write_row ("customer", "customer_number" ,  {"customer_number" : "000100" ,
                                                        "name":"Curt" ,
                                                        "dob":19560606 ,
                                                        "occupation":"retired"})
    print ("rewrite:" ,
        my_db.rewrite_row ("customer", "000100" , {"location" : "Alaska"}))
    my_db.write_row ("customer", "customer_number", {"customer_number" : "000500" ,
                                            "name":"Moe" ,
                                            "dob":19200101 ,
                                            "occupation":"Three stooges"})
    my_db.write_row ("customer", "customer_number", {"customer_number" : "010000" ,
                                            "name":"Larry" ,
                                            "dob":19210202 ,
                                            "occupation":"Three stooges"})
    my_db.write_row ("customer", "customer_number", {"customer_number" : "001000" ,
                                            "name":"Curly" ,
                                            "dob":19250303 ,
                                            "occupation":"Three stooges"})
    my_db.write_row ("invoice",
                    "invoice_number" ,
                    {"invoice_number" : "090001" ,
                    "customer_number" : "001000"})
    my_db.write_row ("invoice_line",
                    ["invoice_number", "line_number"] ,
                    {"invoice_number" : "090001" ,
                    "line_number" : "0001" ,
                    "sku" : "Snake Oil" ,
                    "price" : "100.00"})
    my_db.write_row ("invoice_line",
                    ["invoice_number", "line_number"] ,
                    {"invoice_number" : "090001" ,
                    "line_number" : "0002" ,
                    "sku" : "Aspirin" ,
                    "price" : "12.00"})
    my_db.write_row ("log",
                    0 ,
                    ["20250903122010","Error","Log error"])
    my_db.write_row ("log",
                    0 ,
                    ["20250904141020","Warning", "Log warning"])
    #
    print ("good read:", my_db.read_row ("customer", "000100")) # Good key
    print ("bad read:", my_db.read_row ("customer", "000199")) # bad key
    print ("all keys:", my_db.get_table_keys ("customer"))
    print ("rows:", my_db.get_table_rows ("customer", "000500", "990000"))
    #
    my_db.get_table_items ("customer")

    row = my_db.next_row ("customer")
    while row is not None :
        print ("row:", row)
        row = my_db.next_row ("customer", row["customer_number"])
    #
    row = my_db.next_row ("log")
    while row is not None :
        print ("row:", row)
        row = my_db.next_row ("log", row[0])
    #
    row = my_db.next_row ("error_table")
    while row is not None :
        print ("row:", row)
        row = my_db.next_row ("log", row[0])
    #
    my_db.commit ()
    my_db.dump_all ()
    my_db.close ()

#----------------------------------------------------
if __name__ == "__main__" :
    main ()

