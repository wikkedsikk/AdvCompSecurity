import socket
from Crypto.Random import random
from Crypto.Cipher import AES
from Crypto.Hash import SHA256

sessionID = 0

while True:
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Create socket
    soc.bind((UDP_IP, UDP_PORT))

    serverSecret = random.randint(0, 10000) #Server secret key
    sharedBase = 5
    sharedPrime = 23
    PSK = "0123456701234567"
    secureMessage = "Im server, hello"

    #h = SHA256.new()
    #preHash = PSK + str(sessionID)
    #h.update(preHash)

    ##############################
    ##### PSK-authentication #####
    ##############################
    #clientPSK = soc.recv(4096)
    #soc.sendto(PSK, ("127.0.0.1", 5004))
    #if (h.hexdigest() != clientPSK.hexdigest):
    #    soc.stop()
    #    exit()
    #else:
    #    sessionID += 1
    #    print "Pre-Shared Key is correct"

    ##########################
    #### D-H Key Exchange ####
    ##########################

    clientA = soc.recv(4096) #Recive the servers calculated B
    A = int(clientA)

    B = pow(sharedBase, serverSecret, sharedPrime) #Calculate the A that is sent to the server
    BStr = str(B)
    soc.sendto(BStr, ("localhost", 5004)) #Send the clients A to the server

    sharedSecret = pow(A, serverSecret, sharedPrime) # Calculate the shared secret
    strSecret = str(sharedSecret)
    while len(strSecret) < 16:
        strSecret += "0"


    crypt_secret = soc.recv(4096)
    cipher_client = AES.new(PSK)
    decr_client_PSK = cipher_client.decrypt(crypt_secret)


    cipher_server = AES.new(PSK)
    cipher_PSK = cipher_server.encrypt(secureMessage)
    soc.sendto(cipher_PSK, ("localhost", 5004))

    if(decr_client_PSK == "Im client, hello"):
        clientHash = soc.recv(4096)
        hashCrypt = AES.new(strSecret)
        decrHash = hashCrypt.decrypt(clientHash)

        clientData = soc.recv(4096)
        cipherData = AES.new(strSecret)
        decrData = cipherData.decrypt(clientData)

        h = SHA256.new(decrData)

        if(h.hexdigest() == decrHash):
            if(str(sessionID) == decrData[0]):
                indexEnd = decrData.find("%")
                clientData = decrData[1:indexEnd-1]
                print "These are the values from the IoT device for the time between " + str(sessionID*8) + ":00-" + str((sessionID*8)+8) +":00"
            else:
                print "Session ID not valid, someone is trying to fuck about with replay"
        else:
            print "The data has been altered"
    else:
        "The PSK is not correct, someone is being a snake ass bitch"
    sessionID += 1