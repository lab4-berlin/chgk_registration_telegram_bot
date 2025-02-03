How to run:


```bash
#Install Python
sudo apt update
sudo apt install python3 python3-pip
sudo apt install python3-venv -y

#create virtual environment
python3 -m venv chgk-bot-env
source chgk-bot-env/bin/activate

#Install dependencies:
pip install python-telegram-bot sqlite3

#Run your bot with:
nohup python bot.py &

#Alternatevely: to keep it running even after disconnecting, use screen or tmux:
screen -S mybot
python bot.py
```
