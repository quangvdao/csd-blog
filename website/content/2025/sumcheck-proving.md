+++
# The title of your blogpost. No sub-titles are allowed, nor are line-breaks.
title = "Algorithms for the Sum-check Protocol"
# Date must be written in YYYY-MM-DD format. This should be updated right before the final PR is made.
date = 2025-11-14

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
    {name = "Elaine Shi", url = "https://elaineshi.com/"},
    {name = "Sarah Scheffler", url = "https://www.sarahscheffler.net/"},
    {name = "Harrison Grodin", url = "https://www.harrisongrodin.com/"}
]
+++

<!-- Notes:
1. This is for a general CS audience, not cryptography experts
2. Word count should be around 2-3k words, but not a strict limit
3. Everything should be understandable, well motivated, details laid out clearly -->

# The Need for Verifiability

We increasingly rely on computational results we cannot feasibly verify ourselves. The barrier to verification comes in two forms. First, the computation may involve private data that cannot be shared, such as financial audits, medical studies, and proprietary algorithms. Second, even when data is public, re-executing the computation may be prohibitively expensive: large scientific analyses might require days of cluster time on terabytes of data. How can we trust that such computations were performed correctly?

Cryptographic proof systems solve this dilemma. Such protocols let an untrusted prover, who possesses some private data, convince a verifier that the data satisfies a public property. For example, this could include proving that you are over 18 or that your account has sufficient balance, without revealing anything else such as your full date of birth, or your financial history. Furthermore, the proofs or certificates produced by such systems are relative short, and can be verified in a matter of milliseconds, rather than the days or weeks required to re-execute the computation.

Long in the realm of theory, cryptographic proof systems are now practical enough to be deployed for a number of applications, most notably in the context of making blockchains scalable and private. A number of teams are racing to build the most generic proof systems possible - a _zero-knowledge virtual machine (zkVM)_. Think of it like a virtual computer that allows one to run any computer program (as long as they are compiled to a common ISA like RISC-V), and then produce a certificate that the program was run correctly on any given input, producing the claimed output.

This blog post is a glimpse into these exciting developments. It turns out that the fastest of such zkVMs, such as Jolt, derive its efficiency from a classical protocol first introduced in 1992, called the sum-check protocol. I will give an introduction to the sum-check protocol, detail well-known algorithms for the sum-check prover, and introduce a new technique that speeds up the sum-check prover in settings relevant to zkVMs.

## Sum-Check Protocol Overview

The sum-check protocol is an interactive proof that allows an untrusted prover to convince a computationally limited verifier of the value of a very large sum. Informally, the verifier wants to check the sum of a multivariate polynomial over a large product domain, but would like to avoid explicitly adding up all of the terms.

Formally, we fix a finite field $\mathbb{F}$ and a multivariate polynomial $p(X_1, \dots, X_n) \in \mathbb{F}[X_1,\dots, X_n]$,
of degree bounded by $d$ in each variable. The sum-check claim is then
$$
    \sum_{x_1 \in H_1, \dots, x_n \in H_n} p(x_1,\dots,x_n) = c,    
$$
for some evaluation domains $H_1, \dots, H_n \subseteq \mathbb{F}$ and a claimed value $c \in \mathbb{F}$.
In most applications, and for the remainder of this blog post, we restrict to the Boolean hypercube, i.e., $H_1 = \dots = H_n = \{0,1\}$.

The verifier knows $p$, or at least has oracle access to evaluations of $p$ at points of its choice, but wants to use this query access as little as possible. Naively, the verifier could evaluate $p$ on all $2^n$ points of $\{0,1\}^n$ and sum the results, which takes work on the order of $O(2^n)$. The key idea of sum-check is that, by interacting with an untrusted prover who supplies additional "auxiliary" polynomials, the verifier can reduce the work of checking the original claim to checking a related claim about $p$ at a single randomly chosen point.

