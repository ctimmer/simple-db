#

from microdot import Microdot
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
        }
    }

GET_SCALAR_PARAMETERS = [
    "file_path" ,
    "limit" ,
    "row_data" ,
    "table_name"
    ]
GET_ARRAY_PARAMETERS = [
    "end_key" ,
    "key" ,
    "pk" ,
    "start_key"
    ]
class GetRequest :
    def __init__ (self) :
        self.json = None
        self.scalar_parameters = GET_SCALAR_PARAMETERS
        self.array_parameters = GET_ARRAY_PARAMETERS
    def set_json (self, json_dict) :
        self.json = json_dict
get_request = GetRequest ()
        
class SimpleDBServer :
    def __init__ (self ,
                    db_file_name = "test.db" ,
                    host = '0.0.0.0' ,  # Listen on all available interfaces
                    port = 8080) :
        ## Set up database methods
        self.db = SimpleDB (db_file_name)
        for _, (method_id, method_data) in enumerate (METHODS.items ()) :
            if method_data ["allowed"] :
                method_data["method"] = getattr (self.db, method_id, None)

        ## Set up server
        self.host = host
        self.port = port
        self.rpc_request = None
        self.http_error = None
        self.rpc_reply = None

    def process_post_request (self, request) :
        self.rpc_reply = {
            "jsonrpc" : "2.0" ,
            "id" : None 
            }
        self.http_error = None
        self.process_message (request)
        if self.http_error is not None :
            return self.http_error
        return self.rpc_reply

    def process_message (self, request) :
        #print ("process_message:")
        db_call = None
        try :
            self.rpc_dict = request.json
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
        method_data = METHODS [self.rpc_dict["method"]]
        if not method_data ["allowed"] :
            self.rpc_error (RPC_METHOD_ERROR)        # method not allowed
            return
        if "limit" in self.rpc_dict["params"] :
            if "limit_max" in method_data :
                if self.rpc_dict["params"]["limit"] > method_data["limit_max"] :
                    ## adjust limit maximum
                    self.rpc_dict["params"]["limit"] = method_data["limit_max"]
        #print ("rpc: params", self.rpc_dict["params"])
        try :
            db_call = METHODS [self.rpc_dict["method"]]["method"] (**self.rpc_dict["params"])
        except Exception as e :
            self.rpc_error_message (RPC_DB_CALL_ERROR, str(e))
            return
        self.rpc_reply ["result"] = db_call

    def process_get_request (self, request) :
        request_json = {
            "jsonrpc" : "2.0" ,
            "params" : {}}
        ## conver to rpc parameters
        val = request.args.get ("method")
        if val is not None :
            request_json["method"] = val
        val = request.args.get ("id")
        if val is not None :
            request_json["id"] = val
        for id in get_request.scalar_parameters : #GET_SCALAR_PARAMETERS :
            val = request.args.get (id) # None = id missing
            #print (id, val)
            if val is not None :
                request_json["params"][id] = str (val)
        for id in get_request.array_parameters : #GET_ARRAY_PARAMETERS :
            val = request.args.getlist(id) # always returns array
            #print (id, val)
            if len (val) > 0 :
                request_json["params"][id] = val
        #print ("get:", request_json)
        get_request.set_json (request_json)
        get_reply = db.process_post_request (get_request)
        #print ("reply:", get_reply)
        return json.dumps (get_reply)
        
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

    def return_http_error (self, error_number) :
        print ("return_http_error:", error_number)

    ## Shut down server and database
    def shutdown (self) :
        print ("Stopping Server")
        self.db.close ()         # database

################################################################################

db = SimpleDBServer ()

app = Microdot()

@app.route('/', methods=["GET"])
async def simple_db_get (request):
    return db.process_get_request (request)

@app.route('/', methods=['POST'])
async def simple_db_post (request):
    #print ("simple_db_post")
    reply = db.process_post_request (request)
    #print ("simple_db_post: reply:", reply)
    return reply

app.run(port = 8080)
