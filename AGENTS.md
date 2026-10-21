# Contributor entry

Read the task scope before editing. The implementation is `harness.py`; generated
workspace templates are embedded there so the installed tool is self-contained.
Read only relevant source and tests; the complete guide is a reference.

Preserve reference repositories and existing destinations. Keep configuration
independent of user identity, machine paths and a fixed source revision. Do not
add a service, provider dependency or launcher without a concrete requirement.

Run `python3 -m unittest discover -s tests -v` and `git diff --check` after relevant
changes. Test installation from a fresh checkout using a separate fixture repo
and paths containing spaces. Keep synthetic/scripted evidence distinct from an
actual agent session, and local Git distinct from live hosting state.
