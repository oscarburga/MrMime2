import socket
import json
import time

TIME_FOR_REPORTS = 5

class JsonSocket:

    def __init__(self, process_objects_callback, host='localhost', port=8080):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)
        self.clientSocket = None
        self.clientAddress = None
        self.process_objects_callback = process_objects_callback
        self.shouldStop = False
        self.last_reported_time = time.time()
        self.callback_count = 0
        self.failed_count = 0
        pass

    def accept_wait(self):
        print 'awaiting connection'
        self.clientSocket, self.clientAddress = self.server.accept()
        print 'connected'
    
    def close(self):
        if self.clientSocket:
            self.clientSocket.shutdown(socket.SHUT_RDWR)
            self.clientSocket.close()
            self.clientSocket = None
        
        self.clientAddress = None

    def send_to_client(self, msg):
        if self.clientSocket:
            total_sent = 0
            while total_sent < len(msg):
                sent = self.clientSocket.send(msg[total_sent:])
                if sent == 0:
                    break
                total_sent += sent

    def loop(self):
        if not self.clientSocket or not self.clientAddress:
            print 'cannot loop - no valid client or socket'
            return False
        current_obj_str = ''
        bracket_cnt = 0
        object_list = []
        while not self.shouldStop and self.clientSocket and self.clientAddress:
            # Read from the socket until its empty
            raw_in = self.clientSocket.recv(4 * 1024)
            if len(raw_in) == 0:
                print 'breaking accept_and_loop...', len(raw_in)
                break
            
            ascii_in = raw_in.encode('ascii', 'ignore')
            for i, x in enumerate(list(ascii_in)):
                # close signal: stop everything.
                if x == '!':
                    self.close()
                    print 'exiting main loop.'
                    return True

                old_bracket_cnt = bracket_cnt
                bracket_cnt += int(x == '{')
                bracket_cnt -= int(x == '}')
                current_obj_str += x

                # close a dictionary
                if bracket_cnt == 0 and old_bracket_cnt > 0:
                    # print 'closing dictionary'
                    try:
                        dic = json.loads(current_obj_str)
                        object_list.append(dic)
                    except Exception as e:
                        print 'Failed to parse and load json string'
                        self.failed_count += 1
                        print(e)
                        print current_obj_str
                        pass

                    current_obj_str = ''
            
            if len(object_list) > 0:
                if self.process_objects_callback:
                    self.process_objects_callback(object_list, self)
                    self.callback_count += 1
                object_list = []
            
            # log 
            now = time.time()
            delta_time = now - self.last_reported_time
            if delta_time > TIME_FOR_REPORTS:
                print 'Sent', self.callback_count, '- Failed', self.failed_count
                self.last_reported_time = now

            # End loop
        self.close()
        return True