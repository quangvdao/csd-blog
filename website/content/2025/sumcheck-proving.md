+++
# The title of your blogpost. No sub-titles are allowed, nor are line-breaks.
title = "Algorithms for the Sum-check Protocol"
# Date must be written in YYYY-MM-DD format. This should be updated right before the final PR is made.
date = 2025-10-27

[taxonomies]
# Keep any areas that apply, removing ones that don't. Do not add new areas!
areas = ["Security", "Theory"]
# Tags can be set to a collection of a few keywords specific to your blogpost.
# Consider these similar to keywords specified for a research paper.
tags = [
    "sumcheck",
    "cryptography",
    "proof systems",
    "sumcheck proving",
    "streaming algorithms",
]

[extra]
author = {name = "Quang Dao", url = "https://quangvdao.github.io/" }
# The committee specification is a list of objects similar to the author.
committee = [
    {name = "Bryan Parno", url = "https://www.andrew.cmu.edu/user/bparno/"},
    {name = "Elaine Shi", url = "https://elaineshi.com/"},
    {name = "Harrison Grodin", url = "https://www.harrisongrodin.com/"}
]
+++

# The Need for Verifiability

Modern computing systems produce enormous amounts of data and perform immense quantity of
computation, but with almost no verifiability (even when we need them).

Many important problems that we are facing today are related to 

Two examples:

1. correctness of data analysis on a large, potentially private dataset - an important part of reproducibility in science.
2. correctness of a series of transactions on a blockchain - one that is verified not once, but potentially millions of times across the world

Normally, one would expect that in order to verify that a computation is correct, you have to: (i)
know all the inputs going into the computation, and (ii) re-run the same computation on those data.
*Cryptographic proof systems* provide a way to eliminate these shortcomings.f

Can you verify that a computation has been correctly performed, without re-executing it, or even
knowing all the inputs to the computation?

