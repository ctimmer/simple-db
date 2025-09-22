# simple-db - micropython relational DB using btree

## Module Functions

### Parameter Formats

- table_name
  - Table containing the row data
  - Name should not contain key_separator or dump_separator
- pk primary key
  - ID(s) in the row data used to build the primary key
  - Must be correct type for the row data (dict or array)
  - pk can be a scalar value (1 key) or an array (multiple keys)
  - Key value should not contain key_separator or dump_separator
- key, start_key, end_key
  - key value(s) used to access row data
  - start_key default is low value
  - end_key default is high value
- row_data
  - row data associated with to primary key
  - 2 possible formats
    - dict containing ID/VAL pairs
    - array containing only values
  - Must include the primary key(s)
- update_data
  - Always a dictionary.
  - Used ID/VAL to update specific columns in the row data
  - Dictionary rows
    - if the ID is missing from the row it will be created
  - Array rows
    - Only existing columns can be updated
    - The row array cannot be extended with this function
- limit

### Functions

__init (db_file_path, key_separator, dump_separator, auto_commit)__
- db_file_path Required
  - File name of the database
  - If the file is missing it will be created
- key_separator Default: "."
  - Character used to separate the concatenated table name and key(s)
- dump_separator Default: "~"
  - Character used to separate the primary key from the row values
- auto_commit Default: True

__write_row (table_name, pk, row_data)__
- Creates or overwrites the row for the specified table/key

__rewrite_row (table_name, key, update_data)__
- Updates only those table/key columns specified in update_data 

__read_row (table_name, key)__
- Read a row for the specified table/key
- None is returned if the key does not exist

__first_row (table_name, key)__
- Returns first row with a pk >= key in table

__next_row (table_name, key)__
- Returns first row with a pk > key in table

__row_exists (table_name, key)__
- Returns True if the key exists in table

__get_table_keys (table_name, start_key,  end_key, limit)__
- Returns a list of keys in table from start_key up to end_key

__get_table_rows (table_name, start_key,  end_key, limit)__
- Returns a list of rows in table from start_key up to end_key

__get_table_items (table_name, start_key, end_key, limit)__
- Returns a list of key and rows in table from start_key up to end_key

__dump_all (file_path)__
- Dumps the entire database to a file
- Format: "primary key" + "~" + row_data
- row_data will always be in json format

__load (file_path)__
- Loads database from file created by dump_all

__commit ()__
- Flushes updated cached buffers

__close ()__
- closes btree instance and database file

## Internal Database Structure

Micropython's btree database only stores a simple ID/Value pair. Refer to the dump_all example below.

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
                    "000100" , # key
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