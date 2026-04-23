#!/usr/bin/env bash
# Seed Azurite containers for the Bronze Azure Blob tier.
set -euo pipefail

AZCOPY_CREDENTIAL_TYPE=Anonymous \
az storage container create \
  --account-name devstoreaccount1 \
  --name lakehouse \
  --connection-string "${AZURE_STORAGE_CONNECTION_STRING:-DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://azurite:10000/devstoreaccount1;}" || true

echo "[azurite] lakehouse container ensured"
