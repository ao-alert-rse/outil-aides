# GLOBAL OPERATING MODE

You are working on a large repository and must aggressively minimize token usage.

## Core principles

* Read the minimum amount of code necessary.
* Never read entire files unless explicitly requested.
* Never analyze the entire repository unless explicitly requested.
* Prefer targeted searches over exploration.
* Reuse previous findings instead of rereading files.
* Keep responses concise.

## Search strategy

Always follow this order:

1. rg
2. fd / Glob
3. Read specific files
4. Read specific line ranges
5. Edit minimally

Never:

* read entire directories;
* read entire repositories;
* reread files already summarized.

## Large files

For files larger than 100 KB:

* maximum 300 lines per read;
* maximum 1000 lines total per task;
* summarize findings and reuse summaries.

## Modifications

If more than 3 similar edits are required:

* write a temporary Python script;
* perform all changes in one pass;
* validate results;
* delete the temporary script.

Avoid repeated Edit operations.

## Output rules

Prefer:

* summaries
* counts
* diffs
* targeted snippets

Avoid:

* full files
* large arrays
* large objects
* long logs
* repeated code blocks

## Research

For large verification tasks:

* delegate to one research agent;
* group checks by source;
* return structured data only.

## Planning

Before coding:

1. Understand the request.
2. Produce a short plan.
3. Execute only the approved scope.

Do not perform unrelated refactors.

## Documentation

Update documentation only after implementation is complete.

## Validation

After modifications:

* run the smallest possible validation;
* report only failures and affected lines.

## Objective

Minimize:

* tokens
* context growth
* unnecessary reads
* unnecessary outputs

Maximize:

* correctness
* targeted edits
* deterministic workflows.
