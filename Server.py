import socket
from Crypto.Random import random
from Crypto.Cipher import AES
from Crypto.Hash import MD5
from Crypto.Hash import SHA256

sessionID = 0 #SessionID to keep track of which session we are at

############ Padding function for data ############
BLOCK_SIZE=16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

while True:
    ############ Setup the socket connection ############
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Create socket
    soc.bind((UDP_IP, UDP_PORT))

    ############ Setup the predefined variables ############
    serverSecret = random.randint(10000, 10000000) #Server secret key
    sharedBase = 123123
    sharedPrime = 28179039560857009771306385663575251465052082209256736565907679869413612872371241248284494255009242077272408811726234373148009182527040182165419963413046582426487611124844965777992274583617626036115771440229501145474648321022457058308067410361304658415442447673142889855267530516296541964237928301744697008429310224155979751780042056048479779362563342726170674523163417674197214202557774791726117675762530762368982188520808798163743645092954998925124938709663901524320625995630509126661619543571593502122965594779116520081239146808571199809359872902653368467099079623850650766762691133591987141197121690464975665361051
    PSK = "0#Ab!w&P12b4p6%!"
    #######################################
    #########      Handshake      #########
    #######################################


    ############ Diffe-Hellman key exchange ############
    clientA = soc.recv(4096) #Recive the clients calculated A
    A = long(clientA)
    B = pow(sharedBase, serverSecret, sharedPrime) #Calculate the B that is sent to the client
    Bstr = str(B)
    soc.sendto(Bstr, ("localhost", 5004)) #Send the clients A to the server
    sharedSecret = pow(A, serverSecret, sharedPrime) # Calculate the shared secret
    strSecret = pad(str(sharedSecret))
    #print "The clients A value: " + clientA
    #print "The servers B value: " + Bstr
    #print "The calculated shared secret: " + strSecret

    ############ Authentication of client ############
    salt_PSK = PSK + str(sessionID)
    hash_salt_PSK = SHA256.new(salt_PSK)  # Client encrypts its Secure Message with AES-object.
    soc.sendto(hash_salt_PSK.hexdigest(), ("localhost", 5004))  # Client sends its encrypted Secure Message to authenticate.
    client_hash_PSK = soc.recv(4096)  # Recieves severs encrypted Secure Message
    #print "Servers salted PSK: " + hash_salt_PSK.hexdigest()
    #print "Client salted PSK: " + client_hash_PSK

    if(client_hash_PSK == hash_salt_PSK.hexdigest()): #Compare authentication to approve data transfer

        #######################################
        ############ Data exchange ############
        #######################################

        ######## Recieve the hash of data ########
        clientHash = soc.recv(4096)
        h_secret = MD5.new(strSecret)
        hashCrypt = AES.new(h_secret.hexdigest())
        decrHash = hashCrypt.decrypt(clientHash)

        ############ Recieve the data ############
        clientData = soc.recv(4096) #Recieve the data
        cipherData = AES.new(h_secret.hexdigest())
        decrData = cipherData.decrypt(clientData)
        decrData = unpad(decrData)
        h = SHA256.new(decrData)
        #print "Encrypted data recieved from client: " + clientData
        #print "Decrypted data recieved from client: " + decrData

        if(h.hexdigest() == decrHash): #Check if the data has been altered
            if(str(sessionID) == decrData[0]):#Check if its the correct session or if someone is trying to replay the last message
                print "These are the values from the IoT device for the time between " + str(sessionID*8) + ":00-" + str((sessionID*8)+8) +":00: "+decrData[2:]
            else:
                print "Session ID not valid, someone is trying to fuck about with replay"
        else:
            print "The data has been altered"
    else:
        "The PSK is not correct, someone is being a snake ass bitch"
    if(sessionID == 2):
        sessionID = 0
    else:
        sessionID += 1