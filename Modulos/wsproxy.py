#!/usr/bin/env python
# encoding: utf-8
import socket, threading, select, signal, sys, time, getopt

PASS = ''
LISTENING_ADDR = '0.0.0.0'
try:
    LISTENING_PORT = int(sys.argv[1])
except:
    LISTENING_PORT = 80
BUFLEN = 4096 * 4
TIMEOUT = 60
MSG = ''
COR = '<font color="null">'
FTAG = '</font>'
DEFAULT_HOST = "127.0.0.1:22"
RESPONSE = "HTTP/1.1 101 " + str(COR) + str(MSG) + str(FTAG) + "\r\n\r\n"

class Server(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.running = False
        self.host = host
        self.port = port
        self.threads = []
        self.threadsLock = threading.Lock()
        self.logLock = threading.Lock()

    def run(self):
        self.soc = socket.socket(socket.AF_INET)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.soc.settimeout(2)
        self.soc.bind((self.host, self.port))
        self.soc.listen(5)
        self.running = True

        try:
            while self.running:
                try:
                    c, addr = self.soc.accept()
                    c.setblocking(1)
                except socket.timeout:
                    continue

                conn = ConnectionHandler(c, self, addr)
                conn.start()
                self.addConn(conn)
        finally:
            self.running = False
            self.soc.close()

    def printLog(self, log):
        self.logLock.acquire()
        print(log)
        self.logLock.release()

    def addConn(self, conn):
        with self.threadsLock:
            if self.running:
                self.threads.append(conn)

    def removeConn(self, conn):
        with self.threadsLock:
            self.threads.remove(conn)

    def close(self):
        self.running = False
        with self.threadsLock:
            threads = list(self.threads)
            for c in threads:
                c.close()


class ConnectionHandler(threading.Thread):
    def __init__(self, socClient, server, addr):
        threading.Thread.__init__(self)
        self.clientClosed = False
        self.targetClosed = True
        self.client = socClient
        self.client_buffer = ''
        self.server = server
        self.log = 'Connection: ' + str(addr)

    def close(self):
        if not self.clientClosed:
            try:
                self.client.shutdown(socket.SHUT_RDWR)
            except:
                pass
            finally:
                self.client.close()
                self.clientClosed = True

        if not self.targetClosed:
            try:
                self.target.shutdown(socket.SHUT_RDWR)
            except:
                pass
            finally:
                self.target.close()
                self.targetClosed = True

    def run(self):
        try:
            self.client_buffer = self.client.recv(BUFLEN)

            hostPort = self.findHeader(self.client_buffer, 'X-Real-Host')
            if hostPort == '':
                hostPort = DEFAULT_HOST

            split = self.findHeader(self.client_buffer, 'X-Split')
            if split != '':
                self.client.recv(BUFLEN)

            if hostPort:
                passwd = self.findHeader(self.client_buffer, 'X-Pass')

                if PASS and passwd == PASS:
                    self.method_CONNECT(hostPort)
                elif PASS and passwd != PASS:
                    self.client.send(b'HTTP/1.1 400 WrongPass!\r\n\r\n')
                elif hostPort.startswith('127.0.0.1') or hostPort.startswith('localhost'):
                    self.method_CONNECT(hostPort)
                else:
                    self.client.send(b'HTTP/1.1 403 Forbidden!\r\n\r\n')
            else:
                self.client.send(b'HTTP/1.1 400 NoXRealHost!\r\n\r\n')

        except Exception as e:
            self.log += f' - error: {e}'
            self.server.printLog(self.log)
        finally:
            self.close()
            self.server.removeConn(self)

    def findHeader(self, head, header):
        idx = head.find(f'{header}: ')
        if idx == -1:
            return ''

        idx = head.find(':', idx)
        head = head[idx+2:]
        idx = head.find('\r\n')
        if idx == -1:
            return ''
        return head[:idx]

    def connect_target(self, host):
        i = host.find(':')
        port = int(host[i+1:]) if i != -1 else 443 if self.method == 'CONNECT' else 80
        host = host[:i] if i != -1 else host

        soc_family, soc_type, proto, _, address = socket.getaddrinfo(host, port)[0]
        self.target = socket.socket(soc_family, soc_type, proto)
        self.targetClosed = False
        self.target.connect(address)

    def method_CONNECT(self, path):
        self.log += ' - CONNECT ' + path
        self.connect_target(path)
        self.client.sendall(RESPONSE.encode())
        self.client_buffer = ''
        self.server.printLog(self.log)
        self.doCONNECT()

    def doCONNECT(self):
        socs = [self.client, self.target]
        count = 0
        error = False
        while not error:
            count += 1
            recv, _, err = select.select(socs, [], socs, 3)
            if err:
                error = True
            if recv:
                for in_ in recv:
                    try:
                        data = in_.recv(BUFLEN)
                        if data:
                            if in_ is self.target:
                                self.client.send(data)
                            else:
                                while data:
                                    byte = self.target.send(data)
                                    data = data[byte:]
                            count = 0
                        else:
                            error = True
                            break
                    except:
                        error = True
                        break
            if count == TIMEOUT:
                error = True


def print_usage():
    print('Usage: proxy.py -p <port>')
    print('       proxy.py -b <ip> -p <port>')
    print('       proxy.py -b 0.0.0.0 -p 22')


def parse_args(argv):
    global LISTENING_ADDR, LISTENING_PORT

    try:
        opts, args = getopt.getopt(argv, "hb:p:", ["bind=", "port="])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt in ("-b", "--bind"):
            LISTENING_ADDR = arg
        elif opt in ("-p", "--port"):
            LISTENING_PORT = int(arg)


def main(host=LISTENING_ADDR, port=LISTENING_PORT):
    print("\033[0;34m━" * 8, "\033[1;32m PROXY WEBSOCKET", "\033[0;34m━" * 8, "\n")
    print("\033[1;33mIP:\033[1;32m " + LISTENING_ADDR)
    print("\033[1;33mPORT:\033[1;32m " + str(LISTENING_PORT) + "\n")
    print("\033[0;34m━" * 10, "\033[1;32m VPSMANAGER", "\033[0;34m━\033[1;37m" * 11, "\n")

    server = Server(LISTENING_ADDR, LISTENING_PORT)
    server.start()

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print('Stopping...')
        server.close()


if __name__ == '__main__':
    parse_args(sys.argv[1:])
    main()
