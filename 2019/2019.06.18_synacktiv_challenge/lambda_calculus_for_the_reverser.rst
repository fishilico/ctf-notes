Lambda Calculus for the reverser
================================

Introduction
------------

In June 2019, Synacktiv published a summer challenge that turned out to be an interpreter for Lambda Calculus (LC).
The file provided by the challenge embedded a LC program that checked the user input and printed "Alonzo!" if it was the right one.
The user input was also expected to be a LC program, so solving the challenge required some understanding of how LC worked.

Here are some links:

* The announce: https://twitter.com/Synacktiv/status/1140969127114354688
* The challenge: https://www.synacktiv.com/posts/challenges/2019-summer-challenge-alonzo.html
* The official writeup: https://www.synacktiv.com/posts/challenges/2019-summer-challenge-writeup.html


Formal concepts
---------------

Lambda Calculus is a formal system that can be used for computing.
It uses terms that can be of 3 kinds:

* variables: x
* functions ("abstractions"): λx.F where F is a term where a variable named x can appear
* applications: (M N) where M and N are terms

For example the identity function is the function that takes a variable and returns it:

    I = λx.x

Applying the identity on another variable, y, can be expressed as:

    (I y)

In most programming languages, evaluating a function on parameters consist in replacing the parameters in the function definition by their values.
For LC, this operation is called β-reduction:

    ((λx.M) E) → (M[x:=E])

For the example:

    (I y) = ((λx.x) y) → "x where x is replaced by y" → y

A two-parameter function is expressed as a function that embeds another function.
For example, a function that takes two parameters and returns the first one, named the K combinator, is:

    K = λx.λy.x

Evaluating it on A and B leads to:

    (K A B) = ((K A) B) = (((λx.λy.x) A) B) → ((λy.A) B) → A

The definition of LC also includes α-conversion, which consists in renaming a bound variable in an expression.
A variable is said to be bound if they are in the scope of an abstraction/a function.
Otherwise it is said to be free.
For example, x is bound in λx.x but is free in λy.x

In practise, useful terms (such as functions) do not contain free variables but their terms can use free variables in order to use the function parameters.
A term that has not got free variables is said to be closed.


Applied Lambda Calculus
-----------------------

Here, the subject does not consist in proving theorems of Lambda Calculus but in understanding Synacktiv's challenge.
As such, some details will not be discussed (like η-conversion) and the β-reduction will be written with an equal sign, instead of an equivalence symbol.

Now, let's analyze Synacktiv's program.
How does it execute Lambda Calculus?
How does it handle the user input?

It starts by building a string of characters by concatenating:

* "01"
* a large string from the read-only data section of the binary (``.rodata``)
* the user input

It then calls a function that parses 0 and 1 and builds a tree using a recursive decoding:

* "00" + string_A → tree node {type=1, child=parsed(string_A)}
* "01" + string_A + string_B → tree node {type=2, children=[parsed(string_A), parsed(string_B)]}
* "10" → tree node {type=0, value=0 as 32-bit integer}
* "110" → tree node {type=0, value=1 as 32-bit integer}
* "11...10" => {type=0, value=number of "1" excluding the first one}

