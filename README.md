# pythonfuck
a simple python to brainfuck converter <br>
being made for horizons @ hackclub <br>

## current functionality
### print()
currently print() calls are working great! <br>

previously it was extremely inefficent, since we were <br> generating direct strings (+++++++++), but now we use <br> multiplication loops to make it much much shorter <br>

we also use delta encoding to make it EVEN shorter! <br>
basically instead of resetting and re-adding the ascii values <br> each and every character, we calculate the difference <br> between them and use that! <br>

(2200~ characters -> 330~ characters, about an 85%~ reduction!)

### input()
currently input() is/SHOULD be working great! <br>

it is essentially print() which can accept input through `,` <br> it has a linefeed input, basically it'll accept input <br> until you press enter <br>

it currently serves basically no purpose since we don't have <br>variables implemented yet.

# operations/arithmetic
currently supports very basic arithmetic in functions/operations <br>

+/- works and uhh i have nothing else to say

uhh that's like all for now