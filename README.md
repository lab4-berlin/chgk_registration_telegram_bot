How to run:


```bash
#Install Python
sudo apt update
sudo apt install python3 python3-pip
sudo apt install python3-venv -y
sudo apt install sqlite3 libsqlite3-dev -y

#create virtual environment
python3 -m venv chgk-bot-env
source chgk-bot-env/bin/activate

#Install dependencies:
pip install python-telegram-bot

#Run your bot with:
git clone https://github.com/lab4-berlin/chgk_registration_telegram_bot.git
cd chgk_registration_telegram_bot
nohup python main.py &

#Alternatevely: to keep it running even after disconnecting, use screen or tmux:
screen -S mybot
python bot.py
```