This is a binary encoding of a LC term using De Bruijn indices (cf. https://en.wikipedia.org/wiki/De_Bruijn_index).
In this notation, a variable is encoded by a number that counts the number of binders (the λ symbol) between an occurrence and its corresponding binder.
A tree node can be of three types:

* type=0 for a variable.
* type=1 for a function, that introduces a new variable: the child is the function term.
* type=2 for an application: the children are the function and its parameter.

Contrary to the Wikipedia article, here the indexes start at one instead of zero.
For example:

* the identity I = λx.x is encoded as: 00 10
* the K combinator K = λx.λy.x is encoded as: 00 00 110

Back to the Synacktiv's program, concatenating "01" with a large string and the user input is translated as a LC application: the large string is a LC function that is called on the user input.

Then, the program calls twice a function that adds the strings "Alonzo!" and "Invalid solution" to the parsed tree.
This also maps to LC applications.
In the end, the LC tree that is crafted looks like this:

    (((prgm input) "Alonzo!") "Invalid solution")

The large embedded LC function is named "prgm", as it is the real program that operate on the user input.
It should therefore be a 3-parameter function that checks its first parameter and returns the second one if it is correct, the third one otherwise.
The remaining code in Synacktiv's program is an implementation of a β-reduction algorithm, which computes the value of the program.

As it is possible in LC to craft programs that loop forever when they are β-reduced, the reduction needs to be bounded in time.
The implementation here includes some counters that exit the program after too many loops.


Global variables
----------------

So Synacktiv's program is a Lambda Calculus interpreter that β-reduces a large term (ie. runs a function) on the user input.
What does this term do?
If it was a usual function, it would start with "λx..." in order to capture its parameters in variables.
However it does not do that but instead starts with two applications, followed by 50-ish application-function pattern.
Using a Python script to display a LC term with variables v0, v1, etc. leads to:

    ((λv0.(λv1.(λv2.(λv3.(λv4.(λv5.(λv6.(λv7.(λv8.(λv9.
    [...]
    λv220.λv221.λv222.((v220 (v1 v222)) v221))
    λv223.v0)
    λv224.λv225.v224)
    λv226.v226)
    λv227.λv228.((v227 ...)))

In the second parameters of these applications, there are the identity function (λv226.v226) and the K combinator (λv224.λv225.v224).

Said in another way, the program uses: ((λx.E) I) where E is a term that use x as the identity function I.
This construction can be used to define some kind of variables that are constant (they do not depend on the function inputs) and used in the main code (E in the example).
Let's call these variables "global variables".

In the reverse engineering world, a quick way of gaining a better understanding of a subject and of grasping an overview of a problem consists in naming things.
Instead of performing β-reduction (ie. instead of executing the function), let's name the global variable terms accordingly to their use and use these names while writing LC terms.


Building blocks
---------------

Most websites about Lambda Calculus define three terms as a basis to build other terms:

* The identity: I = λx.x
* The K combinator: K = λx.λy.x
* The S combinator: S = λx.λy.λz.x z (y z)

K can be used to define "constant functions", as (K x) is a function that takes one parameter, y, and always returns x.
S can be seen as a generalized version of application: (S x y) is a function that takes one parameter, z, and returns x' applied to y' where x' and y' are the result of substituting z into x and y.

Alonzo Church defined a way to encode booleans and integers using Lambda Calculus: the Church encoding (https://en.wikipedia.org/wiki/Church_encoding).
In this encoding, a boolean is a function of two variables that returns the first one in order to mean "true" and the second one to mean "false".
This means that:

* True = λt.λf.t = K
* False = λt.λf.f = λt.I = (K I)

Conditional expressions (If-Then-Else constructions) can be built using a function that takes 5 parameters: a condition C, an expression if C is true, T, an expression if C is false, and two variables to encode a boolean:

    If = λC.λT.λF.λt.λf. (C (T t f) (F t f))

This expression can be simplified into:

    If = λC.λT.λF. (C T F)

Likewise, some operations can be defined between to boolean predicates:

* And = λp.λq.p q p = λp.λq.λt.λf.p (q t f) f
* Or = λp.λq.p p q  = λp.λq.λt.λf.p t (q t f)
* Not = λp.λt.λf.p f t  (With evaluation strategy being applicative order)
* Xor = λp.λq.p (Not q) q = λp.λq.p (λt.λf.q f t) q

Then, Church defined an encoding of numbers: a number n is a function of two variables, f and x, that returns (ie. β-reduces to) the result of n applications of f on x:

    n f x = :math:`f^n(x)`

Therefore:

* 0 = λf.λx.x = K I = False
* 1 = λf.λx.f x
* 2 = λf.λx.f (f x)
* 3 = λf.λx.f (f (f x))
* etc.

In mathematics, a way to define the set of natural numbers consists in defining zero and a successor function (this relies on Peano axioms).
In Lambda Calculus, the successor function of Church's encoding is the function that maps a number, n, to a function of two variables, f and x, that returns the result of n+1 applications of f on x:

    Succ = λn.λf.λx.f (n f x)

The main arithmetic functions can then be defined as:

* Addition: Plus = λm.λn.λf.λx m f (n f x)
* Multiplication: Mult = λm.λn.λf.λx.m (n f) x
* Exponentiaion: Exp = λm.λn.m n

Moreover, it is possible to check whether a number is zero by applying it to a function that returns False it is called:

    IsZero = λn.n (λx.False) True

The predecessor function, named Pred, is a little bit more complex to build:

* First, let's define a container function that maps a value v and a function h to h(v):

      value = λv.λh.h v

* Second, let's define an increment function on this container:

  * init = value x
  * inc init = value (f x)
  * inc (inc init) = value (f (f x))
  * etc.

* Then, with any v and f, inc (value v) = value (f v). Let g = (value v). Then:

  * g f = value v f = f v
  * inc g = value (f v) = value (g f) = (λv.λh.h v) (g f) = λh.h (g f)
  * So, inc = λg.λh.h (g f)  (This function is specific to the context where f is a function seen as first parameter of a number)

* Third, there is a way to extract a value from its container, by applying the identity function:

      extract = λk.k I

* This allows building a function that takes a number and returns this number:

      samenum = λn.λf.λx.n f x = λn.λf.λx.extract (value (n f x)) = λn.λf.λx.extract (n inc init)

* To implement Pred, all that is needed is to replace init with a function that does not apply f at the first iteration. This is function const:

  * inc const = value x
  * λh.h (const f) = λh.h x
  * This equation is satisfied with const = λf.x

* Therefore: Pred = λn.λf.λx.extract (n inc const) = λn.λf.λx.(n inc const) I

      Pred = λn.λf.λx.(n (λg.λh.h (g f)) (λu.x)) (λv.v)

This leads to defining three more operations:

* Subtraction: Minus = λm.λn.(n Pred) m
* Lower or equal: LEQ = λm.λn.IsZero (Minus m n)
* Equal: EQ = λm.λn.And (LEQ m n) (LEQ n m)

If you feel like you missed understanding the key ideas of this section, https://learnxinyminutes.com/docs/lambda-calculus/ or Wikipedia might provide clearer explanations.


Back to the program
-------------------

Now let's take a look at the first global variables that are defined by Synacktiv's program, as displayed by `<writeup.py>`_:

* Globvar_0 is λv226.v226
* Globvar_1 is λv224.λv225.v224
* Globvar_2 is λv223.Globvar_0

So Globvar_0 is the identity I, Globvar_1 is the K combinator, used in order to encode True, and Globvar_2 is λt.I, which means False.

The next variables matches Church's encoding of booleans and numbers:

* Globvar_3 is λv220.λv221.λv222.((v220 (True v222)) v221) = IsZero
* Globvar_4 is λv217.λv218.λv219.(v218 ((v217 v218) v219)) = Succ
* Globvar_5 is (Succ False) = Number_1
* Globvar_6 is (Succ Number_1) = Number_2
* Globvar_7 is (Succ Number_2) = Number_3
* Globvar_8 is λv213.λv214.λv215.λv216.((v213 v215) ((v214 v215) v216)) = Or
* Globvar_9 is λv208.λv209.λv210.(((v208 λv211.λv212.(v212 (v211 v209))) (True v210)) Identity) = Pred
* Globvar_10 is λv206.λv207.((v207 Pred) v206) = Minus
* Globvar_11 is λv204.λv205.(IsZero ((Minus v204) v205)) = LEQ
* Globvar_12 is λv201.λv202.λv203.(v201 (v202 v203)) = Mult
* Globvar_13 is ((Mult Number_3) Number_3) = Number_9
* Globvar_14 is λv199.λv200.v199 = True
* Globvar_15 is λv197.λv198.v198 = False
* Globvar_16 is λv193.λv194.λv195.λv196.((v193 ((v194 v195) v196)) v196) = And
* Globvar_17 is λv189.λv190.λv191.λv192.((v189 v191) ((v190 v191) v192)) = Or
* Globvar_18 is λv186.λv187.λv188.((v186 v188) v187) = Not
* Globvar_19 is λv184.λv185.((And ((LEQ v184) v185)) ((LEQ v185) v184)) = EQ
* Globvar_20 is λv182.λv183.v183 = False

Then, there is something unknown:

* Globvar_21 is λv178.λv179.λv180.λv181.((v180 v178) v179)
* Globvar_22 is λv177.(v177 True)

Moreover, the *main function* (that results from the simplification of all the global variables) only invoking Globvar_50 on a term that uses an unknown construction:

    (Globvar_50 λv227.λv228.((v227 λv229.λv230.((v229 λv231.λv232.(v231 (v231 (v231 (v231 v232))))) ... λv581.λv582.((v581 λv583.λv584.v584) λv585.λv586.v586)))))))))) λv587.λv588.v588))))))))))


