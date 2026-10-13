# Eastern Bay Document Generator

Final version includes:
- Annexure A
- Annexure C
- Synchronization Certificate
- PDF and Word (.docx) download options

## Easiest demo on a Windows computer
1. Install Python 3.11+ from python.org if it is not already installed.
2. Extract this ZIP.
3. Double-click `run_windows.bat`.
4. Wait for the browser to open.
5. Choose the document, enter details, click Generate, then Download.

## Mac / Linux
Open Terminal in this folder and run:
`./run_mac_linux.sh`

## Phone installation
This package is a web app. To use it like an app on Android/iPhone, deploy the folder to a web host that supports Streamlit. Open the resulting HTTPS link in the phone browser and use **Add to Home screen / Install app**.

No uploaded customer details are sent anywhere by this code itself; where data goes depends on the hosting environment you choose.

## Appearance and location
- Use the Appearance switch to select White or Black. White uses the supplied solar photograph behind readable white panels; both themes use the supplied Eastern Bay logo.
- In Annexure C, edit District / City on Page 1. The value appears in both PDF and Word exports.
- Appearance changes the app only; official document exports retain their black text on white pages.
- Keep the bundled assets/ directory with the app when deploying.

## Checks
Install `requirements-dev.txt`, then run `python -m unittest test_app -v` to check all forms in both themes and the District / City PDF and Word exports.
