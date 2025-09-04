+++
# The title of your blogpost. No sub-titles are allowed, nor are line-breaks.
title = "Algorithms for the Sum-check Protocol"
# Date must be written in YYYY-MM-DD format. This should be updated right before the final PR is made.
date = 2025-09-25

[taxonomies]
# Keep any areas that apply, removing ones that don't. Do not add new areas!
areas = ["Cryptography", "Theory"]
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
    {name = "Cayden Codel", url = "hhttps://www.crcodel.com/"}
]
+++

The sum-check protocol is a foundational primitive in the design of modern cryptographic proof
systems, enabling efficient proofs about sums of evaluations of multivariate polynomials over large
finite fields. Because of its central role, the running time and memory usage of the sum-check
protocol, especially on the prover side, has become a major bottleneck in many proof systems.

In this post, we give a survey of existing algorithms sum-check proving, with a focus on new
techniques that were developed in my recent work. I will describe existing algorithms, known time-space tradeoffs for any sum-check proving algorithms, and new techniques that get us closer to the ideal computational complexity of sum-check proving.

# Introduction to Sum-Check

Describe protocol, observe its properties.

# Why sum-check?

Describe how various computational claims can be encoded in sum-check format.

# Existing Algorithms for Sum-Check Proving

1. Linear-time, linear-space algorithm
2. Quasilinear-time, logarithmic-space algorithm

# New Techniques for Sum-Check Proving

O(N (\log \log N + k)) time, O(N^{1/k}) space algorithm

# Algorithms in specific settings

Small-value sum-check proving

High-degree optimization

Equality polynomial optimization

# Conclusion {#conclusion}
