address_normalizer
==================

A fast, international postal address normalizer and deduper.

## What it does

The use case for this system is a well-known one: given several real-world postal addresses entered by humans as natural language text, find (and destroy) all duplicates. 

Like many problems in information extraction and NLP, this may sound trivial initially, but in fact can be quite complicated in real natural language texts.

As a motivating example, consider the following two equivalent ways to write a particular Manhattan street address with varying conventions and degrees of verbosity.

* 30 W 26th St Fl #7
* 30 West Twenty-sixth Street Floor Number 7

Obviously '30 W 26th St Fl #7 != '30 West Twenty-sixth Street Floor No. 7' in a string comparison sense, but a human can grok that these two addresses refer to the same physical location.

This library helps convert messy addresses that humans use into clean normalized forms suitable for machine comparison. It also includes a LevelDB/RocksDB-backed near duplicate store for checking new candidate addresses against an index of previously ingested addresses to see if it is a near duplicate of any of them while doing minimal comparisons (suitable for ingestion pipelines).

## Usage

```
from address_normalizer import normalize_street_address
addr1_expansions = normalize_street_address('30 West Twenty-sixth Street Floor Number 7')
addr2_expansions = normalize_street_address('30 W 26th St Fl #7')
# Share at least one expansion in common
addr1_expansions & addr2_expansions
```

## What it doesn't do

* verify that a location is a valid address

## References

For further reading and some less intuitive examples of addresses, see "[Falsehoods Programmers Believe About Addresses](http://www.mjt.me.uk/posts/falsehoods-programmers-believe-about-addresses/)".

## TODOS

* sequence model to parse addresses into components like house number, street name, etc. (needs a small amount of training data)
* sequence model for predicting which expansion is the correct one. "Dr" can mean either "Doctor" or "Drive" but for the purposes of deduping we just save both expansions. (needs some training data)
* parse postal addresses from texts such as web documents