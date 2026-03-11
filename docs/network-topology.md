# Network topology

## Recommended mode: direct Ethernet + SSH

When both machines are physically next to each other:

- connect laptop and workstation via Ethernet
- assign a small static point-to-point subnet
- keep Wi-Fi active on the laptop for normal internet/VPN use
- run the model tunnel over SSH on the direct link

Example:

- workstation: `10.23.0.1/30`
- laptop: `10.23.0.2/30`

## Alternative mode: VPN

If the machines are on different networks:

- connect them with a VPN
- run the same SSH tunnel
- keep Ollama bound to localhost on the workstation

## Security rule

Do **not** open `11434` to the broader LAN or internet unless you add proper access control and explicitly accept the risk.