Lists and arrays
----------------

The *main function* of the Lambda Calculus of the program uses a construction that includes many False instances and some numbers, but with an unknown encoding. For example it ends with:

    λv549.λv550.((v549 Number_1) λv553.λv554.((v553 False)
    λv557.λv558.((v557 Number_4) λv561.λv562.((v561 False)
    λv565.λv566.((v565 False) λv569.λv570.((v569 False)
    λv573.λv574.((v573 False) λv577.λv578.((v577 False)
    λv581.λv582.((v581 False) False)))))))))) False))))))))))

Let's name a few terms:

* t581 = λv581.λv582.((v581 False) False)
* t577 = λv577.λv578.((v577 False) t581)
* t573 = λv573.λv574.((v573 False) t577)
* etc.
* t549 = λv549.λv550.((v549 Number_1) t553)

This looks like a list of items: [1, 0, 4, 0, 0, 0, 0, 0, 0], built by concatenating values to existing lists.
This is like the list construction operator (Cons) of some programming langages such as OCaml. Applied on a head h and tail t:

    Cons h t = λx.λy.(x h t)

The empty list seems to be encoded as False, which is λx.λy.y.

These semantics mean that a list is encoded as a function that takes two parameters, x and y, and that returns y if empty and (x h t) otherwise, with h its head and t its tail.

