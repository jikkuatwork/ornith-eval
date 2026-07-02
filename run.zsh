podman run -d \
  --name open-webui \
  --network=slirp4netns:allow_host_loopback=true \
  -p 3000:8080 \
  -v open-webui-data:/app/backend/data \
  -e OLLAMA_BASE_URL=http://10.0.2.2:11434 \
  ghcr.io/open-webui/open-webui:main