In particular, the data that the prover sends at each round are the "one-dimensional" slices of this multivariate
polynomial. In the first round, the prover sends the univariate polynomial
$$
    s_1(X) = \sum_{(x_2,\dots,x_n) \in \{0,1\}^{n-1}} p(X, x_2,\dots,x_n).
$$
If the original claim is correct, then $s_1(X)$ has degree at most $d$, and moreover
$s_1(0) + s_1(1) = c$.
The verifier checks precisely these two conditions, and rejects if either fails.

If both checks pass, the verifier samples a random challenge $r_1 \gets \mathbb{F}$ and sends it to the prover.
The point of this random challenge is to "pin down" the prover’s behavior at a point of the verifier’s choice:
if the prover has lied about $s_1(X)$, then with high probability (at most $d / |\mathbb{F}$|)
the fake $s_1$ will disagree with the true polynomial at $X = r_1$.
If we set the finite field size to be sufficiently large, e.g., at least $128$ bits for cryptographic security, then this probability is truly negligible.

After this first round of interaction, the prover and verifier have effectively reduced the problem to showing that
$$
    \sum_{(x_2,\dots, x_n) \in \{0,1\}^{n-1}} p_{r_1}(x_2, \dots, x_n) = c_1,
$$
where we define $p_{r_1}(x_2,\dots,x_n) := p(r_1, x_2,\dots,x_n)$ and $c_1 := s_1(r_1)$.
That is, we have "fixed" the first variable to $r_1$ and now need to verify a new sum-check claim in $n-1$
variables.
The protocol then repeats the same pattern on this new instance:
in the second round, the prover sends a univariate polynomial
$$
    s_2(X) = \sum_{(x_3,\dots,x_n) \in \{0,1\}^{n-2}} p_{r_1}(X, x_3,\dots,x_n),
$$
the verifier checks the degree and a simple consistency relation analogous to $s_1(0) + s_1(1) = c_1$,
samples a fresh random $r_2 \gets \mathbb{F}$, and so on.

After $n$ rounds, all variables have been fixed to random challenges $r_1,\dots,r_n \in \mathbb{F}$,
and the verifier is left with a single claim of the form
$$
    p(r_1,\dots,r_n) = c_n
$$
that it can check directly using its oracle access to $p$.

What properties does the sum-check protocol satisfy? The first is **completeness**. If the original sum claim is correct and the prover follows the rules, then every round’s check passes, and at the end we really do have $p(r_1,\dots,r_n) = c_n$, so the verifier accepts.

The more interesting property is **soundness**, which is about what happens when the original claim is actually false. In that case, no matter how a (possibly malicious) prover behaves, at some round it must send a polynomial that is not the "right" one. Two different low-degree polynomials over a field can only agree on a small fraction of inputs (also known as the Schwartz–Zippel lemma); thus, a random challenge $r_i$ will land on a point where they differ except with probability at most $d / |\mathbb{F}|$. Thus, even when the claim is wrong, a cheating prover can make the verifier accept only with negligible probability.

## Brief Interlude on Multilinear Polynomials

So far, we have only described sum-check as a protocol on polynomials over finite fields. But how does this relate to any
computation performed in the real world? The key bridge between the two is called the **arithmetization** of the computation:
we first transform the computation trace—such as the values of all registers over time, or the sequence of memory accesses and
intermediate constraint values—into polynomials, and then we use sum-check to reason about those polynomials instead of the
original computation.

The most common arithmetization method used in modern proof systems is to package these traces and constraint tables into
**multilinear polynomials**.
A multilinear polynomial is a multivariate polynomial where each variable appears with degree at most $1$.
For instance,
$$
    q(X_1, X_2, X_3) = 3X_1 X_3 + 2X_2 + 5
$$
is multilinear, while $X_1^2 + X_2$ is not. A key fact is that a multilinear polynomial in $n$ variables is uniquely
determined by its values on the $2^n$ points of the Boolean hypercube $\{0,1\}^n$. This means we can equivalently think
of a length-$2^n$ vector as giving the evaluations of some multilinear polynomial on $\{0,1\}^n$.