This simplifies the term of the main function to a list of 9 lists of 9 numbers each::

    [
        [4, 0, 0, 0, 0, 0, 8, 0, 5],
        [0, 3, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 7, 0, 0, 0, 0, 0],
        [0, 2, 0, 0, 0, 0, 0, 6, 0],
        [0, 0, 0, 0, 8, 0, 4, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 6, 0, 3, 0, 7, 0],
        [5, 0, 0, 2, 0, 0, 0, 0, 0],
        [1, 0, 4, 0, 0, 0, 0, 0, 0],
    ]

Let's call it Table9x9.

In order to operate on these lists, some functions need to be defined.
The program includes the following global variables:

* Globvar_21 is λv178.λv179.λv180.λv181.((v180 v178) v179)
* Globvar_22 is λv177.(v177 True)
* Globvar_23 is λv174.((v174 λv175.λv176.v176) False)
* Globvar_24 is λv171.((v171 λv172.λv173.False) True)

The first one is already known as Cons.
If the second one is applied to a list l and a value v, it β-reduces to:

    Globvar_22 l v = (λv177.v177 True) l v = l (λh.λt.h) v

If l is empty, (Globvar_22 l v) = v, so v is the return value for empty lists.
Otherwise, l has a head h and a tail t and (l (λh.λt.h) v) = ((λh.λt.h) h t) = h.
Therefore, Globvar_22 is a function that takes as argument a list and a value and returns the head of the list if possible, otherwise the value.
Let's call this function Head.

Likewise:

    Globvar_23 l = l (λh.λt.t) False = "t if l is not empty, False otherwise"

This is a function for getting the tail of a list.
Let's call it Tail.

Then:

    Globvar_24 l = l (λh.λt.False) True

This function returns True if the list is empty, False otherwise.
Let's call is IsListEmpty.

This encoding of lists is not Church's one.
It seems that this better matches the encoding published by Dana Scott, which can be found in https://users.fit.cvut.cz/~staryja2/MIMSI/scott-lambda-calculus-some-models-some-philosophy.pdf.


The fixed-point combinator
--------------------------

The next global variable uses a new concept:

    Globvar_25 is (λv164.(λv165.(v165 v165) λv166.(v164 (v166 v166)))
    λv167.λv168.((v168 λv169.λv170.(Succ (v167 v170))) False))

Let's call Y the first part of the expression and rename some bound variables:

    Y = λf.(λx.(x x) λy.(f (y y)))

