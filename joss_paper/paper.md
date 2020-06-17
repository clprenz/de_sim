---
title: 'DE-Sim: An Object-Oriented Discrete-Event Simulator in Python'
tags:
  - Python
  - dynamics
  - modeling
  - simulation
  - discrete-event simulation
  - object-oriented simulation
  - parallel discrete-event simulation
authors:
  - name: Arthur P. Goldberg
    orcid: 0000-0003-2772-1484
    affiliation: "1, 2" # (Multiple affiliations must be quoted)
affiliations:
 - name: Icahn Institute for Genomics and Multiscale Biology
   index: 1
 - name: Department of Genetics and Genomic Sciences, Icahn School of Medicine at Mount Sinai, New York, NY, 10029, USA
   index: 2
date: 20 July 2020
bibliography: paper.bib
---

# Summary

Discrete-event simulation (DES) is a dynamical simulation method that analyzes systems whose events occur at discrete instants in time.
Many fields employ models that use DES, including computer network performance analysis, biochemical modeling, war gaming, modeling of infectious disease transmission, and others [@banks2005discrete].

The construction of DES models can be simplified and accelerated by using a DES simulator that implements the generic features needed by all DES models, such as executing events in increasing simulation time order.
Model construction can be further enhanced, and models can be made more comprehensible and reusable, by structuring models as object-oriented programs.
This approach, which is known as *object-oriented discrete-event simulation*, encourages modelers to represent entities in the system being modeled as objects in a model, and represent interactions between entities as event messages in the model.
OO DES began in the 1960s, with the SIMULA language, which was also the first object-oriented language [@dahl1966simula; @nygaard1978development].



DE-Sim is a Python package that provides a DES simulator and supports object-oriented (OO) DES models.

# Research purpose

An OO DES Python package is needed by researchers who wish to build OO DES models of dynamical systems.
(Cite kylan's SIP model)
Existing open source Python simulators, such as SimPy, do not provide an OO, message-passing interface.

DES models often take very long to simulate.
An important benefit of implementing models in an object-oriented, message-passing framework is that parallel simulation can reduce their simulation times.
The OO framework makes this feasible because 1) properly constructed objects do not share memory references, and 2) a parallel DES simulator interfaces with simulation objects via event message send and receive operations.

Python p
Whole-cell models ... [@goldberg2016toward]

# Features

# Implementation

# Example

# Acknowledgements

# References