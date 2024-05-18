```
 +       ( n1 n2 -- n1+n2 )
 -       ( n1 n2 -- n1-n2 )
 *       ( n1 n2 -- n1*n2 )   \ Signed multiplication
 /       ( n1 n2 -- n1/n2 )   \ Signed division
 mod     ( n1 n2 -- n1%n2 )
 and     ( n1 n2 -- n1&n2 )
 or      ( n1 n2 -- n1|n2 )
 invert  ( n -- ~n )          \ Bitwise logical inversion
 negate  ( n -- -n )          \ Arithmetic negation, i.e. 0-n
 1-      ( n -- n-1 )         \ Decrement by 1
 1+      ( n -- n+1 )         \ Increment by 1  
 true   ( -- -1 )        \ Pushes true (-1)
 false  ( -- 0 )         \ Pushes false (0)
 
 dup  ( a -- a a )
 drop ( a -- )
 swap ( a b -- b a )
 over ( a b -- a b a )
 
 @  ( adr -- l )    \ Fetch a 32-bit value
 !  ( l adr -- )    \ Store a 32-bit value
 +!  ( l adr -- )    \ Increase by l a 32-bit value
 
 i ( -- iter ) \get most inner for-loop counter
 
 =    ( n1 n2 -- flag )  \ True if n1 = n2
 <>   ( n1 n2 -- flag )  \ True if n1 != n2
 <    ( n1 n2 -- flag )  \ True if n1 < n2  (signed)
 >    ( n1 n2 -- flag )  \ True if n1 > n2  (signed)
 <=   ( n1 n2 -- flag )  \ True if n1 <= n2  (signed)
 >=   ( n1 n2 -- flag )  \ True if n1 >= n2  (signed)
 0=   ( n -- flag )      \ True if n = 0   (logical not, like '!' in C)
 0<>  ( n -- flag )      \ True if n != 0
 0<   ( n -- flag )      \ True if n < 0
 0>   ( n -- flag )      \ True if n > 0
 0<=  ( n -- flag )      \ True if n <= 0
 0>=  ( n -- flag )      \ True if n >= 0
 
 2dup   ( $ -- $ $ )                   \ Stack copy of string limits
 2drop  ( $ -- )                       \ Discard string limits
 
 io@  ( dev reg -- v )  blocking read device[register]
 io!  ( val dev reg -- )  blocking write device[register]
 
 . ( n -- )      \ output byte
 emit ( c -- )   \ output char
 cr ( -- )       \ output \n
 ." ( -- )       \ output const string
 type   ( $ -- ) \ output const string
 key ( -- n )    \ blocking read byte
 ```
 
 
 ```
 maybe implement:
 u<   ( u1 u2 -- flag )  \ True if n1 < n2  (unsigned)
 u>   ( u1 u2 -- flag )  \ True if n1 > n2  (unsigned)
 u<=  ( u1 u2 -- flag )  \ True if n1 <= n2  (unsigned)
 u>=  ( u1 u2 -- flag )  \ True if n1 >= n2  (unsigned)
 /mod    ( n1 n2 -- n1%n2 n1/n2 )
 xor     ( n1 n2 -- n1^n2 )
 lshift  ( n1 n2 -- n1<<n2 )
 <<      ( n1 n2 -- n1<<n2 )  \ Synonym for lshift
 >>      ( n1 n2 -- n1>>n2 )  \ Synonym for rshift
 rshift  ( n1 n2 -- n1>>n2 )  \ Zero-extends
 >>a     ( n1 n2 -- n1>>n2 )  \ Sign-extends
 abs     ( n -- u )           \ Absolute value
 max     ( n1 n2 -- max )     \ Signed maximum
 min     ( n1 n2 -- min )     \ Signed minimum
 umax    ( u1 u2 -- max )     \ Unsigned maximum
 umin    ( u1 u2 -- min )     \ Unsigned minimum
 2/      ( n -- n/2 )         \ Divide by 2
 2*      ( n -- n*2 )         \ Multiply by 2 
 between  ( n low high -- flag )  \ True if low <= n <= high
 within   ( n low high -- flag )  \ True if low <= n <  high
```