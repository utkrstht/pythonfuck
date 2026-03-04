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


### operations/arithmetic
currently supports very basic arithmetic in functions/operations <br>

+/-/division/* are supported, however due to brainfuck cells <br> being 8-bit integers, they cannot store floating point values.

### variables
we now have variables!!!

i completely reworked the compiler since it now requires a state remembering thing to remember the state/value of the variables and uh yeah

ahh, after so long it's working, so the variables can now store
proper string and integers, and do not convert them to their ascii representation!! <br>

### if/else statements + comparision
we now have if/else statements, uhh no elif though.

this is like half working, i think there's something wrong with the else statement but like idk 

we have all the comparision operators as well (!=, ==, >, <)

uhh that's like all for now