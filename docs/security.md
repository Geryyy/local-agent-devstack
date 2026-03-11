# Security notes

## Default posture
- local-first
- tunnelled access
- no public model endpoint exposure
- no secrets committed to git

## Practical recommendations
- use SSH keys for laptop -> workstation
- do not run Ollama on `0.0.0.0` unless you really need it
- prefer direct Ethernet or VPN + SSH
- keep model-serving credentials and cloud API keys in shell env or a secret store
- use closed models only when the task justifies it

## Data handling
By default, private code and documents should stay local. Closed-model tools are opt-in and should be used intentionally.
