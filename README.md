# CloudedBats WIRC-2025-backend

Welcome to the backend part of the WIRC system (Wireless InfraRed Camera) for bat monitoring.

The WIRC system is intended as a complement to the WURB system (Wireless Ultrasonic Recorder for Bats), 
but instead of focusing on ultrasonic sound we now are focusing on using infrared light to monitor the bats.

Both WURB and WIRC runs on Raspberry Pi and they can be installed together. Both systems provide APIs, and also web applications that can be used directly without any installation on the client computer. By default WURB-2024 is running on port 8080 and WIRC-2025 uses the port 8082.

A WIRC-2025 client app is under development and in the future there will be apps with more functionality that can be installed on mobile phones and desktop computers. More info will appear here:
https://github.com/cloudedbats/wirc_2025 

With this WIRC-2025-backend system you can use the web application to check the live preview image stream, adjust exposure time and gain, take jpeg photos, and record videos. The selected exposure time is used both for photos and video and is the key setting to get sharp images on fast moving objects.
To download and manage recorded files you have to use an SFTP client, like FileZilla or WinSCP. In the future the new client app will take care of that.

"To monitor bats we have to use ultra for sound and infra for light."

## The web user interface

TODO: Image.



The simple web app that is a part of the WIRC-2025-backend. Watching birds in daylight now, flying bats with IR-light is not possible in February in Sweden. Image: CloudedBats - CC0.

The web user interface only contains the most basic functionality and settings.
Then there is a possibility to make adjustments in a configuration file called "wirc_config.yaml".

## About infrared cameras and light

There are some more information available in this GitHub repository:

TODO: https://github.com/cloudedbats/wirc_camera_basics


## Installation

This is a short instruction on how to install camera support on a Raspberry Pi computer.

The installation is similar to the one used for CloudedBats WURB-2024,
but there is a difference for installed python libraries.
It is recommended to use "apt" to install the "picamera2" library. 
Therefore some libraries are installed outside the virtual environment that is normally used for python libraries.

The first step is to use the **Raspberry Pi Imager** to install the **Raspberry Pi OS** on a SD card.

Note that both the WIRC and WURB systems should be installed with the "wurb" user.
This is because it should be possible to run them i parallell.

Use these settings, or similar, when running the **Raspberry Pi Imager**:

- Select OS version: Raspberry Pi OS Lite (32-bit). 
- Hostname: wurb01c
- User: wurb
- Password: your-secret-password
- WiFi SSID: your-home-network
- Password: your-home-network-password
- Wireless LAN country: your-country-code
- Time zone: your-time-zone
- Activate SSH. Is located under the tab "Services".

Connect to the Raspberry Pi with SSH and do an update.

    ssh wurb@wurb01c.local
    
    sudo apt update
    sudo apt upgrade -y

Install some linus packages that is common for both WURB and WIRC.

    sudo apt install git python3-venv python3-dev -y
    sudoapt install  libatlas-base-dev libopenblas-dev -y
    sudoapt install pulseaudio pmount -y

Additions for camera support.

    sudo apt install -y python3-picamera2
    sudo apt install -y python3-pyqt5 python3-opengl
    sudo apt install -y python3-prctl python3-kms++ 
    sudo apt install -y ffmpeg
    sudo apt autoremove

Install the software in this repository.

    git clone https://github.com/cloudedbats/wirc_2025_backend.git
    cd wirc_2025_backend/
    python -m venv --system-site-packages venv
    source venv/bin/activate
    pip install -r requirements.txt

    sudo cp /home/wurb/raspberrypi_files/wirc_2024.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable wirc_2024.service
    sudo systemctl start wirc_2024.service

## Attached cameras

Attached cameras should be available after a reboot if they are directly supported by Raspberry Pi.

If you use other cameras like the OV9281 you have to tell the system what you are using.
Raspberry Pi 5 supports two cameras (cam0 and cam1) and the other models supports one.

    sudo nano /boot/firmware/config.txt

    # Replace "camera-auto-detect=1" with
    camera-auto-detect=0
    
    # At the end of the file add this:
    dtoverlay=ov9281

    # If you are using Raspberry Pi 5 and want to connect two cameras you have to add
    # it like this (with two different global shutter cameras as an example):
    dtoverlay=ov9281,cam0
    dtoverlay=imx296,cam1

## Remote access

TODO.

## Web app and API

TODO.

## Contact

Arnold Andreasson, Sweden.

<info@cloudedbats.org>
