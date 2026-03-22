# Naming Decision

This repository has multiple naming layers. To reduce confusion, use the following naming convention moving forward.

## Canonical Naming

- **Repository:** `branchbot-deploy`
- **System / product line:** **BranchOS Revenue Stack**
- **Dashboard label:** **BranchOS Dashboard**
- **API label:** **BranchOS Revenue API**

## Why This Decision

- `branchbot-deploy` remains the repository identity on GitHub.
- `BranchOS` is the stronger business-facing system identity.
- `Revenue Stack`, `Dashboard`, and `Revenue API` are clearer than mixing in multiple unrelated names.

## Guidance

Use `BranchOS` in user-facing copy, demos, and documentation.
Use `branchbot-deploy` when referencing the GitHub repository.
Avoid introducing additional primary names unless they represent a new product.

## Cleanup Targets

When editing existing files later, normalize the following:

- README headings and product language
- service names in deployment docs
- dashboard titles and sidebars
- package/module references where renaming is safe
- issue and PR titles