This correspondence can be made precise. Given a function $p : \{0,1\}^n \to \mathbb{F}$ (for example, a vector of trace or constraint values indexed by
$y \in \{0,1\}^n$), its **multilinear extension** is the unique multilinear polynomial $\widetilde{p}(X_1,\dots,X_n)$
that agrees with $p$ on all Boolean points. One convenient way to write this extension is
$$
    \widetilde{p}(X_1,\dots, X_n) = \sum_{y \in \{0,1\}^n} \widetilde{eq}(\vec{X}, y) \cdot p(y),
$$
where the "equality" polynomial $\widetilde{eq}$ is defined by
$$
    \widetilde{eq}(\vec{X}, \vec{Y}) = \prod_{i=1}^n \big((1 - X_i)(1 - Y_i) + X_i Y_i\big).
$$
For $\vec{x}, \vec{y} \in \{0,1\}^n$, this satisfies $\widetilde{eq}(\vec{x}, \vec{y}) = 1$ if $\vec{x} = \vec{y}$
and $0$ otherwise, so each term in the sum "picks out" the value $p(y)$ at exactly one point on the hypercube.

As a tiny example of a multilinear extension in one variable, imagine a 2-cycle program where a register holds values
$(a_0, a_1)$ over time. We can view this as a function $p : \{0,1\} \to \mathbb{F}$ with $p(0) = a_0$ and $p(1) = a_1$.
Its multilinear extension is the unique degree-1 polynomial
$$
    \widetilde{p}(X) = a_0 \cdot (1 - X) + a_1 \cdot X,
$$
which agrees with the original values at $X = 0$ and $X = 1$, but can also be evaluated at non-Boolean points such as
$X = 1/2$, or indeed any point in the finite field $\mathbb{F}$. In exactly the same way, an $n$-dimensional table of
values can be turned into a multilinear polynomial in $n$ variables.

This multilinear extension viewpoint is what lets us turn discrete objects like execution traces and constraint
tables into low-degree polynomials, which are precisely the objects that sum-check knows how to handle.

### Example: Arithmetizing a Batched Zero-Check

To see how this connects back to sum-check, consider a very simple proof goal: you want to prove that **four constraints
all vanish**. Label the four points of $\{0,1\}^2$ as
$(0,0), (0,1), (1,0), (1,1)$, and suppose you have two functions
$$
    p, q : \{0,1\}^2 \to \mathbb{F}
$$
such that you want to prove
$$
    p(x_1, x_2) \cdot q(x_1, x_2) = 0 \quad \text{for all } (x_1, x_2) \in \{0,1\}^2.
$$
You can think of each pair $p(x_1, x_2), q(x_1, x_2)$ as encoding one local constraint, so this is just a
**batched zero-check** for four constraints.

This pointwise condition can be bundled into a single sum over the hypercube. Define
$$
    g(x_1, x_2) = p(x_1, x_2) \cdot q(x_1, x_2),
$$
and consider the claim that
$$
    g(x_1, x_2) = 0 \quad \text{for all } (x_1, x_2) \in \{0,1\}^2.
$$
Equivalently, the multilinear extension $\widetilde{g}$ should vanish on all Boolean points. Using the equality
polynomial, we can package this as the single identity
$$
    \sum_{(x_1, x_2) \in \{0,1\}^2} \widetilde{eq}\big((r_1, r_2), (x_1, x_2)\big) \cdot p(x_1, x_2) \cdot q(x_1, x_2) = 0
$$
for a randomly chosen point $(r_1, r_2) \in \mathbb{F}^2$.
The left-hand side is exactly the evaluation $\widetilde{g}(r_1, r_2)$ of the multilinear extension of $g$
at the random point $(r_1, r_2)$. So, instead of checking four separate equalities $g(x) = 0$ at the cube points,
we check a **single** polynomial identity at a random point.

