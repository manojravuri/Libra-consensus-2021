import os

class Logger:

    @staticmethod
    def cleanup():
        dir = os.path.dirname(os.getcwd())+'/logs/'
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))
        


    @staticmethod
    def log(msg,filename):
        dir = os.path.dirname(os.getcwd())+'/logs/'
        filename=dir+filename
        file=open(filename,"a+")
        file.write(msg+"\n")
        print(msg)
        file.close()



