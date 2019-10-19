"""
Name: Andy Lu
Time To Completion: 8 hours
Comments:

Sources: Professor's Example Tokenizer
http://interactivepython.org/runestone/static/pythonds/SortSearch/TheBubbleSort.html
"""
import string
from operator import itemgetter

_ALL_DATABASES = {}


class Connection(object):
    def __init__(self, filename):
        """
        Takes a filename, but doesn't do anything with it.
        (The filename will be used in a future project).
        """
        self.filename = filename
        self.tokens = []
        self.tables_list = []
        pass
    """ Tokenizer """
    def collect_characters(self, query, allowed_characters):
        letters = []
        for letter in query:
            if letter not in allowed_characters:
                break
            letters.append(letter)
        return "".join(letters)

    def remove_leading_whitespace(self, query, tokens):
        whitespace = self.collect_characters(query, string.whitespace)
        return query[len(whitespace):]
    
    def remove_word(self, query, tokens):
        word = self.collect_characters(query, string.ascii_letters+"_"+string.digits)
        if word == "NULL":
            tokens.append(None)
        else:
            tokens.append(word)
        return query[len(word):]

    def remove_text(self, query, tokens):
        assert query[0] == "'"
        query = query[1:]
        end_quote_index = query.find("'")
        text = query[:end_quote_index]
        tokens.append(text)
        query = query[end_quote_index+1:]
        return query

    def remove_integer(self, query, tokens):
        int_str = self.collect_characters(query, string.digits)
        tokens.append(int_str)
        return query[len(int_str):]
    
    def remove_numbers(self, query, tokens):
        query = self.remove_integer(query, tokens)
        if query[0] == ".":
            whole_str = tokens.pop()
            query = query[1:]
            query = self.remove_integer(query, tokens)
            frac_str = tokens.pop()
            float_str = whole_str + "." + frac_str
            tokens.append(float(float_str))
        else:
            int_str = tokens.pop()
            tokens.append(int(int_str))
        return query
        
    def tokenize(self, query):
        tokens = []
        while query:
            if query[0] in string.whitespace:
                query = self.remove_leading_whitespace(query, tokens)
                continue
            if query[0] in (string.ascii_letters + "_"):
                query = self.remove_word(query, tokens)
                continue
            if query[0] in "(),;*":
                tokens.append(query[0])
                query = query[1:]
                continue
            if query[0] == "'":
                query = self.remove_text(query, tokens)
                continue
            if query[0] in string.digits:
                query = self.remove_numbers(query, tokens)
                continue
        return tokens
    """
    ----------------------------------------------------------------------------
    End of Tokenizer
    ----------------------------------------------------------------------------
    """
    """
    Checks if table exists within self.tables_list.
    If it does, returns the index at which it is found
    """
    def check_table(self, name):
        table_exist = False
        table_index = 0
        for i in self.tables_list:
            if name == i.get_name():
                return table_index
            else:
                table_index = table_index+1
        return None
    """
    Creates a table with the name argument and tokens as its columns
    """
    def create_table(self, name, tokens):
        self.output = Table()
        self.output.set_name(name)
        key = False
        for i in range(0, len(tokens)-1):
            if key==True:
                self.output.add_column(tokens[i], tokens[i+1])
            key=False
            if tokens[i] in "(,":
                key=True
        return self.output
    """
    Checks the name of table in tables_list, and stores index.
    Then, it calls the table function add_values to store the following tokens
    """
    def insert_into(self, name, tokens):
        table_exist = False
        table_index = 0
        for i in range(0, len(self.tables_list)):
            if name == self.tables_list[i].get_name():
                tables_exist = True
                table_index = i
        self.tables_list[table_index].add_values(tokens)
        pass
    """
    Second part of the select function.Takes in a list of strings of columns, a singular table, and a list of strings of order.First, it runs through the list of orders and gets the index for that order column. Then, it stores it in a list of integers of orders. Afterwards, it bubble sorts according to the starting index of the order_index list. Then, it loops through the columns list and get the index of each column to display in the following order. 
    """
    def order_by(self, columns, table, orders):
        table_index = self.check_table(table)
        print(table_index)
        temp_tab = self.tables_list[table_index]
        tab = temp_tab.get_values()
        order_index = []
        column_index = []
        starting_order = None
        for order in orders:
            order_index.append(temp_tab.get_column_position(order))
        starting_order = order_index[0]
        for i in range(len(tab)-1, 0, -1):
            for j in range(i):
                if (tab[j][starting_order]) > (tab[j+1][starting_order]):
                    temp = tab[j]
                    tab[j] = tab[j+1]
                    tab[j+1] = temp
                elif tab[j][starting_order] == tab[j+1][starting_order]:
                    if len(order_index)>1:
                        next_order = order_index[1]
                        if tab[j][next_order] > tab[j+1][next_order]:
                            temp = tab[j]
                            tab[j] = tab[j+1]
                            tab[j+1] = temp
        for column in columns:
            column_index.append(temp_tab.get_column_position(column))
        temp_tuple = ()
        final_tuple_list = []
        for i in range(0, len(tab)):
            for column in column_index:
                temp = (tab[i][column],)
                temp_tuple = temp_tuple + temp
            final_tuple_list.append(temp_tuple)
            temp_tuple = ()
        return final_tuple_list
    """
    Breaks down the tokens for select, then calls order by to make appropriate table display
    """
    def select(self, tokens):
        select_columns = []
        select_table = None
        select_order = []
        bool_columns = False
        bool_tables = False
        bool_order = False
        bool_star = False
        for token in tokens:
            if token == ";":
                break;
            if token == "*":
                bool_star = True
                bool_columns = False
            if bool_columns == True and token != "," and token != "FROM":
                select_columns.append(token)
            elif bool_tables == True:
                select_table = token
                bool_tables = False
            elif bool_order == True and token != ",":
                select_order.append(token)
            if token == "SELECT":
                bool_columns = True
            elif token == "FROM":
                bool_columns = False
                bool_tables = True
            elif token == "BY":
                bool_tables = False
                bool_order = True
        if bool_star == True:
            table_index = self.check_table(select_table)
            temp_tab = self.tables_list[table_index]
            tuple_list = temp_tab.get_column_tuples()
            for column in tuple_list:
                select_columns.append(column[0])
        return self.order_by(select_columns, select_table, select_order)
    def execute(self, statement):
        """
        Takes a SQL statement.
        Returns a list of tuples (empty unless select statement
        with rows to return).
        """
        self.tokens = self.tokenize(statement)
        for count in self.tokens:
            if count == "CREATE":
                self.tokens.pop(0)
                self.tokens.pop(0)
                self.tables_list.append(self.create_table(self.tokens[0],self.tokens[1:]))
            if count == "INSERT":
                self.tokens.pop(0)
                self.tokens.pop(0)
                self.insert_into(self.tokens[0],self.tokens[1:])
            if count == "SELECT":
                return self.select(self.tokens)
            pass
        pass

    def close(self):
        """
        Empty method that will be used in future projects
        """
        pass
def connect(filename):
    """
    Creates a Connection object with the given filename
    """
    return Connection(filename)


class Database:
    def __init__(self):
        self.tables = []
    pass


class Table:
    def __init__(self):
        self.identity = "";
        self.column_tuples = [];
        self.values = [];
        
    def set_name(self, name):
        self.identity = name
        
    def get_name(self):
        return self.identity
        
    def get_values(self):
        return self.values
        
    def get_column_tuples(self):
        return self.column_tuples
        
    def add_column(self, name, data_type):
        tuple_type = (name, data_type)
        self.column_tuples.append(tuple_type)
        pass
    def get_column_position(self, column_name):
        index = 0
        for i in self.column_tuples:
            if i[0] == column_name:
                return index
            index = index + 1
        
    def add_values(self, items):
        key = False
        start_quote = False
        end_quote = False
        key_tuple = ()
        for item in items:
            if key == True:
                key_tuple = key_tuple + (item,)
            key = False
            if item == "(":
                key = True
            if item == ",":
                key = True
        self.values.append(key_tuple)

    