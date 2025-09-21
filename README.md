# simple-db - micropython relational DB using btree

## Internal Database Structure

Micropython's btree database only stores a simple ID/Value pair. Refer ti the dump_all example below.

 To simulate a database table with a primary key(s) the btree ID is built from the table name concatenated with 1 or more keys in the row data. In the 1st line below the table name is "customer" and the primary key is "000100" (customer_number). A "~" separates the primary key from the row data.

 The row data can be in 2 formats, json object or array.

The 1st line below was created with the following calls (json object):

```
my_db.write_row ("customer", # table_name
                "customer_number" , # primary key in object
                {"customer_number" : "000100" , # row data
                    "name":"Curt" ,
                    "dob":19560606 ,
                    "occupation":"retired"})
my_db.rewrite_row ("customer", # table name
                    "000100" , # pk
                    {"location" : "Alaska"}) # row update
```
The last line below was created with the following calls (json array):

```
my_db.write_row ("log", # table name
                0 ,     # primary key array index
                ["20250904141020", # row data
                "Warning",
                "Log warning"])
```

__dump_all example:__

```

customer.000100~{"dob": 19560606, "customer_number": "000100", "name": "Curt", "occupation": "retired", "location": "Alaska"}
customer.000500~{"dob": 19200101, "customer_number": "000500", "name": "Moe", "occupation": "Three stooges"}
customer.001000~{"dob": 19250303, "customer_number": "001000", "name": "Curly", "occupation": "Three stooges"}
customer.010000~{"dob": 19210202, "customer_number": "010000", "name": "Larry", "occupation": "Three stooges"}
invoice.090001~{"invoice_number": "090001", "customer_number": "001000"}
invoice_line.090001.0001~{"invoice_number": "090001", "sku": "Snake Oil", "price": "100.00", "line_number": "0001"}
invoice_line.090001.0002~{"invoice_number": "090001", "sku": "Aspirin", "price": "12.00", "line_number": "0002"}
log.20250903122010~["20250903122010", "Error", "Log error"]
log.20250904141020~["20250904141020", "Warning", "Log warning"]
```



## Files

- simple_db.py
  - Provides a relational type database interface using btree
- simple_db_client.py
  - simple_db interface to a remote server.
  - Function call are the same as simple_db.py
  - Tested with simple_db_microdot.py server.
- simple_db_server.py
  - Accepts json RPC requests database requests and returns the results.
  - This module does not handle any communications.
  - Imports btree.
- simple_db_microdot.py
  - HTTP server that handles POST (json RPC) and GET requests.
  - All results are returned in json RPC format. 
  - Imports simple_db_server
- README.md
  - This documentation file