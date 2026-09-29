# Validation of this publication package

- The experimental patch applied with `git apply --check` to the reconstructed two-file base after the selected upstream patches.
- Both resulting source SHA256 values exactly matched the supplied tested end-apply snapshots documented in SOURCE.md.
- All packaged Python files passed syntax parsing.
- Five offline decision tests passed: target transition, no transition, already-Gen2, training-in-progress, and rejection of unexpected/mismatched link states.
- The watcher help command ran successfully. The packaged watcher and benchmark have not been executed on hardware by the package preparer. Reported bandwidth results come from the supplied experiment transcript.
- Text was scanned for the experiment's actual usernames, hostnames, IPs, PCI addresses, paths and common credential/MAC patterns. No matches were found.
- Only explicitly selected text files are archived. Original uploads, compiled modules, logs, bytecode, repository history, symlinks and filesystem ownership metadata are excluded. Archive timestamps are normalized.

These checks reduce accidental disclosure and transcription errors. They do not establish complete anonymity, absence of every possible secret, or reliability across other hardware.
