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

while sessionID < 3:
    ############ Setup the socket connection ############
    UDP_IP = "localhost"
    UDP_PORT = 5004
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soc.bind((UDP_IP, UDP_PORT))

    ############ Setup the predefined variables ############
    clientSecret = random.randint(10000, 10000000)
    sharedBase = 123123
    sharedPrime = 28179039560857009771306385663575251465052082209256736565907679869413612872371241248284494255009242077272408811726234373148009182527040182165419963413046582426487611124844965777992274583617626036115771440229501145474648321022457058308067410361304658415442447673142889855267530516296541964237928301744697008429310224155979751780042056048479779362563342726170674523163417674197214202557774791726117675762530762368982188520808798163743645092954998925124938709663901524320625995630509126661619543571593502122965594779116520081239146808571199809359872902653368467099079623850650766762691133591987141197121690464975665361051
    PSK = "0#Ab!w&P12b4p6%!"

    #######################################
    #########      Handshake      #########
    #######################################

    ############ Diffe-Hellman key exchange ############
    A = pow(sharedBase, clientSecret, sharedPrime)
    Astr = str(A)
    soc.sendto(Astr, ("127.0.0.1", 5005)) # Calculated Diffie-Hellmans A is sent to server.
    serverB = soc.recv(4096) # Servers calculated Diffie-Hellmans B is recieved by client.
    B = long(serverB)
    sharedSecret = pow(B, clientSecret, sharedPrime)
    strSecret = pad(str(sharedSecret)) # Padding to get length of multiple of 16.
    #print "The clients A value: " + Astr
    #print "The servers B value: " + serverB
    #print "The calculated shared secret: " + strSecret

    ############ Authentication of client ############
    salt_PSK = PSK + str(sessionID)
    hash_salt_PSK = SHA256.new(salt_PSK)# Client encrypts its Secure Message with AES-object.
    soc.sendto(hash_salt_PSK.hexdigest(), ("127.0.0.1",5005)) # Client sends its encrypted Secure Message to authenticate.
    server_hash_PSK = soc.recv(4096) # Recieves severs encrypted Secure Message
    #print "Servers salted PSK: " + hash_salt_PSK.hexdigest()
    #print "Client salted PSK: " + server_hash_PSK

    if server_hash_PSK == hash_salt_PSK.hexdigest(): #Compare authentication to approve data transfer
        #######################################
        ############ Data exchange ############
        #######################################

        ######## Collection of data ########
        maxLength = 0
        data = str(sessionID) + " "
        print "Numbers entered will be the simulated data from a IoT sensor between " + str(sessionID*8) +":00-" + str((sessionID*8)+8) +":00"
        while maxLength < 3:
            value = input("Data:")
            data += str(value) + " "
            maxLength += 1

        ######## Send the hash of data ########
        h = SHA256.new(data)
        h_secret = MD5.new(strSecret)
        hCypher = AES.new(h_secret.hexdigest())
        hcrypt = hCypher.encrypt(h.hexdigest())
        soc.sendto(hcrypt, ("127.0.0.1", 5005))
        #print "Encrypted data sent from client: " + hcrypt
        #print "Decrypted data sent from client: " + data

        ############ Send the data ############
        obj = AES.new(h_secret.hexdigest())
        cipher = obj.encrypt(pad(data))
        soc.sendto(cipher, ("127.0.0.1", 5005))

        sessionID += 1

    else:
        print "Wrong authentication"
        soc.close()