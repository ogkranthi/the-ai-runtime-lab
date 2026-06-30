# The AI Runtime Field Lab 01

A Reliability Layer for Web-Grounded Agents. Build a design-partner sourcing agent
on Apify, then prove which of its leads are safe to act on.

Lab page: https://lab.theairuntime.com/01/

The build is split into two modules, each in its own folder, each runnable on its
own.

## Module 1: the sourcing agent

Folder: [`web-agents-apify/`](web-agents-apify/)

Point it at a list of target companies and it plans which Apify Actors to run,
crawls public pages, and returns a prospect list where every field traces to a
source. The list looks done.

    cd web-agents-apify
    python agent.py

## Module 2: the reliability layer

Folder: [`web-agents-trust/`](web-agents-trust/)

It takes module 1's list and decides which of it is actually safe to act on: a
source-agnostic trust core that catches stale, unsupported, conflicting, and
wrong-entity values, a thin fit filter on top, and an eval that proves the core
works against a planted trap set. Two of the four candidates fall.

    cd web-agents-trust
    python pipeline.py     # the reveal
    python eval.py         # grade the trust core

## The arc

Module 1 produces a list that looks done. Module 2 reveals which of it is real.
That gap, between a list that looks done and a list you can act on, is the whole
point of the lab. Each folder has its own README and an `ARCHITECTURE.md` written
as learning material.