Y is a closed expression.
When applied to a function, it β-reduces to:

    Y f = (λx.(x x) λy.(f (y y))
    = (λy.(f (y y)) λz.(f (z z)))
    = (f (λz.(f (z z)) λt.(f (t t))))
    = (f (Y f))

The β-reduction never ends!
Y is called the fixed-point combinator and it has a whole Wikipedia article dedicated to itself: https://en.wikipedia.org/wiki/Fixed-point_combinator#Y_combinator.
There is also a news website with its name! https://news.ycombinator.com/.
It is the main building-block that allows using loops and recursion in Lambda-Calculus.

For example the function that computes the factorial of a number can be defined as:

    Factorial = Y F with F = λf.λn.(IsZero n) 1 (Mult n (f (Pred n)))

The β-reduction yields to:

    Factorial 0 = Y F 0 = F (Y F) 0 = F Factorial 0
    = (IsZero 0) 1 (Mult 0 (Factorial (Pred 0)))
    = True 1 (Mult 0 (Factorial (Pred 0)))
    = 1

And for n greater than 0:

    Factorial n = F Factorial n
    = (IsZero n) 1 (Mult n (Factorial (Pred n)))
    = False 1 (Mult n (Factorial (Pred n)))
    = Mult n (Factorial (Pred n))

Now, let's get back to Synacktiv's LC term:

    Globvar_25 is (λv164.(λv165.(v165 v165) λv166.(v164 (v166 v166))) λv167.λv168.((v168 λv169.λv170.(Succ (v167 v170))) False))

Renaming some variables lead to:

    Globvar_25 = Y λf.λl.((l λh.λt.(Succ (f t))) 0)

Here is a way to read this How to read this definition:

* f is the recursive function which is defined
* l is the list given as a parameter
* h is the head of the list
* t is the tail of the list
* (l x y) β-reduces to y if the list is empty, or to (x head tail) if the list is (Cons head tail)
* (Succ (f t)) is a function that adds 1 to the value of the recursive function on the tail
* Globvar_25 returns 0 on an empty list.

Therefore Globvar_25 computes the length of a list.
Let's call this function Length.

The next global variables are:

* Globvar_26 = (Y λf.λfct.λl.((l λh.λt.(Cons (fct h) (f fct t))) False)) = Map (map function fct on items of list l and return a new list)
* Globvar_27 = (Y λf.λl1.λl2.((l1 λh.λt.(Cons h (f t l2))) l2)) = Concat (concatenate two lists)
* Globvar_28 = (Y λf.λfct.λres.λl.((l λh.λt.(fct h (f fct res t))) res)) = Reduce (combine the items of a list using a function that maps a value and a previous result to a new result, and a default result if the list is empty)
* Globvar_29 = Reduce Concat False = Flatten2DList (concatenate the sublists of a 2D-list)
* Globvar_30 = (Y λf.λfct.λlA.λlB.(lA λhA.λtA.(lB λhB.λtB.((Cons (fct hA hB)) (f fct tA tB)) False) False)) = MapTwoListsTogether (map function fct on items of lists lA and lB and return the list of results)
* Globvar_31 = λn.λx.(n (Cons x) False) = Repeat (build a list by repeating n times a value x)
* Globvar_32 = λfct.(Reduce λitem.λres.(And (fct item) res) True) = AllTrueForEach (call a boolean function fct on every item of the list and return True if the list is empty or if every call returned True)


The real checks
---------------

Up to now, every global variable defined a LC function related to booleans, numbers and lists.
The only thing that was specific was the parameter used by the main function, which turned out to be a 9x9 list of integers, called Table9x9.

The main function is thus simplified to:

    (Globvar_50 Table9x9)

The last global variable which is defined as::

    Globvar_50 = λv51.λv52.
      (And
        (And
          (And
            (And
              (AllTrueForEach
                Identity
                (MapTwoListsTogether Globvar_47 v51 v52)
              )
              (AllTrueForEach Globvar_40 v52)
            )
            (AllTrueForEach Globvar_40 (Globvar_41 v52))
          )
          (AllTrueForEach Globvar_40 (Globvar_45 v52))
        )
        (Globvar_44 v52)
      )

Globvar_50 takes two parameters, performs several checks on them and returns a boolean.
Synacktiv's challenge applies the main function to three parameters: the user input and the strings "Alonzo!" and "Invalid solution".
This leads to executing:

    (Globvar_50 Table9x9 UserInput "Alonzo!" "Invalid solution")

According to Church's encoding of booleans, this is equivalent to writing in another programming language::

    if (Globvar_50(Table9x9, UserInput)) {
        return "Alonzo!"
    } else {
        return "Invalid solution"
    }

Now, let's find out what Globvar_50 does, by naming the used global variables.
For this, let's call a list of 9 lists of 9 numbers a *grid*.

* Globvar_41 is λgrid.(Reduce (MapTwoListsTogether Cons) (Repeat (Length (Head grid False)) False) grid) = SwapGridDimensions (swap the lines and the columns by computing a list of 9 empty lists, then calling Reduce with MapTwoListsTogether Cons in order to merge the last line as a last columns, then calling again for the previous line, etc.)
* Globvar_42 is (Y λf.λl.(l λh1.λt1.(t1 λh2.λt2.(t2 λh3.λt3.(Cons (Cons h1 (Cons h2 (Cons h3 False))) (f t3)) (Cons (Cons h1 (Cons h2 False)) False)) (Cons (Cons h1 False) False)) False)) = SplitListIn3ItemsList (split a list in sub-lists of 3 items each)
* Globvar_43 is λl.(EQ (Length l) Number_9) = IsLength9 (check that the length of a list is 9)
* Globvar_44 is λgrid.(And (IsLength9 grid) (AllTrueForEach IsLength9 grid)) = Is9x9List (check that this is 9x9 grid)
* Globvar_45 is λgrid.(Map Flatten2DList (Flatten2DList (Map SplitListIn3ItemsList (SwapGridDimensions (Map SplitListIn3ItemsList grid))))) = Group3x3Squares (group the 9 3x3 squares of a grid to a list of 9 lists of numbers)
* Globvar_46 is λx.λy.(And (And (Not (IsZero y)) (LEQ y Number_9)) (Or (IsZero x) (EQ x y))) = [x,y→0<y<=9&&(x==0||x==y)] (perform some checks on two numbers)
* Globvar_47 is λlA.λlB.(AllTrueForEach Identity (MapTwoListsTogether [x,y→0<y<=9&&(x==0||x==y)] lA lB)) = MatchPatternListOfNumbers (match the number in list lB with the pattern defined in list lA)

This leads to simplifying the main function as::

    main = λgrid.
      (And
        (And
          (And
            (And
              (AllTrueForEach
                Identity
                (MapTwoListsTogether MatchPatternListOfNumbers Table9x9 grid)
              )
              (AllTrueForEach Globvar_40 grid)
            )
            (AllTrueForEach Globvar_40 (SwapGridDimensions grid))
          )
          (AllTrueForEach Globvar_40 (Group3x3Squares grid))
        )
        (Is9x9List grid)
      )

The user input is expected to be a grid that verifies 5 conditions:

* it contain numbers that matche the pattern defined in Table9x9
* Globvar_40 returns True for every line of the grid
* Globvar_40 returns True for every column of the grid (because columns are the lines of (SwapGridDimensions grid))
* Globvar_40 returns True for every 3x3 sub-square of the grid (because squares are the lines of (Group3x3Squares grid))
* it is a 9x9 grid

These are the rules of a Sudoku!
Globvar_40 may be a function that checks that a list of 9 integers contain all the numbers between 1 and 9.
Without needed to fully understand this function, it is possible to craft an input for the program.

The given Sudoku has one solution, which is::

    4 1 7 | 3 6 9 | 8 2 5
    6 3 2 | 1 5 8 | 9 4 7
    9 5 8 | 7 2 4 | 3 1 6
    ------+-------+------
    8 2 5 | 4 3 7 | 1 6 9
    7 9 1 | 5 8 6 | 4 3 2
    3 4 6 | 9 1 2 | 7 5 8
    ------+-------+------
    2 8 9 | 6 4 3 | 5 7 1
    5 7 3 | 2 9 1 | 6 8 4
    1 6 4 | 8 7 5 | 2 9 3

Translating it directly to a LC term leads to something too large for a terminal.
By defining global variables like Synacktiv did, it is possible to craft an input which is accepted by the solver: `<solution.out.txt>`_:

.. code-block:: sh

    $ firejail --net=none --nonewprivs --x11=none --private ./alonzo_v2 $(cat solution.out.txt)
    Alonzo!


After the end: the last global variables
----------------------------------------

While studying the global variables, those between Globvar_33 and Globvar_40 have not been described:

* Globvar_33 is λv121.λv122.v122 = False
* Globvar_34 is λv116.λv117.λv118.λv119.λv120.(v119 v116 v117 v118)
* Globvar_35 is (Y λf.λv111.λv112.(v112 λv113.λv114.λv115.(LEQ v111 v114 (Globvar_34 (f v111 v113) v114 v115) (Globvar_34 v113 v114 (f v111 v115))) (Globvar_34 False v111 False)))
* Globvar_36 is (Y λf.λv102.λv103.(v103 λv104.λv105.λv106.(EQ v102 v105 True (LEQ v102 v105 (f v102 v104) (f v102 v106))) False))
* Globvar_37 is (Y λf.λv94.(v94 λv95.λv96.λv97.(Succ (Or (f v95) (f v97))) False))
* Globvar_38 is (Y λf.λv86.λl.(l λh.λt.(Globvar_36 h v86 False (f (Globvar_35 h v86) t)) (EQ (Globvar_37 v86) Number_9)))
* Globvar_39 is (Y λf.λv78.λv79.(v79 λv80.λv81.(Globvar_36 v80 v78 v78 (f (Globvar_35 v80 v78) v81)) v78))
* Globvar_40 is (Globvar_38 Globvar_33) = (Globvar_38 False)

What do these LC terms do?
Globvar_40 is called on a list of nine numbers in order to check the Sudoku rules on it.
(Globvar_40 list) gets β-reduced to (Globvar_38 Globvar_33 list), where Globvar_33 is simply False.
It is strange to define False again: it is already Globvar_2, Globvar_15 and Globvar_20.
But when looking at the usages, it appears that Globvar_2 is used as "number 0", Globvar_15 as "False" and Globvar_20 as "Empty list".
Globvar_33 is probably the "empty" of a new kind of object, that is used to store the numbers of the list.

In Globvar_37's expression, Using "Succ (Or (...))" looks suspicious: Or returns a boolean, not a number.
By looking at the definition of Or, it appears it is equivalent to the addition:

* Or = λp.λq.λt.λf.p t (q t f)
* Plus = λm.λn.λf.λx m f (n f x)

Therefore Globvar_37 is a recursive function that loops other its parameter, v94, in order to compute something that may be Globvar_37(v95) + Globvar_37(v97) + 1 when v95 and v97 are items of v94.
This feels limilar to the definition of Length for lists, but for binary trees: a node v94 may be either empty or with two children.

Let's take a step back and try to define something that looks like a binary tree that matched the global variables:

    A binary tree is a function that takes two parameters:

    * a function that takes three parameters, λleft.λval.λright which is called with a node that has a value val and two children trees, left and right
    * a value which is returns when the tree is empty

An empty tree would then be λf.λv.v, which matches with Globvar_33 = False.
Let's call this EmptyTree.

Globvar_34 is like Cons for lists, it builds a tree out of its components:

    Globvar_34 = λleft.λval.λright.λnodefct.λempty.(nodefct left val right) = ConsTree

Globvar_37 would count the number of nodes in a tree:

    Globvar_37 = (Y λf.λtree.(tree λleft.λval.λright.(Succ (Plus (f left) (f right))) Number_0)) = TreeLength

Globvar_36 checks whether a number is in the tree, which is a sorted binary tree:

    Globvar_36 = (Y λf.λn.λtree.(tree λleft.λval.λright.(EQ n val True (LEQ n val (f n left) (f n right))) False)) = IsInTree

Globvar_35 adds a number to a tree, respecting the sort order:

    Globvar_35 = (Y λf.λn.λtree.(tree λleft.λval.λright.(LEQ n val (ConsTree (f n left) val right) (ConsTree left val (f n right))) (ConsTree EmptyTree n EmptyTree))) = InsertInTree

Globvar_39 is an unused function that inserts numbers into a tree unless a number already exists and returns the resulting tree:

    Globvar_39 = (Y λf.λtree.λl.(l λh.λt.(IsInTree h tree tree (f (InsertInTree v80 tree) t)) tree)) = FillTreeFromList

Then comes the recursive function that inserts numbers from a list into the sorted binary tree and checks that the tree contains 9 distinct items in the end:

    Globvar_38 = (Y λf.λtree.λl.(l λh.λt.(IsInTree h tree False (f (InsertInTree h tree) t)) (EQ (TreeLength tree) Number_9))) = FillTreeFromListAndCheck9

The final check calls this function with an empty tree:

   Globvar_40 = (FillTreeFromListAndCheck9 EmptyTree) = Check9DistinctNumbers


Conclusion
----------

Synacktiv's summer challenge was fun and interesting.
Many thanks to the author, who achieved in creating something that is quite out of the ordinary.
I have not encountered Lambda Calculus since my studies, where I implemented a kind of compiler for Lambda Calculus in Coq (its repo is still available on https://github.com/fishilico/INF565-coq-project).

I tried to write down in this document the steps I followed in order to solve the challenge.
If there are bugs or if something looks strange, feel free to open issues and to submit pull requests to fix things up.

Thank you for reading!


Epilogue: the bonus level
-------------------------

Once Synacktiv's challenge was over, the author published a larger function on https://www.synacktiv.com/posts/challenges/2019-summer-challenge-writeup.html::

    010001000100010001000100010001000100010001000100010001000100000001010000
    000001011111001011110110101001010000000001011111001011110110101001010000
    000001011111001011110110101001010000000001011111001011110110101001011111
    111000100101011111111100000010111111111100010010101111111111100000010100
    000000010111110010111101101010000001011110000101010111111111111111111111
    110111101111111111111111111110111011010000001011111000010101011111111111
    111111111101111101111011101101101101011010010111111110111111010010111111
    110111111001111110100101111111101111110010111111111111011111111100111111
    111100101111111111110111100111111001011111111111101111010000001010111111
    011100101010111111111101111101110110101000010111111111111001111111111101
    011111111111100100011010000100000101100000010110000001011000000101000000
    000101110111101110000001011101111111100000010111011111111000000101110111
    111110000010011111111101000000101110000001011101111111100000010111011111
    111000001000001000000101110000001011101111110000010000010000010011010000
    101011111110011111000000000010111011110111001010111111111001011000001100
    000100000000101110000010111000001010010100011010000000010110000001010101
    010001101000010000000101100000000101010111111111111111111110111110110000
    011001010101111111111111111111111011111011001011111110111110111001011111
    110111110100000100110101101111000001001010111111011111001010100011010000
    100000001011000000001010101111111111111111111111011111011001010100000000
    000101011101111101111011100101111111011111011101101000000101011101111101
    111001011111111101111111011100000010101110000010111100000100110101101111
    010010111111111110010100011010000100000101100000000111111111111111111111
    000000101011111111011111011001010111111110111011010000010011010110111111
    111110000010000101111100000000001010111111011110010111101101010000011001
    000110100001000000000101110000001011110000001010000000001011101111011100
    101111111101111011001010111111111011111110111010000010000010011010010110
    010001101000000001011100000000001011101111001010111111110111111101110111
    110100000100100011010000000000101100000010111111011001010101111111011111
    101111101111010110010001101000000001011000000000010111001111111011110010
    101111111101111111011111101110000010010001101000000101100000011111111110
    010111110111101000001000000101000000000101111100101111011010100101111101
    101001011111010110000111100111101000000000010101011110000000010101111000
    000110011101111000110001011110001101100110011001100000100000000111001011
    11011010

This used the same functions as the challenge, but in a more compact form.
Using the same simplifications lead to the following global variables (obtained from script `<bonus_level.py>`_):

* BonusGlobvar_0 is Succ
* BonusGlobvar_1 is Number_3
* BonusGlobvar_2 is LEQ
* BonusGlobvar_3 is Number_9
* BonusGlobvar_4 is EQ
* BonusGlobvar_5 is Length
* BonusGlobvar_6 is Map
* BonusGlobvar_7 is Reduce
* BonusGlobvar_8 is Flatten2DList
* BonusGlobvar_9 is MapTwoListsTogether
* BonusGlobvar_10 is AllTrueForEach
* BonusGlobvar_11 is Check9DistinctNumbers
* BonusGlobvar_12 is SwapGridDimensions
* BonusGlobvar_13 is SplitListIn3ItemsList
* BonusGlobvar_14 is IsLength9

Then, the main function of this program does not include a Sudoku grid, but is the checker::

    main = λpattern.λinput.(
      (And
        (And
          (And
            (And
              (AllTrueForEach
                Identity
                (MapTwoListsTogether MatchPatternListOfNumbers pattern input)
              )
              (AllTrueForEach Check9DistinctNumbers input)
            )
            (AllTrueForEach Check9DistinctNumbers (SwapGridDimensions input))
          )
          (AllTrueForEach
            Check9DistinctNumbers
            (Map Flatten2DList
              (Flatten2DList
                (Map SplitListIn3ItemsList
                  (SwapGridDimensions
                    (Map SplitListIn3ItemsList input)
                  )
                )
              )
            )
          )
        )
      )
      λtrue.λfalse.(
        IsLength9 input (AllTrueForEach IsLength9 input true false) false
      )
    )
