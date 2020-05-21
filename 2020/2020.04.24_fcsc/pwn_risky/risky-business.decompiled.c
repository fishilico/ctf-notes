// Simplified program

fgets(a0 = var_96, a1=67, a2 = stdin):

var_108 = strlen(var_96);
var_120 = var_108 - 1
var_116 = var_108 - 1

var_128 = (var_96[var_116--] >> 4) & 0xff
var_112 = (var_108 - 1) * 2

while (var_112 >= 0) {
    if (var_112 & 1) {
        var_124 = (var_96[var_116--] >> 4) & 0xff;
    } else {
        var_124 = var_96[var_120--] & 0xf;
    }
    if (var_128 == 7 && var_124 == 3) return 0; // Filter 00000073 ecall
    if (var_128 == 0 && var_124 == 0) return 0;
    if (var_128 == 0 && var_124 == 0xa) return 0;
    var_128 = var_124;
    var_112 --;
}
var_104 = &var_96
call var_104
return 0;
