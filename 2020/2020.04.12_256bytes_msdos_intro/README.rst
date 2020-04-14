Analysis of a 256-bytes MS-DOS intro
====================================

Source
------

https://www.pouet.net/prod.php?which=85227

    memories by Desire (https://www.facebook.com/groups/303317629035)

https://twitter.com/rygorous/status/1249184844850106369

    In case you missed what is almost certainly going to be the winning PC 256 byte demo of Revision 2020 on stream, here it is on YouTube: https://youtube.com/watch?v=Imquk_3oFf4
    yes. 256 bytes.

Disassembly of memory.com
-------------------------

Here is an analysis for `<memories2/memory.com>`_.
Even though the source code is available (`<memories2/memories.asm>`_), this explains what is going on in animations.

The entry point of COM executables is fixed at ``0x0100``.
The executable can thus be disassembled with::

    objdump -D -bbinary -mi8086 -Mintel --adjust-vma=256 memories.com


Entry point
~~~~~~~~~~~

::

    100: b0 13        mov    al,0x13
    102: cd 10        int    0x10

With ``ah = 0``, this calls function *Set video mode* (https://en.wikipedia.org/wiki/INT_10H, http://www.ctyme.com/intr/rb-0069.htm) in order to switch to *Mode 13h* (https://en.wikipedia.org/wiki/Mode_13h).

    *Mode 13h* is the standard 256-color mode on VGA graphics hardware introduced in 1987 with the IBM PS/2.
    It has a resolution of 320×200 pixels.
    The VGA has 256 KiB of video memory consisting of 4 banks of 64 KiB, known as planes (or 'maps' in IBM's documentation).

(300×200 = 640000, rounded to 65536 = 0x10000)

The video memory consists in 256 KiB located at high address ``0xA000``.

::

    104: 95           xchg   bp,ax

Put into ``bp`` the result of ``int 0x10``, documented as:

    AL = video mode flag / CRT controller mode byte

::

    105: 68 f6 9f     push   0x9ff6
    108: 07           pop    es

Set ``es`` to ``0xa000 - 10``, in order to address video memory

::

    109: b8 1c 25     mov    ax,0x251c
    10c: b2 45        mov    dl,0x45
    10e: cd 21        int    0x21

Call DOS Function ``ah = 0x25``, *Set interrupt Vector*:

* ``al = 0x1c``: interrupt number, "User Timer Tick", called at every timer tick (18.2 times per second, or every 55 ms, by default)
* ``ds:dx = 0x145`` (assume ``dh = 1``): interrupt handler

Main loop
~~~~~~~~~

::

    110: b8 cd cc     mov    ax,0xcccd
    113: f7 e7        mul    di
    115: 00 e0        add    al,ah
    117: 30 e4        xor    ah,ah
    119: 01 e8        add    ax,bp
    11b: c1 e8 09     shr    ax,0x9
    11e: 24 0f        and    al,0xf
    120: 93           xchg   bx,ax
    121: b7 01        mov    bh,0x1
    123: 8a 5f 3a     mov    bl,BYTE PTR [bx+0x3a]
    126: ff d3        call   bx
    128: aa           stos   BYTE PTR es:[di],al
    129: 47           inc    di
    12a: 47           inc    di
    12b: 75 e3        jne    0x110

    12d: b0 85        mov    al,0x85
    12f: e6 40        out    0x40,al
    131: e4 60        in     al,0x60
    133: fe c8        dec    al
    135: 75 d9        jne    0x110

    137: c3           ret

    138: 0b 93
    ; Effects jump table
    13a: 74     ; 0x174: Effect 2: board of chessboards
    13b: 7e     ; 0x17e: Effect 1: circles, zooming
    13c: 61     ; 0x161: Effect 0: tilted plane, scrolling
    13d: 90     ; 0x190: Effect 3: parallax checkerboards
    13e: a5     ; 0x1a5: Effect 4: sierpinski rotozoomer
    13f: c8     ; 0x1c8: Effect 5: raycast bent tunnel
    140: ea     ; 0x1ea: Effect 6: ocean night / to day sky
    141: 37     ; 0x137: nop (return al from previous bl: 0x37 = blue)
    142: 43     ; 0x143: stop (exit the main loop)
    143: 58           pop    ax
    144: c3           ret

The rough equivalent C-code of this function looks like:

.. code-block:: c

    for (;;) {
        // dx:ax = di * 0xcccd with 0xcccd = 0x10000 * 4/5
        ax = (di * 0xcccd) & 0xffff;
        dx = di * 4 / 5;
        ax = (ax & 0xff) + (ax >> 8);
        bx = ((bp + ax) >> 9) & 0xf;
        es:[di] = call jump_table_13a[bx];
        di = (di + 2) & 0xffff;
        if (di == 0) {
            outb(0x40, 0x85);
            if (inb(0x60) == 0x01)
                return;
        }
    }

This calls several effects, from a jump table.
The parameters of every effect handlers are:

* ``bp``: the timer tick counter (it is incremented at each timer tick)
* ``di``: the current pixel position (increment by 2 at each loop)
* ``dx``: the 4/5 of the current pixel position. As 256 = 320×4/5, in fact:

  - ``dl`` is the X coordinate of the current pixel
  - ``dh`` is the Y coordinate of the current pixel

The computation around ``ax`` is a pseudo-random number generator that computes transitions between two effects: for some pixels, a "+1" is added to the index in the effect table, and this "+1" becomes more likely as time passes.
This is all behind this seemingly-simple line of code: ``bx = ((bp + ax) >> 9) & 0xf;`` (``bp`` is a time counter and ``ax`` a random value between 0 and ``0xff``).
This also means that every 512 ticks (where ``bp`` increments), the frame changes.

``mov al,0x85 ; out 0x40,al`` sends value 133 to port ``0x40``, which is channel 0 of the PIT (Programmable Interval Timer, 8253/8254 chip, https://wiki.osdev.org/PIT).
The oscillator used by the PIT runs at 1.193182 MHz.
Sending value ``0x85`` configures the tempo of the IRQ0 to 1193182 / 133 = 8971.29 Hz.
This *beat* is computed in the source code as ``%define tempo 1193182/256/targetFPS`` with ``%define targetFPS 35`` (indeed ``round(1193182/256/35) = 133``).
So this configures the PIT to trigger 256 interruptions for each target frame, for a FPS (number of frames per seconds) at 35 Hz.

``in al,0x60`` requests the content of the Data Port of an PS/2 keyboard controller (https://wiki.osdev.org/%228042%22_PS/2_Controller).
When a ``0x01`` is read from this port, it means that the key with this scancode is being pressed.
According to scancode tables, this scancode is ``Esc``.
So when the user presses ``Esc``, the program stops.


Handler for interrupt ``0x1c`` (User Timer Tick)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    145: 45           inc    bp
    146: f7 c5 07 00  test   bp,0x7
    14a: 75 14        jne    0x160

    14c: ba 30 03     mov    dx,0x330
    14f: be 37 01     mov    si,0x137
    152: 6e           outs   dx,BYTE PTR ds:[si]
    153: 6e           outs   dx,BYTE PTR ds:[si]
    154: 6e           outs   dx,BYTE PTR ds:[si]
    155: 69 c5 80 f6  imul   ax,bp,0xf680
    159: c1 e8 0a     shr    ax,0xa
    15c: 04 16        add    al,0x16
    15e: ee           out    dx,al
    15f: 6e           outs   dx,BYTE PTR ds:[si]

    160: cf           iret

``bp`` holds a counter which is incremented for each tick.
Every 8 beats, several words are outputted to port ``0x0330``.
This is a UART port to a MPU-401 (MIDI Processing Unit), that receives MIDI messages.
These messages are read from address ``0x137``::

* ``c3 0b``: *Program Change* for channel 4, to program 11 (Music Box, in Chromatic Percussion: https://en.wikipedia.org/wiki/General_MIDI)
* ``93 <al> 74``: *Note On* event, channel 4, key ``<al> & 0x7f`` velocity 116

Here, ``<al>`` is ``(0x16 + (((bp * 0xf680) & 0xffff) >> 10)) & 0xff`` (with ``bp`` incrementing 8 by 8).
This is a Pseudo-random number generators that loops every 64 iterations (so every time ``bp`` crosses a multiple of 512).
An iteration consists in key notes between 22 and 85.
In MIDI, note 60 is the middle C (C4, 262 Hz) and adding or subtracting 1 is the equivalent to moving a half step.
This leads to the following music sheet, grouped by 4 notes::

    22 = Bb0 (  29 Hz)   67 = G4  ( 392 Hz)   48 = C3  ( 131 Hz)   29 = F1  (  44 Hz)
    74 = D5  ( 587 Hz)   55 = G3  ( 196 Hz)   36 = C2  (  65 Hz)   81 = A5  ( 880 Hz)
    62 = D4  ( 294 Hz)   43 = G2  (  98 Hz)   24 = C1  (  33 Hz)   69 = A4  ( 440 Hz)
    50 = D3  ( 147 Hz)   31 = G1  (  49 Hz)   76 = E5  ( 659 Hz)   57 = A3  ( 220 Hz)
    38 = D2  (  73 Hz)   83 = B5  ( 988 Hz)   64 = E4  ( 330 Hz)   45 = A2  ( 110 Hz)
    26 = D1  (  37 Hz)   71 = B4  ( 494 Hz)   52 = E3  ( 165 Hz)   33 = A1  (  55 Hz)
    78 = F#5 ( 740 Hz)   59 = B3  ( 247 Hz)   40 = E2  (  82 Hz)   85 = C#6 (1109 Hz)
    66 = F#4 ( 370 Hz)   47 = B2  ( 123 Hz)   28 = E1  (  41 Hz)   73 = C#5 ( 554 Hz)
    54 = F#3 ( 185 Hz)   35 = B1  (  62 Hz)   80 = G#5 ( 831 Hz)   61 = C#4 ( 277 Hz)
    42 = F#2 (  92 Hz)   23 = B0  (  31 Hz)   68 = G#4 ( 415 Hz)   49 = C#3 ( 139 Hz)
    30 = F#1 (  46 Hz)   75 = Eb5 ( 622 Hz)   56 = G#3 ( 208 Hz)   37 = C#2 (  69 Hz)
    82 = Bb5 ( 932 Hz)   63 = Eb4 ( 311 Hz)   44 = G#2 ( 104 Hz)   25 = C#1 (  35 Hz)
    70 = Bb4 ( 466 Hz)   51 = Eb3 ( 156 Hz)   32 = G#1 (  52 Hz)   77 = F5  ( 698 Hz)
    58 = Bb3 ( 233 Hz)   39 = Eb2 (  78 Hz)   84 = C6  (1047 Hz)   65 = F4  ( 349 Hz)
    46 = Bb2 ( 117 Hz)   27 = Eb1 (  39 Hz)   72 = C5  ( 523 Hz)   53 = F3  ( 175 Hz)
    34 = Bb1 (  58 Hz)   79 = G5  ( 784 Hz)   60 = C4  ( 262 Hz)   41 = F2  (  87 Hz)


Effect 0: tilted plane, scrolling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    161: b8 29 13     mov    ax,0x1329
    164: 00 c6        add    dh,al  ; dh = Y coordinate
    166: f6 f6        div    dh     ; divide ax by dh, quotient al remainder ah
    168: 92           xchg   dx,ax  ; swap dx and ax (al becomes the X coordinate)
    169: f6 ea        imul   dl     ; ax = al * dl
    16b: 29 ea        sub    dx,bp  ; dx -= bp (timer tick counter)
    16d: 30 d4        xor    ah,dl
    16f: 88 e0        mov    al,ah
    171: 24 1c        and    al,0x1c  ; return (ah ^ dl) & 0x1c
    173: c3           ret

Equivalent C code:

.. code-block:: c

    // Y pixel position from 0 to 200 => dl between 119 and 20
    dl = (4905 // (dh_Y + 41)) & 0xff;
    // The more the pixel is "far", the more we see tiles
    ah = (dl_X * dl) // 256;
    // chessboard plane with "x^y", scrolling to the top
    return (ah ^ (dl - bp_timer)) & 0x1c;

Used VGA colors:

* ``0x00``: black
* ``0x04``: dark red
* ``0x08``: dark grey
* ``0x0c``: light red
* ``0x10``: black
* ``0x10``: dark grey
* ``0x18``: light grey
* ``0x1c``: very light grey


Effect 2: board of chessboards
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    174: 92           xchg   dx,ax
    175: 29 e8        sub    ax,bp
    177: 30 e0        xor    al,ah
    179: 0c db        or     al,0xdb
    17b: 04 13        add    al,0x13
    17d: c3           ret

Equivalent C code:

.. code-block:: c

    // Horizontal sliding effet from left to right
    ax = dx - bp;
    // chessboard effect: set index to x ^ y
    al = (ax & 0xff) ^ (ax >> 8);
    // Alternate colors:
    // [0xee,0xf2,0xee,0xf2,0xee,0xf2,0xee,0xf2,
    //  0x0e,0x12,0x0e,0x12,0x0e,0x12,0x0e,0x12][(al // 4) % 16]
    return ((al | 0xdb) + 0x13) & 0xff;

Used VGA colors:

* ``0xee``: dark green
* ``0xf2``: dark green
* ``0x0e``: yellow
* ``0x12``: black

This results in a chessboard of 4x4 squares, grouped 8x8, with some chessboard yellow-and-black and others green-and-green.

Effect 1: circles, zooming
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    17e: 88 f0        mov    al,dh      ; al = Y coordinate
    180: 2c 64        sub    al,0x64    ; al = dh - 100
    182: f6 e8        imul   al         ; ax = al * al
    184: 92           xchg   dx,ax      ; dx = ax; al = X coordinate
    185: f6 e8        imul   al         ; ax = X * X
    187: 00 e6        add    dh,ah
    189: 88 f0        mov    al,dh      ; al = dh + ah
    18b: 01 e8        add    ax,bp      ; add the tick counter bp
    18d: 24 18        and    al,0x18    ; return (al + bp) & 0x18
    18f: c3           ret

Equivalent C code:

.. code-block:: c

    return (((dh_Y - 100) * (dh_Y - 100) + dh_X * dh_X) / 256 + bp) & 0x18

Used VGA colors:

* ``0x00``: black
* ``0x08``: dark grey
* ``0x10``: black
* ``0x18``: light grey

This results in rings of alternating colors, reducing to the center.

Effect 3: parallax checkerboards
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    190: 89 e9        mov    cx,bp      ; cx = timer
    192: bb f0 ff     mov    bx,0xfff0  ; bx = -16
                                        ; do {
    195: 01 f9        add    cx,di      ;   cx += di
    197: b8 33 03     mov    ax,0x333
    19a: f7 e9        imul   cx         ;   dx:ax = cx * 0x333
    19c: d1 ca        ror    dx,1       ;   dx = ror(dx, 1); CF = MSB(dx)
    19e: 43           inc    bx         ;   bx++
    19f: 77 f4        ja     0x195      ; } while (!(CF = 1 or ZF = 1))

    1a1: 8d 47 1f     lea    ax,[bx+0x1f] ; return bx + 0x1f
    1a4: c3           ret

Equivalent C code:

.. code-block:: c

    for (cx = bp_timer, bx = -15; bx != 0;bx++) {
        cx += di_pixelposition;
        if ((cx * 0x333) & 0x10000)
            break;
    }
    return 0x10 + (15 + bx);

This returns a level of grey (VGA colors between ``0x10`` for black and ``0x1f`` for white), depending on the number of iterations of the loop.

Effect 4: sierpinski rotozoomer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    1a5: 8d 8e 00 f8  lea    cx,[bp-0x800]
    1a9: c1 e1 03     shl    cx,0x3         ; cx = (timer - 0x800) * 8
    1ac: 0f b6 c6     movzx  ax,dh          ; ax = Y position
    1af: 0f be d2     movsx  dx,dl          ; dx = X position
    1b2: 89 c3        mov    bx,ax
    1b4: 0f af d9     imul   bx,cx          ; bx = ax * cx
    1b7: 00 d7        add    bh,dl          ; bh += dl
    1b9: 0f af d1     imul   dx,cx          ; dx = dx * cx
    1bc: 28 f0        sub    al,dh
    1be: 20 f8        and    al,bh
    1c0: 24 fc        and    al,0xfc        ; al = (al - dh) & bh & 0xfc
    1c2: d6           salc                  ; al = CF ? 0xff : 0
    1c3: 75 02        jne    0x1c7          ; return ZF ? 0 : 0x2a
    1c5: b0 2a        mov    al,0x2a
    1c7: c3           ret

Equivalent C code:

.. code-block:: c

    cx = (bp_timer - 0x800) * 8;
    ax = dh_Y;
    bh = ((dh_Y * cx) >> 8) + dl_X;
    dh = (dl_X * cx) >> 8;
    return (dh_Y - dh) & bh & 0xfc ? 0x2a : 0;
    // 0 is black, 0x2a is light orange


Effect 5: raycast bent tunnel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    1c8: b1 f7        mov    cl,0xf7    ; for (cl = 247; cl; cl--) {

    1ca: 52           push   dx
    1cb: 88 f0        mov    al,dh
    1cd: 2c 64        sub    al,0x64    ;   al = Y position - 100
    1cf: f6 e9        imul   cl         ;   dx = al * cl
    1d1: 92           xchg   dx,ax      ;   al = X position
    1d2: 00 c8        add    al,cl
    1d4: f6 e9        imul   cl         ;   ax = (al + cl) * cl
    1d6: 88 f0        mov    al,dh
    1d8: 30 e0        xor    al,ah
    1da: 04 04        add    al,0x4     ;   al = (dh ^ ah) + 4
    1dc: a8 f8        test   al,0xf8    ;   if (al & 0xf8) break;
    1de: 5a           pop    dx
    1df: e1 e9        loope  0x1ca      ; } (jump if count != 0 and ZF=1)

    1e1: 29 e9        sub    cx,bp      ; cx -= timer
    1e3: 30 c8        xor    al,cl      ; al ^= cl
    1e5: d4 06        aam    0x6        ; ah = al / 6 ; al = al % 6
    1e7: 04 14        add    al,0x14    ; al += 0x14
    1e9: c3           ret

Equivalent C code:

.. code-block:: c

    for (cl = 247; cl; cl--) {
        dh = ((dh_Y - 100) * cl) >> 8
        ah = ((dh_X + cl) * cl) >> 8
        al = (dh ^ ah) + 4
        if (al >= 8)
            break;
    }
    return 0x14 + ((al ^ (cl - bp_timer)) % 6);


Effect 6: ocean night / to day sky
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    1ea: 80 ee 78     sub    dh,0x78                ; if (Y < 120) return al;
    1ed: 78 10        js     0x1ff                  ;   ... al being 0xea (address)
    1ef: 89 10        mov    WORD PTR [bx+si],dx    ; [bx+si] = {y,x}
    1f1: df 00        fild   WORD PTR [bx+si]       ; Push int on the FPU stack (ST(0))
    1f3: da 38        fidivr DWORD PTR [bx+si]      ; Reverse Divide: ST(0) = *[bx+si] / ST(0)
    1f5: d9 58 ff     fstp   DWORD PTR [bx+si-0x1]
    1f8: 8b 00        mov    ax,WORD PTR [bx+si]    ; ax = 16 middle bits of ST(0)
    1fa: 01 e8        add    ax,bp
    1fc: 24 80        and    al,0x80                ; return ((al + bp_timer) & 0x80) - 1;
    1fe: 48           dec    ax
    1ff: c3           ret

This uses ``si`` from the music position and ``bx = 0x1ea`` (address of the function), so this targets random memory which is likely available.

This performs operations using the FPU (using a logarithm from the way floating points numbers are stored) to return a color which is either:

* ``0xea`` (dark pale yellow?) for the "sky" (top half of the screen)
* ``0x7f`` (dark blue) or ``0xff`` (black) for the "see" (bottom half)
