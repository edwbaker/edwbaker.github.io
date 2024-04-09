# Visualisation of Collatz Conjecture in R

## Intro

Take any positive integer, n. If n is even divide it by 2 (n/2). If n is odd multiple by 3 and add 1 (3n+1). Repeat the process on the new value. The Collatz Conjecture is that this sequence will eventually reach 1 (or more accurately will get stuck in the loop 4 -> -> 2 -> 1 -> 4). The routes from n to 1 can be visualised as a graph.

<img src="/imgs/collatz-graph.png" alt="Graph of Collatz COnjecture" height="593" width="72"/>
Graph of the collatz conjecture from [Wikimedia](https://en.wikipedia.org/wiki/File:Collatz-graph-all-30-no27.svg).

While this display is informative, prettier visualisations of many more numbers are possible (inspired by the below YouTube video).

{% include youtube.html id ="LqKpkdRRLZw" title="Collatz Conjecture in Color - Numberphile" %}

## Visualisation

The R code (link below) generates a graph of all numbers between 1 and the highest value (bigNumber in the script). When plotting the graph edges ending in an even number are plotted slightly anti-clockwise from the previous node, and odd numbers are plotted slightly clockwise. The amount of anti-clockwise rotation does not need to be the same as the amount of clockwise rotation, which allows the overall graph to be plotted relatively straight, and careful choice of values will prevent lines performing complete revolutions.

The graph is plotted just using R plot primitives (`segments()`) rather than any other package.

5000 terms of the Collatz Conjecture graphed in R  
n=1-5000, odd-rotation=1.2, even-rotation=-0.54

<img src="/imgs/collatz1.png" alt="Graph of Collatz COnjecture in R 1" width="743" height="521" />


50000 terms of the Collatz Conjecture graphed in R  
n=1-50000, odd-rotation=4.1, even-rotation=-2.3

<img src="/imgs/collatz2.png" alt="Graph of Collatz COnjecture in R 2" width="743" height="521" />

## Code

The code is available on GitHub: [Collatz Conjecture visualisation in R](https://github.com/edwbaker/collatz).
