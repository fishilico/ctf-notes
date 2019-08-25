#!/usr/bin/env python3
"""
Writeup for Synacktiv's summer challenge 2019

https://www.synacktiv.com/posts/challenges/2019-summer-challenge-alonzo.html
"""
from pathlib import Path
import re
import sys


ALONZO_CHALLENGE = Path(__file__).parent / 'alonzo_v2'


def str_to_tree_rec(s):
    """
    Transform an input binary string to a tree

    - 00 + text => {type=1, from(text)} => [str_to_tree(text)]
    - 01 + A + B => {type=2, from(A), from(B)} => [str_to_tree(A), str_to_tree(B)]
    - 10 => {type=0, value_u32=0} => 0
    - 1 {111111111} 0 => {type=0, value_u32 = number of 1} => number of 1
    """
    if s[0] == '0':
        if s[1] == '0':
            child, s = str_to_tree_rec(s[2:])
            return [child], s
        else:
            assert s[1] == '1'
            first_child, s = str_to_tree_rec(s[2:])
            second_child, s = str_to_tree_rec(s)
            return [first_child, second_child], s
    else:
        assert s[0] == '1'
        idx = 1
        while s[idx] == '1':
            idx += 1
        return (idx - 1), s[idx + 1:]


def str_to_tree(s):
    """Transform an input binary string to a tree"""
    tree, remaining = str_to_tree_rec(s)
    assert remaining == '', f"unexpected {repr(remaining)}"
    return tree


def tree_to_str(tree):
    """Reverse str_to_tree"""
    if isinstance(tree, int):
        return '1' + ('1' * tree) + '0'
    if isinstance(tree, str):
        # Replace strings by 0
        return '10'
    if len(tree) == 1:
        return '00' + tree_to_str(tree[0])
    assert len(tree) == 2
    return '01' + tree_to_str(tree[0]) + tree_to_str(tree[1])


# Sanity checks
assert str_to_tree('0010') == [0]  # I = λx.x
assert str_to_tree('0000110') == [[1]]  # K = λx.λy.x
assert tree_to_str([0]) == '0010'
assert tree_to_str([[1]]) == '0000110'


def display_prog(tree, indent='', depth_of_ones=0, fd=sys.stdout):
    """Display a Lambda Calcul Tree"""
    if isinstance(tree, str):
        fd.write(f"{indent}* Text[{depth_of_ones}]: {tree}\n")
        return
    if isinstance(tree, int):
        fd.write(f"{indent}* Value[{depth_of_ones}]: {tree}\n")
        assert tree < depth_of_ones
        return
    if len(tree) == 1:
        if 0 and isinstance(tree[0], int):
            fd.write(f"{indent}* Applied value[{depth_of_ones+1}]: {tree[0]}\n")
            assert tree[0] < depth_of_ones + 1
        else:
            fd.write(f"{indent}* One child [{depth_of_ones}->{depth_of_ones+1}]:\n")
            display_prog(tree[0], indent+' ', depth_of_ones=depth_of_ones+1, fd=fd)
        return
    if len(tree) == 2:
        fd.write(f"{indent}* Two[{depth_of_ones}]:\n")
        display_prog(tree[0], indent+' ', depth_of_ones=depth_of_ones, fd=fd)
        display_prog(tree[1], indent+' ', depth_of_ones=depth_of_ones, fd=fd)
        return
    assert False


def betareduce_one_step(tree):
    if isinstance(tree, (int, str)) or len(tree) == 1:
        return tree
    assert len(tree) == 2
    ptVar1 = betareduce_one_step(tree[0])
    if isinstance(ptVar1, (int, str)) or len(ptVar1) == 2:
        return [ptVar1, betareduce_one_step(tree[1])]
    assert len(ptVar1) == 1
    return betareduce_one_step_firstdepth(ptVar1[0], tree[1], 0)


def betareduce_one_step_firstdepth(t1, t2, count_number_of_OneChild_traversed):
    if isinstance(t1, int):
        if t1 == count_number_of_OneChild_traversed:
            return betareduce_one_step_cond_increment_with_bound(t2, t1)
        if count_number_of_OneChild_traversed < t1:
            return t1 - 1
        return t1
    if isinstance(t1, str):
        if t1.startswith('input'):
            if '1' <= t1[5] <= '9':
                m = re.match(r'^input([0-9]+)_', t1)
                if m:
                    input_depth = int(m.group(1))
                    if input_depth <= count_number_of_OneChild_traversed - 1:
                        # Ignore parameters which are much deeper that the possible input
                        return t1
                    if count_number_of_OneChild_traversed == 0:
                        return t1

            str_t2 = str(t2)
            if len(str_t2) >= 500:  # Truncate t2 representation
                if 'Alonzo' in str_t2[500:]:
                    str_t2 = str_t2[:500] + ' with Alonzo...'
                else:
                    str_t2 = str_t2[:500] + '...'
            t1 += '.eval_{}({})'.format(count_number_of_OneChild_traversed - 1, str_t2)
        return t1
    if len(t1) == 1:
        return [betareduce_one_step_firstdepth(t1[0], t2, count_number_of_OneChild_traversed+1)]
    if len(t1) == 2:
        return [
            betareduce_one_step_firstdepth(t1[0], t2, count_number_of_OneChild_traversed),
            betareduce_one_step_firstdepth(t1[1], t2, count_number_of_OneChild_traversed)
        ]
    assert False


def betareduce_one_step_cond_increment_with_bound(tree, count_number_of_OneChild_traversed_from_a_value):
    if isinstance(tree, int):
        if count_number_of_OneChild_traversed_from_a_value <= tree:
            return tree + 1
        return tree
    if isinstance(tree, str):
        return tree
    if len(tree) == 1:
        return [betareduce_one_step_cond_increment_with_bound(tree[0], count_number_of_OneChild_traversed_from_a_value + 1)]
    if len(tree) == 2:
        return [
            betareduce_one_step_cond_increment_with_bound(tree[0], count_number_of_OneChild_traversed_from_a_value),
            betareduce_one_step_cond_increment_with_bound(tree[1], count_number_of_OneChild_traversed_from_a_value)
        ]
    assert False


