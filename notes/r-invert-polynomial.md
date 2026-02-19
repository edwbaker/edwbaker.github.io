---
title: "Invert a polynomial in R"
note_category: "Coding"
note_subcategory: "R"
---

# Inverting a polynomial using R

R code to numerically find the inverse of a polynomial.

```r
# Define a polynomial function to invert
pn <- function(x) {
  return(3*x^3 + 2*x^2)
}

# Generic invert() function
invert = function(fn, interval = NULL, ...){
  Vectorize(function(y){
    uniroot(function(x){fn(x)-y}, interval, ...)$root
  })
}

# Inversion function specific to pn()
pn.inverse <- invert(pn, interval = c(-10, 10))

# Find the inverse for a specific value
pn.inverse(4)
```
