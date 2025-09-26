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

from microdot import Microdot

from simple_db_server import SimpleDBServer

GET_SCALAR_PARAMETERS = [
    "epoch_seconds" ,
    "file_path" ,
    "limit" ,
    "row_data" ,
    "table_name"
    ]
GET_ARRAY_PARAMETERS = [
    "end_key" ,
    "key" ,
    "pk" ,
    "column_list" ,
    "start_key"
    ]

################################################################################

db = SimpleDBServer ()
db.load ('financial_dump.txt')
app = Microdot()

@app.route('/', methods=["GET"])
async def simple_db_get (request):
    #print ("simple_db_microdot_get")
    request_json = {
        "jsonrpc" : "2.0" ,
        "params" : {}}
    ## convert get parameters to rpc parameters
    val = request.args.get ("method")
    if val is not None :
        request_json["method"] = val
    val = request.args.get ("id")
    if val is not None :
        request_json["id"] = val
    for id in GET_SCALAR_PARAMETERS :
        val = request.args.get (id) # None = id missing
        if val is not None :
            request_json["params"][id] = str (val)
    for id in GET_ARRAY_PARAMETERS :
        val = request.args.getlist(id) # always returns array
        if len (val) > 0 :
            request_json["params"][id] = val
    reply = db.process_request (json.dumps (request_json))
    #print ("simple_db_microdot_get: reply:", reply)
    return reply

@app.route('/', methods=['POST'])
async def simple_db_post (request):
    #print ("simple_db_microdot_post")
    reply = db.process_request (request.body)
    #print ("simple_db_microdot_post: reply:", reply)
    return reply

app.run(port = 8080)