def evaluation_loop(current_tree):
    """Evaluate a LC tree through β-reduction"""
    for step in range(1000000):
        new_tree = betareduce_one_step(current_tree)
        if new_tree == current_tree:
            return current_tree
        current_tree = new_tree
        if step > 1000:
            print("step %d... %d" % (step, len(str(current_tree))))
            if len(str(current_tree)) > 10000000:
                raise RuntimeError("Too big!")
    raise RuntimeError("Too many steps!")


class LambdaCExpr:
    """Base class for a Lambda Calculus expression (aka. term)"""
    pass


class Variable(LambdaCExpr):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def replace_with_fct(self, fct):
        result = fct(self)
        if result is None:
            return self
        return result


class Lambda(LambdaCExpr):
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr

    def __str__(self):
        return 'λ{}.{}'.format(self.var, self.expr)

    def replace_with_fct(self, fct):
        result = fct(self)
        if result is None:
            return Lambda(self.var, self.expr.replace_with_fct(fct))
        return result


class AppSubs(LambdaCExpr):
    """LC Application / Substitution"""
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2

    def __str__(self):
        return '({} {})'.format(self.e1, self.e2)

    def replace_with_fct(self, fct):
        result = fct(self)
        if result is None:
            return AppSubs(self.e1.replace_with_fct(fct), self.e2.replace_with_fct(fct))
        return result


class ConstantFunction(LambdaCExpr):
    """Simplify using a constant function"""
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def replace_with_fct(self, fct):
        result = fct(self)
        if result is None:
            return self
        return result


class DeBruijnIndexParser:
    """Convert De Bruijn index into a Lambda Calculus expression using classes"""
    def __init__(self, tree, init_vars):
        self.current_varnames = []
        self.next_var_index = 0
        self.init_vars = list(init_vars) if init_vars else []
        self.result = self.build_lambda_expr_rec(tree, depth_of_ones=0)

    def build_lambda_expr_rec(self, tree, depth_of_ones):
        assert len(self.current_varnames) == depth_of_ones
        if isinstance(tree, int):
            assert tree < depth_of_ones
            var_name = self.current_varnames[depth_of_ones - tree - 1]
            return Variable(var_name)
        if len(tree) == 1:
            if self.init_vars:
                new_var = self.init_vars[0]
                self.init_vars = self.init_vars[1:]
            else:
                new_var = 'v{}'.format(self.next_var_index)
            self.next_var_index += 1
            self.current_varnames.append(new_var)
            result = Lambda(new_var, self.build_lambda_expr_rec(tree[0], depth_of_ones=depth_of_ones+1))
            self.current_varnames.pop()
            return result
        if len(tree) == 2:
            e1 = self.build_lambda_expr_rec(tree[0], depth_of_ones=depth_of_ones)
            e2 = self.build_lambda_expr_rec(tree[1], depth_of_ones=depth_of_ones)
            return AppSubs(e1, e2)
        raise ValueError("Invalid LC tree")


def build_lambda_expr(tree, init_vars=None):
    return DeBruijnIndexParser(tree, init_vars).result


# self-checks from https://en.wikipedia.org/wiki/De_Bruijn_index
KNOWN_TRANSFORMS = (
    ([[1]], ['x', 'y'], 'λx.λy.x'),  # K = λ λ 2
    ([[[[[2, 0], [1, 0]]]]], ['x', 'y', 'z'], 'λx.λy.λz.((x z) (y z))'),  # S = λ λ λ 3 1 (2 1)
    ([[ [[0, [0]]], [[1, 0]] ]],  ['z', 'y', 'x1', 'x2'], 'λz.(λy.(y λx1.x1) λx2.(z x2))'),  # λ (λ 1 (λ 1)) (λ 2 1)  # noqa
)

for test_tree, test_initvars, test_lambdastr in KNOWN_TRANSFORMS:
    test_computed_lambda = build_lambda_expr(test_tree, test_initvars)
    test_computed_lambdastr = str(test_computed_lambda)
    assert test_computed_lambdastr == test_lambdastr, "issue with %r: %r != %r" % (test_tree, test_computed_lambdastr, test_lambdastr)


def pretty_print(expr, indent='', fd=sys.stdout):
    if isinstance(expr, Variable):
        fd.write('{}{}\n'.format(indent, expr))
        return
    if isinstance(expr, ConstantFunction):
        fd.write('{}{}\n'.format(indent, expr))
        return
    if isinstance(expr, Lambda):
        str_exprexpr = str(expr.expr)
        if 'λ' not in str_exprexpr and 'Loop' not in str_exprexpr and 'ForEach' not in str_exprexpr:
            fd.write('{}λ{}.{}\n'.format(indent, expr.var, str_exprexpr))
            return
        fd.write('{}λ{}.\n'.format(indent, expr.var))
        pretty_print(expr.expr, indent=indent + '  ', fd=fd)
        return
    if isinstance(expr, AppSubs):
        str_expr = str(expr)
        if 'λ' not in str_expr and 'Loop' not in str_expr and 'ForEach' not in str_expr:
            fd.write('{}{}\n'.format(indent, str_expr))
            return

        fd.write('{}(\n'.format(indent))
        pretty_print(expr.e1, indent=indent + '  ', fd=fd)
        pretty_print(expr.e2, indent=indent + '  ', fd=fd)
        fd.write('{})\n'.format(indent))
        return
    raise NotImplementedError("Missing type %r for pretty_print" % type(expr))


