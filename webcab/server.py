import web
from controllers.index import *

urls = (
     '/(.*)', 'StartPage'
)

if __name__ == "__main__": web.run(urls, globals())