The sum-check protocol, introduced by Lund, Fortnow, Karloff, and Nisan in 1992 [[1]](#ref-1), is 

sum-check is now at the core of state-of-the-art polynomial commitment schemes (WHIR, Basefold, FRI-Binius), folding schemes (HyperNova, LatticeFold(+)), and zero-knowledge virtual machine such as Jolt. For the last one

## Overview of the Sum-Check Protocol

We work over a finite field $\mathbb{F}$. The setting of sum-check is that there is a multivariate polynomial $p(X_1, \dots, X_n) \in \mathbb{F}[X_1,\dots, X_n]$, of degree bounded by $d$ in each variable, and that the prover wants to convince the verifier that
\[
    \sum_{(x_1,\dots,x_n) \in \{0,1\}^n} p(x_1,\dots,x_n) = c,    
\]

for some claim $c \in \mathbb{F}$. The verifier also knows about $p$ (or at least has access to
an ``oracle'' that can respond with the evaluation of $p$ at any given value). Because of this, it
is possible for the verifier to verify the claim itself - but this would take work on the order of
$O(2^n)$. The key idea of sum-check is that by leveraging interaction with an untrusted prover, who
may supply the verifier with additional ``auxiliary'' data, it may reduce the work of checking the
original claim, to checking a claim about the polynomial $p$ at a \emph{single} point.

In particular, the data that the prover will send are "one-dimensional" slices of this multivariate polynomial. In the first round, the prover would send the univariate polynomial
\[
    s_1(X) = \sum_{(x_2,\dots,x_n) \in \{0,1\}^{n-1}} p(X, x_2,\dots,x_n).
\]
If the original claim was correct, then $s_1(X)$ would have its degree bounded by $d$, and that $s_1(0) + s_1(1) = c$. The verifier checks precisely these two properties, then samples a random challenge $r_1 \gets \mathbb{F}$ from the finite field, and sends it to the prover. The point of this challenge is to enforce honesty from the prover 

After one round of interaction, the prover and verifier has effectively reduced the problem to showing that
\[
    \sum_{(x_2,\dots, x_n) \in \{0,1\}^{n-1}} p_{r_1}(x_2, \dots, x_n) = c_1
\]

Brief discussion on correctness (obvious) and soundness (not-so-obvious). The idea is that, if the
prover cheats and does not send the ``expected'' polynomial for some round, then it would be caught
with high probability, due to the error-amplifying nature of polynomials (also called the
Schwartz-Zippel lemma (cite)).

## Brief Interlude on Multilinear Polynomials

So far, we have only describe sum-check as a protocol on polynomials. But how does this relate to any
computation performed in the real world? The key answer is encoding, or arithmetization. The computation
that we want to prove will need to first be transformed into a number of polynomial identities, which
are then proven via a series of sum-checks.

The most common encoding process is by lifting vectors of some quantity we care about (i.e. the
value being read over all cycles of a program) into the finite field, and then interpreting it as
representing a _multilinear polynomial_

What they are: multivariate polynomial where each variable is of degree at most $1$. Example: (some 3-variate multilinear)

In general, $n$ variables give $2^n$ coefficients. In fact, it is more convenient to think of these vectors as representing the _evaluations_ of the polynomial at some interpolating set, say the _Boolean hypercube_ $\{0,1\}^n$[^1]

What is an interpolating set? This is just another word for ``basis'', namely that 

This leads us to the \emph{multilinear extension} formula:
\[ \widetilde{p}(X_1,\dots, X_n) = \sum_{y \in \{0,1\}^n} \widetilde{eq}(\vec{X}, y) \cdot p(y),\]
with equality polynomial chosen for being the basis of this evaluation domain
\[\widetilde{eq}(\vec{X}, \vec{Y}) = \prod_{i=1}^n ((1-X_i) \cdot (1-Y_i) + X_i \cdot Y_i),\]
which satisfy the condition that for $\vec{x}, \vec{y} \in \{0,1\}^n$, $\widetilde{eq}(x, y) = (x \overset{?}{=} y) \in \{0,1\}$.

## Existing Algorithms for Sum-Check

Special focus: sum-check over low-degree functions applied to a number of multilinear polynomials

Why? captures known applications. Example: a zero-check of quadratic constraints.

In fact, let's just focus on a single case: a product of two multilinear polynomials:

\[
    \sum_{x \in \{0,1\}^n} p(x) * q(x) = c.
]

We assume $p$ and $q$ are given by their evaluations on $\{0,1\}^n$.

### Linear-time algorithm

This first algorithm is due to vsbw13 and thaler13 (add refs to cites)

Compute $s_1(X)$ from its evaluations at $0, 1, 2$ (degree-2 requires 3 evaluations) via summing over ...

Then compute the bound polynomials $p, q$ at $r_1$, and recurse.

Complexity analysis: $O(2^n)$ time and $O(2^n)$ space

Problem: requires linear space as well. Quickly grows untenable as the number of terms grow
(cannot prove billion-sized statements)

assume the trace still fits in memory (which is the case when proving up to one hundred million
RISC-V cycles). however, there won't be enough space to store the evaluations as in the linear-time algorithm

### Log-space / streaming algorithm

Note the model: assume there is enough storage (perhaps in a hard
drive) to store all the coefficients, but not enough storage in RAM to store the intermediate
values.

So, we can compute from scratch every round, or at least until there is enough space to
materialize the polynomial

## New Idea: Round Compression and its Benefits


## Conclusion

This blog post describes a recent result that achieves a better balance of time vs. space usage
for the sum-check protocol. In combination with many other techniques for sum-check (prefix-suffix, etc.)
we are now closer than ever to having practical, ubiquitous verifiable computation become a reality.



[^1]: However, it is possible to interpret the coefficients of a multilinear polynomial as evaluations over the set $\{0,\infty\}^n$, under an appropriate definition of "evaluation at infinity". This is a non-standard choice with potential efficiency benefits, but we do not discuss it further here.

Citations:

<a id="ref-1"></a>[1] Lund, C., Fortnow, L., Karloff, H., & Nisan, N. (1992). Algebraic methods for interactive proof systems. Journal of the ACM, 39(4), 859–868. https://dl.acm.org/doi/10.1145/146585.146605

[2] Cormode, G., Mitzenmacher, M., & Thaler, J. (2012). Practical Verified Computation with Streaming Interactive Proofs. In Proceedings of the 2nd Innovations in Theoretical Computer Science Conference (ITCS 2012), 90–112. ACM.

[3] Thaler, J. (2013). Time-Optimal Interactive Proofs for Circuit Evaluation. In Advances in Cryptology – CRYPTO 2013 (LNCS 8042, pp. 71–89). Springer.

[4] Vu, V., Setty, S., Blumberg, A. J., & Walfish, M. (2013). A Hybrid Architecture for Verifiable Computation. In Proceedings of the 2013 IEEE Symposium on Security and Privacy (SP), 223–237. IEEE.

[5] Baweja, A., Chiesa, A., Fedele, E., Fenzi, G., Mishra, P., Mopuri, T., & Zitek-Estrada, A. (2025). Time-Space Trade-Offs for Sumcheck. In Theory of Cryptography Conference (TCC 2025).

[6] Bagad, S., Dao, Q., Domb, Y., & Thaler, J. (2025). Speeding Up Sum-Check Proving. Cryptology ePrint Archive, Paper 2025/1117. https://eprint.iacr.org/2025/1117



<!-- AI generated content starts here, all commented out

### **1. Introduction: The Problem of Verifiable Computation**

Imagine a junior engineer is tasked with a massive, week-long computation—say, training a complex machine learning model on a colossal dataset. At the end of the week, they report a final result: "The model's accuracy is 87.4%." A senior engineer needs to sign off on this, but they don't have another week to spare to re-run the entire job. How can they efficiently verify the junior engineer's claim without redoing all the work?

This is a classic problem in computer science, known as **verifiable computation**. How can a computationally weak party (the "Verifier") check the work of a powerful but potentially untrusted or buggy party (the "Prover")? The answer lies in a powerful cryptographic tool called an **Interactive Proof**. In an interactive proof, the Prover doesn't just provide the final answer; they engage in a short conversation with the Verifier, providing extra information that convinces the Verifier of the answer's correctness. The sum-check protocol is one of the most fundamental and elegant interactive proofs in this domain.

### **2. Background: The Magic of Multilinear Polynomials**

Before we dive into the protocol itself, we need to understand its core mathematical object: the multilinear polynomial.

A polynomial is simply a mathematical expression involving variables and coefficients, like $f(x) = 3x^2 + 2x - 5$. A **multilinear polynomial** is a special type where the degree of each variable in any given term is at most 1. For example, $g(X_1, X_2) = 2X_1X_2 + 3X_1 + 5X_2 + 1$ is multilinear. In contrast, $g(X_1, X_2) = X_1^2 + X_2$ is *not* multilinear because $X_1$ has a degree of 2.

What makes multilinear polynomials so special for verifiable computation is their relationship with the **boolean hypercube**. A multilinear polynomial in $\ell$ variables is uniquely defined by its evaluations on the $2^\ell$ points of the boolean hypercube $\{0,1\}^\ell$. This means if you know the value of the polynomial for every binary input string of length $\ell$, you know everything about the polynomial. This property creates a powerful bridge, allowing us to take any function that operates on binary data and represent it using the rich algebraic structure of a polynomial. This is the key to encoding complex computational claims in a way that a protocol like sum-check can understand.

### **3. The Sum-Check Protocol: A Detailed Walkthrough**

The sum-check protocol is designed to verify a specific type of claim: that the sum of a multilinear polynomial $g(X_1, \ldots, X_\ell)$ over the entire boolean hypercube is equal to a certain value $C$.

**The Claim:**
$$ \sum_{x \in \{0,1\}^\ell} g(x) = C $$

The protocol proceeds in $\ell$ rounds, systematically reducing the complexity of this claim.

*   **Round 1:**
    1.  **Prover's Move:** The Prover computes a new, single-variable polynomial $s_1(X_1)$ by summing $g$ over all variables *except* the first one:
        $$ s_1(X_1) = \sum_{x_2, \ldots, x_\ell \in \{0,1\}^{\ell-1}} g(X_1, x_2, \ldots, x_\ell) $$
        The Prover sends $s_1(X_1)$ to the Verifier.
    2.  **Verifier's Check:** The Verifier performs a consistency check. If the original claim is true, then $s_1(0) + s_1(1)$ must equal $C$. If not, the Verifier rejects immediately.
    3.  **The Challenge:** If the check passes, the Verifier picks a random value $r_1$ from a large finite field $\mathbb{F}$ and sends it to the Prover. The problem is now reduced to proving a new, smaller claim: $\sum_{x_2, \ldots, x_\ell} g(r_1, x_2, \ldots) = s_1(r_1)$.

*   **Round $i$ (for $i=2, \ldots, \ell$):**
    1.  **Prover's Move:** The Prover must now prove the claim from the previous round. It computes the next polynomial $s_i(X_i)$:
        $$ s_i(X_i) = \sum_{x_{i+1}, \ldots, x_\ell \in \{0,1\}^{\ell-i}} g(r_1, \ldots, r_{i-1}, X_i, x_{i+1}, \ldots, x_\ell) $$
        and sends it to the Verifier.
    2.  **Verifier's Check:** The Verifier checks if $s_i(0) + s_i(1) = s_{i-1}(r_{i-1})$. If not, reject.
    3.  **The Challenge:** If the check passes, the Verifier picks a new random challenge $r_i \in \mathbb{F}$ and sends it to the Prover.

*   **The Final Check:**
    After $\ell$ rounds, all variables have been bound to random challenges $(r_1, \ldots, r_\ell)$. The final claim is that $g(r_1, \ldots, r_\ell) = s_\ell(r_\ell)$. The Verifier can now check this directly by evaluating the original polynomial $g$ at this single point. If the equality holds, the Verifier accepts the entire proof.

### **4. Why is this Secure? Soundness and the Schwartz-Zippel Lemma**

The security of the protocol hinges on the **Schwartz-Zippel Lemma**. This fundamental result states that for two different polynomials $P_1$ and $P_2$ of total degree at most $d$, the probability that they evaluate to the same value at a random point $r$ chosen from a field $\mathbb{F}$ is at most $d/|\mathbb{F}|$.

In each round of sum-check, the polynomial $s_i(X_i)$ has a degree of at most $d$ (the degree of $g$). If a cheating Prover sends an incorrect polynomial $s_i'$ instead of the true $s_i$, the difference $h(X_i) = s_i(X_i) - s_i'(X_i)$ is a non-zero polynomial of degree at most $d$. The probability that the Verifier's random challenge $r_i$ happens to be a root of this difference polynomial (i.e., $h(r_i) = 0$, meaning $s_i(r_i) = s_i'(r_i)$) is the **per-round soundness error**, which is at most $d/|\mathbb{F}|$.

