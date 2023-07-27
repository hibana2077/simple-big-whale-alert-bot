
# Simple Big Whale Alert Bot

## Introduction

This is a simple bot designed to alert users about significant cryptocurrency transactions, also known as "whale" transactions. It's a great tool for crypto traders and enthusiasts who want to stay updated about major market movements.

## Features

- Real-time alerts for significant cryptocurrency transactions
- Easy to set up and use
- Supports multiple cryptocurrencies
- Delightful Discord embeds

## Screenshots

![Imgur](https://i.imgur.com/EhrCnOM.png)

![Imgur](https://i.imgur.com/Qt6juBF.png)

![Imgur](https://i.imgur.com/gHvJJYD.png)

## Installation

1. Clone the repository

```bash
git clone https://github.com/hibana2077/simple-big-whale-alert-bot.git
```

2. Navigate to the project directory:

```bash
cd simple-big-whale-alert-bot
```

3. Install the necessary dependencies.

```bash
pip install -r requirements.txt
```

## Usage

Run the script with the following command:

```bash
python main.py -at <Alchemy token> -d <Discord webhook URL> -th <Threshold>
```

or use docker image:

```bash
docker run -d --name mybot -e ALCHEMY_TOKEN=<Alchemy token> -e DISCORD_WEBHOOK_URL=<Discord webhook URL> -e THRESHOLD=<Threshold> hibana2077/sbwab
```

[Get your Alchemy token here](https://alchemy.com/?r=zM4ODUyNDkxNTY0O).

[Get your Discord webhook URL here](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks).

[Docker Hub](https://hub.docker.com/repository/docker/hibana2077/sbwab/general).

## License

This project is licensed under the terms of the MIT license. See the [LICENSE](LICENSE) file for details.

## Contact

If you have any questions, feel free to reach out to [me](hibana2077@gmail.com) or open an issue in the repository.
