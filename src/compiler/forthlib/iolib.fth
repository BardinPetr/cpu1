\ prints string by its address, string in pascal format
: type ( addr -- )
  dup @             \ read length
  0 do
    1+ dup @ emit
  loop
  drop              \ drop last addr
;

\ read line of input before \n into variable pointed by addr, string in pascal format
: read ( -- addr )
  dup              \ save one copy to write len in the end
  begin
    1+             \ increase pointer
    key dup        \ get key and copy for comparison
    10 <>          \ compare \n
  while
    over !         \ copy address and store character
  repeat
  drop             \ remove copy of key
  over - 1-        \ copy base address and calculate string length
                   \ decrease because 1 for \n
  swap !           \ store length in at addr
;