Since the field $\mathbb{F}$ is typically astronomically large (e.g., $|\mathbb{F}| \approx 2^{256}$), this probability is negligible. An error in any single round will, with overwhelming probability, be caught and propagated, causing the final check to fail.

### **5. The Prover's Dilemma: Classical Proving Algorithms**

While the Verifier's work is minimal, the Prover's task of computing the $s_i$ polynomials is the real bottleneck.

*   **Algorithm 1: The Fast but Memory-Hungry Prover (Linear-Time, Linear-Space)**
    *   **How it works:** It computes the full table of $2^\ell$ evaluations of $g$. In round 1, it sums these values to get $s_1$. For round 2, it uses the random challenge $r_1$ to compute a new, smaller table of $2^{\ell-1}$ evaluations of $g(r_1, \ldots)$ and caches it. This halving process continues.
    *   **Cost Analysis:**
        *   **Time:** The work is dominated by the first round. The total time is $\sum_{i=0}^{\ell-1} O(2^{\ell-i}) = O(2^\ell + 2^{\ell-1} + \dots) = O(2^\ell) = O(M)$.
        *   **Space:** It must store the largest intermediate table, which requires $O(2^{\ell-1}) = O(M)$ memory.

*   **Algorithm 2: The Memory-Frugal but Slow Prover (Quasilinear-Time, Log-Space)**
    *   **How it works:** To save memory, it recomputes values from scratch every round. To compute $s_i(u)$, it iterates through all $2^{\ell-i}$ inputs for the remaining variables, re-evaluating $g(r_1, \ldots, r_{i-1}, u, \ldots)$ each time.
    *   **Cost Analysis:**
        *   **Time:** In each of the $\ell$ rounds, it does work proportional to $M$. The total time is roughly $O(\ell \cdot 2^\ell) = O(M \log M)$.
        *   **Space:** It only needs to store the random challenges, requiring just $O(\ell) = O(\log M)$ memory.

