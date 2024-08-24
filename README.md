# yap

## Create a Discord Bot:

1. Go to the [Discord Developer Portal](https://discord.com/developers/)
2. Create a new application.
3. Create a bot user and get the bot token.
4. Invite the bot to your server with the appropriate permissions (Read and Manage Messages).
5. Enable Message Content Intent under the bot section.

![alt text](image.png)

Your DISCORD_BOT_TOKEN can be found here.

![alt text](image-1.png)

## Build pod
```bash
podman build -t yap .
```

## Run pod
```bash
podman run --network host -e DISCORD_BOT_TOKEN="yourtokenhere" --cap-drop=ALL --security-opt=no-new-privileges -d --replace --name yap-container yap
```

## Pod params
```bash
--network host: Ensures the container uses the host’s network stack, bypassing the need for TUN/TAP devices.
#--read-only: Makes the filesystem read-only.
--cap-drop=ALL: Drops all Linux capabilities, ensuring the container runs with the least privileges.
--security-opt=no-new-privileges: Ensures the container processes cannot gain new privileges.
```

## Add this bot to your server
[Click here.](https://discord.com/oauth2/authorize?client_id=1255464592390361128)

## Preview