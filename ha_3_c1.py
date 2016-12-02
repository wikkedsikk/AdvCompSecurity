import matplotlib.pyplot as plt
import hashlib

def h(v, k, x):
    b = str(v) + str(k)
    hash = bin(int(hashlib.sha256(b).hexdigest(), 16))
    return hash[:x+2]

def crackBinding(hash, v, x):
    hitFound = 0
    count = 0
    if(v == 0):
        for p in range(0, 2**16):
            if(hash ==  h(1, bin(p)[2:].zfill(16),x)):
                hitFound += 1
            count += 1
    if (v == 1):
        for p in range(0, 2 ** 16):
            if (hash == h(0, bin(p)[2:].zfill(16),x)):
                hitFound += 1
            count += 1
    return hitFound, count

def crackConc(hash1, x):
    found_hit = 0
    count1 = 0
    count_vec = [0, 0]

    for p in range(0, 2):
        for q in range(0, 2**16):
            if hash1 == h(p, bin(q)[2:].zfill(16), x):
                found_hit += 1
            count1 += 1
        if(found_hit == 0):
            count_vec[p] = "0"
        else:
            count_vec[p] = 1.0/found_hit
        found_hit = 0
    return count_vec, count1/2

bind_plot_vec = []
conc0_plot_vec = []
conc1_plot_vec = []
k = bin(580)[2:].zfill(16)
for x in range(2, 20):
    hashen = h(0, k, x)
    binding, countb = crackBinding(hashen, 1, x)
    conc_vec, countc = crackConc(hashen, x)

    print x, "hash: ", hashen
    print "\tBinding probability and hits: ", float(binding) / countb, binding
    print "\tConcealing probability v=0: ", (float(conc_vec[0]))
    print "\tConcealing probability v=1: ", (float(conc_vec[1]))

    bind_plot_vec.append(float(binding)/countb)
    conc0_plot_vec.append(float(conc_vec[0]))
    conc1_plot_vec.append(float(conc_vec[1]))

plt.plot(conc1_plot_vec)
plt.plot(conc0_plot_vec)
plt.legend(['v equals 1', 'v equals 0'], 2)
plt.title("Probability of finding a unique hash for v")
plt.ylabel("Probability")
plt.xlabel("Length of hash")
plt.show()
