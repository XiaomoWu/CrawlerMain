import chardet
import shutil
import codecs 

filename = "C:/Users/rossz/OneDrive/PrivateResearch/Database-CSMar-Updating/trd.co-2015-08-17/TRD_Co.txt"

content = codecs.open(filename, 'r').read()
chardet.detect(content)