class ExprGlobalVariables:
    """Split the global variables out of the program"""
    def __init__(self, lc_expr):
        self.global_variables = []
        self.global_varsyms = []
        self.main = self.split_expr(lc_expr)

    def split_expr(self, expr):
        if isinstance(expr, AppSubs):
            if isinstance(expr.e1, Lambda):
                # Reduce (λ.x fct arg) to fct(x->arg)
                new_globvar_sym = ConstantFunction(f'Globvar_{len(self.global_variables)}')
                self.global_variables.append(expr.e2)
                self.global_varsyms.append(new_globvar_sym)

                def my_replace(e):
                    if isinstance(e, Variable) and e.name == expr.e1.var:
                        return new_globvar_sym

                new_expr = expr.e1.expr.replace_with_fct(my_replace)
                return self.split_expr(new_expr)

            if isinstance(expr.e1, AppSubs):
                # If application of application, go deeper
                new_e1 = self.split_expr(expr.e1)
                new_expr = AppSubs(new_e1, expr.e2)
                if isinstance(new_e1, Lambda):
                    return self.split_expr(new_expr)
                return new_expr

        return expr


def simplify_lambda_fct(expr):
    if isinstance(expr, Lambda):
        v1 = expr.var
        if isinstance(expr.expr, Variable) and expr.expr.name == v1:
            # λv1.v1 = I
            return ConstantFunction('Identity')

        if isinstance(expr.expr, ConstantFunction):
            if expr.expr.name == 'Identity':
                # λv1.I = λx.λy.y = False
                return ConstantFunction('False')
            if expr.expr.name == 'False':
                # λv1.False
                return ConstantFunction('LambdaFalse')
            if expr.expr.name == 'LambdaFalse':
                return ConstantFunction('LambdaLambdaFalse')

        if isinstance(expr.expr, Lambda) and isinstance(expr.expr.expr, Variable) and expr.expr.expr.name == v1:
            # λx.λy.x = True = K
            return ConstantFunction('True')

        if isinstance(expr.expr, AppSubs):
            str_subexpr = str(expr.expr)
            if str_subexpr == f'(Number_3 (Number_3 {v1}))':
                # λv132.(Number_3 (Number_3 v132)) = mult 3 3 = 9
                return ConstantFunction('Number_9')

            if str_subexpr == f'({v1} True)':
                # λp.(p T) = λp.(p (λx.λy.x)) = first = Head
                return ConstantFunction('Head')

            if str_subexpr == f'(({v1} False) False)':
                # λv174.((v174 False) False) = Tail
                return ConstantFunction('Tail')

            if str_subexpr == f'(({v1} LambdaLambdaFalse) True)':
                return ConstantFunction('IsListEmpty')

            if str_subexpr == f'((EQ (Length {v1})) Number_9)':
                return ConstantFunction('IsLength9')

            if str_subexpr == f'((And (IsLength9 {v1})) ((AllTrueForEach IsLength9) {v1}))':
                return ConstantFunction('Is9x9List')

        if isinstance(expr.expr, Lambda):
            v2 = expr.expr.var
            if isinstance(expr.expr.expr, AppSubs):
                str_subexpr = str(expr.expr.expr)
                if str_subexpr == f'({v1} {v2})':
                    return ConstantFunction('Number_1')
                if str_subexpr == f'({v1} ({v1} {v2}))':
                    return ConstantFunction('Number_2')
                if str_subexpr == f'({v1} ({v1} ({v1} {v2})))':
                    return ConstantFunction('Number_3')
                if str_subexpr == f'({v1} ({v1} ({v1} ({v1} {v2}))))':
                    return ConstantFunction('Number_4')
                if str_subexpr == f'({v1} ({v1} ({v1} ({v1} ({v1} {v2})))))':
                    # λv488.λv489.(v488 (v488 (v488 (v488 (v488 v489))))) = λf.λx.(f (f (f (f (f x))))) = 5
                    return ConstantFunction('Number_5')
                if str_subexpr == f'({v1} ({v1} ({v1} ({v1} ({v1} ({v1} {v2}))))))':
                    return ConstantFunction('Number_6')
                if str_subexpr == f'({v1} ({v1} ({v1} ({v1} ({v1} ({v1} ({v1} {v2})))))))':
                    return ConstantFunction('Number_7')
                if str_subexpr == f'({v1} ({v1} ({v1} ({v1} ({v1} ({v1} ({v1} ({v1} {v2}))))))))':
                    return ConstantFunction('Number_8')
                if str_subexpr == f'({v1} ({v1} ({v1} ({v1} ({v1} ({v1} ({v1} ({v1} ({v1} {v2})))))))))':
                    return ConstantFunction('Number_9')

                if str_subexpr == f'({v1} ((False {v1}) {v2}))':
                    # λx.λy.(x (False x y)) = λx.λy.(x y) = 1
                    return ConstantFunction('Number_1')

                if str_subexpr == f'(({v2} Pred) {v1})':
                    # λm.λn.((n Pred) m) = Minus
                    return ConstantFunction('Minus')
                if str_subexpr == f'(IsZero ((Minus {v1}) {v2}))':
                    # λm.λn.(IsZero (Minus m n) = LEQ = "m <= n"
                    return ConstantFunction('LEQ')
                if str_subexpr == f'((And ((LEQ {v1}) {v2})) ((LEQ {v2}) {v1}))':
                    return ConstantFunction('EQ')

                if str_subexpr == f'(({v1} (Cons {v2})) False)':
                    # Usage with v1=number, v2=False
                    # = λn.λx.(n (Cons x) False)
                    # => empty if n = 0
                    # => [x] if n = 1
                    # => [x, x] if n = 2
                    # ...
                    return ConstantFunction('Repeat')

                if str_subexpr == f'((And ((And (Not (IsZero {v2}))) ((LEQ {v2}) Number_9))) ((Or (IsZero {v1})) ((EQ {v1}) {v2})))':
                    # λv57.λv58.((And ((And (Not (IsZero v58))) ((LEQ v58) Number_9))) ((Or (IsZero v57)) ((EQ v57) v58)))
                    # = y != 0 && y <= 9 && (x == 0 || x == y)
                    return ConstantFunction('[x,y→0<y<=9&&(x==0||x==y)]')

                if isinstance(expr.expr.expr.e1, AppSubs) and \
                        isinstance(expr.expr.expr.e1.e1, Variable) and expr.expr.expr.e1.e1.name == v1 and \
                        isinstance(expr.expr.expr.e1.e2, ConstantFunction) and \
                        isinstance(expr.expr.expr.e2, ConstantFunction):
                    # λv2054.λv2055.((v2054 False_or_value) False_or_sublist)
                    new_item = expr.expr.expr.e1.e2.name
                    if new_item == 'False':
                        new_item = 'Number_0'
                    if new_item.startswith('Number_'):
                        new_item = 'N_' + new_item[7:]
                    if '::' in new_item:
                        new_item = f'[{new_item}]'

                    if expr.expr.expr.e2.name == 'False':
                        return ConstantFunction(f'{new_item}::End')
                    if '::' in new_item:
                        return ConstantFunction(f'{new_item}::[{expr.expr.expr.e2.name}]')
                    return ConstantFunction(f'{new_item}::{expr.expr.expr.e2.name}')

            if isinstance(expr.expr.expr, Lambda):
                v3 = expr.expr.expr.var
                if isinstance(expr.expr.expr.expr, AppSubs):
                    str_subexpr = str(expr.expr.expr.expr)
                    if str_subexpr == f'({v2} (({v1} {v2}) {v3}))':
                        # λn.λf.λx. f ((n f) x) = Succ
                        return ConstantFunction('Succ')
                    if str_subexpr == f'(({v1} {v3}) {v2})':
                        # Not_1 of booleans
                        return ConstantFunction('Not')

                    if str_subexpr == f'(({v1} (True {v3})) {v2})':
                        # λv220.λv221.λv222.((v220 (True v222)) v221) = IsZero
                        return ConstantFunction('IsZero')
                    if str_subexpr == f'({v1} ({v2} {v3}))':
                        # λv201.λv202.λv203.(v201 (v202 v203)) = mult = λm.λn.λf. m (n f)
                        return ConstantFunction('Mult')

                    if isinstance(expr.expr.expr.expr.e2, ConstantFunction) and expr.expr.expr.expr.e2.name == 'Identity' and \
                            isinstance(expr.expr.expr.expr.e1, AppSubs) and \
                            str(expr.expr.expr.expr.e1.e2) == f'(True {v3})' and \
                            isinstance(expr.expr.expr.expr.e1.e1, AppSubs) and \
                            str(expr.expr.expr.expr.e1.e1.e1) == f'{v1}' and \
                            isinstance(expr.expr.expr.expr.e1.e1.e2, Lambda) and \
                            isinstance(expr.expr.expr.expr.e1.e1.e2.expr, Lambda):
                        v4 = expr.expr.expr.expr.e1.e1.e2.var
                        v5 = expr.expr.expr.expr.e1.e1.e2.expr.var
                        if str(expr.expr.expr.expr.e1.e1.e2.expr.expr) == f'({v5} ({v4} {v2}))':
                            # λv208.λv209.λv210.(((v208 λv211.λv212.(v212 (v211 v209))) (True v210)) Identity) = pred
                            return ConstantFunction('Pred')

                if isinstance(expr.expr.expr.expr, Lambda):
                    v4 = expr.expr.expr.expr.var
                    str_subexpr = str(expr.expr.expr.expr.expr)
                    if str_subexpr == f'(({v1} (({v2} {v3}) {v4})) {v4})':
                        # λv1.λv2.λv3.λv4.((v1 ((v2 v3) v4)) v4) = λv1.λv2.λv3.λv4.(if (v1 && v2) {v3} else {v4})
                        return ConstantFunction('And')

                    if str_subexpr == f'(({v1} {v3}) (({v2} {v3}) {v4}))':
                        # λv213.λv214.λv215.λv216.((v213 v215) ((v214 v215) v216)) on two booleans:
                        # λx.λy.λt.λf.(x t (y t f))
                        return ConstantFunction('Or')

                    if str_subexpr == f'(({v3} {v1}) {v2})':
                        # λv178.λv179.λv180.λv181.((v180 v178) v179)
                        # Parameters: bool, ?
                        # Sometimes: v1=other expr with same construction, v2=False
                        # λp.λq.λt.λf.(t p q)
                        # With m = 0: (f 0 n) = ???
                        # Or with list:
                        # λnewitem.λcurlist.λx.λy.(x newitem curlist)
                        #   => with newitem and curlist as parameter, v = λx.λy.(x newitem curlist)
                        #   => (v x y)  β-reduces to (x newitem curlist)
                        #   => like a Cons!
                        # Cons = λh.λt.λp.λu.(p h t)
                        return ConstantFunction('Cons')

    if isinstance(expr, Lambda) and isinstance(expr.expr, AppSubs) and isinstance(expr.expr.e1, Lambda) and isinstance(expr.expr.e2, Lambda):
        v1 = expr.var
        v2 = expr.expr.e1.var
        v3 = expr.expr.e2.var
        if str(expr.expr.e1.expr) == f'({v2} {v2})' and str(expr.expr.e2.expr) == f'({v1} ({v3} {v3}))':
            # λv18.(λv19.(v19 v19) λv20.(v18 (v20 v20))) = Y = fixpoint
            return ConstantFunction('Fixpoint')

    if isinstance(expr, AppSubs) and isinstance(expr.e1, ConstantFunction) and isinstance(expr.e2, ConstantFunction):
        if expr.e1.name == 'Succ':
            if expr.e2.name == 'False':
                return ConstantFunction('Number_1')
            if expr.e2.name == 'Number_1':
                return ConstantFunction('Number_2')
            if expr.e2.name == 'Number_2':
                return ConstantFunction('Number_3')
            if expr.e2.name == 'Number_3':
                return ConstantFunction('Number_4')
            if expr.e2.name == 'Number_4':
                return ConstantFunction('Number_5')
            if expr.e2.name == 'Number_5':
                return ConstantFunction('Number_6')
            if expr.e2.name == 'Number_6':
                return ConstantFunction('Number_7')
            if expr.e2.name == 'Number_7':
                return ConstantFunction('Number_8')

    if isinstance(expr, AppSubs) and isinstance(expr.e1, ConstantFunction) and expr.e1.name == 'Identity':
        # (I e2) = e2
        return expr.e2

    if isinstance(expr, AppSubs) and isinstance(expr.e1, ConstantFunction) and expr.e1.name == 'Fixpoint':
        if isinstance(expr.e2, Lambda) and isinstance(expr.e2.expr, Lambda) and \
                isinstance(expr.e2.expr.expr, AppSubs) and str(expr.e2.expr.expr.e2) == 'False' and \
                isinstance(expr.e2.expr.expr.e1, AppSubs) and str(expr.e2.expr.expr.e1.e1) == expr.e2.expr.var and \
                isinstance(expr.e2.expr.expr.e1.e2, Lambda) and \
                isinstance(expr.e2.expr.expr.e1.e2.expr, Lambda) and \
                isinstance(expr.e2.expr.expr.e1.e2.expr.expr, AppSubs):
            # Recursive functions
            # λv167_index.λv168_loopfct.((v168_loopfct λv169.λv170_f.(Succ (v167_index v170_f))) False)
            # => compute the length
            v_idx = expr.e2.var
            v_f = expr.e2.expr.expr.e1.e2.expr.var
            if str(expr.e2.expr.expr.e1.e2.expr.expr) == f'(Succ ({v_idx} {v_f}))':
                return ConstantFunction('Length')

        if isinstance(expr.e2, Lambda) and isinstance(expr.e2.expr, Lambda) and isinstance(expr.e2.expr.expr, Lambda) and \
                isinstance(expr.e2.expr.expr.expr, AppSubs) and str(expr.e2.expr.expr.expr.e2) == 'False' and \
                isinstance(expr.e2.expr.expr.expr.e1, AppSubs) and str(expr.e2.expr.expr.expr.e1.e1) == expr.e2.expr.expr.var and \
                isinstance(expr.e2.expr.expr.expr.e1.e2, Lambda) and \
                isinstance(expr.e2.expr.expr.expr.e1.e2.expr, Lambda) and \
                isinstance(expr.e2.expr.expr.expr.e1.e2.expr.expr, AppSubs):
            if str(expr) == '(Fixpoint λv159.λv160.λv161.((v161 λv162.λv163.((Cons (v160 v162)) ((v159 v160) v163))) False))':
                # First parameter is a function
                # Second parameter is the input, a 9x9 list
                # = λfself.λa1_block.λa2_list.(a2_list λlhead.λltail.(Cons (a1_block lhead) (fself a1_block ltail)) False))
                # => call the first parameter on the items of the list, and combine the results using Cons with 2 parameters:
                #   * the result on the current item (a1_block lhead)
                #   * the recursive result on the tail (fself a1_block ltail)
                # => Map!
                return ConstantFunction('Map')

        if str(expr) == '(Fixpoint λv151.λv152.λv153.((v152 λv154.λv155.((Cons v154) ((v151 v155) v153))) v153))':
            # (Fixpoint λv151_self.λv152_list.λv153_listtail.(v152_list λv154_head.λv155_tail.(Cons v154_head (v151_self v155_tail v153)) v153))
            # => Concatenate two lists
            return ConstantFunction('Concat')

        if str(expr) == '(Fixpoint λv142.λv143.λv144.λv145.((v145 λv146.λv147.((v143 v146) (((v142 v143) v144) v147))) v144))':
            # (Reduce fbody result_if_empty list) =
            #  * result_if_empty if list is empty
            #  * (fbody head (Reduce ... tail)) otherwise
            return ConstantFunction('Reduce')

        str_expr = str(expr)
        if str_expr == '(Fixpoint λv131.λv132.λv133.λv134.((v133 λv135.λv136.((v134 λv137.λv138.((Cons ((v132 v135) v137)) (((v131 v132) v136) v138))) False)) False))':
            # λfself.λfbody.λlistA.λlistB.((listA λlheadA.λltailA.((listB λv137.λv138.((Cons (fbody lheadA v137)) (fself fbody ltailA v138))) False)) False)
            # Map a function on two lists and craft a list with the mix
            return ConstantFunction('MapTwoListsTogether')

        if str_expr == '(Fixpoint λv110.λv111.λv112.((v112 λv113.λv114.λv115.((((LEQ v111) v114) (((ConsTree ((v110 v111) v113)) v114) v115)) (((ConsTree v113) v114) ((v110 v111) v115)))) (((ConsTree False) v111) False)))':
            return ConstantFunction('InsertInTree')

        if str_expr == '(Fixpoint λv101.λv102.λv103.((v103 λv104.λv105.λv106.((((EQ v102) v105) True) ((((LEQ v102) v105) ((v101 v102) v104)) ((v101 v102) v106)))) False))':
            return ConstantFunction('IsInTree')

        if str_expr == '(Fixpoint λv93.λv94.((v94 λv95.λv96.λv97.(Succ ((Or (v93 v95)) (v93 v97)))) False))':
            return ConstantFunction('TreeLength')

        if str_expr == '(Fixpoint λv85.λv86.λv87.((v87 λv88.λv89.((((IsInTree v88) v86) False) ((v85 ((InsertInTree v88) v86)) v89))) ((EQ (TreeLength v86)) Number_9)))':
            # Usage: (FillTreeFromListAndCheck9 False list) to verify that a list contains all numbers between 1 and 9
            # λfself.λv86.λa1_list.((a1_list λa1Head.λa1Tail.(((IsInTree a1Head v86) False) ((fself (InsertInTree a1Head v86)) a1Tail))) (EQ (TreeLength v86) Number_9)))
            return ConstantFunction('FillTreeFromListAndCheck9')

        if str_expr == '(Fixpoint λv77.λv78.λv79.((v79 λv80.λv81.((((IsInTree v80) v78) v78) ((v77 ((InsertInTree v80) v78)) v81))) v78))':
            return ConstantFunction('FillTreeFromList')

        if str_expr == '(Fixpoint λv65.λv66.((v66 λv67.λv68.((v68 λv69.λv70.((v70 λv71.λv72.((Cons ((Cons v67) ((Cons v69) ((Cons v71) False)))) (v65 v72))) ((Cons ((Cons v67) ((Cons v69) False))) False))) ((Cons ((Cons v67) False)) False))) False))':
            # Split a list into a list of 3-item lists
            return ConstantFunction('SplitListIn3ItemsList')

        # print(str_expr)

    if isinstance(expr, AppSubs) and isinstance(expr.e1, Lambda):
        str_arg = str(expr.e2)
        if 'λ' not in str_arg:
            # Reduce (λ.x fct arg) to fct(x->arg)
            def my_replace(e):
                if isinstance(e, Variable) and e.name == expr.e1.var:
                    return expr.e2
            return expr.e1.expr.replace_with_fct(my_replace)

    if isinstance(expr, AppSubs) and isinstance(expr.e1, AppSubs) and isinstance(expr.e1.e1, ConstantFunction) and str(expr) == '((Mult Number_3) Number_3)':
        return ConstantFunction('Number_9')

    str_expr = str(expr)
    # if str_expr == '(AllTrueForEach Identity)':
    #    return ConstantFunction('AllTrue')

    if str_expr == 'λv116.λv117.λv118.λv119.λv120.(((v119 v116) v117) v118)':
        return ConstantFunction('ConsTree')

    if str_expr == 'λv123.((Reduce λv124.λv125.((And (v123 v124)) v125)) True)':
        # (AllTrueForEach (λx.condition x) list) = True if the condition is tree for each item in the list
        return ConstantFunction('AllTrueForEach')

    if str_expr == 'λv73.(((Reduce (MapTwoListsTogether Cons)) ((Repeat (Length ((Head v73) False))) False)) v73)':
        # parameter is the input, 9x9 array
        # (Reduce (MapTwoListsTogether Cons) {new list with "empty" repeated {len(head) of the list or 0} times} v73)
        # Doc: (Reduce fct_called_with_head_and_recursive_res result_if_empty list)
        # So, like:
        #   result = [[]] * len(a1_list[0])
        #   for item in a1_list[::-1]:
        #       #result = (MapTwoListsTogether Cons item result)
        #       result = [x::y for x, y in zip(item, result)]
        # => swap lines and columns
        return ConstantFunction('SwapGridDimensions')

    if str_expr == 'λv59.((Map ((Reduce Concat) False)) (((Reduce Concat) False) ((Map SplitListIn3ItemsList) (SwapGridDimensions ((Map SplitListIn3ItemsList) v59)))))':
        # parameter is the input, 9x9 array
        # Gather the 3x3 squares in lists
        return ConstantFunction('Gather_3x3squares_content')

    if str_expr == 'λv55.λv56.((AllTrueForEach Identity) (((MapTwoListsTogether [x,y→0<y<=9&&(x==0||x==y)]) v55) v56))':
        return ConstantFunction('MatchPatternListOfNumbers')

    if str_expr == 'λv53.λv54.((AllTrueForEach (FillTreeFromListAndCheck9 False)) v54)':
        return ConstantFunction('call_FillTreeFromListAndCheck9_on_items_of_second_param')  # Unused function

    if str_expr == '((Reduce Concat) False)':
        return ConstantFunction('Flatten2DList')

    if str_expr == 'λv59.((Map Flatten2DList) (Flatten2DList ((Map SplitListIn3ItemsList) (SwapGridDimensions ((Map SplitListIn3ItemsList) v59)))))':
        return ConstantFunction('Group3x3Squares')

    if str_expr == '(FillTreeFromListAndCheck9 False)':
        return ConstantFunction('Check9DistinctNumbers')

    # Bonus level
    if str_expr == 'λv234.λv235.λv236.(((v234 λv237.λv238.(v238 (v237 v235))) λv239.v236) Identity)':
        return ConstantFunction('Pred')
    if str_expr == 'λv230.λv231.λv232.λv233.((((v231 Pred) v230) λv241.v233) v232)':
        # λm.λn.λv232.λv233.((((n Pred) m) λv241.v233) v232)
        # λm.λn.λt.λf.((Minus m n) λv241.f t)
        # λm.λn.λt.λf.(IsZero (Minus m n) t f)
        return ConstantFunction('LEQ')
    if str_expr == 'λv223.λv224.λv227.λv228.((((LEQ v223) v224) ((((LEQ v224) v223) v227) v228)) v228)':
        # (λv216.(v216 v216) λv217.λl.((l λh.λt.(Succ ((v217 v217) t))) False))
        return ConstantFunction('EQ')
    if str_expr == '(λv216.(v216 v216) λv217.λv218.((v218 λv219.λv220.(Succ ((v217 v217) v220))) False))':
        # (λv216.(v216 v216) λv217.λl.((l λh.λt.(Succ ((v217 v217) t))) False))
        return ConstantFunction('Length')
    if str_expr == '(λv206.(v206 v206) λv207.λv208.λv209.((v209 λv210.λv211.λv212.λv213.((v212 (v208 v210)) (((v207 v207) v208) v211))) False))':
        # (λv206.(v206 v206) λv207.λf.λl.(l λh.λt.λv212.λv213.(v212 (f h) ((v207 v207) x t)) False))
        # => Y mixed with applying f and Cons
        return ConstantFunction('Map')
    if str_expr == '(λv199.(v199 v199) λv200.λv201.λv202.λv203.((v203 λv204.λv205.((v201 v204) ((((v200 v200) v201) v202) v205))) v202))':
        # (λv199.(v199 v199) λv200.λf.λemptyRes.λl.((l λh.λt.(f h ((v200 v200) f emptyRes t))) emptyRes))
        return ConstantFunction('Reduce')
    if str_expr == '(λv189.(v189 v189) λv190.λv191.λv192.((v191 λv193.λv194.λv195.λv196.((v195 v193) (((v190 v190) v194) v192))) v192))':
        # (λv189.(v189 v189) λv190.λl.λl2.(l λh.λt.λv195.λv196.(v195 h ((v190 v190) t l2)) l2))
        return ConstantFunction('Concat')
    if str_expr == '(λv171.(v171 v171) λv172.λv174.λv175.λv176.((v175 λv177.λv178.((v176 λv179.λv180.λv183.λv184.((v183 ((v174 v177) v179)) ((((v172 v172) v174) v178) v180))) False)) False))':
        # (λv171.(v171 v171) λv172.λfct.λlA.λlB.(lA λhA.λtA.(lB λhB.λtB.λConsF.λConsT.(ConsF (fct hA hB) ((v172 v172) fct tA tB)) False) False))
        return ConstantFunction('MapTwoListsTogether')
    if str_expr == 'λv164.((Reduce λv165.λv166.λv167.λv168.(((v164 v165) ((v166 v167) v168)) v168)) True)':
        # λfct.(Reduce λval.λprevResult.λtrue.λfalse.(fct val (prevResult true false) false) True)
        return ConstantFunction('AllTrueForEach')
    if str_expr == '(λv151.(v151 v151) λv152.λv154.((v154 λv155.λv156.λv157.(Succ λv158.λv159.((((v152 v152) v155) v158) ((((v152 v152) v157) v158) v159)))) False))':
        # (λv151.(v151 v151) λv152.λtree.((tree λleft.λv156.λright.(Succ λf.λx.(((v152 v152) left f) ((v152 v152) right f x)))) False))
        return ConstantFunction('TreeLength')
    if str_expr == '(λv130.(v130 v130) λv131.λv133.λv134.((v134 λv135.λv136.λv137.((((LEQ v133) v136) λv141.λv142.(((v141 (((v131 v131) v133) v135)) v136) v137)) λv143.λv144.(((v143 v135) v136) (((v131 v131) v133) v137)))) λv145.λv146.(((v145 False) v133) False)))':
        # (λv130.(v130 v130) λv131.λn.λtree.(tree λleft.λval.λright.((LEQ n val λv141.λv142.(v141 ((v131 v131) n left) val right)) λv143.λv144.(v143 left val ((v131 v131) n right))) λv145.λv146.(v145 False n False)))
        return ConstantFunction('InsertInTree')
    if str_expr == '(λv116.(v116 v116) λv117.λv119.λv120.((v120 λv121.λv122.λv123.((((EQ v119) v122) True) ((((LEQ v119) v122) (((v117 v117) v119) v121)) (((v117 v117) v119) v123)))) False))':
        # (λv116.(v116 v116) λv117.λn.λtree.(tree λleft.λval.λright.((EQ n val True) (LEQ n val ((v117 v117) n left) ((v117 v117) n right))) False))
        return ConstantFunction('IsInTree')
    if str_expr == '(λv110.(v110 v110) λv111.λv112.λv113.((v113 λv114.λv115.((((IsInTree v114) v112) False) (((v111 v111) ((InsertInTree v114) v112)) v115))) ((EQ (TreeLength v112)) Number_9)))':
        # ((λv110.(v110 v110) λv111.λtree.λl.(l λh.λt.(IsInTree h tree False ((v111 v111) (InsertInTree h tree) t)) (EQ (TreeLength tree) Number_9))) False)
        return ConstantFunction('FillTreeFromListAndCheck9')
    if str_expr == 'λv94.(((Reduce (MapTwoListsTogether Cons)) (((Length ((v94 True) False)) λv103.λv104.λv105.((v104 False) v103)) False)) v94)':
        return ConstantFunction('SwapGridDimensions')
    if str_expr == '(λv52.(v52 v52) λv53.λv55.((v55 λv56.λv57.((v57 λv58.λv59.((v59 λv60.λv61.((Cons λv66.λv67.((v66 v56) λv68.λv69.((v68 v58) λv70.λv71.((v70 v60) False)))) ((v53 v53) v61))) λv74.λv75.((v74 λv76.λv77.((v76 v56) λv78.λv79.((v78 v58) False))) False))) λv84.λv85.((v84 λv86.λv87.((v86 v56) False)) False))) False))':
        # (λv52.(v52 v52) λv53.λl.((l λh1.λt1.((t1 λh2.λt2.((t2 λh3.λt3.((Cons λv66.λv67.((v66 h1) λv68.λv69.((v68 h2) λv70.λv71.((v70 h3) False)))) ((v53 v53) t3))) λv74.λv75.((v74 λv76.λv77.((v76 h1) λv78.λv79.((v78 h2) False))) False))) λv84.λv85.((v84 λv86.λv87.((v86 h1) False)) False))) False))
        return ConstantFunction('SplitListIn3ItemsList')

    if str_expr == 'λv39.λv40.λv41.λv42.((v39 ((v40 v41) v42)) v42)':
        return ConstantFunction('And')
    if str_expr == 'λv37.λv38.((And λv43.λv44.((v38 λv45.((((LEQ v38) Number_9) v43) v44)) v44)) λv46.λv47.((v37 λv48.((((EQ v37) v38) v46) v47)) v46))':
        # λn1.λn2.((And λt1.λf1.((n2 λv45.(LEQ n2 Number_9 t1 f1)) f1)) λt2.λf2.(n1 λv48.(EQ n1 n2 t2 f2) t2))
        return ConstantFunction('[x,y→0<y<=9&&(x==0||x==y)]')
    if str_expr == 'λv34.λv35.((AllTrueForEach Identity) (((MapTwoListsTogether [x,y→0<y<=9&&(x==0||x==y)]) v34) v35))':
        return ConstantFunction('MatchPatternListOfNumbers')

    return None


