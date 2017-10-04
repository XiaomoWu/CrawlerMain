import chardet
import shutil
import codecs 
import os 
import re 


def convert_encoding(filename, target_encoding):
    # Backup the origin file.
    shutil.copyfile(filename, filename + '.bak')

    # convert file from the source encoding to target encoding
    content = codecs.open(filename, 'r').read()
    source_encoding = chardet.detect(content)['encoding']
    print(source_encoding, filename)
    content = content.decode(source_encoding) #.encode(source_encoding)
    codecs.open(filename, 'w', encoding=target_encoding).write(content[1:])

    #content = open(filename).read()
    #if content[:3] == codecs.BOM_UTF8:
    #    content = content[3:]
    #content.write(filename, "w")

def main(path, target_encoding = "utf-8"):
    #for root, dirs, files in os.walk(os.getcwd()):
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.lower().endswith('.txt'):
                filename = os.path.join(root, f)
                try:
                    convert_encoding(filename, target_encoding)
                except Exception, e:
                    print("error:", filename)

def process_bak_files(path, action='restore'):
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.lower().endswith('.txt.bak'):
                source = os.path.join(root, f)
                target = os.path.join(root, re.sub('\.txt\.bak$', '.txt', f, flags=re.IGNORECASE))
                try:
                    if action == 'restore':
                        shutil.move(source, target)
                    elif action == 'clear':
                        os.remove(source)
                except Exception, e:
                    print("error:", source)

if __name__ == '__main__':
    path = "C:/Users/rossz/OneDrive/PrivateResearch/Database-CSMar-Updating/trd.daylr-2015-08-17"
    process_bak_files(path, action='restore')
    main(path, target_encoding = "UTF-8")