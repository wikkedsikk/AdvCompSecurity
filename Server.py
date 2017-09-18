import socket
from Crypto.Random import random
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util import number
import sys

n_length= 2048
primeNum = number.getPrime(n_length) # Create a random Prime that is 2048 bits long.

sessionID = 0

BLOCK_SIZE=16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

while True:
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Create socket
    soc.bind((UDP_IP, UDP_PORT))

    serverSecret = random.randint(1000, 1000000) #Server secret key

    sharedBase = 123123
    sharedPrime = 28894168311768357401899071200979519367584561514756423416043407424366358089765137721969343124410199219409767121293311844494553978897429563852027241420266248792272446039823985284920518325857671660201824712071585658761783163595939965642429159649000821474939376513696874834821123755837700720260008792402520994463966279163406594495256298820533042016219844237136312035186285435253143971857498938314110927819696637217086882893503422275857455341300900826497977775893550130968292538687465266315987428546046183866136605231770463808246035584917559385136718875090747467053956576939446056421176315711375543516925496498920321902033



    PSK = "0123456701234567"
    secureMessage = "Im server, hello"

    clientA = soc.recv(4096) #Recive the servers calculated B
    A = int(clientA)

    B = pow(sharedBase, serverSecret, sharedPrime) #Calculate the A that is sent to the server
    Bstr = str(B)

    soc.sendto(Bstr, ("localhost", 5004)) #Send the clients A to the server

    sharedSecret = pow(A, serverSecret, sharedPrime) # Calculate the shared secret
    strSecret = pad(str(sharedSecret))


    crypt_secret = soc.recv(4096) #Server recieves clients encrypted Secure message.
    cipher_client = AES.new(PSK)
    decr_client_Secure_Message = cipher_client.decrypt(crypt_secret) # Decrypt the client-sent Secure Message


    cipher_server = AES.new(PSK)
    ecr_server_secure_message = cipher_server.encrypt(secureMessage)
    soc.sendto(ecr_server_secure_message, ("localhost", 5004)) # Server sends its encrypted Secure Message to authenticate.

    if(decr_client_Secure_Message == "Im client, hello"): # Compare sent authentication to approve connection.
        clientHash = soc.recv(4096)
        hashCrypt = AES.new(strSecret)
        decrHash = hashCrypt.decrypt(clientHash)

        clientData = soc.recv(4096)
        cipherData = AES.new(strSecret)
        decrData = cipherData.decrypt(clientData)
        decrData = unpad(decrData)
        h = SHA256.new(decrData)

        if(h.hexdigest() == decrHash):
            if(str(sessionID) == decrData[0]):
                indexEnd = decrData.find("%")
                clientData = decrData[1:indexEnd-1]
                print "These are the values from the IoT device for the time between " + str(sessionID*8) + ":00-" + str((sessionID*8)+8) +":00"+clientData
            else:
                print "Session ID not valid, someone is trying to fuck about with replay"
        else:
            print "The data has been altered"
    else:
        "The PSK is not correct, someone is being a snake ass bitch"
    sessionID += 1