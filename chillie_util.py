import sys


# Change this to allow more space for ChilliePicker to talk
HEADER_LENGTH = 60


# Logger ----
class Logger(object):
    def __init__(self, file_name):
        self.terminal = sys.stdout
        self.log = open(file_name, "a")

    def write(self, message):
        try:
            self.terminal.write(message)
            self.log.write(message)
        except Exception as e:
            e

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass    

def setLogger(file_name):
    sys.stdout = Logger(file_name)

# Headers ----


def repeat_string(message, x):
    result = ""
    for i in range(x):
        result = result + message
    return result
    
def make_line(header_length, message, border_char, thickness, padding):
        message_string = repeat_string(border_char, thickness) + repeat_string(" ", padding) + message
        return message_string + repeat_string(" ", header_length - len(message_string) - thickness) + repeat_string(border_char, thickness)
        
def make_header(header_length, name, message_array, thickness, padding, border_char, is_emoji):
    message_line_limit = header_length - thickness * 2 - padding * 2
    message_lines = []
    
    blank_line_length = header_length - thickness * 2
    blank_line = repeat_string(border_char, thickness) + repeat_string(" ", blank_line_length) + repeat_string(border_char, thickness)
    if is_emoji:
        line = repeat_string(border_char, int(header_length / 2) + 1)
    else:
        line = repeat_string(border_char, header_length)
    
    for message in message_array:
        temp = message
        is_first_time = True
        while len(temp) > message_line_limit or is_first_time:
            
            current_line = temp[:message_line_limit].strip()
            temp = temp[message_line_limit:]
            
            message_lines.append(make_line(header_length, current_line, border_char, thickness, padding))
            if len(temp) <= message_line_limit and len(temp) > 0:
                message_lines.append(make_line(header_length, temp, border_char, thickness, padding))
                
            is_first_time = False
        
        name_string = repeat_string(border_char, thickness) + repeat_string(" ", padding) + name
        name_line = name_string + repeat_string(" ", header_length - len(name_string) - thickness) + repeat_string(border_char, thickness)
        
        
    
    for i in range(thickness):
        print(line)
        

    print(blank_line)
    print(name_line)
    for message in message_lines:
        print(message)
    
    print(blank_line)
        
    for i in range(thickness):
        print(line)

def pooh_header(messages, char, is_emoji):
    make_header(HEADER_LENGTH, "Pooh:", messages, 1, 2, char, is_emoji)
    
def picker_header(messages, char, is_emoji):
    make_header(HEADER_LENGTH, "ChilliePicker:", messages, 1, 2, char, is_emoji)