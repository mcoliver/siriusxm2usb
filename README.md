# 🎵 siriusxm2usb

A powerful CLI tool that find songs from SiriusXM channels on Youtube Music

## Why 
- I love streaming services like Spotify, ytmusic, and siriusxm.  And I pay for them.  You should also if you love music and want artists to keep making it.
- I wanted a project to demonstrate how you can build a powerful cli with colored logging, argparsing, and multiprocessing in less than a day.
- Check your local copyright laws before running this with the --download flag

[![Python](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🚀 Features

- Download tracks from SiriusXM channels to your local storage
- Automatic YouTube Music search and matching
- Organized directory structure per channel
- Support for multiple SiriusXM channels
- Embeded metadata and album artwork
- Robust error handling and logging
- Multi-processing support for faster downloads

## 📋 Prerequisites

- Python 3.6+
- pip (Python package installer)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/mcoliver/siriusxm2usb.git
cd siriusxm2usb
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## 💻 Usage

Basic usage:
```bash
python siriusxm2usb.py -c 'channelname'
```

Multiple channels example:
```bash
python siriusxm2usb.py --channel 'bobmarleystuffgong' -c 'chrisstapletonradio' -c 'lifewithjohnmayer' -c 'noshoesradio' -c 'primecountry' -c 'siriusxmchill' -c 'siriusxmhits1' -c 'thebridge' -c 'thecoffeehouse' -c 'thehighway' -c 'williesroadhouse' -c 'y2kountry'
```

### Command Line Arguments

- `--debug`: Enable debug logging
- `-d, --destination`: Specify a destination folder (default: current directory)
- `-l, --log-file`: Specify custom log file path
- `-c, --channel`: Required. Specify a channel to download. Can use the flag multiple times.
- `--download`: Actually download the files (default: False)

## 🏗️ Project Structure

```
siriusxm2usb/
├── siriusxm2usb.py      # Main application script
├── requirements.txt      # Project dependencies
├── utils/               # Utility modules
│   ├── arg_parser.py    # Command line argument handling
│   └── logging_config.py # Logging configuration with color
├── json/                # Channel JSON data storage
├── logs/                # Application logs
```

## 🔄 Data Flow

1. Fetch and cache available stations from xmplaylist API
2. Process track information for specified channels
3. Search for matching tracks on YouTube Music
4. Download high-quality audio
5. Convert to MP3 and embed metadata
6. Save to channel-specific directories

## 🛡️ Dependencies

- `ytmusicapi`: YouTube Music API interface
- `yt-dlp`: YouTube download functionality
- `colorama`: Terminal color support
- `requests`: HTTP client for API calls

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🐛 Known Issues

- Rate limiting may affect download speeds
- Some tracks may not be found on YouTube Music

## 📞 Support

If you encounter any problems or have suggestions, please open an issue on the GitHub repository.

## 🙏 Acknowledgments

- [xmplaylist.com](https://xmplaylist.com) for their API
- YouTube Music for content availability
- The open-source community for various tools and libraries

---

