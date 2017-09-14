import socket
from Crypto.Random import random
from Crypto.Cipher import AES
from Crypto.Hash import SHA256

sessionID = 0;
while sessionID < 3:
    UDP_IP = "localhost"
    UDP_PORT = 5004
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Create socket
    soc.bind((UDP_IP, UDP_PORT))

    clientSecret = random.randint(0, 10000) #Client secret key
    sharedBase = 5 #The shared base
    sharedPrime = 23 #The shared prime
    PSK = "0123456701234567"
    secureMessage = "Im client, hello"

    ##############################
    ##### PSK-authentication #####
    ##############################


    ##########################
    #### D-H Key Exchange ####
    ##########################

    A = pow(sharedBase, clientSecret, sharedPrime) #Calculate the A that is sent to the server
    Astr = str(A)
    soc.sendto(Astr, ("127.0.0.1", 5005)) #Send the clients A to the server

    serverB = soc.recv(4096) #Recive the servers calculated B
    B = int(serverB)

    sharedSecret = pow(B, clientSecret, sharedPrime) # Calculate the shared secret
    strSecret = str(sharedSecret)
    while len(strSecret) < 16:
        strSecret += "0"

    client_PSK = AES.new(PSK)
    cipher_PSK = client_PSK.encrypt(secureMessage)
    soc.sendto(cipher_PSK, ("127.0.0.1",5005))

    servers_PSK = soc.recv(4096)
    cipher_server_PSK = AES.new(PSK)
    server_PSK_text = cipher_server_PSK.decrypt(servers_PSK)

    if server_PSK_text == "Im server, hello":
        ##############################
        #####    Encrypt data    #####
        ##############################
        maxLength = 0
        data = str(sessionID) + " "
        print "Numbers entered will be the simulated data from a IoT sensor between " + str(sessionID*8) +":00-" + str((sessionID*8)+8) +":00"
        while maxLength < 3:
            value = input("Data:")
            data += str(value) + " "
            maxLength += 1

        while len(data)<16:
            data += "%"
        #for n in range(0,len(info1)-1):
        #    data += str(info1[n]) + " "
        print data

        h = SHA256.new(data)
        hCypher = AES.new(strSecret)
        hcrypt = hCypher.encrypt(h.hexdigest())
        soc.sendto(hcrypt, ("127.0.0.1", 5005))

        obj = AES.new(strSecret)
        cipher = obj.encrypt(data)
        soc.sendto(cipher, ("127.0.0.1", 5005))

        sessionID += 1

    else:
        print "Wrong authentication"
        soc.close()


#obj = Blowfish.new(PSK)
#cipher = obj.encrypt("01234567")

#print obj
#obj2 = Blowfish.new(PSK)
#test = obj2.decrypt(cipher)
#print test