This is now in the right shape for sum-check: it is a sum over $(x_1, x_2) \in \{0,1\}^2$ of a polynomial in
$x_1, x_2, r_1, r_2$. In larger systems, we do the same thing with many more variables and many more constraints:
pointwise "zero checks" $p(x) \cdot q(x) = 0$ over a hypercube are encoded as a single sum-check instance over
a polynomial built from the equality polynomial and the multilinear encodings of $p$ and $q$.

## Existing Algorithms for Sum-Check

Special focus: sum-check over low-degree functions applied to a number of multilinear polynomials

Why? captures known applications. Example: a zero-check of quadratic constraints.

In fact, let's just focus on a single case: a product of two multilinear polynomials:

$$
    \sum_{x \in \{0,1\}^n} p(x) * q(x) = c.
$$

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
drive) to store all the evaluations, but not enough storage in RAM to store the intermediate
values. Alternatively, the evaluations can be generated cheaply on-the-fly, but not enough storage (RAM or otherwise) for the bound evaluations.

So, we can compute from scratch every round, or at least until there is enough space to
materialize the polynomial

Indeed, we can compute from the initial evaluations since
$$
    s_i(X) = \sum_{\vec{x'} \in \{0,1\}^{n - i - 1}} p(r_1, \dots, r_{i-1}, X, \vec{x'}) \cdot q(r_1, \dots, r_{i-1}, X, \vec{x'}) \\
    = \sum_{(x_{i+1},\dots,x_n) \in \{0,1\}^{n - i - 1}} (\sum_{(y_1,\dots,y_{i-1})} \widetilde{eq}(\vec{r}, \vec{y}) \cdot p(\vec{y}, X, \vec{x'})) \cdot (\sum_{(y_1,\dots,y_{i-1})} \widetilde{eq}(\vec{r}, \vec{y}) \cdot q(\vec{y}, X, \vec{x'})).
$$

This looks like a mouthful, but it actually gives us a nice algorithm to compute $s_i(u)$ for all $u
= 0, 1, 2$ via a single pass over the stream of evaluations of $p$ and $q$. We stream, chunk by
$2^{i-1}$ terms, then sum again over those chunked terms. (TODO: write this out more clearly)

## New Idea: Delayed Binding and its Benefits

The standard sum-check prover binds one variable per round to a random challenge from a large field. This makes the first round cheap (inputs are still “small,” e.g., 64-bit), but after that, the prover’s arithmetic immediately moves into the large field, which is much slower.

Our idea is simple: delay binding for a short “window” of rounds. Instead of committing to the verifier’s challenges right away, we treat the next w variables symbolically and precompute just enough to answer those w rounds in one go.

What does that buy us?

- Small-value speedup: In many real systems (like zkVMs), the underlying data are machine-word integers, while the proof system uses a 256-bit field. By batching the first few rounds, we can keep most of the heavy lifting in fast, native arithmetic. We only “pay” the big-field cost when we finally bind the window to the verifier’s challenges.

- Better streaming: If memory is tight, we reuse the same windowing trick across multiple passes. Each pass materializes the evaluations we need for its window, answers those rounds, and moves on. With the right schedule—small windows early, larger windows later—we reduce the prover’s dependence on the polynomial degree from O(d^2) to O(d log d), while staying within a sublinear memory budget.

Intuitively, batching trades a bit of extra precomputation for avoiding many slow multiplications after the first round. The window size w is a knob: too small and we leave performance on the table; too large and we overcompute. In practice, a short window already makes the first (most expensive) rounds dramatically cheaper, and a growing window schedule gives a strictly better streaming prover.

Takeaway: by grouping rounds and binding challenges later, we keep the prover in its “fast lane” longer and shrink the overall runtime—both in the common small-value case and in streaming regimes.

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

 -->