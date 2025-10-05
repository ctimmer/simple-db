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

class SimpleDBLogger :
    def __init__ (self,
                    db ,          # SimpleDB instance
                    table_name = "log" ,
                    sequence_length = 2) :
        self.db = db
        self.log_table_name = table_name
        self.log_dt = ""
        self.log_sequence = 0
        self.pk_seq_format = "{{:0{:d}d}}".format (sequence_length)

    def write_log (self,
                    log_entry = None,  # dictionary or array
                    type = "info") :   # default log entry type
        date_time = self.db.get_date_time ()
        if self.log_dt == date_time :
            self.log_sequence += 1    # duplicate timestamp
        else :
            self.log_dt = date_time   # New timestamp
            self.log_sequence = 0
        log_row = {
            "pk" : [date_time, self.pk_seq_format.format (self.log_sequence)] ,
            "type" : type ,
            "log_entry" : log_entry
            }
        self.db.write_row (self.log_table_name, "pk", log_row)

def main () :
    import os
    from simple_db import SimpleDB, simpledb_available
    if not simpledb_available :
        import sys
        print ("db failed to initialize")
        sys.exit ()
    
    db_file_name = "log_test.db"
    try :
        os.remove (db_file_name)
        print ("Removed:", db_file_name)
    except :
        pass
    my_db = SimpleDB (db_file_name)
    my_logger = SimpleDBLogger (my_db, sequence_length=2)

    my_logger.write_log (type = "db_opened")
    my_logger.write_log ({"current":"weather is great","tip":"Come on up"},type = "weather")
    my_logger.write_log (["now", "is", "the", "time"])
    my_logger.write_log (type = "db_closed")
    my_db.dump_all ()
    my_db.close ()

if __name__ == "__main__" :
    main ()