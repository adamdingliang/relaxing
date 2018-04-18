#!/usr/bin/env bash
# This script creates a Jupyter notebook in an interactive node of hpc
# and forward traffic on the local port to the remote port

HOST="hpc.stjude.org"
ssh $HOST ". ~/.bashrc; hpcf_interactive -q pcgp_heavy_io; ls"
