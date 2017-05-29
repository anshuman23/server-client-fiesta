from eve import Eve
from random import randint
import base64

people = {
'schema': {
    'tests':{
        'type': 'string',
        'required': True
        }
},
    'resource_methods':['GET','POST'],
}

settings = {
'DOMAIN': {
    'people' : people
}
}


def do_work(resource, docs):
    i = randint(0,9)
    if resource == 'people':
        for doc in docs:
            imgdata = base64.b64decode(doc['tests'])
            filename = '/home/ubuntu/flaskClientUpload/testing-images/' +  str(i)  + '.png'
            with open(filename, 'wb') as f:
                f.write(imgdata)

            os.system("sudo docker start 01a4d103a8a2")

            salonName = 'monsoon' #URGENT!!! Change the app to reflect the salon type or get from API call somewhere                                             

            os.system("sudo docker cp testing-images/" + str(i) + ".png  zealous_goodall://root/openface/testing-images/")

            os.system("sudo docker exec zealous_goodall /bin/sh -c \"cd /root/openface; ./demos/classifier.py infer ./generated-embeddings/" + salonName + "/classifier.pkl ./testing-images/"+ str(i) + ".png > output.txt\"")

            os.system("sudo docker cp zealous_goodall://root/openface/output.txt /home/ubuntu/flaskClientUpload/output.txt")

            with open('output.txt') as f:
                for line in f:
                    if line.startswith("Predict"):

                        re1='.*?'# Non-greedy match on filler                                                                                                   
                        re2='(?:[a-z][a-z]+)'# Uninteresting: word                                                                                              
                        re3='.*?'# Non-greedy match on filler                                                                                                   
                        re4='((?:[a-z][a-z]+))'# Word corresponding to name of person whose face is recognized                                   
                        re5='.*?'# Non-greedy match on filler                                                                                                   
                        re6='([+-]?\\d*\\.\\d+)(?![-+0-9\\.])'# Float value corresponding to confidence score                                                   
                    
                        rg = re.compile(re1+re2+re3+re4+re5+re6,re.IGNORECASE|re.DOTALL)
                        m = rg.search(line)

                        if m:
                            name=m.group(1)
                            confidence=m.group(2)
                            print "("+name+")"+":"+"("+confidence+")"+"\n"
                            ### DO API CALL TO SEND NAME AND CONFIDENCE HERE                                                                                    

                os.system('rm -rf testing-images')
                os.system('mkdir testing-images')
                os.system('rm -rf output.txt')
                os.system("sudo docker exec zealous_goodall /bin/sh -c \"cd /root/openface; rm -rf output.txt testing-images; mkdir testing-images \"")
            
                os.system("sudo docker stop 01a4d103a8a2")

    
                

app = Eve(settings=settings)

app.on_insert += do_work

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 8777)
