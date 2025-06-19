# Auto Start Script

✅ Steps to Auto-Start Script on Boot (Headless)

1. ✅ Make sure your script is executable
Let’s assume your script is saved as:

```swift
/home/projects/light-control/script-final.py
```

Make it executable:

```bash
chmod +x /home/projects/light-control/script-final.py
```

If it runs in a virtual environment (pi_env), we’ll include that path too.

2. ✅ Create a systemd service file

Create a new service:

```bash
sudo nano /etc/systemd/system/light-control.service
```

Paste this (adjust paths if needed):

```ini
[Unit]
Description=Audio + Light Fade Control Script
After=network.target sound.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/projects/light-control
ExecStart=/home/projects/light-control/pi_env/bin/python /home/projects/light-control/script-final.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

🔁 Replace pi under User= if your user is different.

3. ✅ Enable and start the service

```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable light-control.service
sudo systemctl start light-control.service
```

✅ It will now run automatically at every boot.

4. 🔍 Check if it's working

After booting:

```bash
sudo systemctl status light-control.service
```

To view logs:

```bash
journalctl -u light-control.service -f
```

🛑 To stop or disable the service

```bash
sudo systemctl stop light-control.service
sudo systemctl disable light-control.service
```

✅ Your Pi is now:
Running your script in the background,

Responding to button input,

Playing audio + fading light,

No UI or terminal needed.

Let me know if you want to add a log file, auto-kill stuck VLC processes, or support for multiple audio tracks.

# Optional Delete Script From Service

🧹 Delete a systemd service
Assuming your service is called light-control.service:

1. Stop the service (if running)
```bash
sudo systemctl stop light-control.service
```

2. Disable it from starting on boot
```bash
sudo systemctl disable light-control.service
```

3. Delete the service file
```bash
sudo rm /etc/systemd/system/light-control.service
```

4. Reload systemd daemon
```bash
sudo systemctl daemon-reload
```

5. (Optional) Verify it's gone
```bash
sudo systemctl status light-control.service
```

You should see:

```bash
Unit light-control.service could not be found.
```