def simplify_lambda(expr):
    for _ in range(100):
        expr = expr.replace_with_fct(simplify_lambda_fct)
    return expr


def load_alonzo_program(prgm_path=ALONZO_CHALLENGE):
    """Load the Lambda Calculus program embedded into the challenge"""
    with prgm_path.open('rb') as fd:
        fd.read(0x2060)
        file_data = fd.read(0x3956 - 0x2060)
        assert file_data.endswith(b'010\0')
        assert file_data[:8] == b'10001010'[::-1]
        assert len(file_data[:-1]) == 0x18F5 == 0x18F8 - 1 - 0x2
        lc_tree = str_to_tree(file_data[:-1].decode('ascii'))
        return lc_tree


if __name__ == '__main__':
    ALONZO_TREE = load_alonzo_program()
    # display_prog(ALONZO_TREE)

    # Check the evaluation
    reduced_tree = evaluation_loop(ALONZO_TREE)
    assert betareduce_one_step(reduced_tree) == reduced_tree

    # Translate the input program
    ALONZO_LAMBDA = build_lambda_expr(ALONZO_TREE)
    # print(f"Program: {ALONZO_LAMBDA}")

    # Find out the global variables
    ALONZO_GLOBVARS = ExprGlobalVariables(ALONZO_LAMBDA)
    for var_idx, var_expr in enumerate(ALONZO_GLOBVARS.global_variables):
        print(f"Globvar_{var_idx} is {var_expr}")

    print("")
    print("------------------------------------------------------------")
    print("")

    # Simplify the variables using known patterns
    for var_idx, var_expr in enumerate(ALONZO_GLOBVARS.global_variables):
        simplified_expr = simplify_lambda(var_expr)
        print(f"* Globvar_{var_idx} is {var_expr} = {simplified_expr}")
        if isinstance(simplified_expr, ConstantFunction):
            # Let's replace the expression in the context
            ALONZO_GLOBVARS.global_varsyms[var_idx].name = simplified_expr.name

    print("")
    print("------------------------------------------------------------")
    print("")
    print(f"Main is {ALONZO_GLOBVARS.main}")
    simplified_expr = simplify_lambda(ALONZO_GLOBVARS.main)
    print("")
    print(f"Simplified main is {simplified_expr}")

    # pretty_print(ALONZO_GLOBVARS.global_variables[50])

    simplified_lambda = simplify_lambda(ALONZO_LAMBDA)
    with open('base_lambda.out.txt', 'w') as fout:
        pretty_print(simplified_lambda, fd=fout)

    # Solve the Sudoku
    SUDOKU_GRID = [
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
    # Sudoku
    expected_input = [
        [4, 1, 7, 3, 6, 9, 8, 2, 5],
        [6, 3, 2, 1, 5, 8, 9, 4, 7],
        [9, 5, 8, 7, 2, 4, 3, 1, 6],
        [8, 2, 5, 4, 3, 7, 1, 6, 9],
        [7, 9, 1, 5, 8, 6, 4, 3, 2],
        [3, 4, 6, 9, 1, 2, 7, 5, 8],
        [2, 8, 9, 6, 4, 3, 5, 7, 1],
        [5, 7, 3, 2, 9, 1, 6, 8, 4],
        [1, 6, 4, 8, 7, 5, 2, 9, 3],
    ]
    assert all(len(set(line)) == 9 for line in expected_input)
    assert all(len(set(expected_input[l][c] for l in range(9))) == 9 for c in range(9))

    # Zero = λf.λx.x
    zero = [[0]]
    assert str(build_lambda_expr(zero)) == 'λv0.λv1.v1'

    # λn.λf.λx. f ((n f) x) = Succ
    succ = [[[[1, [[2, 1], 0]]]]]
    assert str(build_lambda_expr(succ, ['n', 'f', 'x'])) == 'λn.λf.λx.(f ((n f) x))'

    # λh.λt.λx.λy.((x h) t) = Cons, for arrays
    cons = [[[[[[1, 3], 2]]]]]
    assert str(build_lambda_expr(cons, ['h', 't', 'x', 'y'])) == 'λh.λt.λx.λy.((x h) t)'

    # Multiplication: Mult = λm.λn.λf.λx.m (n f) x
    mult = [[[[[[3, [2, 1]], 0]]]]]
    assert str(build_lambda_expr(mult, ['m', 'n', 'f', 'x'])) == 'λm.λn.λf.λx.((m (n f)) x)'

    N_1 = [succ, zero]
    N_2 = [succ, N_1]
    N_3 = [succ, N_2]
    N_4 = [succ, N_3]
    N_5 = [succ, N_4]
    N_6 = [[mult, N_2], N_3]
    N_7 = [succ, N_6]
    N_8 = [[mult, N_2], N_4]
    N_9 = [[mult, N_3], N_3]
    numbers = [zero, N_1, N_2, N_3, N_4, N_5, N_6, N_7, N_8, N_9]
    for idx in range(10):
        exprtree = [[numbers[idx], 'f'], 'x']
        exprtree = evaluation_loop(exprtree)
        # Ensure it is (f x) with recursion
        for c in range(idx):
            assert isinstance(exprtree, list)
            assert len(exprtree) == 2
            assert exprtree[0] == 'f'
            exprtree = exprtree[1]
        assert exprtree == 'x'

    # Use numbers and functions as parameters
    # 10 = cons
    encoded = 0
    for line in expected_input[::-1]:
        current_line = zero
        for value in line[::-1]:
            assert 0 <= value <= 9
            current_line = [[10, value], current_line]
        encoded = [[10, current_line], encoded]
    for cur_number in numbers:
        encoded = [[encoded], cur_number]
    encoded = [[encoded], cons]

    possible_input = tree_to_str(encoded)
    assert str_to_tree(possible_input) == encoded
    print(possible_input)
    current_lambda = build_lambda_expr(evaluation_loop(encoded))  # Tests
    current_lambda = simplify_lambda(current_lambda)
    print(current_lambda)
    with open('solution.out.txt', 'w') as fout:
        fout.write(possible_input + '\n')
    print("Output: %d bytes" % len(possible_input))
    assert len(possible_input) == 3331
