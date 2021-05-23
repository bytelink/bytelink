# Welcome to ZeroCom 👋
[![Twitter: janaSunrise](https://img.shields.io/twitter/follow/janaSunrise.svg?style=social)](https://twitter.com/janaSunrise)

> A secure and advanced chat application in Python.

## Install

The project uses pipenv for dependencies. Here's how to install the dependencies.

```sh
pipenv sync -d
```

## Usage

The server is configured to run in `127.0.0.1` in the port `5700`. The project uses a `.ini`
configuration file to config it, which is located at `config.ini`. You can configure as
you want by tweaking the settings in it.

#### Running the server

Here's how you can run the server, so you can connect using clients.

```sh
python -m server
```

#### Running the client, and logging into a server

Once you have the server running, or someone has a compatible server node running,
Here's how you can login to the server, by running the client like this.

```sh
python -m client <SERVER_IP> <PORT> <USERNAME> <PASSWORD>
```

## Future plans

- [x] Better logging.
- [ ] Improved Client chat features, and usage.
- [ ] Password based server encryption
- [x] Public, Private Key verification, using RSA and SHA-256 pairs.
- [ ] End to End Message Encryption and Decryption
- [ ] [BUG FIX] Remote server functioning doesn't work.

## 🤝 Contributing

Contributions, issues and feature requests are welcome. After cloning & setting up project locally, you can just submit 
a PR to this repo and it will be deployed once it's accepted.

⚠️ It’s good to have descriptive commit messages, or PR titles so that other contributors can understand about your 
commit or the PR Created. Read [conventional commits](https://www.conventionalcommits.org/en/v1.0.0-beta.3/) before 
making the commit message.

## 💬 Get in touch

If you have various suggestions, questions or want to discuss things wit our community, Have a look at
[Github discussions](https://github.com/janaSunrise/useful-python-snippets/discussions) or join our discord server!

[![Discord](https://discordapp.com/api/guilds/695008516590534758/widget.png?style=shield)](https://discord.gg/cSC5ZZwYGQ)

## Show your support

We love people's support in growing and improving. Be sure to leave a ⭐️ if you like the project and 
also be sure to contribute, if you're interested!

<div align="center">
  Made by Sunrit Jana with ❤️
</div>
