.. code:block::sh

    $ (echo '(\\x.x x) (\\y.y)' | tee /dev/tty ; cat ) | socat - TCP:qual-challs.rtfm.re:10003
    (\x.x x) (\y.y)
    No flag for you!

    $ (echo '(\\y.(\\x.y y)) (\\x.x)' | tee /dev/tty ; cat ) | socat - TCP:qual-challs.rtfm.re:10003
    (\y.(\x.y y)) (\x.x)
    Congratulations! Flag: sigsegv{c4nt_h4v3_th0s3_tw0_b1nd1ngs}