### **6. Our New Technique: Round-Batching**

Our recent work introduces **round-batching**, a technique that provides a much better middle ground. The core idea is to delay the binding of random challenges. Instead of processing one round at a time, the Prover handles a "window" of $\omega$ rounds at once, treating the challenges $(X_i, \ldots, X_{i+\omega-1})$ symbolically.

*   **Benefit 1: The Small-Value Optimization**
    *   In many real-world applications (like zkVMs), the underlying data consists of "small" values (e.g., 64-bit integers), while the cryptography requires a "large" field (e.g., 256-bit numbers). Arithmetic on small numbers is dramatically faster. The linear-time prover loses this advantage after round 1, as the random challenge $r_1$ is a large field element. By batching the first few, most expensive rounds, our prover can structure its computation to continue using fast, native CPU arithmetic on small values for the bulk of its work.

*   **Benefit 2: A Better Streaming Algorithm**
    *   By applying round-batching iteratively with a clever schedule (small windows early, large windows late), we can create a superior streaming algorithm. This evaluation-basis approach improves the time complexity's dependence on the polynomial degree $d$ from $O(d^2)$ to $O(d \log d)$, a significant asymptotic and practical improvement for the high-degree polynomials common in modern proof systems.

### **7. Auxiliary Optimizations for Provers**

