import socket
from Crypto.Random import random
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
import sys

BLOCK_SIZE=16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

sessionID = 0;
while sessionID < 3:
    UDP_IP = "localhost"
    UDP_PORT = 5004
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soc.bind((UDP_IP, UDP_PORT))

    clientSecret = random.randint(1000, 1000000)
    sharedBase = 123123
    sharedPrime = 28894168311768357401899071200979519367584561514756423416043407424366358089765137721969343124410199219409767121293311844494553978897429563852027241420266248792272446039823985284920518325857671660201824712071585658761783163595939965642429159649000821474939376513696874834821123755837700720260008792402520994463966279163406594495256298820533042016219844237136312035186285435253143971857498938314110927819696637217086882893503422275857455341300900826497977775893550130968292538687465266315987428546046183866136605231770463808246035584917559385136718875090747467053956576939446056421176315711375543516925496498920321902033
    sharedPrime = int(sharedPrime, 16)

    PSK = "0123456701234567"
    secureMessage = "Im client, hello"

    A = pow(sharedBase, clientSecret, sharedPrime)
    Astr = str(A)

    soc.sendto(Astr, ("127.0.0.1", 5005)) # Calculated Diffie-Hellmans A is sent to server.
    
    serverB = soc.recv(4096) # Servers calculated Diffie-Hellmans B is recieved by client.
    B = int(serverB)

    sharedSecret = pow(B, clientSecret, sharedPrime)
    strSecret = pad(str(sharedSecret)) # Padding to get length of multiple of 16.



    client_PSK = AES.new(PSK) # Creates a AES-object with Pre-Shared-Key
    ecr_client_secure_message = client_PSK.encrypt(secureMessage) # Client encrypts its Secure Message with AES-object.
    soc.sendto(ecr_client_secure_message, ("127.0.0.1",5005)) # Client sends its encrypted Secure Message to authenticate.

    ecr_server_Secure_Message = soc.recv(4096) # Recieves severs encrypted Secure Message
    cipher_server_PSK = AES.new(PSK) # Creates a AES-object to decrypt Servers Secure Message
    decr_server_Secure_Message = cipher_server_PSK.decrypt(ecr_server_Secure_Message) # Decrypts servers encrypted Secure Message

    if decr_server_Secure_Message == "Im server, hello": #Compare servers Secure Message

        maxLength = 0
        data = str(sessionID) + " "
        print "Numbers entered will be the simulated data from a IoT sensor between " + str(sessionID*8) +":00-" + str((sessionID*8)+8) +":00"
        while maxLength < 3:
            value = input("Data:")
            data += str(value) + " "
            maxLength += 1


        print data

        h = SHA256.new(data)
        hCypher = AES.new(strSecret)
        hcrypt = hCypher.encrypt(h.hexdigest())
        soc.sendto(hcrypt, ("127.0.0.1", 5005))

        obj = AES.new(strSecret)
        cipher = obj.encrypt(pad(data))
        soc.sendto(cipher, ("127.0.0.1", 5005))

        sessionID += 1

    else:
        print "Wrong authentication"
        soc.close()


