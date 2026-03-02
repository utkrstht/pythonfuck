# pythonfuck
a simple python to brainfuck converter <br>
being made for horizons @ hackclub <br>

## current functionality
currently print() calls are working great! <br>

previously it was extremely inefficent, since we were <br> generating direct strings (+++++++++), but now we use <br> multiplication loops to make it much much <br>

we also use delta encoding to make it EVEN shorter! <br>
basically instead of resetting and re-adding the ascii values <br> each and every character, we calculate the difference <br> between them and use that! <br>

(2200~ characters -> 330~ characters, about an 85%~ reduction!)

uhh that's like all for now