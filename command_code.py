
class CommandCode():
    
    # Ah . . . I'm kinda new here, and there's probably a much better way
    # to do this.  But this is the way that's obvious to me right now, 
    # so off we go!
    
    NONE = "NONE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    RESET = "RESET"
    INFO = "INFO"
    VERSION = "VERSION"
    OPTIONS = "OPTIONS"
    ERROR = "ERROR"
    GET_ERROR = "GET_ERROR"
    ACK = "ACK"
    CURRENT_ITEM = "CURRENT_ITEM"
    MAX_VIS_IDX = "MAX_VIS_IDX"
    SELECT_VIS = "SELECT_VIS"
    MAX_TRAN_IDX = "MAX_TRAN_IDX"
    SELECT_TRAN = "SELECT_TRAN"
    SET_RATE = "SET_RATE"
    PING = "PING"
    FLIP_FRAME = "FLIP_FRAME"
    SET_FRAME = "SET_FRAME"
    GET_FRAME = "GET_FRAME"
    SET_P_FRAME = "SET_P_FRAME"
    SET_PIXEL = "SET_PIXEL"
    GET_PIXEL = "GET_PIXEL"
    DRAW_LINE = "DRAW_LINE"
    DRAW_BOX = "DRAW_BOX"
    FILL_IMAGE = "FILL_IMAGE"
    SCROLL_TEXT = "SCROLL_TEXT"
    LOAD_ANIM = "LOAD_ANIM"
     
    forward_tuples = [(NONE, -1),
                      (LOGIN, 0), (LOGOUT, 1), (RESET, 10), (INFO, 11),
                      (VERSION, 12), (OPTIONS, 15), (ERROR, 20),
                      (GET_ERROR, 21), (ACK, 25), (CURRENT_ITEM, 30),
                      (MAX_VIS_IDX, 40), (SELECT_VIS, 41), (MAX_TRAN_IDX, 42),
                      (SELECT_TRAN, 43), (SET_RATE, 50), (PING, 60),
                      (FLIP_FRAME, 80), (SET_FRAME, 81), (GET_FRAME, 82),
                      (SET_P_FRAME, 83), (SET_PIXEL, 84), (GET_PIXEL, 85),
                      (DRAW_LINE, 85), (DRAW_BOX, 87), (FILL_IMAGE, 88),
                      (SCROLL_TEXT, 89), (LOAD_ANIM, 90)]
    
    backward_tuples = [(b, a) for a, b in forward_tuples]
    
    names_to_numbers_dict = dict(forward_tuples)
    numbers_to_names_dict = dict(backward_tuples)

    @staticmethod
    def get_number(name):
        return CommandCode.names_to_numbers_dict.get(name)

    @staticmethod
    def get_name(number):
        return CommandCode.numbers_to_names_dict.get(number)

