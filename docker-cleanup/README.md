# Docker Image Cleanup Script

This script removes old Docker images and keeps only the **latest created image per repository**.  
It helps free up disk space by deleting unused or outdated builds while preserving the most recent one.

## How it works

- Lists all repositories (`docker images`).
- Sorts images within each repository by **creation timestamp** (newest first) - NOT using image tag timing since some are in UTC, some are in SGT.
- Keeps only the newest image.
- Deletes all older images for that repository.

## Usage

1. Save the script as `c.sh`:

```bash
vi cleanup_docker_images.sh
```

2. Make it executable:

```bash
chmod +x cleanup_docker_images.sh
```

3. Run the script:

```bash
./cleanup_docker_images.sh
```

**Notes**

- This script uses docker rmi -f to force remove old images.
- Running containers are not affected, only the images.
