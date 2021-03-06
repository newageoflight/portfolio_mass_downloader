# Portfolio Mass Downloader

Does what it says on the tin. Will ask you to login to eMed with your credentials first, then downloads all your portfolio evidence to a folder called "downloaded" (yes, *all* of it).

Subdirectories are organised by evidence type, and then within that, the title of the evidence.

I've only tested it on my own computer with my own account so it might still be quite buggy. If you're having issues please raise them on the issues page or PM me on Facebook.

## Usage instructions

1. Download and run the .exe file from releases.
2. Once started, the program will ask you to log into eMed with your zID and password, so type these in.
3. Your portfolio will be downloaded into a folder called "downloaded" - sit back and enjoy the fireworks!

## Instructions for building from source

1. Download and install [Python 3.8.5](https://www.python.org/downloads/release/python-385/)
    - On Windows, you will also need to install [Git](https://git-scm.com/downloads)
2. Clone this repository from Github: `git clone https://github.com/newageoflight/portfolio_mass_downloader.git`
3. Navigate to the containing folder in the terminal: `cd portfolio_mass_downloader`
4. Create a new virtual environment in the code folder:
    - On Windows: `python -m venv .env`
    - On Mac or Linux: `python3 -m venv .env`
5. Activate the virtual environment
    - On Windows:
        - Command Prompt: `.env\Scripts\activate.bat`
        - PowerShell: `.env\Scripts\Activate.ps1`
    - On Mac or Linux: `source .env/bin/activate`
6. Install all the required packages:
    - On Windows: `pip install -r requirements.txt`
    - On Mac or Linux: `pip3 install -r requirements.txt` or `pip install -r requirements.txt`
7. Run pyinstaller: `pyinstaller -i unswmed.ico --onefile main.py --name portfolio-mass-dl`
8. A binary executable named `portfolio-mass-dl` should be ready under the `/dist` directory.
    - To run it on Mac or Linux, navigate to the containing directory (`cd dist`) and give it permission to run first (`chmod +x portfolio-mass-dl`).
    - For Mac you will need to sign the code: `codesign -s "-" portfolio-mass-dl`
    - Then you should be able to start it (`./portfolio-mass-dl`)
9. Deactivate the virtual environment: `deactivate`

## Instructions for running from source
Unfortunately this seems to be the only way to get the program to work on Mac.

Follow all the instructions under `Instructions for building from source`, just replace steps 7 and 8 with:
- Run this command: `python3 main.py`
