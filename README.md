# archive-vbulletin-thread

A Python script to archive threads from vBulletin-based forums. Downloads all pages of a thread and saves them in both JSON and text formats for easy archival.

## Features

- Downloads all pages of a vBulletin forum thread
- Preserves post content, author information, and timestamps
- Saves in both JSON (for programmatic use) and human-readable text formats
- Includes detailed logging
- Handles pagination automatically
- Respects rate limiting to avoid overwhelming the server

## Requirements

- Python 3.x
- `requests`
- `beautifulsoup4`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/popey/archive-vbulletin-thread.git
cd archive-vbulletin-thread
```

2. Create and activate a virtual environment (using [uv](https://github.com/astral-sh/uv)):
```bash
uv venv
source .venv/bin/activate  # On Unix/Linux
```

3. Install dependencies:
```bash
uv pip install requests bs4
```

## Usage

Run the script with a vBulletin forum thread URL:
```bash
python archive_thread.py "https://forums.example.com/showthread.php?t=123456"
```

For example:
```text
python ./archive_thread.py "https://ubuntuforums.org/showthread.php?t=2501735"
2025-01-19 16:09:09,576 - INFO - Starting to archive thread: https://ubuntuforums.org/showthread.php?t=2501735
2025-01-19 16:09:09,887 - INFO - Thread title: There's no reason to use Linux Mint
2025-01-19 16:09:09,887 - INFO - Found 3 total pages
2025-01-19 16:09:09,887 - INFO - Processing page: https://ubuntuforums.org/showthread.php?t=2501735
2025-01-19 16:09:13,140 - INFO - Processing page: https://ubuntuforums.org/showthread.php?t=2501735&page=2
2025-01-19 16:09:16,394 - INFO - Processing page: https://ubuntuforums.org/showthread.php?t=2501735&page=3
2025-01-19 16:09:19,669 - INFO - Saved JSON to archived_threads/2501735-Theres-no-reason-to-use-Linux-Mint.json
2025-01-19 16:09:19,671 - INFO - Saved text file to archived_threads/2501735-Theres-no-reason-to-use-Linux-Mint.txt
2025-01-19 16:09:19,671 - INFO - Successfully archived thread with 28 posts
Thread archived successfully!
```


## Output

The script creates two files for each archived thread in the `archived_threads` directory:

1. A JSON file containing structured data
2. A text file with human-readable formatted content

Example output structure:
```
archived_threads/
├── 123456-thread-title.json
└── 123456-thread-title.txt
```

The script also creates a detailed log file (`thread_archiver.log`) for tracking the archival process.

For example:


```text
Thread Title: There's no reason to use Linux Mint
Thread URL: https://ubuntuforums.org/showthread.php?t=2501735
Scraped at: 2025-01-19T16:09:09.576915

--- Post #1 ---
Author: volteos
Posted at: October 18th, 2024

Content:
I don't understand why people use Linux Mint, an antiquated OS. People talk about the Cinnamon desktop, but my sentiment is why would you use it when Ubuntu has Cin
namon. I get being a beginner/distro hopper, but it really doesn't make sense to use anything else other than Ubuntu if you're going to use their repo base anyway.
I don't know, I guess I can see it philosophically, maybe they don't like corporate distros, or maybe they don't like snaps (to be frank I like snaps a lot more tha
n flatpaks). But the bottom line is at the end of the day to me, Linux Mint is pointless. When I started, I recall about 5 years ago, I kept switching to different
OS not knowing that the only major real difference was really just the politics and desktop environments. I think a lot of newcomers are unaware of this fact and keep thinking that some how Arch is going to be vastly different as an overall experience than OpenSuse or Fedora...when they virtually use the same sort of packaging scheme. On top of that I can truly say that the best environment I've ever worked with is GNOME, and only two systems come into mind for me philosophically as a superior choice. The first system is Ubuntu, because everything works on it, I like snaps, I just wish they worked with my custom theme, never had a bad experience with snaps either. The second system is Manjaro, which is what I deem the more "non-corporate" distro because you have a vetting system that's handled by the community, and they're not psychotic about code of eihics and stuff like that. Other than that, it really sucks seeing people fall into a hivemind that Linux Mint is somehow a gamechanger, when it's really just Ubuntu. 
```

```json
{
  "title": "There's no reason to use Linux Mint",
  "url": "https://ubuntuforums.org/showthread.php?t=2501735",
  "posts": [
    {
      "timestamp": "October 18th, 2024",
      "author": "volteos",
      "content": "I don't understand why people use Linux Mint, an antiquated OS. People talk about the Cinnamon desktop, but my sentiment is why would you use it w
hen Ubuntu has Cinnamon. I get being a beginner/distro hopper, but it really doesn't make sense to use anything else other than Ubuntu if you're going to use their
repo base anyway. I don't know, I guess I can see it philosophically, maybe they don't like corporate distros, or maybe they don't like snaps (to be frank I like sn
aps a lot more than flatpaks). But the bottom line is at the end of the day to me, Linux Mint is pointless. When I started, I recall about 5 years ago, I kept switc
hing to different OS not knowing that the only major real difference was really just the politics and desktop environments. I think a lot of newcomers are unaware of this fact and keep thinking that some how Arch is going to be vastly different as an overall experience than OpenSuse or Fedora...when they virtually use the same sort of packaging scheme. On top of that I can truly say that the best environment I've ever worked with is GNOME, and only two systems come into mind for me philosophically as a superior choice. The first system is Ubuntu, because everything works on it, I like snaps, I just wish they worked with my custom theme, never had a bad experience with snaps either. The second system is Manjaro, which is what I deem the more \"non-corporate\" distro because you have a vetting system that's handled by the community, and they're not psychotic about code of eihics and stuff like that. Other than that, it really sucks seeing people fall into a hivemind that Linux Mint is somehow a gamechanger, when it's really just Ubuntu."
    },
    {
```

## Rate Limiting

By default, the script waits 3 seconds between page requests to avoid overwhelming the server. This can be adjusted when initializing the archiver if needed.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT

## Acknowledgments

Originally developed for archiving threads from the Ubuntu Forums.
