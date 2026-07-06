from config import HOST, PORT
from server_core import ServerCore

def main():
    server = ServerCore(HOST, PORT)

    try:
        server.start()

    except KeyboardInterrupt:
        print("\nKeyboard Interrupt!")

    finally:
        server.shutdown()


if __name__ == "__main__":
    main()