Beyond round-batching, further optimizations are crucial for state-of-the-art provers.

*   **High-Degree Sum-Checks:**
    *   Often, the polynomial $g$ is a product of many factors, $g = \prod_{k=1}^d p_k$. Naively computing this product takes $d-1$ multiplications for each point.
    *   **Optimization:** A recursive, tree-based multiplication structure (similar to Toom-Cook algorithm) can reduce the number of multiplications from $O(d)$ to $O(\log d)$ per point, offering a significant speedup for high-degree checks.

*   **Decomposable Polynomials (e.g., Equality Check):**
    *   Sometimes, a factor in the product is highly structured. A prime example is the equality polynomial, `eq(a, b)`, which checks if two vectors of variables `a` and `b` are identical.
    *   **Optimization:** The `eq` polynomial is decomposable, meaning it can be expressed as a product of smaller, independent factors: `eq((a_1, ..., a_k), (b_1, ..., b_k)) = \prod_{i=1}^k (a_i b_i + (1-a_i)(1-b_i))`. This structure can be exploited to evaluate and sum it much more efficiently than a generic, opaque polynomial of the same degree. Provers that can detect and leverage this are significantly faster for workloads like zkEVM execution traces.

### **8. Conclusion**

The sum-check protocol is a cornerstone of modern cryptography, but its practical efficiency has long been limited by the prover's cost. Classical algorithms force an unforgiving choice between speed and memory. Our new round-batching technique provides a unifying framework that attacks this tradeoff from both sides, offering huge practical speedups for high-memory provers via small-value optimizations, and better asymptotic performance for memory-constrained streaming provers. When combined with auxiliary optimizations for high-degree and structured polynomials, these advances pave the way for faster, more scalable, and more practical proof systems.

 -->