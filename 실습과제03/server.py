import os
import socket
from datetime import datetime

class SocketServer:
    def __init__(self):
        self.bufsize = 1024
        with open('./response.bin', 'rb') as file:
            self.RESPONSE = file.read()

        self.DIR_PATH = './request'
        self.createDir(self.DIR_PATH)

    def createDir(self, path):
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError:
            print("Error: Failed to create the directory.")

    def run(self, ip, port):
        """서버 실행"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))
        self.sock.listen(10)
        print("Start the socket server...")
        print("\"Ctrl+C\" for stopping the server!\r\n")

        try:
            while True:
                clnt_sock, req_addr = self.sock.accept()
                clnt_sock.settimeout(5.0)
                print("Request message...\r\n")

                # -------------------------------
                # 요청 수신
                data = b""
                while True:
                    try:
                        part = clnt_sock.recv(self.bufsize)
                        if not part:
                            break
                        data += part
                    except socket.timeout:
                        break

                # 요청 저장 (년-월-일-시-분-초.bin)
                now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                req_path = f"./request/{now}.bin"
                with open(req_path, "wb") as f:
                    f.write(data)

                # 이미지가 포함된 경우 따로 저장
                if b"Content-Type: image" in data:
                    # boundary 추출
                    if b"boundary=" in data:
                        boundary = data.split(b"boundary=")[1].split(b"\r\n")[0]
                        parts = data.split(b"--" + boundary)
                        for p in parts:
                            if b"Content-Type: image" in p:
                                img_data = p.split(b"\r\n\r\n", 1)[1].rsplit(b"\r\n", 1)[0]
                                img_path = f"./request/{now}.jpg"
                                with open(img_path, "wb") as img:
                                    img.write(img_data)
                                break
                # -------------------------------

                # 응답 전송
                clnt_sock.sendall(self.RESPONSE)
                clnt_sock.close()

        except KeyboardInterrupt:
            print("\r\nStop the server...")

        self.sock.close()


if __name__ == "__main__":
    server = SocketServer()
    server.run("127.0.0.1", 8000)
