from .surveillance import Handler
import os

if __name__ == '__main__':
    Handler(os.getcwd())()
