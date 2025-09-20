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

import json

from simple_db import SimpleDB, simpledb_available

'''
-32700	Parse error	Invalid JSON was received by the server.
An error occurred on the server while parsing the JSON text.
-32600	Invalid Request	The JSON sent is not a valid Request object.
-32601	Method not found	The method does not exist / is not available.
-32602	Invalid params	Invalid method parameter(s).
-32603	Internal error	Internal JSON-RPC error.
-32000 to -32099	Server error	Reserved for implementation-defined server-errors.
'''

RPC_GENERIC_ERROR = -32000
RPC_DB_CALL_ERROR = -32001
RPC_METHOD_ERROR = -32601
RPC_PARSE_ERROR = -32700
RPC_REQUEST_ERROR = -32600
RPC_PARAMETER_ERROR = -32602
RPC_INTERNAL_ERROR = -32603
RPC_ERRORS = {
    RPC_METHOD_ERROR : "Method not found" ,
    RPC_PARSE_ERROR : "Parse error" ,
    RPC_REQUEST_ERROR : "Invalid request" ,
    RPC_PARAMETER_ERROR : "Invalid method parameter(s)" ,
    RPC_INTERNAL_ERROR : "Internal JSON-RPC error" ,
    RPC_GENERIC_ERROR : "Unknown Error" ,
    RPC_DB_CALL_ERROR : "SimpleDB client call error"
    }

READ_ONLY = False
METHODS = {
    "write_row" : {
        "allowed" : not READ_ONLY ,
        "method" : None
        } ,
    "rewrite_row" : {
        "allowed" : not READ_ONLY ,
        "method" : None
        } ,
    "row_exists" : {
        "allowed" : True ,
        "method" : None
        } ,
    "read_row" : {
        "allowed" : True ,
        "method" : None
        } ,
    "next_row" : {
        "allowed" : True ,
        "method" : None
        } ,
    "get_table_keys" : {
        "allowed" : True ,
        "limit_max" : 500 ,
        "method" : None
        } ,
    "get_table_rows" : {
        "allowed" : True ,
        "limit_max" : 200 ,
        "method" : None
        } ,
    "get_table_items" : {
        "allowed" : True ,
        "limit_max" : 100 ,
        "method" : None
        } ,
    "delete_row" : {
        "allowed" : not READ_ONLY ,
        "method" : None
        } ,
    "commit" : {
        "allowed" : True ,
        "method" : None
        } ,
    "dump_all" : {
        "allowed" : True ,
        "method" : None
        } ,
    "load" : {
        "allowed" : False ,
        "method" : None
        }
    }
        
class SimpleDBServer :
    def __init__ (self ,
                    db_file_name = "test.db") :
        ## Set up database methods
        self.db = SimpleDB (db_file_name)
        for _, (method_id, method_data) in enumerate (METHODS.items ()) :
            if method_data ["allowed"] :
                method_data["method"] = getattr (self.db, method_id, None)

        ## Set up server
        self.rpc_reply = None

    def process_request (self, rpc_request) :
        #print ("process_request:", rpc_request)
        self.rpc_reply = {
            "jsonrpc" : "2.0" ,
            "id" : None 
            }
        self.process_message (rpc_request)
        return self.rpc_reply

    def process_message (self, rpc_request) :
        db_call = None
        try :
            self.rpc_dict = json.loads (rpc_request)
        except :
            self.rpc_error (RPC_PARSE_ERROR)
            return None
        ## test for valid json rpc message
        if "jsonrpc" not in self.rpc_dict \
        or "method" not in self.rpc_dict \
        or "params" not in self.rpc_dict :
            self.rpc_error (RPC_REQUEST_ERROR)
            return None
        if "id" in self.rpc_dict :
            self.rpc_reply ["id"] = self.rpc_dict ["id"] # don't care about "id"
        if self.rpc_dict["method"] not in METHODS :
            self.rpc_error (RPC_METHOD_ERROR)        # Not a valid method
            return
        ## Test for valid/allowed method
        method_data = METHODS [self.rpc_dict["method"]]
        if not method_data ["allowed"] :
            self.rpc_error (RPC_METHOD_ERROR)        # method not allowed
            return
        '''
        # Old
        if "limit" in self.rpc_dict["params"] :
            if "limit_max" in method_data :
                if self.rpc_dict["params"]["limit"] > method_data["limit_max"] :
                    ## adjust limit maximum
                    self.rpc_dict["params"]["limit"] = method_data["limit_max"]
        '''
        # New
        if "limit_max" in method_data :
            if "limit" in self.rpc_dict["params"] :
                if self.rpc_dict["params"]["limit"] > method_data["limit_max"] :
                    self.rpc_dict["params"]["limit"] = method_data["limit_max"]
            else :
                self.rpc_dict["params"]["limit"] = method_data["limit_max"]
        #print ("rpc: params", self.rpc_dict["params"])
        try :
            ## simple db function call
            db_call = METHODS [self.rpc_dict["method"]]["method"] (**self.rpc_dict["params"])
        except Exception as e :
            self.rpc_error_message (RPC_DB_CALL_ERROR, str(e))
            return
        self.rpc_reply ["result"] = db_call   # reply message
        
    def rpc_error_message (self, error_number, error_message) :
        message_save = RPC_ERRORS [error_number]
        RPC_ERRORS [error_number] = error_message
        self.rpc_error (error_number)
        RPC_ERRORS [error_number] = message_save
    def rpc_error (self, error_number) :
        #print ("rpc_error:", error_number)
        self.rpc_reply ["error"] = {
            "code" : error_number ,
            "message" : RPC_ERRORS [error_number]
            }

    ## Shut down server and database
    def shutdown (self) :
        print ("Stopping Server")
        self.db.close ()         # database
